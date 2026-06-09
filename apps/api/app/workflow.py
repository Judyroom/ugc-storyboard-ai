from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.media_tools import generate_image, generate_tts
from app.mock_data import mock_storyboard
from app.planner import plan_storyboard
from app.refiner import refine_storyboard
from app.schemas import GenerateResponse, Storyboard


class WorkflowState(TypedDict, total=False):
    user_prompt: str
    base_url: str
    storyboard: Storyboard
    warnings: list[str]
    mode: str


async def planner_node(state: WorkflowState) -> WorkflowState:
    warnings = list(state.get("warnings", []))
    try:
        storyboard = await plan_storyboard(state["user_prompt"])
        return {**state, "storyboard": storyboard, "warnings": warnings, "mode": "real"}
    except Exception as exc:
        fallback = mock_storyboard(state["user_prompt"], state["base_url"])
        warnings.extend(fallback.warnings)
        warnings.append(f"Planner fallback: {exc}")
        return {
            **state,
            "storyboard": Storyboard.model_validate(fallback.model_dump()),
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

    if state.get("mode") == "mock":
        return state

    scenes = []
    for index, scene in enumerate(storyboard.scenes, start=1):
        image_url, image_warning = await generate_image(scene, state["user_prompt"], state["base_url"])
        audio_url, audio_warning = await generate_tts(scene, state["user_prompt"], state["base_url"])

        if image_warning:
            warnings.append(image_warning)
        if audio_warning:
            warnings.append(audio_warning)

        scenes.append(
            scene.model_copy(
                update={
                    "image_url": image_url or f"{state['base_url']}/mock-assets/scene-{((index - 1) % 5) + 1}.svg",
                    "audio_url": audio_url,
                }
            )
        )

    mode = "partial" if warnings else "real"
    return {
        **state,
        "storyboard": storyboard.model_copy(update={"scenes": scenes}),
        "warnings": warnings,
        "mode": mode,
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


async def generate_storyboard(user_prompt: str, base_url: str) -> GenerateResponse:
    state = await WORKFLOW.ainvoke(
        {
            "user_prompt": user_prompt,
            "base_url": base_url.rstrip("/"),
            "warnings": [],
        }
    )
    storyboard = state["storyboard"]
    return GenerateResponse(
        **storyboard.model_dump(),
        mode=state["mode"],
        warnings=state.get("warnings", []),
        source_prompt=user_prompt,
    )
