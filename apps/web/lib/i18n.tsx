"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export type Locale = "zh" | "en";

const STORAGE_KEY = "ugc-storyboard-locale";

const FRAME_SOURCES_EN: Record<string, string> = {
  cloudflare: "Cloudflare",
  huggingface: "Hugging Face",
  pollinations: "Pollinations",
  sketch: "LLM sketch",
  sample: "Sample sketch",
  mock: "Placeholder",
};

const FRAME_SOURCES_ZH: Record<string, string> = {
  cloudflare: "Cloudflare",
  huggingface: "Hugging Face",
  pollinations: "Pollinations",
  sketch: "LLM 草图",
  sample: "示例线稿",
  mock: "占位画面",
};

const messages = {
  en: {
    appName: "Storyboard",
    appTagline: "UGC shot planner",
    languageLabel: "Language",
    heroEyebrow: "One sentence in, shot list out",
    heroTitle: "Turn a product idea into a creator-ready shot list.",
    heroBody:
      "Describe the product in one line. The agent writes the script, plans every frame, renders visuals, and records a voiceover you can play back.",
    heroSteps: ["Script", "Frames", "Voice"],
    briefLabel: "Your brief",
    briefPlaceholder: "Describe the product, mood, or scene you want to turn into a UGC short video.",
    examplesLabel: "Try",
    examplesHint: "Built-in samples load instantly, no generation needed",
    noLlmHint: "No AI model is connected to the backend yet, so a custom brief returns fixed demo content.",
    sketchHint: "Image generation isn't connected yet, so frames are drawn as line sketches.",
    mockNotice:
      "Demo mode: no AI model is connected yet, so this is fixed sample content and only the title follows your brief.",
    sketchNotice:
      "About the frames: image generation isn't connected yet, so the AI draws a line sketch for each shot. They show composition and camera position, not the final look.",
    orientationLabel: "Frame",
    orientations: { portrait: "Vertical 9:16", landscape: "Horizontal 16:9" },
    loadSample: "View sample",
    shortcutHint: "Ctrl + Enter",
    generate: "Generate storyboard",
    generating: "Generating",
    requestFailed: "Storyboard generation failed.",
    stages: ["Script breakdown", "Visual planning", "Image generation", "Voice pass"],
    emptyTitle: "Your storyboard will appear here",
    emptyBody: "Scenes, frames, voiceover, and an exportable JSON, laid out on a timeline.",
    modes: { real: "Complete", partial: "Partial", mock: "Demo data", sample: "Built-in sample" },
    scenesCount: (count: number) => `${count} scenes`,
    plannedBy: (provider: string) => `planned by ${provider}`,
    sourcePrompt: (prompt: string) => `Brief: ${prompt}`,
    playAll: "Play all",
    pauseAll: "Pause",
    exportJson: "Export JSON",
    status: (count: number) => `Run notes (${count})`,
    timeline: "Timeline",
    scene: (id: number) => `Scene ${id}`,
    imagePrompt: "Image prompt",
    playVoice: "Play voice",
    nowPlaying: "Playing",
    pauseVoice: "Pause",
    voiceUnavailable: "No voice",
    imageUnavailable: "No image",
    imageAlt: (id: number) => `Frame for scene ${id}`,
    frameSource: (provider: string) => FRAME_SOURCES_EN[provider] ?? provider,
    playingAll: (id: number) => `Playing all, scene ${id}`,
    playingScene: (id: number) => `Playing scene ${id}`,
    pausedScene: (id: number) => `Paused scene ${id}`,
    pausedAll: "Paused",
    playbackFailed: "Audio playback failed",
    otherLanguageNotice: "This storyboard was written in Chinese. Generate again for an English version.",
  },
  zh: {
    appName: "Storyboard",
    appTagline: "UGC 分镜工作台",
    languageLabel: "语言",
    heroEyebrow: "一句话进，分镜表出",
    heroTitle: "把一个产品想法，\n变成能直接开拍的分镜。",
    heroBody: "用一句话描述产品。Agent 会写脚本、规划每一帧画面、生成图像，并录好可以直接试听的配音。",
    heroSteps: ["脚本", "画面", "配音"],
    briefLabel: "你的需求",
    briefPlaceholder: "描述你想做成 UGC 短视频的产品、氛围或场景。",
    examplesLabel: "试试",
    examplesHint: "内置示例，点生成直接加载，不消耗额度",
    noLlmHint: "后端还没接入 AI 模型，自定义需求只会返回固定的演示内容。",
    sketchHint: "暂未接入生图服务，画面会以 AI 绘制的线稿草图呈现。",
    mockNotice: "演示模式：后端暂未接入 AI 模型，这里显示的是固定示例内容，只有标题会跟着你的需求变化。",
    sketchNotice: "画面说明：本站暂未接入生图服务，画面是 AI 根据分镜绘制的线稿草图，用来示意构图和机位，不代表最终成片效果。",
    orientationLabel: "画幅",
    orientations: { portrait: "竖屏 9:16", landscape: "横屏 16:9" },
    loadSample: "查看示例分镜",
    shortcutHint: "Ctrl + Enter",
    generate: "生成分镜",
    generating: "生成中",
    requestFailed: "分镜生成失败。",
    stages: ["拆解脚本", "规划画面", "生成画面", "录制配音"],
    emptyTitle: "分镜会出现在这里",
    emptyBody: "场景、画面、配音和可导出的 JSON，按时间轴排好。",
    modes: { real: "完整生成", partial: "部分生成", mock: "演示数据", sample: "内置示例" },
    scenesCount: (count: number) => `${count} 个场景`,
    plannedBy: (provider: string) => `由 ${provider} 规划`,
    sourcePrompt: (prompt: string) => `需求：${prompt}`,
    playAll: "全部播放",
    pauseAll: "暂停",
    exportJson: "导出 JSON",
    status: (count: number) => `运行记录（${count}）`,
    timeline: "时间轴",
    scene: (id: number) => `场景 ${id}`,
    imagePrompt: "画面提示词",
    playVoice: "播放配音",
    nowPlaying: "播放中",
    pauseVoice: "暂停",
    voiceUnavailable: "暂无配音",
    imageUnavailable: "暂无画面",
    imageAlt: (id: number) => `场景 ${id} 的画面`,
    frameSource: (provider: string) => FRAME_SOURCES_ZH[provider] ?? provider,
    playingAll: (id: number) => `全部播放中，场景 ${id}`,
    playingScene: (id: number) => `正在播放场景 ${id}`,
    pausedScene: (id: number) => `已暂停场景 ${id}`,
    pausedAll: "已暂停",
    playbackFailed: "音频播放失败",
    otherLanguageNotice: "这份分镜是用英文写的，重新生成即可得到中文版本。",
  },
};

export type Messages = (typeof messages)["en"];

type I18nContextValue = {
  locale: Locale;
  t: Messages;
  setLocale: (locale: Locale) => void;
};

const I18nContext = createContext<I18nContextValue | null>(null);

function readStoredLocale(): Locale | null {
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored === "zh" || stored === "en" ? stored : null;
  } catch {
    return null;
  }
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("zh");

  useEffect(() => {
    const stored = readStoredLocale();
    if (stored) {
      setLocaleState(stored);
    } else if (!navigator.language.toLowerCase().startsWith("zh")) {
      setLocaleState("en");
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale === "zh" ? "zh-CN" : "en";
  }, [locale]);

  function setLocale(next: Locale) {
    setLocaleState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Storage can be blocked (private mode); the choice just won't persist.
    }
  }

  return (
    <I18nContext.Provider value={{ locale, t: messages[locale], setLocale }}>{children}</I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used inside I18nProvider");
  }
  return context;
}
