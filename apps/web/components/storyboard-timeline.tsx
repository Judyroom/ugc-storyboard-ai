"use client";

import Image from "next/image";
import { useState } from "react";
import { Download, FileJson, Play, Volume2 } from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import type { GenerateResponse, StoryboardScene } from "@/lib/storyboard";

type StoryboardTimelineProps = {
  storyboard: GenerateResponse;
};

function playAudioUrl(url: string) {
  return new Promise<void>((resolve, reject) => {
    const audio = new Audio(url);
    audio.onended = () => resolve();
    audio.onerror = () => reject(new Error("Audio playback failed."));
    void audio.play().catch(reject);
  });
}

function exportJson(storyboard: GenerateResponse) {
  const blob = new Blob([JSON.stringify(storyboard, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ugc-storyboard.json";
  link.click();
  URL.revokeObjectURL(url);
}

function SceneCard({
  scene,
  index,
  onPlay,
}: {
  scene: StoryboardScene;
  index: number;
  onPlay: (scene: StoryboardScene) => void;
}) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.article
      initial={reduceMotion ? false : { opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.45, delay: index * 0.04 }}
      className="grid gap-4 rounded-2xl border border-white/10 bg-white/[0.045] p-4 lg:grid-cols-[0.92fr_1.08fr]"
    >
      <div className="flex min-h-80 flex-col">
        <div className="flex items-center justify-between gap-3">
          <Badge variant="secondary" className="bg-violet-300/15 text-violet-100">
            Scene {scene.id}
          </Badge>
          <span className="font-mono text-xs text-zinc-400">{scene.timing_sec}s</span>
        </div>
        <blockquote className="mt-5 text-xl font-medium leading-8 text-zinc-50">
          “{scene.script_text}”
        </blockquote>
        <p className="mt-4 text-sm leading-6 text-zinc-400">{scene.visual_description}</p>
        <Separator className="my-5 bg-white/10" />
        <p className="line-clamp-4 text-xs leading-5 text-zinc-500">{scene.image_prompt}</p>
        <div className="mt-auto pt-5">
          <Button
            type="button"
            variant="outline"
            disabled={!scene.audio_url}
            onClick={() => onPlay(scene)}
            className="border-white/10 bg-black/20 text-zinc-100 hover:bg-white/10 hover:text-white"
          >
            <Play className="h-4 w-4" />
            {scene.audio_url ? "Play voice" : "Voice unavailable"}
          </Button>
        </div>
      </div>
      <div className="relative min-h-80 overflow-hidden rounded-xl border border-white/10 bg-zinc-950">
        {scene.image_url ? (
          <Image
            src={scene.image_url}
            alt={`Generated visual for scene ${scene.id}`}
            fill
            unoptimized
            sizes="(max-width: 1024px) 100vw, 50vw"
            className="object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-zinc-500">
            Image unavailable
          </div>
        )}
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-4">
          <p className="text-xs font-medium text-zinc-200">Generated visual frame</p>
        </div>
      </div>
    </motion.article>
  );
}

export function StoryboardTimeline({ storyboard }: StoryboardTimelineProps) {
  const [playbackStatus, setPlaybackStatus] = useState<string | null>(null);
  const playableScenes = storyboard.scenes.filter((scene) => scene.audio_url);

  async function handlePlay(scene: StoryboardScene) {
    if (!scene.audio_url) {
      return;
    }

    setPlaybackStatus(`Playing scene ${scene.id}`);
    try {
      await playAudioUrl(scene.audio_url);
      setPlaybackStatus(null);
    } catch {
      setPlaybackStatus("Audio playback failed");
    }
  }

  async function handlePlayAll() {
    for (const scene of playableScenes) {
      await handlePlay(scene);
    }
  }

  return (
    <section className="space-y-5">
      <div className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-black/35 p-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge className="bg-violet-300 text-zinc-950">{storyboard.mode}</Badge>
            <span className="font-mono text-xs text-zinc-500">
              {storyboard.total_duration_sec}s total
            </span>
          </div>
          <h2 className="mt-3 text-2xl font-semibold tracking-tight text-zinc-50">
            {storyboard.title}
          </h2>
          <p className="mt-2 text-sm text-zinc-400">
            Source prompt: {storyboard.source_prompt}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            disabled={playableScenes.length === 0}
            onClick={handlePlayAll}
            className="border-white/10 bg-white/[0.04] text-zinc-100 hover:bg-white/10 hover:text-white"
          >
            <Volume2 className="h-4 w-4" />
            Play all
          </Button>
          <Button
            type="button"
            onClick={() => exportJson(storyboard)}
            className="bg-zinc-100 text-zinc-950 hover:bg-white"
          >
            <Download className="h-4 w-4" />
            Export JSON
          </Button>
        </div>
      </div>

      {storyboard.warnings.length > 0 ? (
        <div className="rounded-2xl border border-amber-300/20 bg-amber-300/[0.06] p-4 text-sm text-amber-100">
          <div className="flex items-center gap-2 font-medium">
            <FileJson className="h-4 w-4" />
            Demo status
          </div>
          <ul className="mt-2 space-y-1 text-amber-100/80">
            {storyboard.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {playbackStatus ? (
        <p className="text-sm text-violet-100">{playbackStatus}</p>
      ) : null}

      <div className="space-y-4">
        {storyboard.scenes.map((scene, index) => (
          <SceneCard key={scene.id} scene={scene} index={index} onPlay={handlePlay} />
        ))}
      </div>
    </section>
  );
}
