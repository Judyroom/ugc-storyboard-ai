import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from app.schemas import GenerateRequest, GenerateResponse
from app.workflow import generate_storyboard


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/generated", StaticFiles(directory=str(GENERATED_DIR)), name="generated")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/mock-assets/{asset_name}")
async def mock_asset(asset_name: str) -> Response:
    scene_id = "".join(character for character in asset_name if character.isdigit()) or "1"
    palette = [
        ("#09090b", "#a855f7", "#f5f3ff"),
        ("#111827", "#22d3ee", "#ecfeff"),
        ("#0f172a", "#f97316", "#fff7ed"),
        ("#18181b", "#84cc16", "#f7fee7"),
        ("#020617", "#f43f5e", "#fff1f2"),
    ]
    bg, accent, ink = palette[(int(scene_id) - 1) % len(palette)]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="900" viewBox="0 0 1280 900">
  <defs>
    <radialGradient id="glow" cx="65%" cy="35%" r="65%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.72"/>
      <stop offset="48%" stop-color="{accent}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{bg}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1280" height="900" fill="{bg}"/>
  <rect width="1280" height="900" fill="url(#glow)"/>
  <rect x="170" y="170" width="940" height="560" rx="28" fill="rgba(255,255,255,0.07)" stroke="rgba(255,255,255,0.22)"/>
  <circle cx="390" cy="380" r="104" fill="{accent}" opacity="0.78"/>
  <rect x="540" y="312" width="355" height="38" rx="19" fill="{ink}" opacity="0.92"/>
  <rect x="540" y="382" width="460" height="24" rx="12" fill="{ink}" opacity="0.54"/>
  <rect x="540" y="435" width="385" height="24" rx="12" fill="{ink}" opacity="0.36"/>
  <text x="190" y="690" font-family="Arial, sans-serif" font-size="28" fill="{ink}" opacity="0.85">UGC storyboard mock frame {scene_id}</text>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")


@app.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest, request: Request) -> GenerateResponse:
    public_base_url = os.getenv("PUBLIC_BASE_URL")
    base_url = public_base_url or str(request.base_url).rstrip("/")
    return await generate_storyboard(payload.user_prompt, base_url)
