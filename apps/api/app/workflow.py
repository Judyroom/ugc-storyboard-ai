import asyncio
import logging
import os
import uuid
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.image_providers import ImageChain
from app.media_tools import cleanup_generated, generate_tts, run_dir
from app.mock_data import mock_storyboard, placeholder_url
from app.planner import PlannerUnavailable, plan_storyboard
from app.refiner import refine_storyboard
from app.schemas import GenerateResponse, Language, Orientation, Scene, Storyboard


logger = logging.getLogger(__name__)

# Caps parallel image calls so a 7-scene board doesn't trip provider rate limits.
IMAGE_CONCURRENCY = int(os.getenv("IMAGE_CONCURRENCY", "3"))

# Providers that return a photo-style frame; anything else counts as a degraded result.
PHOTO_PROVIDERS = {"cloudflare", "huggingface", "pollinations"}


class WorkflowState(TypedDict, total=False):
    user_prompt: str
    language: Language
    orientation: Orientation
    base_url: str
    run_id: str
    storyboard: Storyboard
    planner_provider: str | None
    warnings: list[str]
    mode: str


async def planner_node(state: WorkflowState) -> WorkflowState:
    warnings = list(state.get("warnings", []))
    try:
        storyboard, provider = await plan_storyboard(state["user_prompt"], state["language"], state["orientation"])
        return {**state, "storyboard": storyboard, "planner_provider": provider, "warnings": warnings, "mode": "real"}
    except Exception as exc:
        if not isinstance(exc, PlannerUnavailable):
            logger.exception("Planner failed; falling back to mock storyboard")
        fallback = mock_storyboard(state["user_prompt"], state["base_url"], state["language"], state["orientation"])
        warnings.extend(fallback.warnings)
        warnings.append(f"Planner fallback: {exc}")
        return {
            **state,
            "storyboard": Storyboard.model_validate(fallback.model_dump()),
            "planner_provider": None,
            "warnings": warnings,
            "mode": "mock",
        }


async def refiner_node(state: WorkflowState) -> WorkflowState:
    if state.get("mode") == "mock":
        return state

    return {**state, "storyboard": refine_storyboard(state["storyboard"])}


async def media_node(state: WorkflowState) -> WorkflowState:
    storyboard = state["storyboard"]
    warnings = list(state.get("warnings", []))

    base_url = state["base_url"]
    if state.get("mode") == "mock":
        # Voice is free, so even the demo storyboard gets a playable voiceover.
        voiced = await asyncio.gather(
            *(generate_tts(scene, state["run_id"], base_url, state["language"]) for scene in storyboard.scenes)
        )
        scenes = [scene.model_copy(update={"audio_url": url}) for scene, (url, _) in zip(storyboard.scenes, voiced)]
        return {**state, "storyboard": storyboard.model_copy(update={"scenes": scenes})}

    run_id = state["run_id"]
    out_dir = run_dir(run_id)
    images = ImageChain(state["orientation"])
    image_slots = asyncio.Semaphore(IMAGE_CONCURRENCY)

    if not images.providers:
        warnings.append("No image provider is configured; using placeholder frames.")

    async def image_task(scene: Scene) -> tuple[str, str] | None:
        async with image_slots:
            return await images.generate(scene, out_dir)

    async def build_scene(index: int, scene: Scene) -> tuple[Scene, list[str]]:
        image_result, (audio_url, audio_warning) = await asyncio.gather(
            image_task(scene),
            generate_tts(scene, run_id, base_url, state["language"]),
        )
        scene_warnings = [audio_warning] if audio_warning else []
        if image_result:
            filename, provider = image_result
            image_url = f"{base_url}/generated/{run_id}/{filename}"
        else:
            provider = "mock"
            image_url = placeholder_url(base_url, index, state["orientation"])
            if images.providers:
                scene_warnings.append(f"All image providers failed for scene {scene.id}; using a placeholder.")

        updated = scene.model_copy(
            update={"image_url": image_url, "image_provider": provider, "audio_url": audio_url}
        )
        return updated, scene_warnings

    results = await asyncio.gather(
        *(build_scene(index, scene) for index, scene in enumerate(storyboard.scenes, start=1))
    )
    scenes = [scene for scene, _ in results]
    for _, scene_warnings in results:
        warnings.extend(scene_warnings)
    if images.exhausted:
        warnings.append(f"Quota or auth limit hit: {', '.join(sorted(images.exhausted))}.")
    if any(scene.image_provider == "sketch" for scene in scenes):
        warnings.append("Some frames are LLM-drawn sketches because no photo provider succeeded.")

    all_photos = all(scene.image_provider in PHOTO_PROVIDERS for scene in scenes)
    all_audio = all(scene.audio_url for scene in scenes)
    return {
        **state,
        "storyboard": storyboard.model_copy(update={"scenes": scenes}),
        "warnings": list(dict.fromkeys(warnings)),
        "mode": "real" if all_photos and all_audio else "partial",
    }


def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("planner", planner_node)
    graph.add_node("refiner", refiner_node)
    graph.add_node("media", media_node)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "refiner")
    graph.add_edge("refiner", "media")
    graph.add_edge("media", END)
    return graph.compile()


WORKFLOW = build_graph()


async def generate_storyboard(
    user_prompt: str, base_url: str, language: Language = "zh", orientation: Orientation = "portrait"
) -> GenerateResponse:
    await asyncio.to_thread(cleanup_generated)
    state = await WORKFLOW.ainvoke(
        {
            "user_prompt": user_prompt,
            "language": language,
            "orientation": orientation,
            "base_url": base_url.rstrip("/"),
            "run_id": uuid.uuid4().hex,
            "warnings": [],
        }
    )
    storyboard = state["storyboard"]
    return GenerateResponse(
        **storyboard.model_dump(),
        mode=state["mode"],
        warnings=state.get("warnings", []),
        source_prompt=user_prompt,
        language=language,
        orientation=orientation,
        planner_provider=state.get("planner_provider"),
    )
