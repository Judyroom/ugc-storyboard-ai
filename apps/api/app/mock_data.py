from app.schemas import GenerateResponse, Scene


def mock_storyboard(user_prompt: str, base_url: str = "http://localhost:8000") -> GenerateResponse:
    cleaned_prompt = user_prompt.strip() or "a quiet luxury product launch"
    title = f"{cleaned_prompt[:34].rstrip()} 的真实感种草短片"

    scenes = [
        Scene(
            id=1,
            timing_sec=5,
            script_text="我本来只是随手拆开看一眼，没想到第一秒就被这个质感抓住了。",
            visual_description="清晨窗边的木桌，手机手持低角度靠近包装盒，指尖轻轻拉开丝带，盒面有细微压纹和自然反光。",
            image_prompt=(
                "Shot on iPhone 15 Pro, handheld close-up of a premium product box on a dark walnut table by a morning window, "
                "soft side light, shallow depth of field, visible paper texture, natural fingertips entering frame, realistic UGC unboxing, 35mm, f/1.8"
            ),
            image_url=f"{base_url}/mock-assets/scene-1.svg",
        ),
        Scene(
            id=2,
            timing_sec=6,
            script_text="镜头拉近之后，细节真的很能说明问题，尤其是边缘和材质的处理。",
            visual_description="微距镜头扫过产品边缘，背景里有模糊的咖啡杯和笔记本，画面轻微手抖但稳定真实。",
            image_prompt=(
                "Macro handheld product detail video frame, premium material edge catching soft daylight, blurred coffee cup and notebook in background, "
                "authentic creator desk setup, realistic reflections, fine dust particles, iPhone 15 Pro natural color science"
            ),
            image_url=f"{base_url}/mock-assets/scene-2.svg",
        ),
        Scene(
            id=3,
            timing_sec=5,
            script_text="我试着把它放进日常场景里，发现它不是那种只适合摆拍的东西。",
            visual_description="人物把产品放进真实生活场景，衣料、桌面和皮革质感同框，构图偏生活化而不是棚拍。",
            image_prompt=(
                "Lifestyle UGC frame with a person naturally placing the product into a daily outfit and desk scene, textured fabric, leather notebook, "
                "soft imperfect composition, no studio lighting, believable skin texture, warm practical lamp in background"
            ),
            image_url=f"{base_url}/mock-assets/scene-3.svg",
        ),
        Scene(
            id=4,
            timing_sec=6,
            script_text="真正加分的是这个瞬间，它在移动的时候会有很细的光泽变化。",
            visual_description="慢速手持跟拍，产品随着手腕或手掌移动，局部高光从左到右滑过，环境音轻微。",
            image_prompt=(
                "Natural handheld tracking shot, premium object moving gently in hand, subtle highlight traveling across surface, realistic motion blur, "
                "evening apartment light, tactile material, cinematic but casual UGC, 4k frame"
            ),
            image_url=f"{base_url}/mock-assets/scene-4.svg",
        ),
        Scene(
            id=5,
            timing_sec=5,
            script_text="如果你喜欢低调但有记忆点的东西，它会是那种越看越顺眼的选择。",
            visual_description="成品静置在桌面一角，人物在背景自然走动，前景产品清晰，最后停在一个安静收尾镜头。",
            image_prompt=(
                "Final hero UGC frame, product resting on a clean desk corner, person softly out of focus in background, quiet premium atmosphere, "
                "natural window reflection, realistic shadows, no over-polished commercial look, shot on iPhone 15 Pro"
            ),
            image_url=f"{base_url}/mock-assets/scene-5.svg",
        ),
    ]

    return GenerateResponse(
        title=title,
        total_duration_sec=sum(scene.timing_sec for scene in scenes),
        scenes=scenes,
        mode="mock",
        warnings=["Using deterministic mock media. Add GOOGLE_API_KEY and HF_TOKEN for real generation."],
        source_prompt=user_prompt,
    )
