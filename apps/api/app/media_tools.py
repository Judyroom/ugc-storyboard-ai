import os
import re
from pathlib import Path

from app.schemas import Scene


GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "storyboard"


async def generate_image(scene: Scene, user_prompt: str, base_url: str) -> tuple[str | None, str | None]:
    token = os.getenv("HF_TOKEN")
    if not token:
        return None, "HF_TOKEN is not configured; skipped image generation."

    try:
        from huggingface_hub import InferenceClient

        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        client = InferenceClient(token=token)
        image = client.text_to_image(
            scene.image_prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )
        filename = f"{_slugify(user_prompt)}-scene-{scene.id}.png"
        image_path = GENERATED_DIR / filename
        image.save(image_path)
        return f"{base_url}/generated/{filename}", None
    except Exception as exc:
        return None, f"Image generation failed for scene {scene.id}: {exc}"


async def generate_tts(scene: Scene, user_prompt: str, base_url: str) -> tuple[str | None, str | None]:
    try:
        import edge_tts

        GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{_slugify(user_prompt)}-scene-{scene.id}.mp3"
        audio_path = GENERATED_DIR / filename
        communicate = edge_tts.Communicate(scene.script_text, voice="zh-CN-XiaoxiaoNeural")
        await communicate.save(str(audio_path))
        return f"{base_url}/generated/{filename}", None
    except Exception as exc:
        return None, f"TTS generation failed for scene {scene.id}: {exc}"
