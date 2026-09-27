"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import { ChevronDown, Download, Pause, Play, Volume2 } from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";

import { useI18n } from "@/lib/i18n";
import type { GenerateResponse, Orientation, StoryboardScene } from "@/lib/storyboard";
import { cn, formatTime } from "@/lib/utils";

type StoryboardTimelineProps = {
  storyboard: GenerateResponse;
};

type PlaybackMode = "single" | "all";

type PlaybackState = {
  sceneId: number | null;
  mode: PlaybackMode | null;
  isPlaying: boolean;
};

type TimedScene = StoryboardScene & { start: number };

function exportJson(storyboard: GenerateResponse) {
  const blob = new Blob([JSON.stringify(storyboard, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ugc-storyboard.json";
  link.click();
  // Revoking synchronously can cancel the download in some browsers.
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function withStartTimes(scenes: StoryboardScene[]): TimedScene[] {
  let start = 0;
  return scenes.map((scene) => {
    const timed = { ...scene, start };
    start += scene.timing_sec;
    return timed;
  });
}

// Matches the backend's stage directions: [soft rain], 【音效】, （笑）.
const CUE_PATTERN = /(\[[^\]]*\]|【[^】]*】|（[^）]*）)/;

/** Script text with sound cues set apart as small tags, since they are not spoken. */
function ScriptLine({ text }: { text: string }) {
  return (
    <>
      {text
        .split(CUE_PATTERN)
        .filter(Boolean)
        .map((part, index) =>
          CUE_PATTERN.test(part) ? (
            <span
              key={index}
              className="mr-1 inline-block rounded bg-rule/50 px-1.5 align-[2px] font-mono text-[11px] font-normal leading-5 text-ink-2"
            >
              {part.slice(1, -1)}
            </span>
          ) : (
            <span key={index}>{part.trim()}</span>
          )
        )}
    </>
  );
}

function sceneLabel(id: number) {
  return `S${String(id).padStart(2, "0")}`;
}

/** Rule-of-thirds guides, drawn over empty and placeholder frames. */
export function FrameGuides({ className }: { className?: string }) {
  return (
    <div aria-hidden className={cn("pointer-events-none absolute inset-0", className)}>
      <div className="absolute inset-y-0 left-1/3 w-px bg-current" />
      <div className="absolute inset-y-0 left-2/3 w-px bg-current" />
      <div className="absolute inset-x-0 top-1/3 h-px bg-current" />
      <div className="absolute inset-x-0 top-2/3 h-px bg-current" />
    </div>
  );
}

function TimelineBar({
  scenes,
  total,
  activeSceneId,
}: {
  scenes: TimedScene[];
  total: number;
  activeSceneId: number | null;
}) {
  const { t } = useI18n();

  return (
    <nav aria-label={t.timeline}>
      <div className="flex gap-1">
        {scenes.map((scene) => {
          const isActive = scene.id === activeSceneId;
          return (
            <a
              key={scene.id}
              href={`#scene-${scene.id}`}
              style={{ flexGrow: scene.timing_sec, flexBasis: 0 }}
              className={cn(
                "group min-w-0 rounded-md border px-2 py-2 transition-colors",
                isActive ? "border-ink bg-ink text-paper" : "border-rule bg-sheet hover:border-ink-3"
              )}
            >
              <span className="block truncate font-mono text-[11px] font-medium">{sceneLabel(scene.id)}</span>
              <span className={cn("block truncate font-mono text-[11px]", isActive ? "text-paper/70" : "text-ink-3")}>
                {scene.timing_sec}s
              </span>
            </a>
          );
        })}
      </div>
      <div className="mt-1.5 flex justify-between font-mono text-[10px] text-ink-3">
        <span>0:00</span>
        <span>{formatTime(total)}</span>
      </div>
    </nav>
  );
}

function SceneCard({
  scene,
  index,
  onPlay,
  isPlaying,
  isActive,
  orientation,
  showPrompt,
  onTogglePrompt,
}: {
  scene: TimedScene;
  orientation: Orientation;
  showPrompt: boolean;
  onTogglePrompt: () => void;
  index: number;
  onPlay: (scene: StoryboardScene) => void;
  isPlaying: boolean;
  isActive: boolean;
}) {
  const reduceMotion = useReducedMotion();
  const { t } = useI18n();
  const provider = scene.image_provider ?? "mock";
  const isSketch = provider === "sketch";
  // Placeholders and sample line sketches are pale paper: add guides, and invert them in dark mode.
  const isPaperFrame = provider === "mock" || provider === "sample";

  return (
    <motion.article
      id={`scene-${scene.id}`}
      initial={reduceMotion ? false : { opacity: 0, y: 14 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.4, delay: (index % 3) * 0.05 }}
      className={cn(
        "flex scroll-mt-6 flex-col overflow-hidden rounded-xl border bg-sheet transition-colors",
        isActive ? "border-ink" : "border-rule"
      )}
    >
      <div
        className={cn(
          "relative overflow-hidden",
          orientation === "portrait" ? "aspect-[9/16]" : "aspect-video",
          isSketch ? "bg-[#fafafa]" : "bg-rule/40"
        )}
      >
        {scene.image_url ? (
          <Image
            src={scene.image_url}
            alt={t.imageAlt(scene.id)}
            fill
            unoptimized
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            className={cn(
              isSketch ? "object-contain" : "object-cover",
              // Placeholders are pale paper; invert them in dark mode so they don't glare.
              isPaperFrame && "dark:[filter:invert(0.9)_hue-rotate(180deg)]"
            )}
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-ink-3">{t.imageUnavailable}</div>
        )}
        {isPaperFrame ? <FrameGuides className="text-[#8c8574]/15" /> : null}
        <div className="absolute inset-x-0 top-0 flex items-start justify-between p-2.5">
          <span className="rounded-md bg-ink/80 px-2 py-1 font-mono text-[11px] text-paper backdrop-blur-sm">
            {sceneLabel(scene.id)} · {formatTime(scene.start)}–{formatTime(scene.start + scene.timing_sec)}
          </span>
          {isActive && isPlaying ? (
            <span className="flex items-center gap-1.5 rounded-md bg-signal px-2 py-1 font-mono text-[11px] text-white">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-white" />
              {t.nowPlaying}
            </span>
          ) : null}
        </div>
        <span className="absolute bottom-2.5 right-2.5 rounded-md bg-paper/85 px-2 py-0.5 font-mono text-[10px] text-ink-2 backdrop-blur-sm">
          {t.frameSource(provider)}
        </span>
      </div>

      <div className="flex flex-1 flex-col p-4">
        <p className="text-[15px] font-medium leading-7 text-ink">
          <ScriptLine text={scene.script_text} />
        </p>
        <p className="mt-2 text-sm leading-6 text-ink-2">{scene.visual_description}</p>

        <div className="mt-3 border-t border-rule pt-3">
          <button
            type="button"
            aria-expanded={showPrompt}
            aria-controls={`scene-${scene.id}-prompt`}
            onClick={onTogglePrompt}
            className="flex items-center gap-1 font-mono text-[11px] uppercase tracking-wider text-ink-3 hover:text-ink"
          >
            <ChevronDown className={cn("h-3 w-3 transition-transform", showPrompt && "rotate-180")} />
            {t.imagePrompt}
          </button>
          {showPrompt ? (
            <p id={`scene-${scene.id}-prompt`} className="mt-2 font-mono text-xs leading-5 text-ink-2">
              {scene.image_prompt}
            </p>
          ) : null}
        </div>

        <div className="mt-auto pt-4">
          <button
            type="button"
            disabled={!scene.audio_url}
            onClick={() => onPlay(scene)}
            className={cn(
              "inline-flex h-8 items-center gap-1.5 rounded-full border px-3 text-xs font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50",
              isPlaying ? "border-ink bg-ink text-paper" : "border-rule text-ink hover:border-ink-3"
            )}
          >
            {isPlaying ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
            {scene.audio_url ? (isPlaying ? t.pauseVoice : t.playVoice) : t.voiceUnavailable}
          </button>
        </div>
      </div>
    </motion.article>
  );
}

export function StoryboardTimeline({ storyboard }: StoryboardTimelineProps) {
  // One switch for every card: cards in a grid row share a height, so opening a single
  // prompt would leave its neighbours stretched and empty.
  const [showPrompts, setShowPrompts] = useState(false);
  const [playbackStatus, setPlaybackStatus] = useState<string | null>(null);
  const [playback, setPlayback] = useState<PlaybackState>({
    sceneId: null,
    mode: null,
    isPlaying: false,
  });
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const playAllQueueRef = useRef<StoryboardScene[]>([]);
  const { locale, t } = useI18n();
  const playableScenes = storyboard.scenes.filter((scene) => scene.audio_url);
  const timedScenes = withStartTimes(storyboard.scenes);
  const orientation = storyboard.orientation ?? "portrait";

  useEffect(() => {
    const audio = audioRef.current;

    return () => {
      audio?.pause();
      audioRef.current = null;
      playAllQueueRef.current = [];
    };
  }, []);

  function stopCurrentAudio() {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
  }

  function playScene(scene: StoryboardScene, mode: PlaybackMode) {
    if (!scene.audio_url) {
      return;
    }

    stopCurrentAudio();

    const audio = new Audio(scene.audio_url);
    audioRef.current = audio;
    setPlayback({
      sceneId: scene.id,
      mode,
      isPlaying: true,
    });
    setPlaybackStatus(mode === "all" ? t.playingAll(scene.id) : t.playingScene(scene.id));

    audio.onended = () => {
      if (mode === "all") {
        const [nextScene, ...remainingScenes] = playAllQueueRef.current;
        playAllQueueRef.current = remainingScenes;
        if (nextScene) {
          playScene(nextScene, "all");
          return;
        }
      }

      audioRef.current = null;
      setPlayback({ sceneId: null, mode: null, isPlaying: false });
      setPlaybackStatus(null);
    };

    audio.onerror = () => {
      audioRef.current = null;
      playAllQueueRef.current = [];
      setPlayback({ sceneId: null, mode: null, isPlaying: false });
      setPlaybackStatus(t.playbackFailed);
    };

    void audio.play().catch(() => {
      audioRef.current = null;
      playAllQueueRef.current = [];
      setPlayback({ sceneId: null, mode: null, isPlaying: false });
      setPlaybackStatus(t.playbackFailed);
    });
  }

  function handlePlay(scene: StoryboardScene) {
    if (!scene.audio_url) {
      return;
    }

    if (playback.sceneId === scene.id && playback.isPlaying) {
      audioRef.current?.pause();
      setPlayback((current) => ({ ...current, isPlaying: false }));
      setPlaybackStatus(t.pausedScene(scene.id));
      return;
    }

    if (playback.sceneId === scene.id && !playback.isPlaying && audioRef.current) {
      void audioRef.current.play().then(() => {
        setPlayback((current) => ({ ...current, isPlaying: true }));
        setPlaybackStatus(playback.mode === "all" ? t.playingAll(scene.id) : t.playingScene(scene.id));
      });
      return;
    }

    playAllQueueRef.current = [];
    playScene(scene, "single");
  }

  function handlePlayAll() {
    if (playableScenes.length === 0) {
      return;
    }

    if (playback.mode === "all" && playback.isPlaying) {
      audioRef.current?.pause();
      setPlayback((current) => ({ ...current, isPlaying: false }));
      setPlaybackStatus(t.pausedAll);
      return;
    }

    if (playback.mode === "all" && !playback.isPlaying && audioRef.current) {
      void audioRef.current.play().then(() => {
        setPlayback((current) => ({ ...current, isPlaying: true }));
        setPlaybackStatus(playback.sceneId ? t.playingAll(playback.sceneId) : t.playAll);
      });
      return;
    }

    const [firstScene, ...remainingScenes] = playableScenes;
    playAllQueueRef.current = remainingScenes;
    playScene(firstScene, "all");
  }

  const isPlayingAll = playback.mode === "all" && playback.isPlaying;

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-5 border-t border-ink pt-6 lg:flex-row lg:items-end lg:justify-between">
        <div className="min-w-0">
          <p className="flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-[11px] uppercase tracking-wider text-ink-3">
            <span className="flex items-center gap-1.5 text-ink">
              <span
                className={cn(
                  "h-1.5 w-1.5 rounded-full",
                  storyboard.mode === "real" ? "bg-emerald-600" : storyboard.mode === "partial" ? "bg-amber-500" : "bg-ink-3"
                )}
              />
              {t.modes[storyboard.mode]}
            </span>
            <span>·</span>
            <span>{t.scenesCount(storyboard.scenes.length)}</span>
            <span>·</span>
            <span>{formatTime(storyboard.total_duration_sec)}</span>
            {storyboard.planner_provider ? (
              <>
                <span>·</span>
                <span className="normal-case">{t.plannedBy(storyboard.planner_provider)}</span>
              </>
            ) : null}
          </p>
          <h2 className="display mt-3 text-balance text-2xl font-semibold leading-tight sm:text-3xl">
            {storyboard.title}
          </h2>
          <p className="mt-2 break-words text-sm text-ink-2">{t.sourcePrompt(storyboard.source_prompt)}</p>
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          <span aria-live="polite" className="mr-1 text-xs text-ink-2">
            {playbackStatus}
          </span>
          <button
            type="button"
            disabled={playableScenes.length === 0}
            onClick={handlePlayAll}
            className="inline-flex h-9 items-center gap-2 rounded-full bg-ink px-4 text-sm font-medium text-paper transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {isPlayingAll ? <Pause className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            {isPlayingAll ? t.pauseAll : t.playAll}
          </button>
          <button
            type="button"
            onClick={() => exportJson(storyboard)}
            className="inline-flex h-9 items-center gap-2 rounded-full border border-rule px-4 text-sm font-medium text-ink transition-colors hover:border-ink-3"
          >
            <Download className="h-4 w-4" />
            {t.exportJson}
          </button>
        </div>
      </div>

      {storyboard.mode === "mock" ? (
        <p role="status" className="rounded-lg border border-signal/30 bg-signal/[0.06] px-4 py-3 text-sm leading-6 text-ink">
          {t.mockNotice}
        </p>
      ) : storyboard.mode === "partial" && storyboard.scenes.some((scene) => scene.image_provider === "sketch" || scene.image_provider === "mock") ? (
        <p role="status" className="rounded-lg border border-rule bg-sheet px-4 py-3 text-sm leading-6 text-ink-2">
          {t.sketchNotice}
        </p>
      ) : null}

      {storyboard.language && storyboard.language !== locale ? (
        <p className="rounded-lg bg-sheet px-4 py-3 text-sm text-ink-2">{t.otherLanguageNotice}</p>
      ) : null}

      <TimelineBar
        scenes={timedScenes}
        total={storyboard.total_duration_sec}
        activeSceneId={playback.sceneId}
      />

      <div
        className={cn(
          "grid gap-5",
          orientation === "portrait" ? "grid-cols-1 min-[480px]:grid-cols-2 lg:grid-cols-4" : "sm:grid-cols-2 lg:grid-cols-3"
        )}
      >
        {timedScenes.map((scene, index) => (
          <SceneCard
            key={scene.id}
            scene={scene}
            index={index}
            onPlay={handlePlay}
            isActive={playback.sceneId === scene.id}
            orientation={orientation}
            showPrompt={showPrompts}
            onTogglePrompt={() => setShowPrompts((current) => !current)}
            isPlaying={playback.sceneId === scene.id && playback.isPlaying}
          />
        ))}
      </div>

      {storyboard.warnings.length > 0 ? (
        <details className="group rounded-xl border border-dashed border-rule px-4 py-3">
          <summary className="flex cursor-pointer list-none items-center gap-1.5 font-mono text-[11px] uppercase tracking-wider text-ink-3 hover:text-ink [&::-webkit-details-marker]:hidden">
            <ChevronDown className="h-3 w-3 transition-transform group-open:rotate-180" />
            {t.status(storyboard.warnings.length)}
          </summary>
          <ul className="mt-2 space-y-1 font-mono text-xs leading-5 text-ink-2">
            {storyboard.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </details>
      ) : null}
    </section>
  );
}
