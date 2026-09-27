import pytest

from app import image_providers, media_tools, workflow
from app.image_providers import ImageChain, ProviderExhausted, configured_image_providers, sanitize_svg
from app.llm import configured_providers
from app.media_tools import narration_text, pick_voice
from app.schemas import Scene, Storyboard
from app.workflow import generate_storyboard


PROVIDER_ENV = (
    "LLM_PROVIDERS",
    "GEMINI_API_KEY",
    "DEEPSEEK_API_KEY",
    "LLM_API_KEY",
    "LLM_BASE_URL",
    "LLM_MODEL",
    "IMAGE_PROVIDERS",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
    "HF_TOKEN",
    "POLLINATIONS_TOKEN",
    "POLLINATIONS_ANONYMOUS",
)


def make_scene(scene_id: int, timing_sec: int = 5) -> dict:
    return {
        "id": scene_id,
        "timing_sec": timing_sec,
        "script_text": "旁白 [轻柔雨声]",
        "visual_description": "desk",
        "image_prompt": "a desk",
    }


def make_storyboard(count: int = 3) -> Storyboard:
    return Storyboard.model_validate(
        {"title": "t", "total_duration_sec": 0, "scenes": [make_scene(i) for i in range(1, count + 1)]}
    )


@pytest.fixture(autouse=True)
def no_credentials(monkeypatch, tmp_path):
    for name in PROVIDER_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(media_tools, "GENERATED_DIR", tmp_path)


@pytest.fixture
def fake_tts(monkeypatch):
    async def fake(scene: Scene, run_id: str, base_url: str, language=None):
        return f"{base_url}/generated/{run_id}/scene-{scene.id}.mp3", None

    monkeypatch.setattr(workflow, "generate_tts", fake)


@pytest.fixture
def fake_plan(monkeypatch):
    async def fake(_prompt: str, _language: str, _orientation: str):
        return make_storyboard(), "gemini"

    monkeypatch.setattr(workflow, "plan_storyboard", fake)


@pytest.mark.parametrize("language, needle", [("zh", "种草"), ("en", "first-look")])
async def test_generate_storyboard_falls_back_to_mock(language, needle, fake_tts):
    response = await generate_storyboard("一个北欧风格的奢侈品项链", "http://testserver", language)

    assert response.mode == "mock"
    assert response.language == language
    assert needle in response.title
    assert response.planner_provider is None
    assert response.total_duration_sec == sum(scene.timing_sec for scene in response.scenes)
    assert len(response.scenes) == 5
    assert all(scene.image_url for scene in response.scenes)
    assert all(scene.audio_url for scene in response.scenes)
    assert response.warnings


def test_storyboard_renumbers_ids_and_recomputes_total():
    storyboard = Storyboard.model_validate(
        {
            "title": "t",
            "total_duration_sec": 999,
            "scenes": [make_scene(1, 4), make_scene(1, 6), make_scene(7, 5)],
        }
    )

    assert [scene.id for scene in storyboard.scenes] == [1, 2, 3]
    assert storyboard.total_duration_sec == 15


def test_storyboard_rejects_runaway_scene_count():
    with pytest.raises(ValueError):
        make_storyboard(20)


def test_narration_strips_sound_cues_and_picks_voice():
    assert narration_text("[轻柔雨声] 我本来只是随手拆开看一眼【音效】") == "我本来只是随手拆开看一眼"
    assert pick_voice("我本来只是随手拆开", "en") == "zh-CN-XiaoxiaoNeural"
    assert pick_voice("I only meant to glance at it", "en") == "en-US-AvaNeural"


def test_llm_providers_follow_configured_keys_and_order(monkeypatch):
    assert configured_providers() == []

    monkeypatch.setenv("DEEPSEEK_API_KEY", "x")
    monkeypatch.setenv("GEMINI_API_KEY", "y")
    monkeypatch.setenv("LLM_API_KEY", "z")  # no base URL/model, so not usable
    assert [p.name for p in configured_providers()] == ["gemini", "deepseek"]

    monkeypatch.setenv("LLM_PROVIDERS", "deepseek,gemini")
    assert [p.name for p in configured_providers()] == ["deepseek", "gemini"]


def test_image_providers_follow_configured_keys(monkeypatch):
    assert configured_image_providers() == []

    monkeypatch.setenv("HF_TOKEN", "x")
    monkeypatch.setenv("CLOUDFLARE_ACCOUNT_ID", "a")
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "b")
    monkeypatch.setenv("GEMINI_API_KEY", "y")  # enables the sketch fallback
    assert [p.name for p in configured_image_providers()] == ["cloudflare", "huggingface", "sketch"]


def test_sanitize_svg_rejects_active_content():
    assert sanitize_svg('Here you go:\n<svg viewBox="0 0 10 10"><rect/></svg>').startswith("<svg")
    for bad in ("<svg><script>alert(1)</script></svg>", '<svg onload="x()"></svg>', "<svg><image href='http://x'/></svg>"):
        with pytest.raises(ValueError):
            sanitize_svg(bad)


class FakeProvider(image_providers.ImageProvider):
    def __init__(self, name: str, error: Exception | None = None):
        self.name = name
        self.error = error
        self.calls = 0

    def is_configured(self) -> bool:
        return True

    async def generate(self, scene, out_dir, orientation):
        self.calls += 1
        self.orientation = orientation
        if self.error:
            raise self.error
        return f"scene-{scene.id}.jpg"


async def test_image_chain_falls_through_and_skips_exhausted(monkeypatch, tmp_path):
    quota = FakeProvider("cloudflare", ProviderExhausted("429"))
    flaky = FakeProvider("huggingface", RuntimeError("boom"))
    good = FakeProvider("pollinations")
    monkeypatch.setattr(image_providers, "configured_image_providers", lambda: [quota, flaky, good])

    chain = ImageChain()
    for scene in make_storyboard().scenes:
        assert await chain.generate(scene, tmp_path) == (f"scene-{scene.id}.jpg", "pollinations")

    assert quota.calls == 1  # not retried after the quota error
    assert flaky.calls == 3
    assert chain.exhausted == {"cloudflare"}


async def test_media_uses_placeholders_when_no_image_provider(fake_plan, fake_tts):
    first = await generate_storyboard("一个北欧风格的奢侈品项链", "http://testserver")
    second = await generate_storyboard("一个北欧风格的奢侈品项链", "http://testserver")

    assert first.mode == "partial"
    assert first.planner_provider == "gemini"
    assert all(scene.image_provider == "mock" for scene in first.scenes)
    assert first.scenes[0].image_url.endswith("orientation=portrait")
    assert first.scenes[0].audio_url != second.scenes[0].audio_url  # isolated per run
    assert sum("No image provider" in warning for warning in first.warnings) == 1


async def test_media_is_real_when_every_scene_gets_a_photo(monkeypatch, fake_plan, fake_tts):
    provider = FakeProvider("cloudflare")
    monkeypatch.setattr(image_providers, "configured_image_providers", lambda: [provider])

    response = await generate_storyboard("a travel skincare kit", "http://testserver", "en", "landscape")

    assert response.mode == "real"
    assert response.orientation == "landscape"
    assert provider.orientation == "landscape"
    assert response.warnings == []
    assert response.scenes[0].image_url.endswith("/scene-1.jpg")
    assert {scene.image_provider for scene in response.scenes} == {"cloudflare"}


def test_planner_prompt_carries_framing():
    from app.prompts import planner_user_prompt, sketch_system_prompt

    assert "9:16" in planner_user_prompt("x", "zh", "portrait")
    assert "16:9" in planner_user_prompt("x", "en", "landscape")
    assert 'viewBox="0 0 1600 900"' in sketch_system_prompt("landscape")
