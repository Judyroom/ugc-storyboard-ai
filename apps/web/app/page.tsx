"use client";

import { useEffect, useRef, useState } from "react";
import { AlertCircle } from "lucide-react";

import { PromptComposer } from "@/components/prompt-composer";
import { FrameGuides, StoryboardTimeline } from "@/components/storyboard-timeline";
import { useI18n, type Locale } from "@/lib/i18n";
import { SAMPLES, findSample, sampleStoryboard } from "@/lib/samples";
import {
  PHOTO_PROVIDERS,
  fetchProviders,
  generateStoryboard,
  type GenerateResponse,
  type Orientation,
  type Providers,
} from "@/lib/storyboard";
import { cn } from "@/lib/utils";

const ORIENTATION_KEY = "ugc-storyboard-orientation";

const LOCALES: { value: Locale; label: string }[] = [
  { value: "zh", label: "中文" },
  { value: "en", label: "EN" },
];

function LanguageSwitch() {
  const { locale, t, setLocale } = useI18n();

  return (
    <div role="group" aria-label={t.languageLabel} className="flex rounded-full border border-rule p-0.5">
      {LOCALES.map((option) => (
        <button
          key={option.value}
          type="button"
          aria-pressed={locale === option.value}
          onClick={() => setLocale(option.value)}
          className={cn(
            "h-7 rounded-full px-3 text-xs font-medium transition-colors",
            locale === option.value ? "bg-ink text-paper" : "text-ink-2 hover:text-ink"
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

function EmptyBoard({ orientation }: { orientation: Orientation }) {
  const { t } = useI18n();
  const isPortrait = orientation === "portrait";

  return (
    <section className="rounded-2xl border border-dashed border-rule p-5 sm:p-8">
      <div className={cn("mx-auto grid grid-cols-3 gap-3 sm:gap-5", isPortrait ? "max-w-2xl" : "max-w-4xl")}>
        {[1, 2, 3].map((id) => (
          <div
            key={id}
            className={cn("relative rounded-lg border border-rule bg-sheet", isPortrait ? "aspect-[9/16]" : "aspect-video")}
          >
            <FrameGuides className="text-rule" />
            <span className="absolute left-2.5 top-2.5 font-mono text-[11px] text-ink-3">
              S{String(id).padStart(2, "0")}
            </span>
          </div>
        ))}
      </div>
      <div className="mt-6 text-center">
        <p className="text-sm font-medium text-ink">{t.emptyTitle}</p>
        <p className="mt-1 text-sm text-ink-2">{t.emptyBody}</p>
      </div>
    </section>
  );
}

export default function Home() {
  const { locale, t } = useI18n();
  const [prompt, setPrompt] = useState(SAMPLES[0].prompt.zh);
  const [orientation, setOrientation] = useState<Orientation>("portrait");
  const [storyboard, setStoryboard] = useState<GenerateResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  // Unknown until /providers answers (or stays unknown if the API is unreachable).
  const [providers, setProviders] = useState<Providers | null>(null);

  useEffect(() => {
    void fetchProviders().then(setProviders);
  }, []);

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(ORIENTATION_KEY);
      if (stored === "portrait" || stored === "landscape") {
        setOrientation(stored);
      }
    } catch {
      // Storage can be blocked; portrait stays the default.
    }
  }, []);

  // A sample brief follows the language; text the user typed is never touched.
  // A loaded sample storyboard re-renders in the new language too, since it ships in both.
  useEffect(() => {
    setPrompt((current) => findSample(current)?.prompt[locale] ?? current);
    setStoryboard((current) => (current?.sample_id ? sampleStoryboard(current.sample_id, locale, current.orientation ?? "portrait") : current));
  }, [locale]);

  function handleOrientationChange(next: Orientation) {
    setOrientation(next);
    try {
      window.localStorage.setItem(ORIENTATION_KEY, next);
    } catch {
      // Not persisted; still applies for this visit.
    }
    // Samples have frames for both orientations, so switch them live. API results keep the
    // frame shape they were generated at; the new orientation applies to the next generation.
    setStoryboard((current) => (current?.sample_id ? sampleStoryboard(current.sample_id, locale, next) : current));
  }

  function showResults() {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.requestAnimationFrame(() =>
      resultsRef.current?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" })
    );
  }

  async function handleGenerate() {
    const trimmedPrompt = prompt.trim();
    if (trimmedPrompt.length < 2 || isGenerating) {
      return;
    }

    setError(null);
    const sample = findSample(trimmedPrompt);
    if (sample) {
      setStoryboard(sampleStoryboard(sample.id, locale, orientation));
      showResults();
      return;
    }

    setIsGenerating(true);
    try {
      const result = await generateStoryboard(trimmedPrompt, locale, orientation);
      setStoryboard(result);
      showResults();
    } catch (err) {
      setError(err instanceof Error ? err.message : t.requestFailed);
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <main className="min-h-screen bg-paper text-ink">
      <div className="mx-auto w-full max-w-6xl px-4 sm:px-6 lg:px-8">
        <header className="flex h-16 items-center justify-between gap-4 border-b border-rule">
          <div className="flex items-baseline gap-3">
            <span className="flex items-center gap-2 text-[15px] font-semibold tracking-tight">
              <span aria-hidden className="h-2 w-2 translate-y-[-1px] rounded-full bg-signal" />
              {t.appName}
            </span>
            <span className="hidden font-mono text-xs text-ink-3 sm:inline">{t.appTagline}</span>
          </div>
          <LanguageSwitch />
        </header>

        <section className="grid gap-10 py-10 sm:py-14 lg:grid-cols-[1.15fr_1fr] lg:items-start lg:gap-14 lg:py-16">
          <div className="lg:pt-3">
            <p className="font-mono text-xs uppercase tracking-[0.14em] text-signal">{t.heroEyebrow}</p>
            <h1 className={cn(
                "display mt-4 whitespace-pre-line text-balance font-semibold leading-[1.12] sm:text-5xl",
                // Chinese lines are fixed-width glyphs; size them so each line fits a phone without an orphan.
                locale === "zh" ? "text-[1.85rem]" : "text-4xl"
              )}>
              {t.heroTitle}
            </h1>
            <p className="mt-5 max-w-md text-pretty text-base leading-7 text-ink-2">{t.heroBody}</p>
            <ol className="mt-8 flex flex-wrap gap-x-6 gap-y-2">
              {t.heroSteps.map((step, index) => (
                <li key={step} className="flex items-baseline gap-2 text-sm text-ink">
                  <span className="font-mono text-xs text-ink-3">0{index + 1}</span>
                  {step}
                </li>
              ))}
            </ol>
          </div>
          <PromptComposer
            prompt={prompt}
            orientation={orientation}
            llmReady={providers ? providers.llm.length > 0 : null}
            photoReady={providers ? providers.image.some((name) => PHOTO_PROVIDERS.includes(name)) : null}
            isGenerating={isGenerating}
            onPromptChange={setPrompt}
            onOrientationChange={handleOrientationChange}
            onGenerate={handleGenerate}
          />
        </section>

        {error ? (
          <div
            role="alert"
            className="mb-8 flex items-start gap-3 rounded-xl border border-signal/30 bg-signal/[0.06] p-4 text-sm text-ink"
          >
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-signal" />
            <p className="min-w-0 break-words">{error}</p>
          </div>
        ) : null}

        <div ref={resultsRef} className="scroll-mt-4 pb-20">
          {storyboard ? <StoryboardTimeline storyboard={storyboard} /> : <EmptyBoard orientation={orientation} />}
        </div>
      </div>
    </main>
  );
}
