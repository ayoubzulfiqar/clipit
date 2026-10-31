<br />
<div align="center">
  <a href="https://github.com/ayoubzulfiqar/clipit">
    <img src="assets/images/clipit-logo-8x.png" alt="Clipit Logo" width="360">
  </a>

  <h1 align="center">Clipit</h1>

  <p align="center">
    <strong>Open-Source, Unmetered AI Auto-Clipper & Viral Short-Form Video Factory</strong><br>
    Transform long-form videos (podcasts, streams, interviews, and lectures) into cinematic short-form clips with kinetic karaoke subtitles, face-tracking reframing, dynamic split-screen, SFX compositing, and auto-thumbnails.
  </p>

  <p align="center">
    <a href="https://github.com/ayoubzulfiqar/clipit/actions/workflows/ci.yml">
      <img src="https://img.shields.io/github/actions/workflow/status/ayoubzulfiqar/clipit/ci.yml?branch=main&label=CI%20Tests&logo=github" alt="CI Status">
    </a>
    <a href="https://github.com/ayoubzulfiqar/clipit/actions/workflows/docker.yml">
      <img src="https://img.shields.io/github/actions/workflow/status/ayoubzulfiqar/clipit/docker.yml?branch=main&label=Docker%20GHCR&logo=docker" alt="Docker Build">
    </a>
    <a href="https://github.com/ayoubzulfiqar/clipit/releases">
      <img src="https://img.shields.io/badge/version-1.15.0-blue.svg" alt="Version">
    </a>
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/license-AGPL--3.0-purple.svg" alt="License: AGPL-3.0">
    </a>
    <a href="ACCESSIBILITY.md">
      <img src="https://img.shields.io/badge/a11y-WCAG%202.1%20AA-success.svg" alt="WCAG 2.1 AA">
    </a>
    <a href="https://python.org">
      <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg?logo=python" alt="Python 3.10+">
    </a>
  </p>

  <p align="center">
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
    <a href="Usage.md">📖 Complete Usage Manual</a>
  </p>
</div>

---

## ⚡ Why Clipit?

Unlike proprietary SaaS tools that charge per-minute fees, enforce monthly credit quotas, and upload your raw media to third-party clouds, **Clipit is 100% unmetered, self-hostable, and runs locally on your own hardware or private cloud**:

- 🎬 **Unmetered & Free Forever**: Zero subscription tiers, zero watermarks forced on your exports, zero per-minute credit limits.
- 🎯 **Advanced Spatial Framing**: Real-time face-tracking via **MediaPipe** or **YOLO**, hybrid zoom, and active-speaker dynamic split-screen (**Pyannote 3.1**).
- ⚡ **Native Hardware Subtitle Burning**: Hardware-accelerated `.ASS` subtitles via FFmpeg `libass`—bypassing slow headless Chromium canvas bottlenecks.
- 🎨 **Kinetic Typography & Emojis**: Word-by-word Alex Hormozi/Veed-style kinetic karaoke highlights, semantic transcript-driven animated emojis, and contextual keyword coloring.
- 🔊 **Broadcast Audio Mastering & SFX**: Synthesize punchy whooshes, risers, and impact SFX on viral hook cuts, with automated EBU R128 (-14 LUFS) loudness normalization and BGM sidechain ducking.
- 🖥️ **Dual CLI & Web Studio GUI**: Powerful batch CLI alongside a responsive **FastAPI + React 19** Web Studio with dark/light theme, interactive transcript seeking, and multi-layout aspect previewers.
- 🤖 **AI Agent Native (MCP)**: First-class Model Context Protocol (MCP) server exposing clipping, preset management, and social release scheduling to Claude, Cursor, and AI agents.
- 🏢 **Enterprise Distributed Architecture**: Horizontal worker scaling via Redis task brokers, HMAC-SHA256 signed webhooks, batch API (`/api/batch/jobs`), and pluggable lifecycle hooks.

---

## 📑 Table of Contents

- [Quick Start](#-quick-start)
- [Web Studio GUI](#-web-studio-gui)
- [Key Features](#-key-features)
- [CLI Reference](#-cli-reference)
- [Enterprise & Batch API](#-enterprise--batch-api)
- [Community Template Marketplace](#-community-template-marketplace-clipit-pack)
- [Model Context Protocol (MCP) Server](#-model-context-protocol-mcp-server)
- [Python SDK](#-python-sdk)
- [Docker Deployment](#-docker-deployment)
- [Community & Governance](#-community--governance)
- [License (GNU AGPLv3)](#-license)

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/ayoubzulfiqar/clipit.git
cd clipit

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -e ".[all]"

# Configure API key
cp .env.sample .env
# Add your free Gemini API key to .env: GOOGLE_API_KEY=your_key_here
```

### 2. Generate Your First Clip (CLI)

```bash
# Ingest YouTube video, transcribe with Whisper, and generate 3 viral 9:16 portrait clips
clipit --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --clips 3 --ratio 9:16 --font-style HORMOZI
```

### 3. Launch the Web Studio GUI

```bash
# Start FastAPI backend & open React 19 dashboard
clipit-web --port 8000
```
Open **http://localhost:8000** (or `http://localhost:5173` in development).

### 4. Desktop App Mode

```bash
# Spawns backend on dynamic free port and opens default browser window
python3 -m desktop.launcher
```

---

## 🖥️ Web Studio GUI

The Clipit Web Studio combines the flexibility of an enterprise web application with real-time video workstation tools:

```
┌────────────────────────────────────────────────────────────────────────┐
│  CLIPIT STUDIO                                      [Theme] [Settings] │
├────────────────────────────┬───────────────────────────────────────────┤
│ 📁 JOBS                    │ 🎬 PREVIEW & INSPECTOR                    │
│ • [Done] Lex Fridman #400  │ ┌───────────────────────────────────────┐ │
│ • [Proc] Tech Keynote 2026 │ │                                       │ │
│ • [Done] Gaming Highlights │ │   [9:16]      [1:1]       [16:9]      │ │
│                            │ │  Portrait    Square     Landscape     │ │
│ ⚙️ BULK ACTIONS             │ │                                       │ │
│ [Select All] [Download Zip]│ └───────────────────────────────────────┘ │
│ [Retry]      [Delete]      │ 📝 TRANSCRIPT SEEKER                      │
│                            │ "The secret to AI [01:23] is scale..."    │
└────────────────────────────┴───────────────────────────────────────────┘
```

- **Side-by-Side Multi-Layout Previewer**: Compare 9:16 Portrait (TikTok/Shorts), 1:1 Square (Instagram/LinkedIn), and 16:9 Landscape in real time.
- **Word-Level Interactive Transcript Editor**: Click any transcribed word to seek directly to that video frame.
- **Batch Management**: Search, tag, bulk download ZIP bundles (`/api/outputs/{job_id}/zip`), and retry failed jobs.
- **Accessible & Adaptive**: Full keyboard navigation, screen reader ARIA landmarks, WCAG 2.1 AA compliant contrast, and dark/light modes.

---

## ✨ Key Features

| Capability | Module | Description |
|---|---|---|
| **AI Content Intelligence** | [`clipping/engine.py`](file:///home/sensei/Projects/backend/clipit/clipping/engine.py) | Gemini, Groq, OpenRouter, and NVIDIA NIM providers score viral hooks, context, and emotional peaks. |
| **Kinetic Typography & Emojis** | [`clipping/emoji_engine.py`](file:///home/sensei/Projects/backend/clipit/clipping/emoji_engine.py) | Dynamic keyword highlight palettes and automated transcript-driven animated emojis. |
| **Natural Scene-Cut Snapping** | [`clipping/scene_detect.py`](file:///home/sensei/Projects/backend/clipit/clipping/scene_detect.py) | Detects camera transitions and snaps clip boundaries cleanly to scene cuts. |
| **Audio SFX Synthesis** | [`clipping/studio/sfx.py`](file:///home/sensei/Projects/backend/clipit/clipping/studio/sfx.py) | Generates native FFmpeg audio risers, whooshes, impacts, and pops on key moments. |
| **Dynamic Split-Screen & Multi-Cam** | [`clipping/studio/presets.py`](file:///home/sensei/Projects/backend/clipit/clipping/studio/presets.py) | Pyannote 3.1 speaker diarization stacked split-screen and auto-camera switching for podcasts. |
| **Silence Dead-Air Trimming** | [`clipping/silence.py`](file:///home/sensei/Projects/backend/clipit/clipping/silence.py) | Removes long pauses and dead air before LLM analysis to maximize audience retention. |
| **Multimodal Vision Scoring** | [`clipping/vision_scoring.py`](file:///home/sensei/Projects/backend/clipit/clipping/vision_scoring.py) | Evaluates Laplacian gradient sharpness, contrast, and exposure to pick optimal thumbnail frames. |
| **Auto-Chapters & SEO Show Notes** | [`clipping/chapters.py`](file:///home/sensei/Projects/backend/clipit/clipping/chapters.py) | Generates YouTube description chapter timestamps (`00:00 Intro`) and markdown show notes. |
| **Copyright Safety Analyzer** | [`clipping/copyright.py`](file:///home/sensei/Projects/backend/clipit/clipping/copyright.py) | Audits Content ID risks and recommends pitch-shifting, tempo ramping, and B-roll cadence. |
| **Audience Persona Targeting** | [`clipping/persona.py`](file:///home/sensei/Projects/backend/clipit/clipping/persona.py) | Custom prompt and typography presets for Tech Founders, Creators, Finance, Education, and Fitness. |
| **Streamer & Esports Detection** | [`clipping/stream_highlight.py`](file:///home/sensei/Projects/backend/clipit/clipping/stream_highlight.py) | Identifies audio volume RMS spikes and transcript hype trigger clusters during gameplay. |

---

## 🛠️ CLI Reference

```bash
# Full option help
clipit --help
```

### Common Command Recipes

```bash
# 1. High-Energy Viral Clip with Sound Effects & Emojis
clipit --url "https://..." \
  --clips 5 --ratio 9:16 \
  --font-style HORMOZI \
  --semantic-emojis \
  --keyword-palette modern \
  --use-sfx --sfx-volume 0.85 \
  --snap-scene-cuts

# 2. Podcast Split-Screen with Diarization & Auto Camera Switching
clipit --url "https://..." \
  --split-screen --dynamic-split \
  --diarization-speakers 2 \
  --camera-switch --switch-hold-duration 2.0

# 3. Audio Mastering: Dead-Air Removal & Broadcast LUFS Normalization
clipit --url "https://..." \
  --silence-trim --silence-thresh-db -32.0 \
  --normalize-audio --target-lufs -14.0

# 4. Audience Persona & High-CTR Title Optimization
clipit --url "https://..." \
  --persona tech_founder \
  --thumbnail-variants

# 5. Deterministic CI Dry-Run (No video encoding)
clipit --url "https://..." --dry-run --seed 42
```

---

## 🏢 Enterprise & Batch API

Clipit includes an enterprise-grade REST API:

- **Bulk Video Ingestion**: Submit up to 100 jobs atomically via `POST /api/batch/jobs`.
- **Aggregate Progress**: Poll batch status with counts of queued, processing, completed, and failed tasks via `GET /api/batch/{batch_id}`.
- **Signed Webhook Dispatch**: Receive tamper-proof event delivery (`job.completed`, `job.failed`) signed with HMAC-SHA256 (`X-Clipit-Signature`).
- **Distributed Queue**: Seamless horizontal scaling with Redis FIFO lists (`CLIPIT_REDIS_URL`).

```bash
# Example Batch Ingestion:
curl -X POST http://localhost:8000/api/batch/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"url": "https://youtube.com/watch?v=EP1", "pilihan_rasio": "9:16"},
      {"url": "https://youtube.com/watch?v=EP2", "pilihan_rasio": "1:1"}
    ],
    "default_config": {"font_style": "HORMOZI", "use_sfx": true},
    "batch_webhook_url": "https://my-api.com/clipit-webhook"
  }'
```

---

## 📦 Community Template Marketplace (.clipit-pack)

Export and share complete presets, custom TrueType fonts, and audio assets in portable `.clipit-pack` zip archives:

```python
from clipping.marketplace import export_pack, import_pack

# Export pack
export_pack(
    pack_name="Cyberpunk Viral",
    preset_data={"font_style": "NEON_CYBER", "pilihan_rasio": "9:16", "use_sfx": True},
    output_path="cyberpunk.clipit-pack",
    author="Community Creator",
    asset_files={"custom_fonts/cyber.ttf": "fonts/cyber.ttf"}
)

# Safe install with directory-traversal (Zip-Slip) defense
import_pack("cyberpunk.clipit-pack", install_dir="./")
```

---

## 🤖 Model Context Protocol (MCP) Server

Equip AI agents (Cursor, Claude Desktop, Antigravity) with native video clipping capabilities:

```json
{
  "mcpServers": {
    "clipit": {
      "command": "python3",
      "args": ["-m", "clipping.mcp_server"],
      "env": {
        "GOOGLE_API_KEY": "your_gemini_api_key"
      }
    }
  }
}
```

---

## 🐍 Python SDK

```python
from sdk.python import ClipitClient

client = ClipitClient(base_url="http://localhost:8000", api_key="optional_key")

# Submit clipping job
job = client.submit_job(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    ratio="9:16",
    clips=3,
    preset="tiktok_viral"
)

# Poll until rendering completes
result = client.poll_job_until_done(job["id"], timeout_sec=300)
print(f"Generated {len(result['clips'])} viral clips!")
```

---

## 🐳 Docker Deployment

Clipit is published as a multi-arch container image (`linux/amd64` and `linux/arm64`):

```bash
# Run with Docker Compose (includes Redis and persistent volumes)
docker compose up -d

# Check health endpoint
curl http://localhost:8000/api/health
```

---

## 🤝 Community & Governance

We are committed to building an open, welcoming, and inclusive community:

- 📜 **[Code of Conduct](CODE_OF_CONDUCT.md)**: Contributor Covenant v2.1 standards.
- 💡 **[Contributing Guide](CONTRIBUTING.md)**: Development setup, PR process, and testing standards.
- 🛡️ **[Security Policy](SECURITY.md)**: Vulnerability disclosure and safe harbor guidelines.
- ♿ **[Accessibility Statement](ACCESSIBILITY.md)**: WCAG 2.1 AA conformance standards for both UI and video captions.
- 🗺️ **[Product Roadmap](Roadmap.md)**: Strategic development phases and competitive benchmarks.

---

## 📄 License

**Clipit** is licensed under the **[GNU Affero General Public License v3.0 (AGPL-3.0-or-later)](LICENSE)**.

- **Freedom to Run & Modify**: You may run, inspect, modify, and distribute Clipit for personal or commercial purposes.
- **Copyleft & Network Continuity**: If you run a modified version of Clipit on a network server or provide it as a hosted service, you **must make the complete corresponding source code available to all users** interacting with it over the network under the terms of the AGPLv3.
- **Attribution**: Preserve all original copyright notices and author attributions.

Copyright (c) 2026 Ayoub Zulfiqar and Clipit Contributors.
