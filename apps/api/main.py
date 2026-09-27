import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from app.image_providers import configured_image_providers
from app.llm import configured_providers
from app.schemas import GenerateRequest, GenerateResponse, Orientation
from app.workflow import generate_storyboard


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
logging.basicConfig(level=logging.INFO)

GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="UGC Storyboard AI", version="0.1.0")

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/generated", StaticFiles(directory=str(GENERATED_DIR)), name="generated")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/providers")
async def providers() -> dict[str, list[str]]:
    """Names of the providers that have credentials configured, in the order they are tried."""
    return {
        "llm": [provider.name for provider in configured_providers()],
        "image": [provider.name for provider in configured_image_providers()],
        "tts": ["edge-tts"],
    }


# Rough compositions matching the five mock shots: box on table, macro edge, person in scene,
# object in moving hand, product resting on a desk corner.
MOCK_SKETCHES = [
    '<line x1="0" y1="820" x2="900" y2="820"/><rect x="250" y="520" width="400" height="300" rx="10"/>'
    '<path d="M250 600 H650"/><path d="M450 520 C420 470 380 470 370 500 M450 520 C480 470 520 470 530 500"/>'
    '<path d="M700 250 L760 190 M700 330 L790 300" stroke-dasharray="14 12"/>',
    '<path d="M-20 900 C200 520 520 360 920 330"/><path d="M-20 980 C220 600 540 450 920 420"/>'
    '<circle cx="700" cy="250" r="40" stroke-dasharray="10 10"/><circle cx="170" cy="260" r="70" stroke-dasharray="10 10"/>',
    '<line x1="0" y1="760" x2="900" y2="760"/><circle cx="560" cy="330" r="80"/>'
    '<path d="M430 760 C430 560 470 440 560 430 C650 440 690 560 690 760"/><rect x="240" y="650" width="150" height="110" rx="8"/>',
    '<path d="M180 980 C260 760 380 660 520 640 L640 600"/><path d="M300 980 C360 820 460 740 600 720"/>'
    '<ellipse cx="610" cy="560" rx="120" ry="70"/><path d="M200 420 H360 M160 490 H330" stroke-dasharray="16 14"/>',
    '<line x1="0" y1="800" x2="900" y2="800"/><path d="M0 800 L260 620 H900"/><rect x="520" y="520" width="180" height="140" rx="10"/>'
    '<circle cx="230" cy="300" r="60" opacity="0.45"/><path d="M160 620 C160 470 190 390 230 380 C270 390 300 470 300 620" opacity="0.45"/>',
]


@app.get("/mock-assets/{asset_name}")
async def mock_asset(asset_name: str, orientation: Orientation = Query("portrait")) -> Response:
    scene_id = int("".join(character for character in asset_name if character.isdigit()) or "1")
    sketch = MOCK_SKETCHES[(scene_id - 1) % len(MOCK_SKETCHES)]
    # Sketches are drawn in a 900x1200 box; centre it on a 9:16 or 16:9 canvas.
    if orientation == "landscape":
        width, height, place = 1600, 900, "translate(462.5 0) scale(0.75)"
    else:
        width, height, place = 900, 1600, "translate(0 200)"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#e9e4d9"/>
  <g transform="{place}" fill="none" stroke="#8c8574" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">{sketch}</g>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")


@app.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest, request: Request) -> GenerateResponse:
    public_base_url = os.getenv("PUBLIC_BASE_URL")
    base_url = public_base_url or str(request.base_url).rstrip("/")
    return await generate_storyboard(payload.user_prompt, base_url, payload.language, payload.orientation)
