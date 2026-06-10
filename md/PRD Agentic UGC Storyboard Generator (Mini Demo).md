# PRD: Agentic UGC Storyboard Generator (Mini Demo)

**产品名称**：UGC Storyboard AI  
**版本**：v0.1 Mini Demo  
**目标**：打造一个高品质、展示 Agentic Workflow 的技术 Demo，适合作品集、小红书、技术分享和面试。  
**日期**：2026年6月  

## 1. 产品概述

**一句话描述**：  
用户输入**一句话**，AI Agent 自动拆解成专业 UGC 短视频分镜脚本 + 高精度 AIGC 图片 + TTS 语音，前端以**炫酷分镜时间轴**形式呈现。

**核心亮点**：
- 真正 Agentic 流程（LangGraph 多阶段处理）
- UGC 风格强（参考原子级反泛化提示词 V2.0）
- 免费技术栈部署（Vercel + Hugging Face Spaces）
- 视觉精美、交互流畅

## 2. 用户流程

1. 打开网页 → 看到简洁炫酷首页 + 示例 Prompt 卡片
2. 在大输入框输入一句话（如：“一个北欧风格的奢侈品项链”）
3. 点击「生成分镜」→ 显示 **Agent Pipeline Loading 动画**（展示 4-5 个处理阶段）
4. 生成完成 → 展示**水平/垂直分镜时间轴**
5. 每张分镜卡片包含：
   - 左侧：脚本台词 + Play 按钮（TTS 播放）
   - 右侧：生成的高质量 AIGC 图片
   - 下方：时长标签 + 序号
6. 支持单个播放 / 全部播放 / 导出 JSON

## 3. 功能需求

### Frontend（Next.js + Vercel）
- **首页**：Hero 区域 + 大输入框 + 示例 Prompt 按钮 + Generate 按钮
- **Loading 页面**：炫酷的 Agent Pipeline 进度动画（Script Breakdown → Visual Planning → Image Generation → TTS）
- **结果页面**：Framer Motion 驱动的分镜时间轴（支持水平滚动或垂直布局）
- 暗黑模式优先，移动端完美适配
- 使用 shadcn/ui + Tailwind 组件
- 调用 Backend API

### Backend（FastAPI + Hugging Face Spaces）
- **POST /generate** 接口
- 接收 `{ "user_prompt": "string" }`
- 使用 **LangGraph** 构建 Agent 工作流
- 输出结构化 JSON（详见下方 Prompt）

### AI Agent 工作流（LangGraph）
1. **Planner**：使用优化后的 UGC System Prompt 将一句话拆解为 5-7 个场景
2. **Refiner**：对每个 image_prompt 进行原子级优化（Nano Banana 2 级别）
3. **Image Generator Tool**：调用 Hugging Face InferenceClient（FLUX.1-schnell）
4. **TTS Generator Tool**：使用 edge-tts 生成音频文件
5. 保存图片和音频到 `./generated` 目录并返回可访问 URL

## 4. 技术栈（最终确定）

**Frontend**：
- Next.js 15 (App Router + TypeScript)
- Tailwind CSS + shadcn/ui
- Framer Motion
- Lucide Icons

**Backend**：
- FastAPI (Python 3.11+)
- LangGraph + LangChain
- LLM：Google Gemini 2.5 Flash (`langchain-google-genai`)
- Image：Hugging Face InferenceClient (FLUX.1-schnell)
- TTS：`edge-tts`
- 静态文件服务

**部署**：
- Frontend → Vercel（免费）
- Backend → Hugging Face CPU Space（Docker）

**环境变量**：
- `GOOGLE_API_KEY`
- `HF_TOKEN`（可选，用于 Inference）

## 5. 核心 Prompt（必须严格使用）

### System Prompt（Planner Node）

```text
你是一位顶级 TikTok / 小红书 UGC 视频内容专家 + AI 视觉工程大师。你擅长将用户提供的一句话概念，转化为高传播力、强真实感、情绪共鸣的短视频分镜脚本。

你的核心能力是「Anti-Generalization」（反泛化）原子级拆解：必须做到极致真实、细节丰富、物理正确、镜头语言专业，像 iPhone 15 Pro 原生拍摄的 UGC 视频一样自然。

输出必须严格使用以下 JSON 格式：

{
  "title": "短视频标题（吸引人，适合小红书/TikTok）",
  "total_duration_sec": 30,
  "scenes": [
    {
      "id": 1,
      "timing_sec": 5,
      "script_text": "自然口语化的旁白/对白（适合真人配音，可加音效提示如 [轻柔雨声]）",
      "visual_description": "极致详细的视觉原子描述，包括镜头类型、机位角度、构图、光影、材质、人物微表情、物理动作",
      "image_prompt": "极高质量的 FLUX.1-schnell 英文提示词"
    }
  ]
}

严格规则：
- 5-7 个场景，总时长 20-45 秒
- 真实 UGC 风格（Shot on iPhone 15 Pro, natural handheld, realistic skin texture 等）
- 故事有完整情绪弧线
- image_prompt 必须极度详细，包含真实光影、材质、摄影参数
```