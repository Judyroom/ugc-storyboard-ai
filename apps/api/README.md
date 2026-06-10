---
title: UGC Storyboard API
emoji: 🎬
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
short_description: Agentic UGC storyboard FastAPI demo
---

# UGC Storyboard API

FastAPI backend for the mini demo. It exposes `POST /generate` and returns a UGC storyboard with real generation when credentials are configured, or a deterministic mock fallback when they are not.

## Environment

- `DEEPSEEK_API_KEY`: Enables DeepSeek planner generation.
- `DEEPSEEK_BASE_URL`: Optional OpenAI-compatible base URL. Defaults to `https://api.deepseek.com`.
- `DEEPSEEK_MODEL`: Optional planner model. Defaults to `deepseek-chat`.
- `HF_TOKEN`: Enables FLUX.1-schnell image generation through Hugging Face.
- `PUBLIC_BASE_URL`: Public API URL used to build generated media links.
- `CORS_ORIGINS`: Comma-separated frontend origins.
