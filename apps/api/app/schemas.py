from typing import Literal

from pydantic import BaseModel, Field, model_validator


GenerationMode = Literal["real", "partial", "mock"]
Language = Literal["zh", "en"]
Orientation = Literal["portrait", "landscape"]


class GenerateRequest(BaseModel):
    user_prompt: str = Field(..., min_length=2, max_length=280)
    language: Language = "zh"
    orientation: Orientation = "portrait"


class Scene(BaseModel):
    id: int
    timing_sec: int = Field(..., ge=1, le=15)
    script_text: str = Field(..., min_length=1)
    visual_description: str = Field(..., min_length=1)
    image_prompt: str = Field(..., min_length=1)
    image_url: str | None = None
    image_provider: str | None = None
    audio_url: str | None = None


class Storyboard(BaseModel):
    title: str
    total_duration_sec: int
    scenes: list[Scene] = Field(..., min_length=3, max_length=8)

    @model_validator(mode="after")
    def normalize(self) -> "Storyboard":
        # LLM output often has duplicate ids or a total that doesn't add up; derive both.
        for index, scene in enumerate(self.scenes, start=1):
            scene.id = index
        self.total_duration_sec = sum(scene.timing_sec for scene in self.scenes)
        return self


class GenerateResponse(Storyboard):
    mode: GenerationMode
    warnings: list[str] = Field(default_factory=list)
    source_prompt: str
    language: Language = "zh"
    orientation: Orientation = "portrait"
    planner_provider: str | None = None
