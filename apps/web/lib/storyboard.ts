import type { Locale } from "@/lib/i18n";

// "sample" is a built-in storyboard loaded from /public/samples, never from the API.
export type GenerationMode = "real" | "partial" | "mock" | "sample";
export type Orientation = "portrait" | "landscape";

export type StoryboardScene = {
  id: number;
  timing_sec: number;
  script_text: string;
  visual_description: string;
  image_prompt: string;
  image_url?: string | null;
  image_provider?: string | null;
  audio_url?: string | null;
};

export type GenerateResponse = {
  title: string;
  total_duration_sec: number;
  scenes: StoryboardScene[];
  mode: GenerationMode;
  warnings: string[];
  source_prompt: string;
  language: Locale;
  orientation?: Orientation;
  planner_provider?: string | null;
  sample_id?: string;
};

function apiBaseUrl() {
  return (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");
}

export type Providers = { llm: string[]; image: string[]; tts: string[] };

/** Image providers that return photo-style frames (the rest are sketches or placeholders). */
export const PHOTO_PROVIDERS = ["cloudflare", "huggingface", "pollinations"];

/** Which providers the API has credentials for; null when the API can't be reached. */
export async function fetchProviders(): Promise<Providers | null> {
  try {
    const response = await fetch(`${apiBaseUrl()}/providers`);
    return response.ok ? await response.json() : null;
  } catch {
    return null;
  }
}

export async function generateStoryboard(
  userPrompt: string,
  language: Locale,
  orientation: Orientation
): Promise<GenerateResponse> {
  const response = await fetch(`${apiBaseUrl()}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_prompt: userPrompt, language, orientation }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Storyboard generation failed.");
  }

  return response.json();
}
