# Clipit — Complete Usage Guide

> This guide covers installation, configuration, CLI usage, Web Studio, Docker, and
> advanced workflows for both end users and developers.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Installation](#3-installation)
4. [Configuration (.env)](#4-configuration-env)
5. [Quick Start](#5-quick-start)
6. [CLI Reference](#6-cli-reference)
   - 6.1 Single URL
   - 6.2 Batch Multi-URL
   - 6.3 Story Clip Mode
   - 6.4 Podcast / Split-Screen
   - 6.5 Voice-Over Commentary
   - 6.6 Watermark, BGM, Subtitles
   - 6.7 Video Encoding Tuning
   - 6.8 Cleanup & Dev Mode
7. [Web Studio (FastAPI + React)](#7-web-studio-fastapi--react)
8. [Docker Deployment](#8-docker-deployment)
9. [Google Colab / Kaggle Notebooks](#9-google-colab--kaggle-notebooks)
10. [Uploaders](#10-uploaders)
    - 10.1 YouTube Auto-Uploader
    - 10.2 Facebook Reels Uploader
11. [YouTube Tracker](#11-youtube-tracker)
12. [Output Structure](#12-output-structure)
13. [Troubleshooting](#13-troubleshooting)
14. [FAQ](#14-faq)
15. [Developer Guide](#15-developer-guide)
16. [Contributing](#16-contributing)

---

## 1. Overview

Clipit is an AI-powered auto-clipper that turns long-form video into short-form,
platform-ready clips. Pipeline:

```
Source URL → Download → Whisper Transcription → Gemini AI Analysis
  → Face-Track Crop + B-Roll + BGM + Subtitles + Hook → Final MP4 + Thumbnail
```

Two interfaces: **CLI** (`main.py`) and **Web Studio** (FastAPI + React dashboard).

---

## 2. Prerequisites

| Component | Required | Notes |
|---|---|---|
| Python | 3.10+ | 3.11 recommended |
| FFmpeg | Yes | Must be on PATH |
| CUDA GPU | Optional | CPU fallback available (slower) |
| Google Gemini API Key | Yes (normal mode) | Free tier at aistudio.google.com |
| Pexels API Key | Optional | For B-roll |
| HuggingFace Token | Optional | For podcast diarization (Pyannote) |
| Node.js | Optional | For Web Studio frontend dev |

Check FFmpeg:
```bash
ffmpeg -version
```

---

## 3. Installation

```bash
# 1. Clone
git clone https://github.com/ayoubzulfiqar/clipit.git
cd clipit

# 2. Virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Environment
cp .env.sample .env
# Edit .env and set GOOGLE_API_KEY (and optional keys)

# 5. Verify
python main.py --help
```

Optional (podcast diarization):
```bash
pip install pyannote.audio
```

Optional (GPU Whisper):
```bash
pip install faster-whisper[cuda]
```

---

## 4. Configuration (.env)

See `.env.sample`. Key variables:

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Yes | Gemini API key |
| `PEXELS_API_KEY` | Optional | B-roll stock footage |
| `HF_TOKEN` | Optional | Pyannote diarization |
| `NVIDIA_API_KEY` | Optional | NVIDIA AI provider |
| `MAX_CONCURRENT_JOBS` | Optional | Web Studio worker concurrency (default 1) |
| `APP_TIMEZONE` | Optional | Timezone for scheduling (e.g. Asia/Jakarta) |
| `META_PAGE_ID` / `META_PAGE_ACCESS_TOKEN` | Optional | Facebook Reels uploader |

---

## 5. Quick Start

```bash
# Single video, 5 clips, 9:16
python main.py --url "https://youtube.com/watch?v=XXXX" --clips 5 --ratio 9:16

# Batch
python main.py --url "url1" "url2" "url3" --clips 3

# Story mode
python main.py --story-mode --story-recipe story_recipe.json --sources-json sources.json
```

Outputs land in `outputs/` (or per-URL subfolders in batch mode).

---

## 6. CLI Reference

Run `python main.py --help` for the full list. Key flags by group.

### 6.1 Single URL

```bash
python main.py --url "https://..." \
  --clips 5 --ratio 9:16 \
  --whisper-model large-v3 --whisper-device cuda \
  --gemini-model gemini-2.0-flash
```

### 6.2 Batch Multi-URL

```bash
python main.py --url "u1" "u2" "u3" --clips 3 --cleanup-source
```
Each URL gets its own output subfolder and a combined `batch_manifest.json`.

### 6.3 Story Clip Mode

```bash
python main.py --story-mode \
  --story-recipe story_recipe.json \
  --sources-json sources.json \
  --skip-download          # reuse cached downloads
```

See `docs/STORY_CLIP.md`.

### 6.4 Podcast / Split-Screen

```bash
python main.py --url "..." --split-screen --diarization-speakers 2
python main.py --url "..." --camera-switch --switch-hold-duration 2.0
```

### 6.5 Voice-Over Commentary

```bash
python main.py --url "..." --voiceover \
  --voiceover-style reaction --voiceover-voice en-US-AvaNeural
```

### 6.6 Watermark, BGM, Subtitles

```bash
python main.py --url "..." \
  --watermark --text "@handle" --position bottom-right --opacity 60 \
  --bgm-mode ducking --no-karaoke
```

### 6.7 Video Encoding Tuning

```bash
python main.py --url "..." \
  --video-crf 23 --video-preset medium --video-sharpen 1.2 \
  --render-height 1080 --video-scale-algo lanczos
```

### 6.8 Cleanup & Dev Mode

```bash
python main.py --url "..." --cleanup-source --dev-mode-with-output
```

---

## 7. Web Studio (FastAPI + React)

Backend:
```bash
uvicorn web.api.app:app --host 0.0.0.0 --port 8000 --reload
```
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

Frontend (dev):
```bash
cd web/dashboard
npm install
npm run dev   # http://localhost:5173
```

Features: job creation, progress tracking, file browser, settings.

---

## 8. Docker Deployment

```bash
docker compose up -d
```
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

Volumes persist `outputs/` and `uploads/`. Set env vars in `.env`.

---

## 9. Google Colab / Kaggle Notebooks

- `notebooks/Quick_Start.ipynb` — single-run quick start
- `notebooks/kaggle-studio-server.ipynb` — backend server for Studio
- `notebooks/Lib_clipit.ipynb` — library import

Follow notebook cells; set API keys in Colab secrets or env.

---

## 10. Uploaders

### 10.1 YouTube Auto-Uploader

```bash
python youtube_uploader/generate_youtube_token.py   # one-time OAuth
python run_upload.py
```

### 10.2 Facebook Reels Uploader

```bash
python run_fb_upload.py
```
Requires `META_PAGE_ID` and `META_PAGE_ACCESS_TOKEN` in `.env`.

---

## 11. YouTube Tracker

Local playlist snapshot tracker:
```bash
cd youtube_tracker
python server.py   # serves tracker UI
```

---

## 12. Output Structure

```
outputs/
├── <slug>/                    # per-URL in batch mode
│   ├── clip_1.mp4
│   ├── clip_1.jpg             # thumbnail
│   ├── manifest.json
│   └── video_asli.mp4         # source (deleted if --cleanup-source)
├── batch_manifest.json        # batch summary
└── story_cache/               # story mode transcripts
```

Each clip includes burned-in subtitles, B-roll, BGM, hook, watermark (if enabled).

---

## 13. Troubleshooting

| Problem | Fix |
|---|---|
| `GOOGLE_API_KEY not found` | Set in `.env` or export env var |
| FFmpeg not found | Install FFmpeg, add to PATH |
| Whisper OOM | Use `--whisper-model small` or `--whisper-device cpu` |
| Pyannote missing | `pip install pyannote.audio`, set `HF_TOKEN` |
| Pexels 403 | Check `PEXELS_API_KEY` |
| CUDA errors | `--whisper-device cpu --whisper-compute-type int8` |
| Slow render | Lower `--render-height`, use `--video-preset fast` |
| Port in use | Change `--port` or kill existing process |

---

## 14. FAQ

**Q: Can I run fully offline?**  
A: Transcription (Whisper) runs locally; AI analysis needs Gemini. Use cached `--load-gemini-json` to skip AI.

**Q: Which GPU do I need?**  
A: Any CUDA-capable GPU helps; CPU fallback works but is slower.

**Q: How do I add a custom font?**  
A: Place font files in `custom_fonts/` and use `--font-style`.

**Q: Can I resume a failed job?**  
A: Web Studio supports `reuse_job_id`. CLI: re-run with `--skip-download`.

**Q: Is there a rate limit?**  
A: Gemini free tier limits apply; use fallback model or NVIDIA provider.

---

## 15. Developer Guide

### Project Layout
```
clipit/
├── main.py                 # CLI entry
├── clipping/               # core pipeline package
├── web/api/                # FastAPI backend
├── web/dashboard/          # React (Vite) frontend
├── docs/                   # static docs + studio UI
├── wiki/                   # GitHub wiki
├── notebooks/              # Colab/Kaggle
├── youtube_tracker/        # playlist tracker
├── youtube_uploader/       # YT uploader
├── facebook_uploader/      # FB uploader
└── assets/                 # BGM, images
```

### Adding a Feature
1. Add CLI flag in `clipping/config.py`.
2. Implement in `clipping/` module.
3. Wire into `clipping/runner.py`.
4. Add API field in `web/api/models.py` + route if needed.
5. Update `README.md`, `CHANGELOG.md`, `Roadmap.md`.

### Running Tests
```bash
python -m pytest   # (add tests under tests/)
python -m compileall .
```

### Linting
```bash
ruff check . && black --check . && mypy clipping/
```

### Building Docker
```bash
docker build -t clipit:latest .
```

---

## 16. Contributing

See `wiki/14-Contributing.md`. Conventional commits, PR with lint+tests green, update changelog. Tag releases `vX.Y.Z`.

---

*End of usage guide.*