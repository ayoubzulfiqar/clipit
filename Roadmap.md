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

- **Version:** 1.15.0 (CLI) / 1.12.0 (web package)
- **License:** MIT
- **Author:** Ayoub Zulfiqar
- **Repo:** https://github.com/ayoubzulfiqar/clipit

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  CLI (main.py)  ──►  clipping/ (core pipeline)              │
│  Web (React)    ──►  web/api (FastAPI)  ──►  clipping/      │
└─────────────────────────────────────────────────────────────┘
        │
        ├── clipping/engine.py          download + transcribe + Gemini analysis
        ├── clipping/runner.py          orchestration (single + batch)
        ├── clipping/story_runner.py    multi-source story clip mode
        ├── clipping/studio/            rendering primitives (core, effects,
        │                               subtitles, transitions, bgm, watermark,
        │                               face detection, typography, thumbnail)
        ├── clipping/config.py          CLI args + config builder
        ├── clipping/metadata.py        title/description/tags per platform
        ├── clipping/voiceover.py       TTS commentary pipeline
        ├── clipping/diarization.py     speaker diarization (Pyannote)
        ├── clipping/hook_manager.py    hook V2 management
        └── clipping/studio.py          facade / re-exports
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

1. **No automated tests.** Only `youtube_uploader/test_youtube_refresh.py` (manual, needs OAuth). No unit/integration coverage for pipeline, config, or API.
2. **Version drift.** CLI reports 1.15.0, web package 1.12.0, root() 1.13.0, health 1.12.0. Needs single source of truth.
3. **No CI/CD.** No GitHub Actions for lint/test/build.
4. **Heavy dependencies.** Whisper/MediaPipe/OpenCV/Pyannote install is fragile; no lock file or extras groups.
5. **No auth on web API.** Studio backend is open; CORS only. No user accounts, roles, or API keys.
6. **Job store is in-memory/file-based.** `web/api/store.py` not horizontally scalable; no Redis/DB.
7. **Worker is single-process.** No distributed queue; concurrency via env var only.
8. **No observability.** No metrics, structured tracing, or error reporting (Sentry).
9. **Frontend has no tests.** React dashboard untested; no E2E.
10. **i18n expanded.** README now available in English, Arabic, Russian, Chinese, Korean. UI/CLI localization still pending.
11. **No plugin system.** Extensions require core edits.
12. **Notebooks drift.** Colab/Kaggle notebooks may be out of sync with CLI.
13. **No model caching strategy.** Whisper/Gemini models re-downloaded per environment.
14. **Security.** Uploaded files, path traversal risks in `files.py` need audit. Secrets in `.env` only; no secret manager.
15. **Accessibility.** Static docs/dashboard not WCAG-audited.
16. **No telemetry/opt-in analytics.** Hard to understand usage.

---

## 5. Roadmap

### Phase 0 — Stabilization (0–4 weeks)
- [ ] Single source of truth for version (read from `pyproject.toml`).
- [ ] Add `pyproject` optional dependency groups (`[gpu]`, `[podcast]`, `[dev]`).
- [ ] Generate `requirements-lock.txt` / use `uv` or `poetry`.
- [ ] Add pre-commit hooks (ruff, black, mypy, pytest).
- [ ] Add GitHub Actions: lint + typecheck + unit tests on PR.
- [ ] Add basic unit tests for `config.build_config`, `_make_url_slug`, metadata generators.
- [ ] Fix path-safety in `files.py` (sanitize, allow-list).
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
- [ ] **Persistent job store.** Postgres/SQLite with migrations (Alembic); Redis queue (RQ/Celery/ARQ).
- [ ] **Real-time progress.** WebSocket/SSE for job stages instead of polling.
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
- Unit/integration/E2E test suites
- Load testing for worker queue
- Backup/restore for job store
- Rate limiting & abuse protection
- Audit log
- Health/readiness probes for k8s
- Graceful shutdown (already partial)

---

## 7. Non-Functional Requirements

- **Performance:** 10-min video → 5 clips in < 15 min on mid-tier GPU.
- **Reliability:** 99% job success rate; automatic retry of transient failures.
- **Scalability:** Horizontal worker scaling; stateless API.
- **Security:** Auth, secret management, input validation, sandboxed ffmpeg.
- **Privacy:** No PII in logs; opt-in telemetry; data deletion endpoint.
- **Compatibility:** Python 3.10+, FFmpeg 5+, CUDA 11.8+/CPU fallback.
- **Observability:** Structured logs, metrics (Prometheus), traces (OpenTelemetry).

---

## 8. Success Metrics

- Clip render success rate ≥ 99%
- Median processing time per minute of source ≤ 90s (GPU)
- User-reported "viral hit" rate tracking
- Dashboard Lighthouse score ≥ 90
- Test coverage ≥ 70% on core modules
- Time-to-first-clip for new user ≤ 10 min

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| API key cost/quota (Gemini) | Multi-provider fallback, caching, local LLM option |
| Heavy dependency install failures | Optional groups, lock files, Docker image |
| YouTube/TikTok anti-bot changes | yt-dlp auto-upgrade, cookie support, proxy config |
| Copyright strikes | Voice-over commentary mode, originality transforms |
| GPU availability | CPU fallback, serverless GPU offload |
| Scope creep | Phased roadmap, milestone gating |

---

## 10. Contribution & Release Process

- Branch from `main`; conventional commits.
- PR requires: lint + typecheck + tests green.
- Version bump via `pyproject.toml` (single source of truth).
- Changelog updated per release (keep `CHANGELOG.md`).
- Tag release `vX.Y.Z`; GitHub Actions builds & publishes Docker image + PyPI.

---

## 11. Appendix — CLI Flag Groups

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
