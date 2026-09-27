"""Image providers, tried in order for every scene until one returns a frame.

Each provider is skipped when its env vars are missing, so the chain degrades to
whatever is configured. IMAGE_PROVIDERS (comma-separated names) overrides the order.
Adding a provider: subclass ImageProvider, implement is_configured/generate, register it.
"""

import asyncio
import base64
import logging
import os
import re
from pathlib import Path
from urllib.parse import quote

import httpx

from app.llm import configured_providers
from app.prompts import sketch_system_prompt, sketch_user_prompt
from app.schemas import Orientation, Scene


logger = logging.getLogger(__name__)

DEFAULT_ORDER = "cloudflare,huggingface,pollinations,sketch"
# Width/height per orientation (multiples of 16 for FLUX). Providers that ignore size get cover-cropped in the UI.
SIZES: dict[Orientation, tuple[int, int]] = {
    "portrait": (720, 1280),
    "landscape": (1280, 720),
}
HTTP_TIMEOUT = httpx.Timeout(90.0, connect=10.0)


class ProviderExhausted(Exception):
    """Quota or auth failure: don't try this provider again for the rest of the run."""


class ImageProvider:
    name: str

    def is_configured(self) -> bool:
        raise NotImplementedError

    async def generate(self, scene: Scene, out_dir: Path, orientation: Orientation) -> str:
        """Writes the frame into out_dir and returns its filename."""
        raise NotImplementedError


def _raise_for_status(provider: str, response: httpx.Response) -> None:
    if response.status_code in (401, 402, 403, 429):
        raise ProviderExhausted(f"{provider} returned HTTP {response.status_code}")
    response.raise_for_status()


class CloudflareProvider(ImageProvider):
    name = "cloudflare"

    def is_configured(self) -> bool:
        return bool(os.getenv("CLOUDFLARE_ACCOUNT_ID") and os.getenv("CLOUDFLARE_API_TOKEN"))

    async def generate(self, scene: Scene, out_dir: Path, orientation: Orientation) -> str:
        model = os.getenv("CLOUDFLARE_IMAGE_MODEL", "@cf/black-forest-labs/flux-1-schnell")
        url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/ai/run/{model}"
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}"},
                json={"prompt": scene.image_prompt[:2048], "steps": int(os.getenv("CLOUDFLARE_STEPS", "4"))},
            )
        _raise_for_status(self.name, response)
        image_b64 = response.json()["result"]["image"]
        filename = f"scene-{scene.id}.jpg"
        (out_dir / filename).write_bytes(base64.b64decode(image_b64))
        return filename


class HuggingFaceProvider(ImageProvider):
    name = "huggingface"

    def is_configured(self) -> bool:
        return bool(os.getenv("HF_TOKEN"))

    async def generate(self, scene: Scene, out_dir: Path, orientation: Orientation) -> str:
        from huggingface_hub import AsyncInferenceClient
        from huggingface_hub.errors import HfHubHTTPError

        client = AsyncInferenceClient(token=os.environ["HF_TOKEN"])
        try:
            image = await client.text_to_image(
                scene.image_prompt,
                model=os.getenv("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell"),
                width=SIZES[orientation][0],
                height=SIZES[orientation][1],
            )
        except HfHubHTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status in (401, 402, 403, 429):
                raise ProviderExhausted(f"huggingface returned HTTP {status}") from exc
            raise
        filename = f"scene-{scene.id}.png"
        await asyncio.to_thread(image.save, out_dir / filename)
        return filename


class PollinationsProvider(ImageProvider):
    name = "pollinations"

    def is_configured(self) -> bool:
        # Anonymous use is rate limited hard, so it is opt-in.
        return bool(os.getenv("POLLINATIONS_TOKEN") or os.getenv("POLLINATIONS_ANONYMOUS") == "1")

    async def generate(self, scene: Scene, out_dir: Path, orientation: Orientation) -> str:
        base_url = os.getenv("POLLINATIONS_BASE_URL", "https://image.pollinations.ai/prompt").rstrip("/")
        params = {
            "width": SIZES[orientation][0],
            "height": SIZES[orientation][1],
            "model": os.getenv("POLLINATIONS_MODEL", "flux"),
            "nologo": "true",
        }
        headers = {}
        if token := os.getenv("POLLINATIONS_TOKEN"):
            headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(
                f"{base_url}/{quote(scene.image_prompt[:1500])}", params=params, headers=headers
            )
        _raise_for_status(self.name, response)
        if not response.headers.get("content-type", "").startswith("image/"):
            raise ValueError("pollinations did not return an image")
        filename = f"scene-{scene.id}.jpg"
        (out_dir / filename).write_bytes(response.content)
        return filename


_SVG_BLOCK = re.compile(r"<svg\b.*?</svg>", re.IGNORECASE | re.DOTALL)
_SVG_UNSAFE = re.compile(
    r"<\s*(script|foreignObject|iframe|image|use)\b|\bon\w+\s*=|javascript:|href\s*=",
    re.IGNORECASE,
)


def sanitize_svg(text: str) -> str:
    match = _SVG_BLOCK.search(text)
    if not match:
        raise ValueError("sketch response did not contain an <svg> element")
    svg = match.group(0)
    if _SVG_UNSAFE.search(svg):
        raise ValueError("sketch SVG contained disallowed markup")
    return svg


class SketchProvider(ImageProvider):
    """Line-art storyboard frame drawn by the text LLM as SVG. Costs only text tokens."""

    name = "sketch"

    def is_configured(self) -> bool:
        return os.getenv("SKETCH_ENABLED", "1") == "1" and bool(configured_providers())

    async def generate(self, scene: Scene, out_dir: Path, orientation: Orientation) -> str:
        last_error: Exception | None = None
        for llm in configured_providers():
            try:
                result = await llm.chat_model(temperature=0.4, json_mode=False).ainvoke(
                    [
                        ("system", sketch_system_prompt(orientation)),
                        ("human", sketch_user_prompt(scene.visual_description, scene.image_prompt)),
                    ]
                )
                svg = sanitize_svg(str(result.content))
                filename = f"scene-{scene.id}.svg"
                (out_dir / filename).write_text(svg, encoding="utf-8")
                return filename
            except Exception as exc:
                last_error = exc
                logger.warning("Sketch via %s failed: %s", llm.name, exc)
        raise ValueError(f"all sketch attempts failed: {last_error}")


PROVIDERS: dict[str, ImageProvider] = {
    provider.name: provider
    for provider in (CloudflareProvider(), HuggingFaceProvider(), PollinationsProvider(), SketchProvider())
}


def configured_image_providers() -> list[ImageProvider]:
    order = os.getenv("IMAGE_PROVIDERS", DEFAULT_ORDER)
    names = [name.strip().lower() for name in order.split(",") if name.strip()]
    return [PROVIDERS[name] for name in names if name in PROVIDERS and PROVIDERS[name].is_configured()]


class ImageChain:
    """One per run, so a provider that hits its quota is skipped for the remaining scenes."""

    def __init__(self, orientation: Orientation = "portrait") -> None:
        self.orientation = orientation
        self.providers = configured_image_providers()
        self.exhausted: set[str] = set()

    async def generate(self, scene: Scene, out_dir: Path) -> tuple[str, str] | None:
        for provider in self.providers:
            if provider.name in self.exhausted:
                continue
            try:
                return await provider.generate(scene, out_dir, self.orientation), provider.name
            except ProviderExhausted as exc:
                logger.warning("%s exhausted: %s", provider.name, exc)
                self.exhausted.add(provider.name)
            except Exception:
                logger.exception("Image provider %s failed for scene %s", provider.name, scene.id)
        return None
