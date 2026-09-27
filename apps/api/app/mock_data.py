from app.schemas import GenerateResponse, Language, Orientation, Scene


# (timing_sec, image_prompt) shared by both languages; image prompts are always English.
SHOTS = [
    (
        5,
        "Shot on iPhone 15 Pro, handheld close-up of a premium product box on a dark walnut table by a morning window, "
        "soft side light, shallow depth of field, visible paper texture, natural fingertips entering frame, realistic UGC unboxing, 35mm, f/1.8",
    ),
    (
        6,
        "Macro handheld product detail video frame, premium material edge catching soft daylight, blurred coffee cup and notebook in background, "
        "authentic creator desk setup, realistic reflections, fine dust particles, iPhone 15 Pro natural color science",
    ),
    (
        5,
        "Lifestyle UGC frame with a person naturally placing the product into a daily outfit and desk scene, textured fabric, leather notebook, "
        "soft imperfect composition, no studio lighting, believable skin texture, warm practical lamp in background",
    ),
    (
        6,
        "Natural handheld tracking shot, premium object moving gently in hand, subtle highlight traveling across surface, realistic motion blur, "
        "evening apartment light, tactile material, cinematic but casual UGC, 4k frame",
    ),
    (
        5,
        "Final hero UGC frame, product resting on a clean desk corner, person softly out of focus in background, quiet premium atmosphere, "
        "natural window reflection, realistic shadows, no over-polished commercial look, shot on iPhone 15 Pro",
    ),
]

# (script_text, visual_description) per shot.
COPY: dict[Language, list[tuple[str, str]]] = {
    "zh": [
        (
            "我本来只是随手拆开看一眼，没想到第一秒就被这个质感抓住了。",
            "清晨窗边的木桌，手机手持低角度靠近包装盒，指尖轻轻拉开丝带，盒面有细微压纹和自然反光。",
        ),
        (
            "镜头拉近之后，细节真的很能说明问题，尤其是边缘和材质的处理。",
            "微距镜头扫过产品边缘，背景里有模糊的咖啡杯和笔记本，画面轻微手抖但稳定真实。",
        ),
        (
            "我试着把它放进日常场景里，发现它不是那种只适合摆拍的东西。",
            "人物把产品放进真实生活场景，衣料、桌面和皮革质感同框，构图偏生活化而不是棚拍。",
        ),
        (
            "真正加分的是这个瞬间，它在移动的时候会有很细的光泽变化。",
            "慢速手持跟拍，产品随着手腕或手掌移动，局部高光从左到右滑过，环境音轻微。",
        ),
        (
            "如果你喜欢低调但有记忆点的东西，它会是那种越看越顺眼的选择。",
            "成品静置在桌面一角，人物在背景自然走动，前景产品清晰，最后停在一个安静收尾镜头。",
        ),
    ],
    "en": [
        (
            "I only meant to take a quick look, but the texture got me in the first second.",
            "Wooden table by a morning window. Handheld phone moves in low toward the box, fingertips gently pull the ribbon, subtle embossing catches natural light.",
        ),
        (
            "Up close, the details really speak for themselves, especially the edges and the finish.",
            "Macro pass along the product edge, blurred coffee cup and notebook behind, slight natural hand shake but steady.",
        ),
        (
            "I tried it in my everyday setup, and it's not one of those things that only works in photos.",
            "The person places the product into a real daily scene: fabric, desk, and leather textures in one frame, lived-in rather than studio.",
        ),
        (
            "What really sells it is this moment: the sheen shifts ever so slightly as it moves.",
            "Slow handheld follow shot, the product moves with the wrist, a highlight slides left to right, quiet room tone.",
        ),
        (
            "If you like things that are understated but memorable, this one grows on you.",
            "Product rests on a desk corner, person moving softly in the background, sharp foreground, settles on a calm closing shot.",
        ),
    ],
}

TITLE_TEMPLATE: dict[Language, str] = {
    "zh": "{prompt}的真实感种草短片",
    "en": "{prompt}: an honest first-look short",
}

MOCK_WARNING = "Using deterministic mock media. Add an LLM key (GEMINI_API_KEY or DEEPSEEK_API_KEY) for real generation."


def _shorten(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    # Don't split an English word in half.
    return (cut.rsplit(" ", 1)[0] if " " in cut else cut).rstrip() + "…"


def placeholder_url(base_url: str, index: int, orientation: Orientation) -> str:
    return f"{base_url}/mock-assets/scene-{((index - 1) % len(SHOTS)) + 1}.svg?orientation={orientation}"


def mock_storyboard(
    user_prompt: str,
    base_url: str = "http://localhost:8000",
    language: Language = "zh",
    orientation: Orientation = "portrait",
) -> GenerateResponse:
    cleaned_prompt = user_prompt.strip() or "a quiet luxury product launch"
    title = TITLE_TEMPLATE[language].format(prompt=_shorten(cleaned_prompt, 34 if language == "zh" else 60))

    scenes = [
        Scene(
            id=index,
            timing_sec=timing_sec,
            script_text=script_text,
            visual_description=visual_description,
            image_prompt=image_prompt,
            image_url=placeholder_url(base_url, index, orientation),
            image_provider="mock",
        )
        for index, ((timing_sec, image_prompt), (script_text, visual_description)) in enumerate(
            zip(SHOTS, COPY[language]), start=1
        )
    ]

    return GenerateResponse(
        title=title,
        total_duration_sec=sum(scene.timing_sec for scene in scenes),
        scenes=scenes,
        mode="mock",
        warnings=[MOCK_WARNING],
        source_prompt=user_prompt,
        language=language,
        orientation=orientation,
    )
