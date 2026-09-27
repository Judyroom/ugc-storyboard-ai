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
pip install -r apps/api/requirements-dev.txt
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

- `mock`: No LLM key is configured (or every LLM failed), so the backend returns a deterministic storyboard in the chosen language with placeholder frames.
- `partial`: Planner worked, but one or more media tools failed. The response still includes usable fallback images and warnings.
- `real`: Planner, a photo-style image for every scene, and TTS all completed.

The UI switches between 中文 and English from the header; the choice is also sent to the API so the storyboard is written in that language.

## Deployment

- Deploy `apps/web` to Vercel. Set `NEXT_PUBLIC_API_BASE_URL` to the public backend URL.
- Deploy `apps/api` to a Hugging Face Docker Space. Set `PUBLIC_BASE_URL`, `CORS_ORIGINS`, and whichever provider keys you have (see `apps/api/.env.example`).

## Built-in samples

The three "Try" briefs load a built-in storyboard instantly (line-sketch frames for 9:16 and 16:9, plus recorded zh/en voiceover) from `apps/web/public/samples`, without calling the API. Edit the copy in `apps/web/lib/samples.json`, then rebuild the assets:

```bash
python apps/api/scripts/build_samples.py
```
