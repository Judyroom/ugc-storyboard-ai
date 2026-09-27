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

Every provider is optional and skipped when its key is missing. See `.env.example` for all slots.

- Text LLM, tried in `LLM_PROVIDERS` order: `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, or any OpenAI-compatible endpoint via `LLM_API_KEY` + `LLM_BASE_URL` + `LLM_MODEL`. None configured: mock storyboard.
- Images, tried per scene in `IMAGE_PROVIDERS` order: Cloudflare Workers AI (`CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN`), Hugging Face (`HF_TOKEN`), Pollinations (`POLLINATIONS_TOKEN` or `POLLINATIONS_ANONYMOUS=1`), then `sketch` (the text LLM draws an SVG line sketch). None succeed: placeholder frames.
- Voice: edge-tts, no key. Override voices with `TTS_VOICE_ZH` / `TTS_VOICE_EN`.
- `PUBLIC_BASE_URL`: Public API URL used to build generated media links.
- `CORS_ORIGINS`: Comma-separated frontend origins.

`GET /providers` lists which providers are configured, in the order they are tried.
