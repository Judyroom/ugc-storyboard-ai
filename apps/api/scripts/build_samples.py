"""Builds the built-in sample assets the web app loads without calling the API.

Reads apps/web/lib/samples.json and writes into apps/web/public/samples/<id>/:
  scene-N-portrait.svg / scene-N-landscape.svg   line-sketch frames (9:16 and 16:9)
  <lang>/scene-N.mp3                             edge-tts voiceover per language

Run from the repo root:  python apps/api/scripts/build_samples.py [--skip-audio]
"""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.media_tools import narration_text, pick_voice  # noqa: E402

SAMPLES_JSON = ROOT / "apps" / "web" / "lib" / "samples.json"
OUT_DIR = ROOT / "apps" / "web" / "public" / "samples"

PAPER = "#e9e4d9"
INK = "#8c8574"
FAINT = "#c9c1b0"
TINT = "#ddd6c6"

# Each drawing lives in a 560x560 box; the wrapper centres and scales it for either orientation.
# Default style: no fill, INK stroke, width 5. Override per element with fill/stroke attributes.
SKETCHES: dict[str, list[str]] = {
    "necklace": [
        # 1. Box opening on the table, blind shadows from the left, hand from bottom right.
        f"""
        <path d="M0 90 L150 0 M0 190 L310 0 M0 290 L470 0" stroke="{FAINT}" stroke-width="14"/>
        <rect x="140" y="230" width="270" height="190" rx="10" fill="{TINT}"/>
        <path d="M140 230 L165 130 H435 L410 230"/>
        <path d="M185 330 C225 295 265 360 305 325 S370 300 380 335"/>
        <path d="M560 470 C500 450 460 420 430 385 C415 368 395 372 400 392 C410 430 450 480 520 560"/>
        """,
        # 2. Macro pebble pendant between two fingertips, chain rising out of frame.
        f"""
        <path d="M60 0 V560 M120 0 V560 M440 0 V560 M500 0 V560" stroke="{FAINT}" stroke-width="3"/>
        <path d="M245 205 C235 140 250 70 262 0 M315 205 C325 140 310 70 298 0"/>
        <ellipse cx="280" cy="300" rx="115" ry="92" fill="{TINT}"/>
        <path d="M215 262 C240 238 280 232 312 244" stroke="#f4f0e7" stroke-width="10"/>
        <path d="M0 345 C70 335 125 340 158 312 C172 298 160 282 140 285 C95 290 40 296 0 300"/>
        <path d="M560 345 C490 335 435 340 402 312 C388 298 400 282 420 285 C465 290 520 296 560 300"/>
        """,
        # 3. Mirror, arms raised to fasten the clasp behind the neck.
        f"""
        <rect x="55" y="15" width="450" height="530" rx="34"/>
        <path d="M80 60 q20 -18 40 0 M430 70 q20 -18 40 0" stroke="{FAINT}" stroke-dasharray="8 10"/>
        <circle cx="280" cy="185" r="62"/>
        <path d="M140 545 C150 375 205 312 280 312 C355 312 410 375 420 545" fill="{TINT}"/>
        <path d="M232 300 C248 318 312 318 328 300"/>
        <path d="M205 345 C165 285 185 205 228 178 M355 345 C395 285 375 205 332 178"/>
        <circle cx="280" cy="352" r="9" fill="{INK}"/>
        """,
        # 4. Collarbone-height tracking, pendant swinging, low sun and falling leaves.
        f"""
        <circle cx="470" cy="85" r="42"/>
        <path d="M470 20 V0 M530 85 H560 M515 40 L535 20" stroke="{FAINT}"/>
        <path d="M110 560 C130 390 200 300 280 290 C360 300 430 390 450 560"/>
        <path d="M200 305 C225 380 255 420 280 432 C305 420 335 380 360 305"/>
        <ellipse cx="292" cy="452" rx="14" ry="18" fill="{INK}"/>
        <path d="M250 470 q40 25 80 0" stroke="{FAINT}" stroke-dasharray="10 10"/>
        <path d="M80 120 q18 -22 36 0 q-18 22 -36 0 M150 210 q14 -18 28 0 q-14 18 -28 0" fill="{TINT}"/>
        """,
        # 5. Cafe window seat, chin on hand, latte on the table.
        f"""
        <rect x="20" y="20" width="520" height="330" rx="8" stroke="{FAINT}"/>
        <path d="M280 20 V350" stroke="{FAINT}"/>
        <line x1="0" y1="430" x2="560" y2="430"/>
        <circle cx="210" cy="215" r="64"/>
        <path d="M95 430 C105 330 150 295 210 292 C270 295 315 330 325 430" fill="{TINT}"/>
        <path d="M265 250 C300 290 305 350 285 430"/>
        <circle cx="210" cy="325" r="8" fill="{INK}"/>
        <path d="M390 340 H470 L460 430 H400 Z" fill="{TINT}"/>
        <path d="M470 360 C500 360 500 400 466 400"/>
        <path d="M410 320 q10 -20 0 -40 M440 320 q10 -20 0 -40" stroke="{FAINT}"/>
        """,
    ],
    "espresso": [
        # 1. Narrow counter with a tape measure, sink and a plant.
        f"""
        <path d="M0 330 L560 290 M0 420 L560 360"/>
        <path d="M70 318 L470 290" stroke-width="7"/>
        <path d="M110 316 v-14 M190 310 v-10 M270 304 v-14 M350 299 v-10 M430 293 v-14" stroke-width="3"/>
        <rect x="440" y="262" width="42" height="38" rx="6" fill="{TINT}"/>
        <text x="240" y="275" font-family="ui-monospace, Menlo, monospace" font-size="30" fill="{INK}" stroke="none">60cm</text>
        <path d="M60 385 h120 l-10 24 h-100 z" fill="{TINT}"/>
        <path d="M470 290 v-60 h50 v60" fill="{TINT}"/>
        <path d="M495 230 C470 180 440 170 420 175 M495 230 C505 170 530 150 550 150 M495 230 C480 160 490 120 505 105"/>
        """,
        # 2. Compact machine in the corner, magazine standing beside it for scale.
        f"""
        <line x1="0" y1="440" x2="560" y2="440"/>
        <rect x="170" y="150" width="210" height="260" rx="16" fill="{TINT}"/>
        <rect x="200" y="180" width="150" height="50" rx="8"/>
        <path d="M230 300 h90 v20 h-90 z"/>
        <path d="M230 310 H110" stroke-width="12"/>
        <rect x="190" y="410" width="170" height="30" rx="4"/>
        <rect x="405" y="200" width="95" height="240" rx="4"/>
        <path d="M420 230 h60 M420 250 h45 M420 270 h55" stroke="{FAINT}"/>
        """,
        # 3. Beans into the grinder, grounds into the basket, half-closed door behind.
        f"""
        <rect x="380" y="40" width="150" height="340" stroke="{FAINT}"/>
        <path d="M380 40 L440 70 V400 L380 380" stroke="{FAINT}" stroke-dasharray="12 10"/>
        <path d="M150 60 H330 L290 190 H190 Z" fill="{TINT}"/>
        <ellipse cx="220" cy="30" rx="12" ry="8"/>
        <ellipse cx="260" cy="10" rx="12" ry="8"/>
        <ellipse cx="248" cy="48" rx="12" ry="8"/>
        <rect x="205" y="190" width="70" height="60" rx="6"/>
        <path d="M240 260 v30 M228 262 v20 M252 262 v24" stroke-dasharray="4 8"/>
        <path d="M150 330 C150 400 330 400 330 330 Z" fill="{TINT}"/>
        <path d="M330 350 H470" stroke-width="12"/>
        """,
        # 4. Extraction: two streams into a double-walled glass.
        f"""
        <rect x="140" y="30" width="280" height="70" rx="10" fill="{TINT}"/>
        <path d="M250 100 v30 M310 100 v30" stroke-width="10"/>
        <path d="M250 135 C245 200 255 260 250 330 M310 135 C315 200 305 260 310 330" stroke-width="4"/>
        <path d="M170 300 L190 520 H370 L390 300 Z"/>
        <path d="M188 312 L205 505 H355 L372 312" stroke="{FAINT}"/>
        <path d="M196 430 H364 M199 455 H361" stroke="{FAINT}"/>
        <path d="M200 470 H360 L355 505 H205 Z" fill="{TINT}"/>
        """,
        # 5. Latte, open book, a hand reaching in to lift the cup.
        f"""
        <rect x="30" y="20" width="500" height="250" rx="8" stroke="{FAINT}"/>
        <line x1="0" y1="330" x2="560" y2="330"/>
        <path d="M70 460 L150 360 L270 380 L200 490 Z M200 490 L270 380 L390 380 L330 490 Z" fill="{TINT}"/>
        <path d="M160 400 L240 412 M150 425 L225 436 M285 400 H365 M275 425 H355" stroke="{FAINT}"/>
        <path d="M400 300 H480 L470 390 H410 Z" fill="{TINT}"/>
        <path d="M480 320 C510 320 510 360 476 360"/>
        <path d="M560 250 C520 255 495 270 485 295 C480 310 492 318 505 308 C520 296 540 290 560 290"/>
        """,
    ],
    "skincare": [
        # 1. Rain on the hotel window, neon outside, sitting on the bed edge from behind.
        f"""
        <rect x="30" y="20" width="500" height="330" rx="6"/>
        <rect x="80" y="210" width="40" height="90" fill="{TINT}" stroke="{FAINT}"/>
        <rect x="140" y="180" width="30" height="120" fill="{TINT}" stroke="{FAINT}"/>
        <rect x="380" y="200" width="55" height="100" fill="{TINT}" stroke="{FAINT}"/>
        <path d="M110 40 v60 M200 70 v80 M300 40 v50 M420 60 v90 M470 110 v40" stroke="{FAINT}" stroke-width="3"/>
        <line x1="0" y1="470" x2="560" y2="470"/>
        <circle cx="280" cy="300" r="52"/>
        <path d="M170 470 C180 390 220 360 280 358 C340 360 380 390 390 470" fill="{TINT}"/>
        <path d="M345 390 C360 350 350 320 330 305"/>
        """,
        # 2. Flat lay: open pouch, four bottles, transit card and earbuds.
        f"""
        <rect x="40" y="60" width="480" height="170" rx="30" fill="{TINT}"/>
        <path d="M70 60 H490" stroke-dasharray="10 8" stroke-width="3"/>
        <rect x="70" y="290" width="70" height="200" rx="16"/>
        <rect x="170" y="310" width="60" height="180" rx="14"/>
        <rect x="260" y="330" width="55" height="160" rx="12"/>
        <rect x="345" y="370" width="95" height="120" rx="20"/>
        <path d="M95 290 v-20 h20 v20 M190 310 v-18 h20 v18" />
        <rect x="455" y="300" width="90" height="58" rx="8" stroke="{FAINT}"/>
        <circle cx="480" cy="430" r="16"/><circle cx="520" cy="440" r="16"/>
        """,
        # 3. Mirror close-up: cheek profile, pump bottle, palm patting, droplets.
        f"""
        <path d="M130 0 C120 90 150 150 150 210 C150 250 120 280 128 320 C140 380 200 430 260 470 C300 500 320 540 322 560"/>
        <path d="M150 210 C170 205 190 215 190 232" />
        <rect x="400" y="260" width="90" height="220" rx="16" fill="{TINT}"/>
        <path d="M425 260 v-40 h40 v40 M465 230 h40"/>
        <path d="M200 330 C230 290 290 270 330 280 C350 285 350 305 330 312 C300 322 270 340 250 380"/>
        <circle cx="175" cy="350" r="7" fill="{TINT}"/><circle cx="195" cy="385" r="5" fill="{TINT}"/><circle cx="168" cy="400" r="6" fill="{TINT}"/>
        """,
        # 4. Elevator doors, lit floor display, adjusting a scarf.
        f"""
        <rect x="70" y="60" width="420" height="500"/>
        <path d="M280 60 V560" stroke="{FAINT}"/>
        <rect x="230" y="12" width="100" height="36" rx="6" fill="{TINT}"/>
        <text x="258" y="40" font-family="ui-monospace, Menlo, monospace" font-size="26" fill="{INK}" stroke="none">12</text>
        <circle cx="280" cy="250" r="60" fill="{PAPER}"/>
        <path d="M160 560 C170 420 215 360 280 355 C345 360 390 420 400 560" fill="{PAPER}"/>
        <path d="M215 330 C250 360 310 360 345 330 L352 360 C315 395 245 395 208 360 Z" fill="{TINT}"/>
        <path d="M330 420 L350 470" stroke-width="16"/>
        <path d="M205 300 C200 270 210 250 225 245"/>
        """,
        # 5. Clear umbrella crossing a rainy intersection, glancing back.
        f"""
        <path d="M90 190 C110 60 450 60 470 190 Z" fill="{TINT}"/>
        <path d="M90 190 q47 -20 95 0 q47 -20 95 0 q47 -20 95 0 q47 -20 95 0"/>
        <path d="M280 70 V330"/>
        <circle cx="300" cy="260" r="42" fill="{PAPER}"/>
        <path d="M220 460 C230 360 260 320 300 318 C340 320 370 360 380 460" fill="{PAPER}"/>
        <path d="M40 500 L20 560 M140 500 L125 560 M240 500 L235 560 M340 500 L345 560 M440 500 L455 560" stroke-width="12" stroke="{FAINT}"/>
        <path d="M40 10 L20 60 M520 20 L500 70 M60 250 L45 290 M510 260 L495 300" stroke="{FAINT}" stroke-width="3"/>
        """,
    ],
}

CANVASES = {
    "portrait": (900, 1600),
    "landscape": (1600, 900),
}


def wrap_svg(drawing: str, width: int, height: int) -> str:
    size = min(width, height) * 0.92
    scale = size / 560
    x = (width - size) / 2
    y = (height - size) / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="{PAPER}"/>'
        f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.4f})" fill="none" stroke="{INK}" '
        f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{drawing.strip()}</g></svg>\n'
    )


async def build_audio(sample_id: str, language: str, index: int, script_text: str) -> None:
    import edge_tts

    text = narration_text(script_text)
    path = OUT_DIR / sample_id / language / f"scene-{index}.mp3"
    path.parent.mkdir(parents=True, exist_ok=True)
    await edge_tts.Communicate(text, voice=pick_voice(text, language)).save(str(path))


async def main(skip_audio: bool) -> None:
    samples = json.loads(SAMPLES_JSON.read_text(encoding="utf-8"))
    jobs = []
    for sample in samples:
        drawings = SKETCHES[sample["id"]]
        assert len(drawings) == len(sample["scenes"]), f"{sample['id']}: one sketch per scene"
        for index, (scene, drawing) in enumerate(zip(sample["scenes"], drawings), start=1):
            for orientation, (width, height) in CANVASES.items():
                path = OUT_DIR / sample["id"] / f"scene-{index}-{orientation}.svg"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(wrap_svg(drawing, width, height), encoding="utf-8")
            if not skip_audio:
                for language in ("zh", "en"):
                    jobs.append(build_audio(sample["id"], language, index, scene[language]["script_text"]))

    await asyncio.gather(*jobs)
    print(f"Wrote sample assets to {OUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main(skip_audio="--skip-audio" in sys.argv))
