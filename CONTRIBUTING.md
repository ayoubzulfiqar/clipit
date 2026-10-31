# Contributing to Clipit

First off, thank you for considering contributing to **Clipit**! It is people like you who make Clipit such a powerful, self-hostable, unmetered AI video clipping engine for creators, developers, and researchers worldwide.

Following these guidelines helps maintain project quality, speeds up review cycles, and ensures a smooth collaboration experience for everyone.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Features](#suggesting-features)
   - [Code Contributions](#code-contributions)
   - [Documentation Improvements](#documentation-improvements)
3. [Development Environment Setup](#development-environment-setup)
   - [Prerequisites](#prerequisites)
   - [Local Backend Setup](#local-backend-setup)
   - [Local Web Studio Frontend Setup](#local-web-studio-frontend-setup)
4. [Codebase Architecture](#codebase-architecture)
5. [Git & Commit Conventions](#git--commit-conventions)
6. [Testing & Verification](#testing--verification)
7. [Coding Standards](#coding-standards)
8. [Pull Request Workflow](#pull-request-workflow)
9. [License Note](#license-note)

---

## Code of Conduct

This project and everyone participating in it is governed by the [Clipit Code of Conduct](file:///home/sensei/Projects/backend/clipit/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@clipit.dev](mailto:conduct@clipit.dev).

---

## How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:
- Search existing [GitHub Issues](https://github.com/ayoubzulfiqar/clipit/issues) to verify the bug has not already been reported.
- Ensure your FFmpeg and GPU drivers are up to date.

When opening a bug report, use our [Bug Report Template](file:///home/sensei/Projects/backend/clipit/.github/ISSUE_TEMPLATE/bug_report.yml) and include:
- A clear, descriptive title.
- Exact steps to reproduce the issue.
- Operating system, Python version, and FFmpeg version (`ffmpeg -version`).
- Full console output or stack trace (redacting any private API keys or secrets).
- Expected behavior vs. actual behavior.

### Suggesting Features

We welcome ideas for new features, subtitle styles, AI providers, and workflow integrations! Please submit feature proposals using our [Feature Request Template](file:///home/sensei/Projects/backend/clipit/.github/ISSUE_TEMPLATE/feature_request.yml). Explain:
- The core problem or workflow friction you are addressing.
- Your proposed solution or user experience.
- Any alternative approaches or competitor benchmarks considered.

### Code Contributions

Whether fixing a bug, adding an audio filter, or improving frontend responsiveness:
1. Check existing issues or open a proposal issue first for substantial architectural changes.
2. Fork the repository and create your feature branch from `main`.
3. Keep changes scoped, well-tested, and accompanied by unit tests.

### Documentation Improvements

Documentation is just as valuable as code:
- Correct typos, clarify explanations, or add step-by-step guides.
- Contribute localized README translations.
- Add real-world pipeline workflow examples to `Usage.md`.

---

## Development Environment Setup

### Prerequisites

- **Python**: 3.10, 3.11, 3.12, or 3.13.
- **FFmpeg**: Version 5.0 or later with `libass` support (required for subtitle burning).
- **Node.js**: Version 20+ or 22+ (for building the Web Studio React dashboard).
- **Git**: For version control.
- *(Optional)* **NVIDIA GPU + CUDA 11.8+ / 12+**: For hardware-accelerated NVENC video encoding and local Whisper / Pyannote inference. (CPU mode is fully supported as fallback).

### Local Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayoubzulfiqar/clipit.git
   cd clipit
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -e ".[all]"
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.sample .env
   # Edit .env and supply your GOOGLE_API_KEY (or Groq, OpenRouter, NVIDIA NIM keys)
   ```

5. **Verify installation:**
   ```bash
   python3 main.py --help
   ```

### Local Web Studio Frontend Setup

The Web Studio is a single-page application built with React 19, Vite, and Tailwind CSS.

1. **Navigate to the dashboard directory:**
   ```bash
   cd web/dashboard
   npm install
   ```

2. **Start the frontend development server:**
   ```bash
   npm run dev
   ```

3. **Start the backend API server in a separate terminal:**
   ```bash
   uvicorn web.api.app:app --host 127.0.0.1 --port 8000 --reload
   ```

Open `http://localhost:5173` in your browser.

---

## Codebase Architecture

```
clipit/
├── clipping/                  # Core video processing & intelligence engine
│   ├── config.py              # Configuration parsing & validation
│   ├── runner.py              # Main 7-step pipeline orchestrator
│   ├── engine.py              # Whisper transcription & Gemini AI prompt router
│   ├── studio/                # FFmpeg synthesis, ASS kinetic subtitles & SFX
│   │   ├── subtitles.py       # Libass karaoke & word-level subtitle renderer
│   │   ├── sfx.py             # Native audio whoosh/pop/impact synthesizer
│   │   ├── presets.py         # 9:16 portrait, 1:1 square, and 16:9 layouts
│   │   └── reframing.py       # Face tracking & dynamic split-screen math
│   ├── scene_detect.py        # Natural camera scene-cut boundary auto-snapping
│   ├── emoji_engine.py        # Semantic transcript emoji & keyword coloring
│   ├── ctr_optimizer.py       # Title clickability scorer & thumbnail generator
│   ├── persona.py             # Demographic & niche audience targeting presets
│   ├── stream_highlight.py    # Audio RMS surge & gaming hype detector
│   ├── vision_scoring.py      # Multimodal frame sharpness & thumbnail ranking
│   ├── chapters.py            # YouTube chapters & markdown show notes
│   ├── copyright.py           # Content ID risk analysis & originality transforms
│   ├── marketplace.py         # Portable .clipit-pack bundle exporter & importer
│   ├── plugins.py             # Priority lifecycle hook registry
│   ├── mcp_server.py          # AI agent stdio JSON-RPC MCP server
│   └── webhook.py             # HMAC-SHA256 webhook event dispatcher
├── web/
│   ├── api/                   # FastAPI backend server
│   │   ├── app.py             # FastAPI entrypoint & middleware
│   │   ├── store.py           # SQLite job persistence & orphan recovery
│   │   ├── queue.py           # Local bounded threadpool & Redis broker
│   │   ├── worker.py          # Pipeline worker execution & progress emitter
│   │   └── routes/            # jobs, batch, presets, settings, files, system
│   └── dashboard/             # React 19 + Vite + Tailwind CSS GUI
├── desktop/                   # Desktop launcher & lifecycle orchestrator
├── sdk/python/                # Typed Python client SDK (ClipitClient)
└── tests/                     # Unit & integration test suite (165+ tests)
```

---

## Git & Commit Conventions

Clipit adheres to [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(<scope>): <short imperative description>
```

### Common Types:
- `feat`: A new feature or capability.
- `fix`: A bug fix.
- `docs`: Documentation updates or additions.
- `test`: Adding or updating test cases.
- `refactor`: Code reorganization with no functional change.
- `perf`: Performance or memory optimization.
- `chore`: Maintenance, dependencies, or tooling updates.
- `ci`: CI/CD workflows and automation scripts.

### Commit Guidelines:
- Write in the imperative mood ("add feature", not "added feature").
- Keep commits atomic and focused. Do not combine unrelated refactors into a feature commit.

---

## Testing & Verification

Every pull request must pass all automated tests before merging.

### Run Python Test Suite:
```bash
python3 -m unittest discover -s tests
```
or with `pytest`:
```bash
pytest tests/ -v
```

### Run Frontend Build Verification:
```bash
npm run build --prefix web/dashboard
```

When creating new features, always include corresponding unit tests under `tests/test_<feature>.py`.

---

## Coding Standards

- **Python Style**: Adhere to PEP 8. Format with `black` (line length 100) and lint with `ruff`.
- **Type Annotations**: Use Python 3.10+ modern union types (`int | None`, `list[str]`) and type hints across public functions.
- **Error Handling**: Gracefully catch and log external subprocess errors (FFmpeg, network timeouts) without crashing the server or parent pipeline.
- **Security**: Never commit secrets, API keys, or credentials. Always sanitize file paths to prevent directory traversal / Zip Slip vulnerabilities.

---

## Pull Request Workflow

1. Push your branch to your GitHub fork:
   ```bash
   git push origin feat/my-awesome-feature
   ```
2. Open a Pull Request against the `main` branch of `ayoubzulfiqar/clipit`.
3. Complete the [Pull Request Template](file:///home/sensei/Projects/backend/clipit/.github/pull_request_template.md).
4. Automated GitHub Actions CI will verify test suite execution across Python 3.10, 3.11, 3.12, and 3.13, and build the frontend SPA.
5. Address any reviewer feedback promptly.

---

## License Note

By contributing to Clipit, you agree that your contributions will be licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0-or-later)**.
