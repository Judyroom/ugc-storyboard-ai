"use client";

import { useEffect, useState } from "react";
import { Check, Loader2 } from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";

const STAGES = [
  "Script breakdown",
  "Visual planning",
  "Image generation",
  "TTS voice pass",
];

type PipelineProgressProps = {
  active: boolean;
};

export function PipelineProgress({ active }: PipelineProgressProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    if (!active) {
      setCurrentStage(0);
      return;
    }

    const interval = window.setInterval(() => {
      setCurrentStage((stage) => (stage + 1) % STAGES.length);
    }, 900);

    return () => window.clearInterval(interval);
  }, [active]);

  if (!active) {
    return null;
  }

  return (
    <motion.section
      initial={reduceMotion ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-violet-300/20 bg-violet-300/[0.06] p-5"
    >
      <div className="flex items-center gap-3">
        <Loader2 className="h-5 w-5 animate-spin text-violet-200" />
        <div>
          <p className="text-sm font-medium text-violet-100">Agent pipeline is working</p>
          <p className="text-sm text-zinc-400">Planning scenes, prompts, images, and voice assets.</p>
        </div>
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-4">
        {STAGES.map((stage, index) => {
          const isDone = index < currentStage;
          const isCurrent = index === currentStage;

          return (
            <div
              key={stage}
              className="rounded-xl border border-white/10 bg-black/30 p-3"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-medium text-zinc-200">{stage}</span>
                {isDone ? (
                  <Check className="h-4 w-4 text-emerald-300" />
                ) : (
                  <span
                    className={`h-2 w-2 rounded-full ${
                      isCurrent ? "bg-violet-200" : "bg-zinc-700"
                    }`}
                  />
                )}
              </div>
              <div className="mt-3 h-1 overflow-hidden rounded-full bg-white/10">
                <motion.div
                  className="h-full bg-violet-300"
                  initial={false}
                  animate={{ width: isDone || isCurrent ? "100%" : "0%" }}
                  transition={{ duration: reduceMotion ? 0 : 0.5 }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </motion.section>
  );
}
