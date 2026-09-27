import type { Locale } from "@/lib/i18n";
import type { GenerateResponse, Orientation } from "@/lib/storyboard";

import samplesJson from "./samples.json";

// Built-in storyboards for the "Try" briefs. They load instantly from /public/samples
// (sketch frames + recorded voiceover) and never call the API.
// Regenerate the assets with: python apps/api/scripts/build_samples.py

type SampleCopy = { script_text: string; visual_description: string };

type Sample = {
  id: string;
  prompt: Record<Locale, string>;
  title: Record<Locale, string>;
  scenes: ({ timing_sec: number; image_prompt: string } & Record<Locale, SampleCopy>)[];
};

export const SAMPLES = samplesJson as Sample[];

export function samplePrompts(locale: Locale) {
  return SAMPLES.map((sample) => ({ id: sample.id, prompt: sample.prompt[locale] }));
}

/** The sample whose brief matches the text exactly, in either language. */
export function findSample(prompt: string): Sample | undefined {
  const trimmed = prompt.trim();
  return SAMPLES.find((sample) => sample.prompt.zh === trimmed || sample.prompt.en === trimmed);
}

export function sampleStoryboard(sampleId: string, locale: Locale, orientation: Orientation): GenerateResponse | null {
  const sample = SAMPLES.find((candidate) => candidate.id === sampleId);
  if (!sample) {
    return null;
  }

  const scenes = sample.scenes.map((scene, index) => ({
    id: index + 1,
    timing_sec: scene.timing_sec,
    script_text: scene[locale].script_text,
    visual_description: scene[locale].visual_description,
    image_prompt: scene.image_prompt,
    image_url: `/samples/${sample.id}/scene-${index + 1}-${orientation}.svg`,
    image_provider: "sample",
    audio_url: `/samples/${sample.id}/${locale}/scene-${index + 1}.mp3`,
  }));

  return {
    title: sample.title[locale],
    total_duration_sec: scenes.reduce((total, scene) => total + scene.timing_sec, 0),
    scenes,
    mode: "sample",
    warnings: [],
    source_prompt: sample.prompt[locale],
    language: locale,
    orientation,
    planner_provider: null,
    sample_id: sample.id,
  };
}
