import pytest

from app.workflow import generate_storyboard


@pytest.mark.asyncio
async def test_generate_storyboard_falls_back_to_mock(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)

    response = await generate_storyboard("一个北欧风格的奢侈品项链", "http://testserver")

    assert response.mode == "mock"
    assert response.source_prompt == "一个北欧风格的奢侈品项链"
    assert response.total_duration_sec == sum(scene.timing_sec for scene in response.scenes)
    assert len(response.scenes) == 5
    assert all(scene.image_url for scene in response.scenes)
    assert response.warnings
