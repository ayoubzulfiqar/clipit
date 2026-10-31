# Clipit — Comprehensive Production Usage Guide

> **Clipit** is an open-source, unmetered AI video auto-clipper and teaser engine that transforms long-form videos (podcasts, streams, interviews, webinars, gaming, and lectures) into viral short-form clips optimized for TikTok, YouTube Shorts, Instagram Reels, and LinkedIn.

---

## Table of Contents

1. [Architectural Overview](#1-architectural-overview)
2. [Installation & Requirements](#2-installation--requirements)
   - 2.1 System Requirements & Hardware Acceleration
   - 2.2 Local Python Setup (Pip & Virtualenv)
   - 2.3 Docker & Docker Compose Deployment
   - 2.4 Desktop Application Mode
3. [Environment Configuration (.env)](#3-environment-configuration-env)
4. [Quick Start Cheatsheet](#4-quick-start-cheatsheet)
5. [Complete CLI Reference & Flag Groups](#5-complete-cli-reference--flag-groups)
   - 5.1 Source Input & Download Flags
   - 5.2 Speech-to-Text (Whisper ASR) Tuning
   - 5.3 AI Intelligence & Multi-Provider Routing
   - 5.4 Smart Trimming, Silence Removal & Scene Snapping
   - 5.5 Visual Framing, Face-Tracking & Dynamic Split-Screen
   - 5.6 Kinetic Subtitles, Semantic Emojis & Typography
   - 5.7 Audio Mastering, BGM & Sound Effects (SFX)
   - 5.8 Gaming & Streamer Highlight Detector
   - 5.9 Content Persona Targeting & CTR Optimization
   - 5.10 Output Encoding, Video Quality & Hardware Acceleration
   - 5.11 Dry-Run, Seeding & Reproducibility
6. [Interactive Web Studio (FastAPI + React 19)](#6-interactive-web-studio-fastapi--react-19)
   - 6.1 Starting the Web Studio
   - 6.2 Managing Jobs & Real-Time Telemetry
   - 6.3 Side-by-Side Multi-Layout Aspect Previewer (9:16 / 1:1 / 16:9)
   - 6.4 Word-Level Interactive Transcript Editor
   - 6.5 Presets System & Community Template Marketplace (.clipit-pack)
7. [Enterprise Batch API & Distributed Workers](#7-enterprise-batch-api--distributed-workers)
   - 7.1 Single & Bulk Job Submissions
   - 7.2 Redis Distributed Task Queue
   - 7.3 Webhooks & HMAC-SHA256 Signature Verification
8. [Serverless GPU Offload (Modal & RunPod)](#8-serverless-gpu-offload-modal--runpod)
9. [Multimodal Vision & Auto-Chapters Engine](#9-multimodal-vision--auto-chapters-engine)
   - 9.1 Visual Frame Sharpness & Thumbnail Ranking
   - 9.2 YouTube Chapters & Markdown Show Notes
   - 9.3 Copyright Safety & Originality Transforms
10. [Typed Python Client SDK](#10-typed-python-client-sdk)
11. [Model Context Protocol (MCP) Server for AI Agents](#11-model-context-protocol-mcp-server-for-ai-agents)
12. [Plugin Architecture & Lifecycle Hooks](#12-plugin-architecture--lifecycle-hooks)
13. [Troubleshooting & Diagnostics](#13-troubleshooting--diagnostics)
14. [Licensing (GNU AGPLv3)](#14-licensing-gnu-agplv3)

---

## 1. Architectural Overview

Clipit operates as a deterministic 7-stage media transformation pipeline:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CLIPIT CORE ENGINE PIPELINE                     │
└────────────────────────────────────────────────────────────────────────┘
  [1] INGESTION        yt-dlp video stream fetch / local upload verification
       │
  [2] SPEECH-TO-TEXT   Faster-Whisper ASR with word-level timestamps & VAD
       │
  [3] AI INTELLIGENCE  Gemini / Groq / OpenRouter / NVIDIA viral clip scoring
       │
  [4] PRE-TRIM AUDIT   Dead-air removal + Camera transition scene-cut snapping
       │
  [5] NORMALIZATION    Audience persona prompt tuning + CTR title generation
       │
  [6] STUDIO COMPOSITE Dynamic split-screen (Pyannote) / Face crop (YOLO/MP)
       │               + ASS kinetic karaoke subtitles + Contextual emojis
       │               + SFX audio synthesis + BGM sidechain ducking + LUFS
       │
  [7] MANIFEST & PACK  Render manifest generation + Webhook notification
```

---

## 2. Installation & Requirements

### 2.1 System Requirements & Hardware Acceleration

| Dependency | Minimum Version | Recommended | Purpose |
|---|---|---|---|
| **Python** | 3.10 | 3.11 / 3.12 | Core runtime |
| **FFmpeg** | 5.0+ with `libass` | 6.0+ with NVENC / VAAPI | Video decoding, ASS subtitle burning, and encoding |
| **GPU (Optional)** | CUDA 11.8+ / 12+ | NVIDIA RTX 3060+ (6GB+ VRAM) | Fast NVENC encoding & local Faster-Whisper GPU execution |
| **RAM** | 8 GB | 16 GB - 32 GB | High-resolution video compositing |
| **Node.js** | 20+ | 22+ (LTS) | React 19 Web Studio dashboard development |

Verify FFmpeg installation and `libass` support:
```bash
ffmpeg -version | grep --color=always -E "libass|nvenc"
```

### 2.2 Local Python Setup (Pip & Virtualenv)

```bash
# 1. Clone repository
git clone https://github.com/ayoubzulfiqar/clipit.git
cd clipit

# 2. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install core & optional feature packages
pip install --upgrade pip
pip install -e ".[all]"

# 4. Copy environment template
cp .env.sample .env
```

### 2.3 Docker & Docker Compose Deployment

Clipit provides production-ready multi-arch container images (`linux/amd64` and `linux/arm64`):

```bash
# Run backend + Redis queue + Web Studio
docker compose up -d

# Check service health
curl -f http://localhost:8000/api/health
```

### 2.4 Desktop Application Mode

Clipit features an integrated desktop orchestrator that verifies local FFmpeg binaries, binds a dynamic free port, spawns the FastAPI server, opens your native browser, and guarantees clean process shutdown on exit:

```bash
# Launch Desktop Studio
python3 -m desktop.launcher

# Or validate environment in dry-run mode
python3 -m desktop.launcher --dry-run
```

---

## 3. Environment Configuration (.env)

Edit `.env` in the project root:

```ini
# ==========================================
# Core AI Intelligence Providers
# ==========================================
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
GEMINI_FALLBACK_MODEL=gemini-1.5-flash

# Optional Alternative Providers
AI_PROVIDER=gemini                     # Options: gemini, groq, openrouter, nvidia
GROQ_API_KEY=
OPENROUTER_API_KEY=
NVIDIA_API_KEY=

# ==========================================
# Podcast Diarization & B-Roll
# ==========================================
HF_TOKEN=                              # Hugging Face token for pyannote.audio
PEXELS_API_KEY=                        # Free Pexels key for contextual B-roll

# ==========================================
# Web Studio & API Security
# ==========================================
CLIPIT_API_KEY=                        # Secret key for Bearer auth (optional in local dev)
MAX_CONCURRENT_JOBS=2                  # Worker concurrency
CLIPIT_REDIS_URL=                      # e.g. redis://localhost:6379/0 for distributed queue
CLIPIT_WEBHOOK_URL=                    # Global webhook URL for job completion events
CLIPIT_WEBHOOK_SECRET=                 # HMAC-SHA256 signing secret
APP_TIMEZONE=UTC
```

---

## 4. Quick Start Cheatsheet

```bash
# 1. Generate 3 viral clips (9:16 portrait) with Hormozi kinetic subtitles
clipit --url "https://www.youtube.com/watch?v=VIDEO_ID" --clips 3 --ratio 9:16 --font-style HORMOZI

# 2. Podcast dynamic split-screen with camera-switching & diarization
clipit --url "https://..." --split-screen --dynamic-split --diarization-speakers 2

# 3. Add sound effects (SFX), semantic animated emojis, and scene-cut snapping
clipit --url "https://..." --use-sfx --semantic-emojis --snap-scene-cuts

# 4. Silence dead-air trimming + LUFS broadcast audio normalization
clipit --url "https://..." --silence-trim --normalize-audio --target-lufs -14

# 5. Launch interactive Web Studio
clipit-web --port 8000
```

---

## 5. Complete CLI Reference & Flag Groups

### 5.1 Source Input & Download Flags

- `--url <URL>...`: One or more YouTube/web video URLs.
- `--source <path>`: Local video file path instead of downloading.
- `--yt-cookies <path>`: Netscape-format cookie file for age-gated or membership YouTube videos.
- `--skip-download`: Reuse already downloaded video in `outputs/`.
- `--reuse <job_id>`: Resume an existing job from its saved transcription and AI analysis.
- `--cleanup-source`: Delete large raw input video files after rendering clips to save disk space.

### 5.2 Speech-to-Text (Whisper ASR) Tuning

- `--whisper-model <size>`: `tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3` (default: `large-v3`).
- `--whisper-device <device>`: `cuda` or `cpu`.
- `--whisper-compute-type <type>`: `float16`, `int8_float16`, or `int8` (for memory-constrained GPUs).
- `--use-dlp-subs`: Skip Whisper and extract official subtitles from YouTube if available.

### 5.3 AI Intelligence & Multi-Provider Routing

- `--ai-provider <provider>`: `gemini` (default), `groq`, `openrouter`, or `nvidia`.
- `--gemini-model <model>`: e.g. `gemini-2.0-flash`.
- `--gemini-fallback-model <model>`: Automatic fallback model on 429 quota exhaustion.
- `--load-gemini-json <path>`: Skip AI call and load pre-existing AI response JSON.

### 5.4 Smart Trimming, Silence Removal & Scene Snapping

- `--silence-trim`: Enable audio VAD to eliminate long pauses and dead air before segmentation.
- `--silence-thresh-db <dB>`: Threshold in dB below which audio is classified as silence (default: `-32.0`).
- `--silence-min-duration <sec>`: Minimum duration of pause to strip (default: `0.6`).
- `--snap-scene-cuts`: Automatically snap clip start and end timestamps to the nearest visual camera transition.
- `--scene-snap-distance <sec>`: Maximum distance to snap boundaries (default: `1.5s`).
- `--scene-cut-detector-threshold <float>`: Sensitivity for FFmpeg scene detection (default: `0.35`).

### 5.5 Visual Framing, Face-Tracking & Dynamic Split-Screen

- `--ratio <ratio>`: `9:16` (portrait / TikTok / Shorts), `1:1` (square / Instagram / LinkedIn), `16:9` (landscape), or `4:5`.
- `--face-detector <engine>`: `mediapipe` or `yolo`.
- `--split-screen`: Enable stacked layout for multi-person interviews or reaction videos.
- `--dynamic-split`: Dynamically switch between single-speaker close-up and dual-speaker split view.
- `--diarization-speakers <num>`: Number of distinct speakers for Pyannote speaker diarization.
- `--camera-switch`: Auto-cut camera view to focus on whoever is currently speaking.
- `--switch-hold-duration <sec>`: Minimum hold duration (default: `2.0s`) to prevent jittery camera cuts.

### 5.6 Kinetic Subtitles, Semantic Emojis & Typography

- `--font-style <preset>`: `HORMOZI`, `DEVIN`, `MRBEAST`, `ALI_ABDAAL`, `CLEAN_MODERN`, `NEON_CYBER`.
- `--semantic-emojis`: Automatically detect high-impact keywords (e.g. "money", "rocket", "shock", "fire", "danger") and burn contextual animated emojis directly into the subtitle stream.
- `--keyword-palette <palette>`: Color highlights for emphasized words: `modern` (cyan/yellow), `gold_amber` (gold/amber), `neon_cyber` (hot pink/cyan), `bold_red` (crimson/yellow), `classic` (yellow/green).
- `--no-subs`: Disable subtitle rendering completely.
- `--no-karaoke`: Disable animated word-by-word kinetic highlight, showing static lines instead.

### 5.7 Audio Mastering, BGM & Sound Effects (SFX)

- `--use-sfx`: Synthesize or layer punchy sound effects (whooshes, risers, impacts, pops) on viral hook transitions and scene changes.
- `--sfx-volume <float>`: Volume multiplier for sound effects (default: `0.85`).
- `--no-bgm`: Disable background music synthesis.
- `--bgm-mode <mode>`: `ducking` (sidechains BGM under speech by -16 dB), `loop`, or `custom`.
- `--normalize-audio`: Apply broadcast-standard EBU R128 loudness normalization.
- `--target-lufs <float>`: Target integrated loudness (default: `-14.0 LUFS` for streaming platforms).

### 5.8 Gaming & Streamer Highlight Detector

- `--streamer-mode`: Enable automated high-energy gameplay and stream moment detection.
- Combines audio volume RMS energy spike surge analysis with transcript hype trigger detection ("NO WAY", "LETS GO", "INSANE", "PENTAKILL") to pinpoint viral clips even without traditional speech narrative.

### 5.9 Content Persona Targeting & CTR Optimization

- `--persona <persona>`: Apply demographic and audience-tailored prompting:
  - `tech_founder`: Sharp, analytical hooks, engineering jargon, concise pacing.
  - `creator_entertainment`: High energy, curiosity gaps, emotive kinetic captions.
  - `finance_investor`: Actionable numbers, ROI insights, bold amber typography.
  - `education_explainer`: Step-by-step clarity, clean modern subtitles.
  - `fitness_motivation`: Driving tempo, high-contrast neon red styling.
- `--thumbnail-variants`: Generate high-CTR title variations and high-contrast thumbnail phrases with curiosity gaps.

### 5.10 Output Encoding, Video Quality & Hardware Acceleration

- `--video-encoder <encoder>`: `auto` (auto-detects `h264_nvenc` or falls back to `libx264`), `h264_nvenc`, `libx264`, or `h264_vaapi`.
- `--video-crf <int>`: CRF quality factor for `libx264` (default: `23`).
- `--video-cq <int>`: Constant Quality level for `h264_nvenc` (default: `24`).
- `--video-preset <preset>`: `slow`, `medium`, `fast`, or `p4`/`p5` for NVENC.
- `--render-height <int>`: Output vertical resolution (default: `1920` for 1080x1920 portrait).

### 5.11 Dry-Run, Seeding & Reproducibility

- `--dry-run`: Execute full downloading, transcription, deduplication, scene-cut snapping, and metadata generation while skipping heavy video encoding. Generates `render_manifest.json` for validation in CI pipelines.
- `--seed <int>`: Provide an integer seed to guarantee deterministic clip selection, BGM track alignment, and color randomization.

---

## 6. Interactive Web Studio (FastAPI + React 19)

### 6.1 Starting the Web Studio

```bash
# Start backend API (with auto-reload for development)
clipit-api --host 0.0.0.0 --port 8000

# Access interactive documentation:
# Swagger UI:  http://localhost:8000/docs
# ReDoc:       http://localhost:8000/redoc
# Health Ping: http://localhost:8000/api/health
```

In development, start Vite in `web/dashboard`:
```bash
cd web/dashboard && npm run dev
```

### 6.2 Managing Jobs & Real-Time Telemetry

The Web Studio provides:
- Live 7-stage progress tracking with percentage meters.
- Search, filter by status (`completed`, `processing`, `queued`, `failed`), and multi-tag filtering.
- Bulk actions: multi-job select, bulk cancel, retry, and recursive directory deletion.
- One-click zip bundle download (`/api/outputs/{job_id}/zip`) packing all rendered MP4s, thumbnails, and manifests.

### 6.3 Side-by-Side Multi-Layout Aspect Previewer

On the **Job Detail** page, creators can instantly toggle between:
- **9:16 Portrait**: TikTok, YouTube Shorts, Instagram Reels.
- **1:1 Square**: Instagram Feed, LinkedIn, Twitter/X.
- **16:9 Landscape**: YouTube long-form teasers.

### 6.4 Word-Level Interactive Transcript Editor

Inspect the generated transcript with sub-second word-level granularity. Clicking any word automatically seeks the video player to that exact timestamp, allowing creators to audit captions and hook timings before downloading.

### 6.5 Presets System & Community Template Marketplace (.clipit-pack)

Export and import portable `.clipit-pack` distribution bundles containing custom font files, background music, sound effects, and typography styling:

```bash
# Python SDK export:
from clipping.marketplace import export_pack, import_pack

export_pack(
    pack_name="Cyberpunk Viral",
    preset_data={"font_style": "NEON_CYBER", "pilihan_rasio": "9:16", "use_sfx": True},
    output_path="cyberpunk.clipit-pack",
    author="Clipit Community",
    asset_files={"custom_fonts/cyber.ttf": "/path/to/cyber.ttf"}
)

# Safe import with path traversal (Zip-Slip) prevention:
import_pack("cyberpunk.clipit-pack", install_dir="/path/to/clipit")
```

---

## 7. Enterprise Batch API & Distributed Workers

### 7.1 Single & Bulk Job Submissions

Submit batches of up to 100 video URLs or uploads atomically:

```http
POST /api/batch/jobs HTTP/1.1
Content-Type: application/json

{
  "items": [
    {
      "url": "https://www.youtube.com/watch?v=EPISODE_1",
      "pilihan_rasio": "9:16",
      "jumlah_klip": 3
    },
    {
      "url": "https://www.youtube.com/watch?v=EPISODE_2",
      "pilihan_rasio": "1:1",
      "jumlah_klip": 5
    }
  ],
  "default_config": {
    "font_style": "HORMOZI",
    "use_sfx": true,
    "semantic_emojis": true
  },
  "batch_webhook_url": "https://api.yourdomain.com/webhooks/clipit"
}
```

Response:
```json
{
  "batch_id": "batch_91fa4b18c0",
  "total_jobs": 2,
  "created_at": 1740838120.5,
  "jobs": [
    { "job_id": "job_01", "url": "https://...", "status": "pending" },
    { "job_id": "job_02", "url": "https://...", "status": "pending" }
  ]
}
```

Check aggregate batch progress:
```http
GET /api/batch/batch_91fa4b18c0
```

Cancel all jobs in a batch:
```http
POST /api/batch/batch_91fa4b18c0/cancel
```

### 7.2 Redis Distributed Task Queue

For horizontal scaling across multiple GPU worker nodes, configure `CLIPIT_REDIS_URL` in `.env`:
```ini
CLIPIT_REDIS_URL=redis://:strongpassword@redis-master:6379/0
```
Jobs are enqueued onto Redis FIFO lists, enabling multiple headless worker instances to consume tasks concurrently without duplicate execution.

### 7.3 Webhooks & HMAC-SHA256 Signature Verification

When a job completes or fails, Clipit dispatches a signed webhook:

```http
POST /your-webhook-endpoint HTTP/1.1
Content-Type: application/json
X-Clipit-Signature: sha256=d2f9b8c3e4...
X-Clipit-Timestamp: 1740838120

{
  "event": "job.completed",
  "timestamp": 1740838120.0,
  "data": {
    "job_id": "job_abc123",
    "status": "completed",
    "clips_count": 3,
    "download_urls": ["/api/files/download/job_abc123/clip_1.mp4"]
  }
}
```

Verify signatures in Python:
```python
from clipping.webhook import verify_webhook_signature

is_valid = verify_webhook_signature(
    payload_bytes=request.body,
    signature_header=request.headers.get("X-Clipit-Signature"),
    secret="YOUR_WEBHOOK_SECRET"
)
```

---

## 8. Serverless GPU Offload (Modal & RunPod)

When deploying Clipit on CPU-only instances or lightweight Kubernetes nodes, video rendering and Whisper transcription can be offloaded to serverless GPU workers:

Set in `.env`:
```ini
CLIPIT_GPU_OFFLOAD_PROVIDER=modal      # or 'runpod'
MODAL_ENDPOINT_URL=https://your-org--clipit-worker.modal.run/render
MODAL_AUTH_TOKEN=your_token
```

```python
from clipping.gpu_offload import get_gpu_offload_provider

provider = get_gpu_offload_provider()
task_id = provider.submit_task("render", {"manifest": [...], "video_url": "..."})
status = provider.get_status(task_id)
```

---

## 9. Multimodal Vision & Auto-Chapters Engine

### 9.1 Visual Frame Sharpness & Thumbnail Ranking

Automatically extract candidate frames across clip boundaries and rank them for clickability based on Laplacian gradient sharpness, dynamic contrast range, and luminance balance:

```python
from clipping.vision_scoring import rank_clip_frames

ranked_frames = rank_clip_frames(
    video_path="outputs/video.mp4",
    start_time=15.0,
    end_time=45.0,
    sample_count=5
)
# Returns list sorted descending by composite_score (0-100)
best_thumbnail = ranked_frames[0]["frame_path"]
```

### 9.2 YouTube Chapters & Markdown Show Notes

Convert transcribed segments into formatted YouTube description chapters and SEO markdown summaries:

```python
from clipping.chapters import generate_chapters_from_clips, generate_show_notes

chapters = generate_chapters_from_clips(clips)
# Formats timestamps: 00:00 - Introduction, 01:23 - The Big Secret

show_notes = generate_show_notes(
    title="Episode 55: AI Breakthroughs",
    summary="A deep dive into frontier models.",
    chapters=chapters,
    takeaways=["Inference speed matters", "Open weights lead adoption"],
    source_url="https://youtube.com/watch?v=..."
)
```

### 9.3 Copyright Safety & Originality Transforms

Audit candidate clips for automated Content ID risks:

```python
from clipping.copyright import analyze_content_safety, recommend_originality_transforms

report = analyze_content_safety(
    transcript="Track performed by Taylor Swift under Universal Music",
    has_commercial_bgm=True,
    continuous_duration_sec=60.0
)

# Suggests fair-use transformations:
transforms = recommend_originality_transforms(report)
# Includes: +1.2 semitone audio pitch shifting, 1.03x tempo ramping,
# dynamic B-roll cutaway cadence, and voiceover sidechain ducking.
```

---

## 10. Typed Python Client SDK

Clipit includes a typed Python client SDK located at `sdk/python/clipit_sdk.py`:

```python
from sdk.python import ClipitClient

client = ClipitClient(base_url="http://localhost:8000", api_key="my_secret_key")

# Submit a job
job = client.submit_job(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ratio="9:16",
    clips=3,
    preset="tiktok_viral"
)
print(f"Created job: {job['id']}")

# Poll until complete
result = client.poll_job_until_done(job["id"], timeout_sec=600)
for clip in result.get("clips", []):
    print(f"Clip {clip['rank']}: {clip['download_url']}")
```

---

## 11. Model Context Protocol (MCP) Server for AI Agents

Clipit provides an integrated stdio Model Context Protocol (MCP) server (`clipping/mcp_server.py`) allowing AI assistants (Claude Desktop, Cursor, OpenCode, Antigravity) to orchestrate video clipping tasks:

Add to your MCP configuration (e.g. `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "clipit": {
      "command": "python3",
      "args": ["-m", "clipping.mcp_server"],
      "env": {
        "GOOGLE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Exposed Tools:
- `clipit_generate_clips`: Generate clips with ratio, typography, and AI parameters.
- `clipit_get_system_health`: Inspect FFmpeg availability and encoder hardware readiness.
- `clipit_list_presets`: List available pipeline presets.
- `clipit_schedule_calendar`: Generate a 7-day multi-platform social release calendar.

---

## 12. Plugin Architecture & Lifecycle Hooks

Extend pipeline execution with custom Python hook handlers:

```python
from clipping.plugins import hook, HOOK_DOWNLOAD_COMPLETE, HOOK_RENDER_COMPLETE

@hook(HOOK_DOWNLOAD_COMPLETE, priority=5)
def custom_watermark_injector(payload):
    video_path = payload.get("video_path")
    print(f"Downloaded video at {video_path}. Injecting custom pre-filter...")
    return {"tagged": True}

@hook(HOOK_RENDER_COMPLETE, priority=10)
def sync_to_s3(payload):
    manifest = payload.get("render_manifest")
    # Upload rendered MP4 files to S3 / Cloudflare R2
    return {}
```

Place `.py` plugin files in `plugins/` or set `CLIPIT_PLUGIN_DIR` to auto-discover and load them on startup.

---

## 13. Troubleshooting & Diagnostics

| Symptom | Probable Cause | Recommended Resolution |
|---|---|---|
| `FFmpeg was not detected in system PATH` | FFmpeg missing or not in PATH | Install FFmpeg via package manager (`sudo apt install ffmpeg` / `brew install ffmpeg`) and verify with `ffmpeg -version`. |
| `GOOGLE_API_KEY not found` | Environment variable missing | Set `GOOGLE_API_KEY` in `.env` or pass via Web Studio Settings. |
| `CUDA out of memory` during Whisper | Whisper model too large for VRAM | Use `--whisper-model small` or `--whisper-compute-type int8` or `--whisper-device cpu`. |
| Subtitle characters garbled | Missing font glyphs | Install fonts or place TrueType fonts in `custom_fonts/` and use `--font-style`. |
| Web Studio shows `503 Service Unavailable` on `/api/health/ready` | FFmpeg missing or disk full | Run `curl http://localhost:8000/api/health/ready` to view specific component readiness breakdown. |
| YouTube download fails (HTTP 429 / bot detection) | Outdated yt-dlp or IP rate limit | Update yt-dlp (`pip install -U yt-dlp`) and provide browser cookies via `--yt-cookies cookies.txt`. |

Run self-diagnostic check:
```bash
python3 -c "from clipping.hardware import check_system_readiness; print(check_system_readiness())"
```

---

## 14. Licensing (GNU AGPLv3)

Clipit is free software licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0-or-later)**.

- You have the freedom to run, modify, inspect, and distribute Clipit.
- If you run a modified version of Clipit on a network server or provide it as a hosted service, you **must make the complete source code of the modified version available to all network users** under the AGPLv3 license.
- See the full license text in the [LICENSE](file:///home/sensei/Projects/backend/clipit/LICENSE) file.
