"use client";

import { useState } from "react";
import { AlertCircle, Clapperboard, WandSparkles } from "lucide-react";

import { PipelineProgress } from "@/components/pipeline-progress";
import { PromptComposer } from "@/components/prompt-composer";
import { StoryboardTimeline } from "@/components/storyboard-timeline";
import { generateStoryboard, type GenerateResponse } from "@/lib/storyboard";

export default function Home() {
  const [prompt, setPrompt] = useState("一个北欧风格的奢侈品项链");
  const [storyboard, setStoryboard] = useState<GenerateResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt || isGenerating) {
      return;
    }

    setIsGenerating(true);
    setError(null);
    try {
      const result = await generateStoryboard(trimmedPrompt);
      setStoryboard(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed.");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <main className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_20%_10%,rgba(139,92,246,0.24),transparent_32%),radial-gradient(circle_at_85%_5%,rgba(34,211,238,0.14),transparent_30%),#050505] text-zinc-50">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8 lg:py-10">
        <header className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-300 text-zinc-950">
              <Clapperboard className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-zinc-100">UGC Storyboard AI</p>
              <p className="text-xs text-zinc-500">Agentic mini demo</p>
            </div>
          </div>
          <div className="hidden rounded-full border border-white/10 px-3 py-1 text-xs text-zinc-400 sm:block">
            Next.js + FastAPI + LangGraph
          </div>
        </header>

        <section className="grid gap-8 lg:grid-cols-[0.88fr_1.12fr] lg:items-end">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-violet-300/20 bg-violet-300/10 px-3 py-1 text-sm text-violet-100">
              <WandSparkles className="h-4 w-4" />
              One sentence to UGC video storyboard
            </div>
            <div className="space-y-4">
              <h1 className="max-w-4xl text-balance text-5xl font-semibold tracking-[-0.035em] text-zinc-50 sm:text-6xl lg:text-7xl">
                Turn a product idea into a creator-ready shot list.
              </h1>
              <p className="max-w-2xl text-pretty text-base leading-7 text-zinc-400 sm:text-lg">
                The agent plans scenes, refines visual prompts, generates media assets, and returns a polished timeline for a short UGC video.
              </p>
            </div>
          </div>
          <PromptComposer
            prompt={prompt}
            isGenerating={isGenerating}
            onPromptChange={setPrompt}
            onGenerate={handleGenerate}
          />
        </section>

        {error ? (
          <div className="flex items-start gap-3 rounded-2xl border border-red-300/20 bg-red-300/[0.06] p-4 text-sm text-red-100">
            <AlertCircle className="mt-0.5 h-4 w-4" />
            <p>{error}</p>
          </div>
        ) : null}

        <PipelineProgress active={isGenerating} />

        {storyboard ? (
          <StoryboardTimeline storyboard={storyboard} />
        ) : (
          <section className="rounded-2xl border border-dashed border-white/10 bg-white/[0.025] p-8 text-center text-zinc-500">
            Generate a storyboard to see scripts, image prompts, generated frames, TTS status, and exportable JSON.
          </section>
        )}
      </div>
    </main>
  );
}
