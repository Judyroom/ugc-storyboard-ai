"use client";

import { ArrowRight, Loader2, RectangleHorizontal, RectangleVertical } from "lucide-react";

import { PipelineProgress } from "@/components/pipeline-progress";
import { useI18n } from "@/lib/i18n";
import { findSample, samplePrompts } from "@/lib/samples";
import type { Orientation } from "@/lib/storyboard";
import { cn } from "@/lib/utils";

const MAX_LENGTH = 280;

const ORIENTATIONS: { value: Orientation; Icon: typeof RectangleVertical }[] = [
  { value: "portrait", Icon: RectangleVertical },
  { value: "landscape", Icon: RectangleHorizontal },
];

type PromptComposerProps = {
  prompt: string;
  orientation: Orientation;
  llmReady: boolean | null;
  photoReady: boolean | null;
  isGenerating: boolean;
  onPromptChange: (value: string) => void;
  onOrientationChange: (value: Orientation) => void;
  onGenerate: () => void;
};

function OrientationSwitch({
  value,
  onChange,
}: {
  value: Orientation;
  onChange: (value: Orientation) => void;
}) {
  const { t } = useI18n();

  return (
    <div role="group" aria-label={t.orientationLabel} className="flex rounded-full border border-rule p-0.5">
      {ORIENTATIONS.map(({ value: option, Icon }) => (
        <button
          key={option}
          type="button"
          aria-pressed={value === option}
          onClick={() => onChange(option)}
          className={cn(
            "inline-flex h-8 items-center gap-1.5 rounded-full px-2.5 text-xs font-medium transition-colors sm:px-3",
            value === option ? "bg-ink text-paper" : "text-ink-2 hover:text-ink"
          )}
        >
          <Icon className="h-3.5 w-3.5" />
          {t.orientations[option]}
        </button>
      ))}
    </div>
  );
}

export function PromptComposer({
  prompt,
  orientation,
  llmReady,
  photoReady,
  isGenerating,
  onPromptChange,
  onOrientationChange,
  onGenerate,
}: PromptComposerProps) {
  const { locale, t } = useI18n();
  const canGenerate = !isGenerating && prompt.trim().length >= 2;
  const isSample = Boolean(findSample(prompt));

  return (
    <section className="overflow-hidden rounded-2xl border border-rule bg-sheet shadow-[0_1px_0_var(--rule),0_12px_32px_-18px_rgba(26,24,20,0.25)]">
      <div className="p-4 sm:p-5">
        <div className="flex items-center justify-between">
          <label htmlFor="story-prompt" className="text-sm font-medium text-ink">
            {t.briefLabel}
          </label>
          <span className="font-mono text-[11px] text-ink-3">
            {prompt.length}/{MAX_LENGTH}
          </span>
        </div>
        <textarea
          id="story-prompt"
          value={prompt}
          maxLength={MAX_LENGTH}
          onChange={(event) => onPromptChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
              event.preventDefault();
              onGenerate();
            }
          }}
          placeholder={t.briefPlaceholder}
          rows={3}
          className="mt-3 block w-full resize-none bg-transparent text-lg leading-8 text-ink outline-none placeholder:text-ink-3"
        />
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="mr-1 font-mono text-[11px] uppercase tracking-wider text-ink-3">{t.examplesLabel}</span>
          {samplePrompts(locale).map(({ id, prompt: example }) => (
            <button
              key={id}
              type="button"
              onClick={() => onPromptChange(example)}
              className={cn(
                "rounded-full border px-3 py-1 text-xs transition-colors",
                prompt.trim() === example
                  ? "border-ink bg-ink text-paper"
                  : "border-rule text-ink-2 hover:border-ink-3 hover:text-ink"
              )}
            >
              {example}
            </button>
          ))}
        </div>
        <p className="mt-2 text-xs text-ink-3">{t.examplesHint}</p>
        {llmReady === false && !isSample ? (
          <p className="mt-2 flex items-start gap-1.5 text-xs text-signal">
            <span aria-hidden className="mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full bg-signal" />
            {t.noLlmHint}
          </p>
        ) : null}
        {llmReady && photoReady === false && !isSample ? (
          <p className="mt-2 flex items-start gap-1.5 text-xs text-ink-2">
            <span aria-hidden className="mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full bg-ink-3" />
            {t.sketchHint}
          </p>
        ) : null}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-rule bg-paper/60 px-4 py-3 sm:px-5">
        <OrientationSwitch value={orientation} onChange={onOrientationChange} />
        <button
          type="button"
          onClick={onGenerate}
          disabled={!canGenerate}
          title={t.shortcutHint}
          className="ml-auto inline-flex h-10 items-center gap-2 rounded-full bg-ink px-5 text-sm font-medium text-paper transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {isGenerating ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {isGenerating ? t.generating : isSample ? t.loadSample : t.generate}
          {isGenerating ? null : <ArrowRight className="h-4 w-4" />}
        </button>
      </div>

      <PipelineProgress active={isGenerating} />
    </section>
  );
}
