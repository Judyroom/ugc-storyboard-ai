"use client";

import { Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

const EXAMPLES = [
  "一个北欧风格的奢侈品项链",
  "a quiet luxury espresso machine for small apartments",
  "a travel skincare kit for rainy Tokyo mornings",
];

type PromptComposerProps = {
  prompt: string;
  isGenerating: boolean;
  onPromptChange: (value: string) => void;
  onGenerate: () => void;
};

export function PromptComposer({
  prompt,
  isGenerating,
  onPromptChange,
  onGenerate,
}: PromptComposerProps) {
  return (
    <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 shadow-[0_8px_30px_rgba(0,0,0,0.22)] sm:p-5">
      <label htmlFor="story-prompt" className="text-sm font-medium text-zinc-100">
        One sentence brief
      </label>
      <Textarea
        id="story-prompt"
        value={prompt}
        onChange={(event) => onPromptChange(event.target.value)}
        placeholder="Describe the product, mood, or scene you want to turn into a UGC short video."
        className="mt-3 min-h-32 resize-none border-white/10 bg-black/40 text-base text-zinc-50 placeholder:text-zinc-500 focus-visible:ring-violet-400"
      />
      <div className="mt-4 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => onPromptChange(example)}
              className="rounded-full border border-white/10 px-3 py-1.5 text-xs text-zinc-300 transition hover:border-violet-300/50 hover:text-white"
            >
              {example}
            </button>
          ))}
        </div>
        <Button
          type="button"
          onClick={onGenerate}
          disabled={isGenerating || prompt.trim().length < 2}
          className="h-11 bg-violet-300 text-zinc-950 hover:bg-violet-200"
        >
          <Sparkles className="h-4 w-4" />
          {isGenerating ? "Generating" : "Generate storyboard"}
        </Button>
      </div>
    </section>
  );
}
