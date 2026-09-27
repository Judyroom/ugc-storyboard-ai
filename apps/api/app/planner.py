import json
import logging
import re
from typing import Any

from pydantic import ValidationError

from app.llm import LLMProvider, configured_providers
from app.prompts import fix_json_prompt, planner_system_prompt, planner_user_prompt
from app.schemas import Language, Orientation, Storyboard


logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2


class PlannerUnavailable(RuntimeError):
    pass


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Planner response did not contain JSON.")

    return json.loads(cleaned[start : end + 1])


async def _plan_with(
    provider: LLMProvider, user_prompt: str, language: Language, orientation: Orientation
) -> Storyboard:
    model = provider.chat_model()
    messages = [
        ("system", planner_system_prompt(language)),
        ("human", planner_user_prompt(user_prompt, language, orientation)),
    ]

    last_error: Exception | None = None
    for _ in range(MAX_ATTEMPTS):
        result = await model.ainvoke(messages)
        content = str(result.content)
        try:
            return Storyboard.model_validate(_extract_json(content))
        except (ValueError, ValidationError) as exc:
            last_error = exc
            # Show the model its own output and what was wrong with it, then ask again.
            messages += [("ai", content), ("human", fix_json_prompt(exc, language))]

    raise ValueError(f"invalid storyboard after {MAX_ATTEMPTS} attempts: {last_error}")


async def plan_storyboard(
    user_prompt: str, language: Language = "zh", orientation: Orientation = "portrait"
) -> tuple[Storyboard, str]:
    """Returns the storyboard and the name of the provider that produced it."""
    providers = configured_providers()
    if not providers:
        raise PlannerUnavailable("No LLM provider is configured.")

    for provider in providers:
        try:
            return await _plan_with(provider, user_prompt, language, orientation), provider.name
        except Exception:
            logger.exception("Planner provider %s failed", provider.name)

    raise PlannerUnavailable(f"All LLM providers failed: {', '.join(p.name for p in providers)}.")
