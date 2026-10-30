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

- **Version:** 1.15.0 (Unified CLI, Web Studio, API, and Package Manifests)
- **License:** MIT
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

### Phase 0 — Stabilization (Shipped & Hardened)
- [x] Single source of truth for version (unified `1.15.0` across `clipping`, `pyproject.toml`, `main.py`, `web/api`, `package.json`).
- [x] Add GitHub Actions: multi-Python matrix test (3.10–3.13) + Node 22 frontend build on push/PR (`.github/workflows/ci.yml`).
- [x] Add automated unit & integration test suite (29 passing tests in `tests/` covering config, store, metadata, security, ASS, health, and E2E).
- [x] Fix path-safety in `files.py` (canonical realpath and commonpath validation against directory escape).
- [x] Resolve package import collision in `clipping/studio` (eliminated dynamic `importlib` spec hack; canonical package with relative imports).
- [x] Lock frontend dependencies (`web/dashboard/package-lock.json`) and ignore `node_modules` in `.gitignore`.
- [ ] Add `pyproject` optional dependency groups (`[gpu]`, `[podcast]`, `[dev]`).
- [ ] Generate `requirements-lock.txt` / use `uv` or `poetry`.
- [ ] Add pre-commit hooks (ruff, black, mypy, pytest).
- [ ] Normalize logging (structured, levels, request IDs).
- [ ] Document environment variables in `.env.sample` (already good; add validation).

### Phase 1 — Core Pipeline Enhancements (1–3 months)
- [ ] **Multi-provider AI abstraction.** Interface for LLM providers (Gemini, OpenAI, Anthropic, local Ollama) with fallback chain and cost tracking.
- [ ] **Local/offline mode.** Run with Whisper + local LLM (Ollama) without cloud keys; cache models.
- [ ] **Resume/retry.** Checkpoint pipeline stages; resume from failure without re-running transcription.
- [ ] **Better clip ranking.** Viral-potential scoring (hook strength, pacing, emotion) with explainable factors.
- [ ] **Smart silence trimming improvements.** Scene-aware cut points, filler-word removal.
- [ ] **Multi-language subtitles.** Auto-translate subtitles (Gemini) to N languages; sidecar SRT/VTT.
- [ ] **Aspect-ratio presets for platforms.** TikTok/Reels/Shorts/LinkedIn/X with safe zones.
- [ ] **Thumbnail A/B variants.** Generate multiple thumbnails; pick by CTR prediction.
- [ ] **Audio normalization & loudness (LUFS).** EBU R128 target, true-peak limiting.
- [ ] **GPU auto-detection & fallback.** Pick CUDA/CPU automatically; report capabilities.

### Phase 2 — Web Studio & UX (2–4 months)
- [ ] **Authentication & multi-user.** JWT/OAuth, per-user jobs, quotas, roles (admin/user).
- [x] **Persistent job store.** SQLite with WAL mode, auto-migration from legacy `jobs.json`, and startup orphan recovery (`web/api/store.py`).
- [x] **Real-time progress.** SSE streaming for job stages (`web/api/routes/jobs.py`).
- [x] **Health & readiness diagnostics.** `/api/health` and `/api/health/ready` endpoints (`web/api/routes/system.py`).
- [ ] **Distributed task queue.** Decouple in-process threadpool to Redis queue (ARQ/Celery/RQ) for multi-worker scaling.
- [ ] **Job management.** Cancel, retry, clone, tag, search, filter, bulk actions.
- [ ] **File manager improvements.** Preview (video player), rename, download zip, retention policies.
- [ ] **Settings UI.** Secrets management, provider selection, presets, import/export config.
- [ ] **Preset system.** Save/load full pipeline presets (named profiles).
- [ ] **Dark/light theme polish + accessibility audit.**
- [ ] **Mobile-responsive dashboard.**
- [ ] **i18n.** English/Indonesian (and more) via i18next; CLI messages localized.

### Phase 3 — Content Intelligence (3–6 months)
- [ ] **Performance feedback loop.** Ingest YouTube/TikTok analytics; correlate with clip features.
- [ ] **CTR/title optimization.** Generate and score titles/thumbnails; A/B test suggestions.
- [ ] **Audience persona targeting.** Tune hooks/subtitles for niche.
- [ ] **Duplicate/near-duplicate detection.** Avoid re-rendering similar clips.
- [ ] **Content calendar & scheduling.** Plan posts across platforms; optimal time suggestions.
- [ ] **Auto-posting.** Direct publish to YouTube/TikTok/IG/FB with OAuth.
- [ ] **Brand kit.** Logos, fonts, colors, intro/outro templates applied automatically.

### Phase 4 — Platform & Distribution (4–8 months)
- [ ] **Docker images published** to GHCR; multi-arch (amd64/arm64).
- [ ] **One-click deploy.** Render/Fly.io/Railway templates; Helm chart.
- [ ] **Serverless GPU.** Modal/RunPod workers for render offload.
- [ ] **Desktop app.** Tauri/Electron wrapper bundling backend + ffmpeg.
- [ ] **CLI distribution.** PyPI package (`pip install clipit`), Homebrew, Scoop.
- [ ] **API product.** Public REST API with keys, rate limits, webhooks, SDKs (Python/JS).

### Phase 5 — Extensions & Ecosystem (6–12 months)
- [ ] **Plugin architecture.** Hook points for custom analyzers, renderers, uploaders.
- [ ] **Marketplace.** Share presets, BGM packs, font packs, templates.
- [ ] **Webhook/Zapier/Make integrations.**
- [ ] **MCP server.** Expose Clipit as tools for AI agents (generate clips from chat).
- [ ] **Batch API & webhooks for enterprise.**
- [ ] **White-label.** Rebrandable studio for agencies.

### Phase 6 — Research & Advanced (12+ months)
- [ ] **On-device models.** Quantized Whisper/LLM for edge.
- [ ] **Multimodal analysis.** Use vision models to score frames for thumbnails/hooks.
- [ ] **Speaker-aware editing.** Auto-switch camera, name tags, lower-thirds.
- [ ] **Auto-chapters & summaries.** Generate chapters, descriptions, SEO.
- [ ] **Copyright safety.** Detect copyrighted audio/visual; suggest transformations.
- [ ] **Federated learning (opt-in).** Improve scoring models from anonymized feedback.

---

## 6. Backlog by Category

### Core Engine
- Retry transient download/transcription failures with backoff
- Parallel clip rendering (process pool)
- Memory-efficient long-video handling (chunked)
- Deterministic seeds for reproducible renders
- Dry-run mode (analysis only, no render)

### Studio / Rendering
- Custom LUT/color grading
- Animated lower-thirds & intro/outro
- Picture-in-picture reaction layout
- Green-screen/chroma key
- Stabilization pass
- Speed ramping / slow-mo highlights
- Auto-crop to 4:5/1:1 with safe zones
- Subtitle style presets (TikTok, Reels, Shorts)

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
- SDK + typed client
- OpenAPI spec published
- Webhook docs + signature verification
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
- [ ] **Transcript Semantic Emoji Engine:** Detect keywords in transcript (e.g. "money", "rocket", "shock", "warning") and auto-composite contextual animated emojis into the ASS subtitle stream.
- [ ] **Dynamic Sound Effects (SFX) Compositing:** Auto-layer whooshes, pops, risers, and impact sound effects on hook transitions and punchlines.
- [ ] **Auto-Highlight Keyword Coloring:** Multi-palette color highlights driven by LLM emphasis markers.

#### B. Smart Trimming & Retention Engineering (Wisecut & Opus Clip Benchmark)
- [ ] **Automated Silence & Dead-Air Removal (Jump-Cutter):** Pre-pass audio VAD / FFmpeg `silencedetect` to auto-splice pauses and filler words before LLM segmentation.
- [ ] **Scene-Cut Auto-Snapping:** Detect natural camera transitions (`select='gt(scene,0.4)'`) and snap clip boundaries to clean scene changes.

#### C. Interactive Web Studio Experience (Veed.io, Vizard AI & Opus Clip Benchmark)
- [ ] **Interactive Waveform Trimmer:** Browser-based visual waveform trimming (`wavesurfer.js`) in the React 19 dashboard for non-destructive pre-render adjustment.
- [ ] **Transcript Text-Based Video Editor:** Interactive text editor allowing users to click/delete words to slice corresponding video frames.
- [ ] **Side-by-Side Multi-Layout Previewer:** Real-time aspect ratio comparison (9:16 vs 1:1 vs 16:9).

#### D. Multi-Platform Publishing & Scheduling (Munch, Short.ai & SendShort Benchmark)
- [ ] **Native OAuth Multi-Platform Publishing:** Direct scheduled publishing to TikTok Content Posting API, YouTube Shorts API, and Instagram Reels Graph API.
- [ ] **Automated Social Copy Customization:** Platform-specific character count and hashtag limit enforcement per destination channel.

#### E. Distributed Infrastructure & Scaling (SupoClip & Enterprise Benchmark)
- [ ] **Decoupled Task Broker:** Transition in-process `ThreadPoolExecutor` to Redis-backed ARQ/Celery worker pool for horizontal scaling across multi-GPU nodes.
- [ ] **Serverless GPU Offload:** Optional runner backend targeting Modal / RunPod / Replicate for zero-local-hardware deployments.

#### F. Gaming & Streaming Highlights (Nexus Clips, Spikes Studio & CutLabs Benchmark)
- [ ] **Streamer & Esports Highlight Detector:** Twitch API / VOD markers integration to detect chat velocity spikes, audio volume peaks, and high-intensity gameplay moments.

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
- Rendering: `--font-style`, `--no-subs`, `--no-karaoke`, `--hook-duration`, `--no-hook`, `--hook-v2*`
- B-roll: `--no-broll`, `--hook-source`, `--hook-source-start`
- Audio: `--no-bgm`, `--bgm-mode`, `--no-subs`, `--edge-glow*`, `--original-volume`
- Podcast: `--split-screen`, `--dynamic-split`, `--split-*`, `--diarization-speakers`, `--camera-switch`, `--switch-*`
- Watermark: `--watermark`, `--image`, `--text`, `--position`, `--opacity`, `--padding`, `--watermark-*`
- Voice-over: `--voiceover*`
- Story mode: `--story-mode`, `--story-recipe`, `--sources-json`, `--story-output-dir`, `--skip-download`
- Video encoding: `--video-crf`, `--video-cq`, `--video-bitrate`, `--video-preset`, `--video-sharpen`, `--video-scale-algo`, `--render-height`, `--source-height`
- Misc: `--dev-mode*`, `--white-flash-duration`, `--silence-trim`, `--scene-cut-threshold`

---

*End of roadmap. Contributions welcome — see `wiki/14-Contributing.md`.*
