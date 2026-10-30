# Architectural Remediation & Technical Debt Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate architectural technical debt, fix package import collision in `clipping/studio`, unify project versioning, harden file serving against path traversal, replace in-memory job state with thread-safe SQLite persistence, introduce typed configuration modeling, and establish an automated test suite.

**Architecture:** Refactor `clipping/studio` from an `importlib` script shim into a standard Python package with an `__init__.py` facade; introduce a typed `ClipitConfig` class preserving backwards compatibility; harden `web/api/routes/files.py` using canonical path validation; upgrade `web/api/store.py` to SQLite with WAL mode; unify versioning across CLI, backend, and package manifests; and build a comprehensive `unittest` test suite covering config, metadata, security, and storage.

**Tech Stack:** Python 3.10+, FastAPI, SQLite (WAL mode), Pydantic v2 / Dataclasses, Standard Library `unittest`.

**Spec:** Architectural Review & Technical Debt Assessment from preceding analysis.

## Global Constraints
- Do not break backward compatibility of CLI (`main.py`) or API endpoints (`web/api`).
- Retain all existing public function signatures and configuration attributes (`getattr(cfg, ...)` must continue to work).
- Maintain documentation integrity and preserve all existing comments and docstrings.
- Python 3.10+ compatibility across all modifications.

## Review Focus
- Path traversal attack vectors in `/api/outputs/{job_id}/{filename}` attempting directory escape.
- Concurrent reads and writes in `web/api/store.py` under parallel job submission.
- Preserving `SimpleNamespace`-like duck typing on `ClipitConfig` for downstream callers.
- Regression in `clipping/studio` imports when called from outside package boundaries.
- Graceful migration of pre-existing `outputs/jobs.json` to SQLite.

---

### Task 1: Package Modernization & Import Resolution (`clipping/studio`)

**Files:**
- Create: `clipping/studio/__init__.py`
- Modify: `clipping/studio/core.py`
- Modify: `clipping/studio/render_hybrid.py`
- Modify: `clipping/studio/render_split_screen.py`
- Modify: `clipping/studio/render_camera_switch.py`
- Modify: `clipping/studio/subtitles.py`
- Modify: `clipping/studio/face_detection.py`
- Delete: `clipping/studio.py`
- Test: `tests/test_studio_imports.py`

**Interfaces:**
- Produces: Standard package `clipping.studio` re-exporting `proses_klip`, `detect_video_encoder`, `buat_video_hybrid`, `buat_video_split_screen`, `buat_video_camera_switch`, `buat_thumbnail`, `buat_file_ass`, `siapkan_glitch_video`, etc.

- [ ] **Step 1: Write the failing test for standard studio package imports**
- [ ] **Step 2: Run test to verify it fails (or relies on importlib shim)**
- [ ] **Step 3: Move `clipping/studio.py` logic to `clipping/studio/__init__.py` using standard relative imports, delete `clipping/studio.py`**
- [ ] **Step 4: Refactor internal `_load_studio_internal_module` in `core.py`, `render_hybrid.py`, `render_split_screen.py`, `render_camera_switch.py`, `subtitles.py`, and `face_detection.py` to relative imports**
- [ ] **Step 5: Run tests to verify all studio imports succeed natively**

---

### Task 2: Single Source of Truth for Versioning

**Files:**
- Modify: `clipping/__init__.py`
- Modify: `pyproject.toml`
- Modify: `main.py`
- Modify: `web/api/app.py`
- Modify: `web/dashboard/package.json`
- Test: `tests/test_version.py`

**Interfaces:**
- Produces: `clipping.__version__ == "1.15.0"` accessible across all services.

- [ ] **Step 1: Write test asserting unified versioning across all modules**
- [ ] **Step 2: Run test to verify current version mismatch**
- [ ] **Step 3: Define `__version__ = "1.15.0"` in `clipping/__init__.py`, update `pyproject.toml`, `main.py`, `web/api/app.py`, and `package.json`**
- [ ] **Step 4: Run test to verify version alignment passes**

---

### Task 3: Security & Path Traversal Hardening (`web/api/routes/files.py`)

**Files:**
- Modify: `web/api/routes/files.py`
- Test: `tests/test_security_files.py`

**Interfaces:**
- Consumes: `OUTPUTS_DIR`, `UPLOAD_DIR`
- Produces: Hardened `serve_output(job_id, filename)` raising 403 on traversal; sanitized `upload_video` rejecting unsafe filenames.

- [ ] **Step 1: Write failing security tests for path traversal attacks (`../`, `%2e%2e/`, absolute paths)**
- [ ] **Step 2: Run test to verify vulnerabilities**
- [ ] **Step 3: Implement canonical path resolution with `os.path.realpath` and `os.path.commonpath` checks**
- [ ] **Step 4: Run security tests to verify traversal attempts are rejected with 403/400**

---

### Task 4: Robust SQLite-Backed Job Store (`web/api/store.py`)

**Files:**
- Modify: `web/api/store.py`
- Test: `tests/test_job_store.py`

**Interfaces:**
- Produces: Thread-safe, persistent SQLite-backed job store implementing `create_job`, `get_job`, `list_jobs`, `update_job`, `delete_job`, `set_status`, `update_progress`, `set_error`, `add_clip`, `add_log`.

- [ ] **Step 1: Write failing unit tests for job store CRUD, progress tracking, and legacy JSON migration**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement SQLite database layer with WAL mode and automatic legacy `jobs.json` import**
- [ ] **Step 4: Run test to verify all job store operations pass**

---

### Task 5: Strict Configuration Modeling & Typing (`clipping/config.py`, `web/api/config_adapter.py`)

**Files:**
- Modify: `clipping/config.py`
- Modify: `web/api/config_adapter.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Produces: `ClipitConfig` class providing typed fields, validation, dict conversion, and `SimpleNamespace`-compatible attribute access.

- [ ] **Step 1: Write failing unit tests for `ClipitConfig` instantiation, default preservation, validation, and dict conversion**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `ClipitConfig` in `clipping/config.py` and update `build_config` and `config_adapter.py`**
- [ ] **Step 4: Run test to verify all configuration tests pass**

---

### Task 6: Metadata & Subtitle Quality Verification Tests

**Files:**
- Create: `tests/test_metadata.py`
- Create: `tests/test_subtitles.py`
- Modify: `clipping/metadata.py` (if edge cases detected)

**Interfaces:**
- Consumes: `clipping.metadata`, `clipping.studio.subtitles`
- Produces: Test coverage for metadata normalization, hashtag cleanup, description generation, and ASS file synthesis.

- [ ] **Step 1: Write tests for `_trim_title`, `_normalize_hashtags`, `_normalize_keyword_tags`, and Indonesian language heuristics**
- [ ] **Step 2: Write tests for `buat_file_ass` subtitle structure and timestamp math**
- [ ] **Step 3: Run all test suites together (`python3 -m unittest discover -s tests`) to confirm 100% pass rate**
