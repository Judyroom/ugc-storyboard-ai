"use client";

import { useEffect, useState } from "react";
import { Check } from "lucide-react";

import { useI18n } from "@/lib/i18n";
import { cn } from "@/lib/utils";

const STAGE_COUNT = 4;

type PipelineProgressProps = {
  active: boolean;
};

export function PipelineProgress({ active }: PipelineProgressProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const { t } = useI18n();

  useEffect(() => {
    if (!active) {
      setCurrentStage(0);
      return;
    }

    // Estimated progress until the API streams real stages: advance, then hold on the last one.
    const interval = window.setInterval(() => {
      setCurrentStage((stage) => Math.min(stage + 1, STAGE_COUNT - 1));
    }, 2500);

    return () => window.clearInterval(interval);
  }, [active]);

  if (!active) {
    return null;
  }

  return (
    <ol aria-live="polite" className="grid grid-cols-2 gap-px border-t border-rule bg-rule sm:grid-cols-4">
      {t.stages.map((stage, index) => {
        const isDone = index < currentStage;
        const isCurrent = index === currentStage;

        return (
          <li
            key={stage}
            aria-current={isCurrent ? "step" : undefined}
            className="flex items-center gap-2 bg-sheet px-4 py-3 text-xs"
          >
            {isDone ? (
              <Check className="h-3.5 w-3.5 text-ink-2" />
            ) : (
              <span
                className={cn(
                  "h-1.5 w-1.5 rounded-full",
                  isCurrent ? "animate-pulse bg-signal" : "bg-rule"
                )}
              />
            )}
            <span className={cn(isCurrent ? "font-medium text-ink" : isDone ? "text-ink-2" : "text-ink-3")}>
              {stage}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
