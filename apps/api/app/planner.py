import json
import os
import re
from typing import Any

from app.prompts import PLANNER_SYSTEM_PROMPT, planner_user_prompt
from app.schemas import Storyboard


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


async def plan_storyboard(user_prompt: str) -> Storyboard:
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured.")

    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", os.getenv("LLM_MODEL", "deepseek-chat")),
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", os.getenv("LLM_BASE_URL", "https://api.deepseek.com")),
        temperature=0.8,
    )
    result = await model.ainvoke(
        [
            ("system", PLANNER_SYSTEM_PROMPT),
            ("human", planner_user_prompt(user_prompt)),
        ]
    )
    payload = _extract_json(str(result.content))
    return Storyboard.model_validate(payload)
