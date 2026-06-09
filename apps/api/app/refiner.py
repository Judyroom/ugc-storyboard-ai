from app.schemas import Storyboard


REFINEMENT_SUFFIX = (
    ", authentic short-form UGC frame, shot on iPhone 15 Pro, natural handheld camera, "
    "realistic texture, physically plausible lighting, no CGI, no glossy studio render"
)


def refine_storyboard(storyboard: Storyboard) -> Storyboard:
    refined_scenes = []
    for scene in storyboard.scenes:
        image_prompt = scene.image_prompt.strip()
        if "iPhone 15 Pro" not in image_prompt:
            image_prompt = f"{image_prompt}{REFINEMENT_SUFFIX}"

        refined_scenes.append(scene.model_copy(update={"image_prompt": image_prompt}))

    return storyboard.model_copy(update={"scenes": refined_scenes})
