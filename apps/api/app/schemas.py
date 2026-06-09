from typing import Literal

from pydantic import BaseModel, Field


GenerationMode = Literal["real", "partial", "mock"]


class GenerateRequest(BaseModel):
    user_prompt: str = Field(..., min_length=2, max_length=280)


class Scene(BaseModel):
    id: int
    timing_sec: int
    script_text: str
    visual_description: str
    image_prompt: str
    image_url: str | None = None
    audio_url: str | None = None


class Storyboard(BaseModel):
    title: str
    total_duration_sec: int
    scenes: list[Scene]


class GenerateResponse(Storyboard):
    mode: GenerationMode
    warnings: list[str] = Field(default_factory=list)
    source_prompt: str
