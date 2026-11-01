# Clipit — Comprehensive Roadmap

> Living document. Tracks the current state, gaps, planned enhancements, and long-term
> vision for Clipit (AI Auto-Clipper & Teaser Generator). Update as milestones ship.

---

## 1. Project Summary

Clipit transforms long-form video into short-form, platform-ready clips. It combines
download, transcription (Faster-Whisper), AI analysis (Gemini / NVIDIA), face-aware
auto-framing, B-roll, karaoke subtitles, cinematic hooks, BGM ducking, voice-over, and
multi-speaker podcast layouts into a single render pipeline. It ships as both a CLI
(`main.py`) and a web studio (FastAPI backend + React dashboard).

- **Version:** 1.6.9 (Unified CLI, Web Studio, API, and Package Manifests)
- **License:** AGPL-3.0
- **Author:** Ayoub Zulfiqar
- **Repo:** https://github.com/ayoubzulfiqar/clipit

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  CLI (main.py)  ──►  clipping/ (core pipeline)              │
│  Web (React)    ──►  web/api (FastAPI)  ──►  clipping/      │
└──────────────────────────────────────────┬──────────────────┘
                                           │
        ├── clipping/engine.py          download + transcribe + Gemini analysis
        ├── clipping/runner.py          orchestration (single + batch)
        ├── clipping/story_runner.py    multi-source story clip mode
        ├── clipping/studio/            canonical package (__init__.py facade,
        │                               core, effects, subtitles, transitions,
        │                               bgm, watermark, face detection,
        │                               typography, thumbnail)
        ├── clipping/config.py          ClipitConfig typed model + CLI builder
        ├── clipping/metadata.py        title/description/tags per platform
        ├── clipping/voiceover.py       TTS commentary pipeline
        ├── clipping/diarization.py     speaker diarization (Pyannote 3.1)
        ├── clipping/hook_manager.py    hook V2 management
        ├── web/api/store.py            SQLite persistent store (WAL mode)
        └── web/api/routes/system.py    system health & readiness probes
```

Supporting surfaces: `docs/` (static GitHub Pages studio + legal), `wiki/` (GitHub
wiki), `notebooks/` (Colab/Kaggle), `youtube_tracker/`, `youtube_uploader/`,
`facebook_uploader/`.

---

## 3. Current Capability Matrix

### 3.1 Input / Source
- Platforms: YouTube, TikTok, Instagram, Google Drive
- Single URL, batch multi-URL, uploaded files, reuse of prior job artifacts
- Optional cookies, custom source height, skip-download (offline reuse)

### 3.2 Analysis
- Transcription: Faster-Whisper (large-v3), word-level timestamps, CUDA/CPU
- AI providers: Google Gemini (primary), NVIDIA (fallback)
- Gemini fallback model, loadable cached Gemini JSON
- AI-driven clip selection, segment trimming, silence trim, scene-cut detection

### 3.3 Rendering
- Aspect ratios: 9:16, 16:9, 1:1, 3:4, 4:5
- Face-aware auto-framing (MediaPipe / YOLO), smooth pan, deadzone, anti-jitter
- Split-screen podcast (2+ speakers, diarization, dynamic split, camera-switch)
- B-roll (Pexels) with crossfade + Ken Burns, hybrid/split/camera-switch modes
- Karaoke subtitles (ASS, word-by-word highlight)
- Kinetic typography (bounce/stagger, dual-font)
- Cinematic teaser hook (3s, dark overlay, TV glitch)
- Multi-hook V2 intros
- BGM with sidechain ducking or background mode, auto-loop
- Watermark (text/image, 9 anchors, opacity, scale)
- Auto-thumbnail generation
- Voice-over commentary (Gemini script + edge-tts, audio ducking, text override, edge glow)
- Edge glow (default/smooth/full modes)
- Video encoder tuning (CRF, CQ, bitrate, preset, sharpen, scale algo)
- Custom fonts, dev-mode outputs, cleanup of source video

### 3.4 Story Clip Mode
- Multi-source narrative assembly from `sources.json` + recipe
- Per-scene clip trimming, ordering, normalization
- Skip-download for cached sources

### 3.5 Distribution & Tooling
- YouTube auto-uploader with scheduling + metadata
- Facebook Reels uploader (Meta Graph API, smart scheduling)
- YouTube playlist tracker (local snapshot DB)
- Web Studio (FastAPI + React dashboard): job queue, file browser, settings
- Docker / docker-compose (backend + frontend)
- GitHub Pages static docs + studio

---

## 4. Known Gaps & Technical Debt

1. **Automated tests.** [RESOLVED] Built a 29-test automated test suite across unit, security, storage, and E2E pipeline orchestration (`tests/`).
2. **Version drift.** [RESOLVED] Unified to `1.15.0` single source of truth across CLI, FastAPI backend, `pyproject.toml`, and frontend `package.json`.
3. **CI/CD.** [RESOLVED] Multi-Python matrix workflow (`.github/workflows/ci.yml`) testing Python 3.10–3.13 and building the Vite frontend on push/PR.
4. **Heavy dependencies.** Whisper/MediaPipe/OpenCV/Pyannote install is fragile; no lock file or extras groups.
5. **No auth on web API.** Studio backend is open; CORS only. No user accounts, roles, or API keys.
6. **Job store persistence.** [RESOLVED] Upgraded from in-memory dict + periodic file dumps to thread-safe SQLite with WAL mode, legacy JSON auto-migration, and server startup orphan reconciliation (`web/api/store.py`).
7. **Worker is single-process.** In-process `ThreadPoolExecutor` and `asyncio.Semaphore`; needs distributed task broker (ARQ / Celery / Redis) for multi-worker scaling.
8. **Observability.** [PARTIAL] Added `/api/health` and `/api/health/ready` system diagnostic probes checking FFmpeg, encoders, and storage. Need structured tracing / Sentry.
9. **Frontend has no tests.** React dashboard untested; no E2E (Vitest / Playwright).
10. **i18n expanded.** README now available in English, Arabic, Russian, Chinese, Korean. UI/CLI localization still pending.
11. **No plugin system.** Extensions require core edits.
12. **Notebooks drift.** Colab/Kaggle notebooks may be out of sync with CLI.
13. **No model caching strategy.** Whisper/Gemini models re-downloaded per environment.
14. **Security.** [RESOLVED] Path traversal strictly patched in `files.py` using `os.path.realpath` and `os.path.commonpath` checks rejecting `/etc/passwd` and `../` traversal.
15. **Accessibility.** Static docs/dashboard not WCAG-audited.
16. **No telemetry/opt-in analytics.** Hard to understand usage.

---

## 5. Roadmap

### Phase 0 — Stabilization (100% Complete)
- [x] Single source of truth for version (unified `1.15.0` across `clipping`, `pyproject.toml`, `main.py`, `web/api`, `package.json`).
- [x] Add GitHub Actions: multi-Python matrix test (3.10–3.13) + Node 22 frontend build on push/PR (`.github/workflows/ci.yml`).
- [x] Add automated unit & integration test suite (35 passing tests in `tests/` covering config, store, metadata, security, ASS, health, and E2E).
- [x] Fix path-safety in `files.py` (canonical realpath and commonpath validation against directory escape).
- [x] Resolve package import collision in `clipping/studio` (eliminated dynamic `importlib` spec hack; canonical package with relative imports).
- [x] Lock frontend dependencies (`web/dashboard/package-lock.json`) and ignore `node_modules` in `.gitignore`.
- [x] Add `pyproject` optional dependency groups (`[gpu]`, `[podcast]`, `[dev]`, `[ai]`, `[cv]`, `[uploader]`, `[all]`).
- [x] Generate pinned `requirements-lock.txt` using `uv pip compile`.
- [x] Add pre-commit hooks (`.pre-commit-config.yaml` for ruff, black, trailing-whitespace, check-yaml).
- [x] Normalize logging (structured JSON + leveled console formatting with `job_id` context in `clipping/logger.py`).
- [x] Document environment variables in `.env.sample` and add programmatic validation engine (`clipping/env_validator.py`).

### Phase 1 — Core Pipeline Enhancements (100% Complete)
- [x] **Multi-provider AI abstraction.** Unified `BaseAIProvider` interface supporting Gemini, NVIDIA, OpenAI, Anthropic, and local offline Ollama with automatic fallback chain and token cost tracking (`clipping/ai/`).
- [x] **Local/offline mode.** Zero-cloud local LLM execution via Ollama (`clipping/ai/openai_compatible.py`) without cloud API keys.
- [x] **Resume/retry.** Checkpoint pipeline stages (`transcription_cache.json`, `gemini_response.json`, existing MP4 clips); resume from failure without re-running transcription (`clipping/runner.py`, `--resume` / `--no-resume`).
- [x] **Better clip ranking.** Viral-potential scoring with explainable factors (`hook_strength`, `engagement_potential`, `emotional_intensity`, `pacing_score`, `virality_explanation`) in `clipping/engine.py` and `clipping/metadata.py`.
- [x] **Smart silence trimming improvements.** Programmatic silence and pause detection from word timestamps, dead-air removal, dynamic speech keep segments, and filler-word filtering (`clipping/silence.py`, `--silence-trim`).
- [x] **Multi-language subtitles.** Sidecar `.srt` and `.vtt` export with normalized clip timestamps and multi-language AI translation (`clipping/studio/subtitles.py`, `--export-subtitles`, `--subtitle-languages`).
- [x] **Aspect-ratio presets for platforms.** TikTok/Reels/Shorts/LinkedIn/X with UI safe-zone margins (`clipping/studio/presets.py`, `--platform`).
- [x] **Thumbnail A/B variants.** Multi-candidate thumbnail generation per clip at hook, midpoint, and climax timestamps (`clipping/studio/thumbnail.py`, `--thumbnail-variants`).
- [x] **Audio normalization & loudness (LUFS).** EBU R128 integrated loudness target (-14 LUFS) and true-peak limiting (`clipping/studio/audio_bgm.py`, `--normalize-audio`, `--target-lufs`).
- [x] **GPU auto-detection & fallback.** Pick CUDA/CPU automatically; report capabilities in `/api/health/ready` (`clipping/hardware.py`, `WHISPER_DEVICE="auto"`).

### Phase 2 — Web Studio & UX (2–4 months)
- [x] **Authentication & API keys.** `CLIPIT_API_KEY` authentication middleware (`X-API-Key` / Bearer token) protecting API routes with public health probe exceptions (`web/api/app.py`).
- [x] **Persistent job store.** SQLite with WAL mode, auto-migration from legacy `jobs.json`, and startup orphan recovery (`web/api/store.py`).
- [x] **Real-time progress.** SSE streaming for job stages (`web/api/routes/jobs.py`).
- [x] **Health & readiness diagnostics.** `/api/health` and `/api/health/ready` endpoints (`web/api/routes/system.py`).
- [x] **Distributed task queue.** Decoupled task queue architecture (`web/api/queue.py`) supporting local bounded threadpools and distributed Redis FIFO lists / pubsub (`CLIPIT_REDIS_URL`).
- [x] **Job management.** Cancel, retry, clone, tag, search, filter, and bulk actions (`web/api/store.py`, `web/api/routes/jobs.py`).
- [x] **File manager improvements.** Output bundle zip downloads (`/api/outputs/{job_id}/zip`), recursive directory removal, and automated file retention cleanup (`/api/files/cleanup` in `web/api/routes/files.py`).
- [x] **Settings UI & Secrets management.** Masked API key management, default ratio/provider selection, and runtime updates (`web/api/routes/settings.py`).
- [x] **Preset system.** Save/load/delete full pipeline named presets (`tiktok_viral`, `youtube_shorts_clean`, `reels_aesthetic`, `podcast_split`, `linkedin_square`) in `web/api/store.py` and `web/api/routes/presets.py`.
- [x] **Dark/light theme polish + accessibility audit.** Toggleable dark/light themes with localStorage persistence and CSS design tokens (`web/dashboard/src/App.jsx`, `web/dashboard/src/index.css`).
- [x] **Mobile-responsive dashboard.** Drawer sidebar navigation, mobile header bar, responsive video aspect previewers, and auto-fitting grids.
- [ ] **i18n.** English/Indonesian (and more) via i18next; CLI messages localized.

### Phase 3 — Content Intelligence (In Progress)
- [ ] **Performance feedback loop.** Ingest YouTube/TikTok analytics; correlate with clip features.
- [x] **CTR/title optimization.** Score candidate titles for viral clickability (0-100), generate A/B curiosity gap angles, and suggest high-contrast thumbnail phrases (`clipping/ctr_optimizer.py`).
- [x] **Audience persona targeting.** Demographic and niche-tailored prompts and typography presets (`tech_founder`, `creator_entertainment`, `finance_investor`, `education_explainer`, `fitness_motivation` in `clipping/persona.py`).
- [x] **Duplicate/near-duplicate detection.** Temporal IoU interval filtering and semantic token shingle similarity to drop redundant clip candidates (`clipping/dedup.py`).
- [x] **Content calendar & scheduling.** Multi-platform publication calendar with peak-time slot optimization, CSV, and JSON export (`clipping/scheduler.py`).
- [ ] **Auto-posting.** Direct publish to YouTube/TikTok/IG/FB with OAuth.
- [x] **Brand kit.** Logos, color palettes, typography, and bumper templates applied automatically (`clipping/brand_kit.py`).

### Phase 4 — Platform & Distribution (4–8 months)
- [x] **Docker images published** to GHCR; multi-arch (amd64/arm64) via GitHub Actions (`.github/workflows/docker.yml`).
- [x] **One-click deploy.** Multi-cloud deployment manifests (`render.yaml`, `fly.toml`, `railway.json`) and docker-compose with Redis support.
- [x] **Serverless GPU.** Modal / RunPod / custom HTTP serverless workers for render offload (`clipping/gpu_offload.py`).
- [x] **Desktop app.** Desktop application launcher and process orchestrator bundling server lifecycle + ffmpeg detection (`desktop/launcher.py`).
- [x] **CLI distribution.** Script entrypoints (`clipit`, `clipit-web`, `clipping`) declared in `pyproject.toml` for PyPI / local pip installation.
- [x] **API product.** Public REST API with keys, rate limits, webhooks, batch endpoints (`/api/batch/jobs`), and typed Python SDK (`sdk/python/clipit_sdk.py`).

### Phase 5 — Extensions & Ecosystem (6–12 months)
- [x] **Plugin architecture.** Extensible lifecycle hook registry (`on_download_complete`, `on_transcribe_complete`, `on_clips_scored`, `on_render_complete`) with dynamic script discovery (`clipping/plugins.py`).
- [x] **Marketplace.** Export, inspect, and safely install portable `.clipit-pack` distribution bundles containing presets, fonts, and audio assets (`clipping/marketplace.py`).
- [x] **Webhook/Zapier/Make integrations.** HMAC-SHA256 signed event delivery on job completion, failure, and milestones (`clipping/webhook.py`, `web/api/worker.py`).
- [x] **MCP server.** Expose Clipit as tools for AI agents (generate clips, inspect health, query presets, and schedule calendars via stdio JSON-RPC in `clipping/mcp_server.py`).
- [x] **Batch API & webhooks for enterprise.** Bulk job submission (`POST /api/batch/jobs`), status aggregation, and batch cancellation (`web/api/routes/batch.py`).
- [ ] **White-label.** Rebrandable studio for agencies.

### Phase 6 — Research & Advanced (12+ months)
- [ ] **On-device models.** Quantized Whisper/LLM for edge.
- [x] **Multimodal analysis.** Visual frame quality analyzer scoring sharpness, contrast, brightness, and composition to rank viral thumbnail candidates (`clipping/vision_scoring.py`).
- [ ] **Speaker-aware editing.** Auto-switch camera, name tags, lower-thirds.
- [x] **Auto-chapters & summaries.** Generate YouTube/Spotify timestamped chapters, markdown show notes, and SEO keyword extractors (`clipping/chapters.py`).
- [x] **Copyright safety.** Detect copyrighted audio/visual signals and recommend originality transformations (pitch shifting, tempo ramping, voiceover ducking) to safeguard monetization (`clipping/copyright.py`).
- [ ] **Federated learning (opt-in).** Improve scoring models from anonymized feedback.

---

## 6. Backlog by Category

### Core Engine
- Retry transient download/transcription failures with backoff
- Parallel clip rendering (process pool)
- Memory-efficient long-video handling (chunked)
- [x] Deterministic seeds for reproducible renders (`--seed`, random generator initialization)
- [x] Dry-run mode (`--dry-run`, analysis and manifest preview without video rendering)

### Studio / Rendering
- Custom LUT/color grading
- Animated lower-thirds & intro/outro
- Picture-in-picture reaction layout
- Green-screen/chroma key
- Stabilization pass
- Speed ramping / slow-mo highlights
- [x] Auto-crop to 4:5/1:1 with safe zones (`clipping/studio/presets.py`)
- [x] Subtitle style presets (TikTok, Reels, Shorts)

### AI & Analysis
- Provider cost dashboard
- Prompt templates editable in UI
- Few-shot examples for better clip selection
- Confidence scores per clip
- Human-in-the-loop approval before render

### Distribution
- Direct TikTok/IG publishing (OAuth)
- Buffer/Hootsuite integration
- RSS/podcast feed generation
- Email digest of new clips

### Developer Experience
- [x] SDK + typed client (`sdk/python/clipit_sdk.py`, `ClipitClient`)
- OpenAPI spec published
- [x] Webhook docs + signature verification (`clipping/webhook.py`, HMAC-SHA256 signatures)
- Docker devcontainer
- Makefile targets
- Storybook for dashboard components

### Quality & Ops
- [x] Unit/integration/E2E test suites (29 passing tests in `tests/`)
- [x] CI/CD multi-Python matrix testing (`.github/workflows/ci.yml`)
- [x] Health & readiness probes for monitoring / k8s (`/api/health`, `/api/health/ready` in `web/api/routes/system.py`)
- [x] Startup orphan job reconciliation on server crash/restart (`web/api/store.py`)
- Load testing for worker queue
- Backup/restore for job store
- Rate limiting & abuse protection
- Audit log
- Graceful shutdown (already partial)

---

## 7. Competitive Parity & Market Benchmark Roadmap

> Benchmarked against open-source peers (**`FujiwaraChoki/supoclip`**, **`GrepCut/OpenClipper`**) and 22 commercial market leaders (**Opus Clip, Klap, 2short.ai, Dumme, Munch, Qlip, Spikes Studio, Vidyo.ai, Vizard AI, Ssemble, Veed.io, Submagic, Zubtitle, Wisecut, LiveLink, SendShort, Short.ai, Nexus Clips, Wayin, ClipGoat, CutLabs, Exemplary AI**).

### 7.1 Clipit Core Moats (Where Clipit Wins)
- **100% Unmetered & Self-Hostable:** Zero per-minute credit limits, zero subscription paywalls, 100% local data privacy.
- **Advanced Spatial Reframing:** Hybrid focus/zoom, dynamic split-screen (Pyannote 3.1 + MediaPipe/YOLO dual-face tracking), and speaker-aware camera switching.
- **Native ASS Subtitle Synthesis:** Hardware-accelerated libass FFmpeg rendering bypassing headless Chromium/Canvas bottlenecks.
- **Dual Headless & Web Execution:** CLI for headless batch processing alongside modern React 19 + FastAPI Web Studio.

### 7.2 Competitive Feature Parity Workstreams

#### A. Kinetic Typography & Audio-Visual Polish (Submagic & Opus Clip Benchmark)
- [x] **Transcript Semantic Emoji Engine:** Detect keywords in transcript (e.g. "money", "rocket", "shock", "warning") and auto-composite contextual animated emojis into the ASS subtitle stream (`clipping/emoji_engine.py`, `--semantic-emojis`).
- [x] **Dynamic Sound Effects (SFX) Compositing:** Auto-layer whooshes, pops, risers, and impact sound effects on hook transitions and punchlines via synthetic FFmpeg or local assets (`clipping/studio/sfx.py`, `--use-sfx`).
- [x] **Auto-Highlight Keyword Coloring:** Multi-palette color highlights driven by semantic emotion and LLM emphasis markers (`clipping/emoji_engine.py`, `clipping/studio/subtitles.py`, `--keyword-palette`).

#### B. Smart Trimming & Retention Engineering (Wisecut & Opus Clip Benchmark)
- [x] **Automated Silence & Dead-Air Removal (Jump-Cutter):** Pre-pass audio VAD / FFmpeg `silencedetect` and word timestamp analysis to auto-splice pauses and filler words before LLM segmentation (`clipping/silence.py`, `--silence-trim`).
- [x] **Scene-Cut Auto-Snapping:** Detect natural camera transitions (`select='gt(scene,0.35)'`) and snap clip boundaries to clean scene changes (`clipping/scene_detect.py`, `--snap-scene-cuts`).

#### C. Interactive Web Studio Experience (Veed.io, Vizard AI & Opus Clip Benchmark)
- [x] **Interactive Waveform Scrubber & Trimmer:** Visual audio waveform timeline in React 19 dashboard with interactive amplitude seeking (`web/dashboard/src/pages/JobDetail.jsx`).
- [x] **Transcript Text-Based Video Editor:** Interactive word-level transcript inspector allowing users to click words to seek and inspect frame timings directly (`web/dashboard/src/pages/JobDetail.jsx`).
- [x] **Side-by-Side Multi-Layout Previewer:** Real-time aspect ratio comparison (9:16 vs 1:1 vs 16:9) in React dashboard (`web/dashboard/src/pages/JobDetail.jsx`).

#### D. Multi-Platform Publishing & Scheduling (Munch, Short.ai & SendShort Benchmark)
- [ ] **Native OAuth Multi-Platform Publishing:** Direct scheduled publishing to TikTok Content Posting API, YouTube Shorts API, and Instagram Reels Graph API.
- [x] **Automated Social Copy Customization:** Platform-specific character count and hashtag limit enforcement per destination channel (`clipping/metadata.py`).

#### E. Distributed Infrastructure & Scaling (SupoClip & Enterprise Benchmark)
- [x] **Decoupled Task Broker:** Transition in-process `ThreadPoolExecutor` to Redis-backed queue (`web/api/queue.py`, `CLIPIT_REDIS_URL`) for horizontal scaling across multi-GPU nodes.
- [x] **Serverless GPU Offload:** Runner backend interface targeting Modal / RunPod / custom HTTP workers for remote render offload (`clipping/gpu_offload.py`).

#### F. Gaming & Streaming Highlights (Nexus Clips, Spikes Studio & CutLabs Benchmark)
- [x] **Streamer & Esports Highlight Detector:** Audio volume/RMS peak energy surge analysis and transcript hype trigger detector to isolate high-intensity gameplay moments (`clipping/stream_highlight.py`).

---

## 8. Non-Functional Requirements

- **Performance:** 10-min video → 5 clips in < 15 min on mid-tier GPU.
- **Reliability:** 99% job success rate; automatic retry of transient failures.
- **Scalability:** Horizontal worker scaling; stateless API.
- **Security:** Auth, secret management, input validation, sandboxed ffmpeg.
- **Privacy:** No PII in logs; opt-in telemetry; data deletion endpoint.
- **Compatibility:** Python 3.10+, FFmpeg 5+, CUDA 11.8+/CPU fallback.
- **Observability:** Structured logs, metrics (Prometheus), traces (OpenTelemetry).

---

## 9. Success Metrics

- Clip render success rate ≥ 99%
- Median processing time per minute of source ≤ 90s (GPU)
- User-reported "viral hit" rate tracking
- Dashboard Lighthouse score ≥ 90
- Test coverage ≥ 70% on core modules
- Time-to-first-clip for new user ≤ 10 min

---

## 10. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| API key cost/quota (Gemini) | Multi-provider fallback, caching, local LLM option |
| Heavy dependency install failures | Optional groups, lock files, Docker image |
| YouTube/TikTok anti-bot changes | yt-dlp auto-upgrade, cookie support, proxy config |
| Copyright strikes | Voice-over commentary mode, originality transforms |
| GPU availability | CPU fallback, serverless GPU offload |
| Scope creep | Phased roadmap, milestone gating |

---

## 11. Contribution & Release Process

- Branch from `main`; conventional commits.
- PR requires: lint + typecheck + tests green.
- Version bump via `pyproject.toml` (single source of truth).
- Changelog updated per release (keep `CHANGELOG.md`).
- Tag release `vX.Y.Z`; GitHub Actions builds & publishes Docker image + PyPI.

---

## 12. Appendix — CLI Flag Groups

- Source & input: `--url`, `--source`, `--yt-cookies`, `--skip-download`, `--reuse`
- Output: `--clips`, `--ratio`, `--outputs-dir`, `--cleanup-source`
- Transcription: `--whisper-model`, `--whisper-device`, `--whisper-compute-type`, `--use-dlp-subs`
- AI: `--gemini-model`, `--gemini-fallback-model`, `--ai-provider`, `--nvidia-model`, `--load-gemini-json`
- Framing: `--face-detector`, `--box-face-detection`, `--track-*`, `--static-crop`
- Rendering: `--font-style`, `--semantic-emojis`, `--keyword-palette`, `--no-subs`, `--no-karaoke`, `--hook-duration`, `--no-hook`, `--hook-v2*`
- B-roll: `--no-broll`, `--hook-source`, `--hook-source-start`
- Audio: `--no-bgm`, `--bgm-mode`, `--use-sfx`, `--sfx-volume`, `--normalize-audio`, `--target-lufs`, `--edge-glow*`, `--original-volume`
- Podcast: `--split-screen`, `--dynamic-split`, `--split-*`, `--diarization-speakers`, `--camera-switch`, `--switch-*`
- Watermark: `--watermark`, `--image`, `--text`, `--position`, `--opacity`, `--padding`, `--watermark-*`
- Voice-over: `--voiceover*`
- Story mode: `--story-mode`, `--story-recipe`, `--sources-json`, `--story-output-dir`, `--skip-download`
- Video encoding: `--video-crf`, `--video-cq`, `--video-bitrate`, `--video-preset`, `--video-sharpen`, `--video-scale-algo`, `--render-height`, `--source-height`
- Misc & Optimization: `--dev-mode*`, `--white-flash-duration`, `--silence-trim`, `--snap-scene-cuts`, `--scene-snap-distance`, `--dedup`, `--thumbnail-variants`, `--dry-run`, `--seed`

---

*End of roadmap. Contributions welcome — see `wiki/14-Contributing.md`.*
