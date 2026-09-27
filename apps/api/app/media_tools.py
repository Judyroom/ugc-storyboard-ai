import os
import re
import shutil
import time
from pathlib import Path

from app.schemas import Language, Scene


GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
GENERATED_TTL_SEC = int(os.getenv("GENERATED_TTL_SEC", str(6 * 60 * 60)))
VOICES: dict[Language, str] = {
    "zh": os.getenv("TTS_VOICE_ZH", "zh-CN-XiaoxiaoNeural"),
    "en": os.getenv("TTS_VOICE_EN", "en-US-AvaNeural"),
}

# Sound cues like [轻柔雨声] are stage directions for the editor, not narration.
_STAGE_DIRECTION = re.compile(r"\[[^\]]*\]|【[^】]*】|（[^）]*）")
_CJK = re.compile(r"[一-鿿]")


def narration_text(script_text: str) -> str:
    return re.sub(r"\s+", " ", _STAGE_DIRECTION.sub("", script_text)).strip()


def pick_voice(text: str, language: Language | None = None) -> str:
    # Chinese narration always needs the Chinese voice, even in an English session.
    if _CJK.search(text):
        return VOICES["zh"]
    return VOICES[language or "en"]


def run_dir(run_id: str) -> Path:
    path = GENERATED_DIR / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def cleanup_generated(max_age_sec: int = GENERATED_TTL_SEC) -> None:
    if not GENERATED_DIR.exists():
        return

    cutoff = time.time() - max_age_sec
    for path in GENERATED_DIR.iterdir():
        if path.is_dir() and path.stat().st_mtime < cutoff:
            shutil.rmtree(path, ignore_errors=True)


async def generate_tts(
    scene: Scene, run_id: str, base_url: str, language: Language | None = None
) -> tuple[str | None, str | None]:
    text = narration_text(scene.script_text)
    if not text:
        return None, f"Scene {scene.id} has no narration to voice."

    try:
        import edge_tts

        filename = f"scene-{scene.id}.mp3"
        communicate = edge_tts.Communicate(text, voice=pick_voice(text, language))
        await communicate.save(str(run_dir(run_id) / filename))
        return f"{base_url}/generated/{run_id}/{filename}", None
    except Exception as exc:
        return None, f"TTS generation failed for scene {scene.id} ({type(exc).__name__})."
