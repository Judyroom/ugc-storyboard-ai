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

The two apps deploy separately. **Pushing to GitHub only updates the web app; the API has to be pushed to Hugging Face on its own.**

| | Web (`apps/web`) | API (`apps/api`) |
| --- | --- | --- |
| Host | Vercel | Hugging Face Docker Space |
| Live URL | https://ugc-storyboard-ai.vercel.app | https://heyjudy-ugc-storyboard-backend.hf.space |
| Deploys when | a commit lands on `main` (other branches get a preview URL) | you run `bash scripts/deploy-api-to-hf.sh` |
| Config | `NEXT_PUBLIC_API_BASE_URL` = the API URL above | Space Settings → Variables and secrets |

### Web on Vercel

The Vercel project is connected to this GitHub repo with `apps/web` as its root. Push to `main` for production; push a branch to get a preview deploy. The only environment variable is `NEXT_PUBLIC_API_BASE_URL`. Never put LLM or image keys in Vercel: they belong to the API, and anything prefixed `NEXT_PUBLIC_` is shipped to the browser.

### API on Hugging Face

The Space repo holds the contents of `apps/api` at its root (a copy, not a subfolder), so it is updated with a script rather than a plain push:

```bash
git remote add hf https://huggingface.co/spaces/heyjudy/ugc-storyboard-backend  # once
bash scripts/deploy-api-to-hf.sh
```

The script takes `apps/api` as committed on your current `HEAD` (leaving out tests and scripts), shows what will change, asks before pushing, and pushes on top of the Space's `main`. The Space then rebuilds in a few minutes and the API is briefly unavailable. The first push asks for credentials: your HF username, and an HF access token with write access as the password.

Space settings (Settings → Variables and secrets):

- **Secrets** (private): `DEEPSEEK_API_KEY` or `GEMINI_API_KEY`, plus optional image keys such as `HF_TOKEN` or `CLOUDFLARE_ACCOUNT_ID` + `CLOUDFLARE_API_TOKEN`. See `apps/api/.env.example` for every slot.
- **Variables** (public): `PUBLIC_BASE_URL` (the API URL above, used to build media links), `CORS_ORIGINS` (the production web URL), and `CORS_ORIGIN_REGEX` for Vercel preview URLs, which change on every deploy:
  `https://ugc-storyboard-[a-z0-9]+-ruyu-s-projects\.vercel\.app`

Things to know:

- The Hugging Face proxy adds permissive CORS headers to every Space response, so on HF the CORS settings don't actually restrict who can call the API. There is no rate limit, so anyone who finds the URL can spend the LLM quota.
- Free Spaces sleep when idle. If one shows `Runtime error: Scheduling failure`, use **Restart space**; that's a scheduling hiccup, not a code error. Avoid **Factory rebuild** unless dependencies really need reinstalling.
- `GET /providers` on the API lists which LLM and image providers have keys, which is the quickest way to check the Space picked up new secrets.

## Built-in samples

The three "Try" briefs load a built-in storyboard instantly (line-sketch frames for 9:16 and 16:9, plus recorded zh/en voiceover) from `apps/web/public/samples`, without calling the API. Edit the copy in `apps/web/lib/samples.json`, then rebuild the assets:

```bash
python apps/api/scripts/build_samples.py
```
