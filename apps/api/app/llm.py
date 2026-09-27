"""Chat model providers, tried in order until one is configured and answers.

Every provider speaks the OpenAI chat API, so adding one is a new entry in PROVIDERS
plus its env vars. LLM_PROVIDERS (comma-separated names) overrides the order.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMProvider:
    name: str
    key_env: str
    base_url_env: str
    default_base_url: str
    model_env: str
    default_model: str

    @property
    def api_key(self) -> str | None:
        return os.getenv(self.key_env) or None

    @property
    def base_url(self) -> str:
        return os.getenv(self.base_url_env) or self.default_base_url

    @property
    def model(self) -> str:
        return os.getenv(self.model_env) or self.default_model

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    def chat_model(self, temperature: float = 0.8, json_mode: bool = True):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=temperature,
            timeout=90,
            max_retries=1,
            model_kwargs={"response_format": {"type": "json_object"}} if json_mode else {},
        )


PROVIDERS = {
    "gemini": LLMProvider(
        name="gemini",
        key_env="GEMINI_API_KEY",
        base_url_env="GEMINI_BASE_URL",
        default_base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model_env="GEMINI_MODEL",
        default_model="gemini-2.5-flash",
    ),
    "deepseek": LLMProvider(
        name="deepseek",
        key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
        default_base_url="https://api.deepseek.com",
        model_env="DEEPSEEK_MODEL",
        default_model="deepseek-chat",
    ),
    # Any other OpenAI-compatible endpoint (OpenRouter, SiliconFlow, Qwen, a local Ollama, ...).
    "custom": LLMProvider(
        name="custom",
        key_env="LLM_API_KEY",
        base_url_env="LLM_BASE_URL",
        default_base_url="",
        model_env="LLM_MODEL",
        default_model="",
    ),
}

DEFAULT_ORDER = "gemini,deepseek,custom"


def configured_providers() -> list[LLMProvider]:
    order = os.getenv("LLM_PROVIDERS", DEFAULT_ORDER)
    names = [name.strip().lower() for name in order.split(",") if name.strip()]
    return [PROVIDERS[name] for name in names if name in PROVIDERS and PROVIDERS[name].is_configured]
