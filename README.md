# UGC Storyboard AI Mini Demo

One sentence in, agentic UGC storyboard out. This repo contains a Next.js frontend and a FastAPI backend that follows the PRD workflow: planner, refiner, image generation, TTS, and a reliable mock fallback.

## Project Structure

```text
apps/
  web/   Next.js 15 App Router frontend
  api/   FastAPI + LangGraph backend
```

## Local Setup

Install frontend dependencies:

```bash
npm --prefix apps/web install
```

Create a Python environment and install backend dependencies:

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r apps/api/requirements.txt
```

Copy environment templates:

```bash
copy apps\web\.env.example apps\web\.env.local
copy apps\api\.env.example apps\api\.env
```

Run the API:

```bash
npm run dev:api
```

Run the web app in another terminal:

```bash
npm run dev:web
```

Open `http://localhost:3000`.

## Generation Modes

- `mock`: No generation keys are configured, so the backend returns deterministic storyboard data and SVG mock frames.
- `partial`: Planner worked, but one or more media tools failed. The response still includes usable fallback images and warnings.
- `real`: Planner, image generation, and TTS all completed.

## Deployment

- Deploy `apps/web` to Vercel. Set `NEXT_PUBLIC_API_BASE_URL` to the public backend URL.
- Deploy `apps/api` to a Hugging Face Docker Space. Set `PUBLIC_BASE_URL`, `CORS_ORIGINS`, `DEEPSEEK_API_KEY`, and optional `HF_TOKEN`.
