export type GenerationMode = "real" | "partial" | "mock";

export type StoryboardScene = {
  id: number;
  timing_sec: number;
  script_text: string;
  visual_description: string;
  image_prompt: string;
  image_url?: string | null;
  audio_url?: string | null;
};

export type GenerateResponse = {
  title: string;
  total_duration_sec: number;
  scenes: StoryboardScene[];
  mode: GenerationMode;
  warnings: string[];
  source_prompt: string;
};

export async function generateStoryboard(userPrompt: string): Promise<GenerateResponse> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  const response = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_prompt: userPrompt }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Storyboard generation failed.");
  }

  return response.json();
}
