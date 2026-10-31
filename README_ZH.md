<br />
<div align="center">
  <a href="https://github.com/ayoubzulfiqar/clipit">
    <img src="assets/images/clipit-logo-8x.png" alt="Logo" width="350">
  </a>

  <h3 align="center">Clipit</h3>

  <p align="center">
    <strong>终极 AI Auto-Clipper & Teaser Generator</strong><br>
    开源内容工厂，将长视频转换为电影级短视频，包含 Hook、卡拉 OK 字幕和自动缩略图。
    <br />
    <br />
    <a href="README.md">🇬🇧 English</a>
    &middot;
    <a href="README_AR.md">🇸🇦 العربية</a>
    &middot;
    <a href="README_RU.md">🇷🇺 Русский</a>
    &middot;
    <a href="README_ZH.md">🇨🇳 中文</a>
    &middot;
    <a href="README_KO.md">🇰🇷 한국어</a>
    &middot;
    <a href="https://github.com/ayoubzulfiqar/clipit/issues/new">报告 Bug</a>
    &middot;
    <a href="https://github.com/ayoubzulfiqar/clipit/issues/new">功能请求</a>
  </p>
</div>

---

🟢 **积极维护中**：欢迎贡献、Bug 报告和 PR。

---

## ✨ 功能

| 功能 | 描述 |
|---|---|
| **AI Transcriber** | 使用 Faster-Whisper (large-v3) 进行词级转录 |
| **AI Content Curator** | Gemini 分析上下文，挑选最病毒式时刻并生成元数据 |
| **Smart Auto-Framing** | 基于 MediaPipe 的人脸追踪，带 Smooth Pan 和 Deadzone |
| **Cinematic Teaser Hook** | 3 秒 Hook，带暗色遮罩和 TV Glitch 转场 |
| **Karaoke Subtitles** | 词级高亮的 .ASS 字幕 |
| **Kinetic Typography** | AI 驱动的单词强调，带 bounce/stagger 动画 |
| **B-Roll Integration** | 从 Pexels 自动获取 stock 素材 |
| **Multi-Hook Intro (V2)** | 3-4 个高留存微 Hook |
| **Smart Segment Trimming** | AI 动态选择最佳片段 |
| **Auto-BGM & Ducking** | 本地 BGM 资源池，sidechain ducking 或背景模式 |
| **Auto-Thumbnail** | 带暗色遮罩和大标题文字的帧提取 |
| **Watermark Engine** | 文本/图片水印，9 个锚点 |
| **Cross-Platform Metadata** | YouTube 标题/描述/标签 + TikTok 文案 |
| **Auto YouTube Uploader** | 自动上传并支持调度 |
| **Auto Facebook Reels Uploader** | 上传 Reels 到 Facebook Pages，智能调度 |
| **Podcast Split-Screen** | 自动说话人分离，上下分屏 |
| **Podcast Camera Switch** | 自动活跃说话人检测 |
| **AI Voice-Over** | 使用 Gemini + edge-tts 生成评论音轨 |

> 🎬 **新功能: Story Clip Mode (`--story-mode`)**  
> 👉 **[阅读 Story Clip 文档](docs/STORY_CLIP.md)**

## 📋 前提条件

- Python 3.10+
- FFmpeg 已安装并在 PATH 中
- 推荐 CUDA GPU（CPU fallback 可用）
- Google Gemini API Key

## 🚀 安装

```bash
git clone https://github.com/ayoubzulfiqar/clipit.git
cd clipit
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
# 在 .env 中添加 GOOGLE_API_KEY
```

## 🎬 使用

```bash
python main.py --url "https://youtube.com/watch?v=..." --clips 5 --ratio 9:16
python main.py --url "url1" "url2" "url3" --clips 3
python main.py --story-mode --story-recipe story_recipe.json --sources-json sources.json
```

## 📄 许可证

本项目基于 GNU AGPLv3 License — 详见 [LICENSE](LICENSE) 文件。

Copyright (c) 2026 Ayoub Zulfiqar