"""
web.api.store — SQLite-backed job store with WAL mode and JSON file compatibility.

Stores job state in an embedded SQLite database (outputs/jobs.sqlite3).
Supports automatic migration from legacy jobs.json and exports snapshot backups.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Optional

from .models import (
    ClipDetail,
    JobProgressEvent,
    JobStatus,
)

_lock = threading.Lock()

# Resolve absolute path to the project root (2 levels up from web/api)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PERSIST_PATH = os.path.join(PROJECT_ROOT, "outputs", "jobs.json")
DB_PATH = os.path.join(PROJECT_ROOT, "outputs", "jobs.sqlite3")


# ---------------------------------------------------------------------------
# Helpers & Database Initialization
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def _init_db() -> None:
    """Initialize database tables and migrate from legacy jobs.json if needed."""
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                url TEXT,
                upload_filename TEXT,
                source TEXT,
                config TEXT,
                progress TEXT,
                clips TEXT,
                error TEXT,
                log TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);")

        # Ensure 'tags' column exists for existing SQLite tables
        cols = [c[1] for c in conn.execute("PRAGMA table_info(jobs);").fetchall()]
        if "tags" not in cols:
            conn.execute("ALTER TABLE jobs ADD COLUMN tags TEXT;")

        # Presets table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS presets (
                name TEXT PRIMARY KEY,
                description TEXT,
                config TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )

        # Seed default built-in presets if empty
        cur_p = conn.execute("SELECT COUNT(*) FROM presets;")
        if cur_p.fetchone()[0] == 0:
            default_presets = [
                (
                    "tiktok_viral",
                    "Aggressive viral TikTok setup with Hormozi typography, auto BGM ducking, and 9:16 safe zones.",
                    json.dumps({
                        "pilihan_rasio": "9:16",
                        "platform": "tiktok",
                        "gaya_font_aktif": "HORMOZI",
                        "use_auto_bgm": True,
                        "bgm_mode": "ducking",
                        "use_hook_glitch": True,
                        "use_karaoke_effect": True,
                        "normalize_audio": True,
                        "target_lufs": -14.0,
                    }),
                    _now().isoformat(),
                    _now().isoformat(),
                ),
                (
                    "youtube_shorts_clean",
                    "Clean high-retention YouTube Shorts preset with Storyteller typography and EBU R128 audio.",
                    json.dumps({
                        "pilihan_rasio": "9:16",
                        "platform": "shorts",
                        "gaya_font_aktif": "STORYTELLER",
                        "use_auto_bgm": True,
                        "bgm_mode": "background",
                        "use_hook_glitch": False,
                        "use_karaoke_effect": True,
                        "normalize_audio": True,
                        "target_lufs": -14.0,
                    }),
                    _now().isoformat(),
                    _now().isoformat(),
                ),
                (
                    "reels_aesthetic",
                    "Aesthetic Instagram Reels style with Cinematic typography and smooth edge glow.",
                    json.dumps({
                        "pilihan_rasio": "9:16",
                        "platform": "reels",
                        "gaya_font_aktif": "CINEMATIC",
                        "use_auto_bgm": True,
                        "bgm_mode": "ducking",
                        "use_karaoke_effect": True,
                        "edge_glow": "smooth",
                        "normalize_audio": True,
                    }),
                    _now().isoformat(),
                    _now().isoformat(),
                ),
                (
                    "podcast_split",
                    "Two-speaker podcast mode with Pyannote diarization and dynamic split-screen layout.",
                    json.dumps({
                        "pilihan_rasio": "9:16",
                        "platform": "reels",
                        "use_split_screen": True,
                        "use_dynamic_split": True,
                        "split_auto_zoom": True,
                        "split_trigger": "diarization",
                        "diarization_speakers": 2,
                    }),
                    _now().isoformat(),
                    _now().isoformat(),
                ),
                (
                    "linkedin_square",
                    "1:1 Square professional video preset with clean subtitles for LinkedIn and X.",
                    json.dumps({
                        "pilihan_rasio": "1:1",
                        "platform": "linkedin",
                        "gaya_font_aktif": "DEFAULT",
                        "use_auto_bgm": False,
                        "use_hook_glitch": False,
                    }),
                    _now().isoformat(),
                    _now().isoformat(),
                ),
            ]
            conn.executemany(
                "INSERT INTO presets (name, description, config, created_at, updated_at) VALUES (?, ?, ?, ?, ?);",
                default_presets,
            )

        # Check if table is empty and legacy jobs.json exists
        cur = conn.execute("SELECT COUNT(*) FROM jobs;")
        count = cur.fetchone()[0]
        if count == 0 and os.path.exists(PERSIST_PATH):
            try:
                with open(PERSIST_PATH, "r", encoding="utf-8") as f:
                    legacy_data = json.load(f)
                for jid, entry in legacy_data.items():
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO jobs (
                            id, status, url, upload_filename, source,
                            config, progress, clips, error, log,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            jid,
                            entry.get("status", JobStatus.QUEUED.value),
                            entry.get("url"),
                            entry.get("upload_filename"),
                            entry.get("source", "youtube"),
                            json.dumps(entry.get("config") or {}, ensure_ascii=False),
                            json.dumps(entry.get("progress"), ensure_ascii=False) if entry.get("progress") else None,
                            json.dumps(entry.get("clips") or [], ensure_ascii=False),
                            entry.get("error"),
                            json.dumps(entry.get("log") or [], ensure_ascii=False),
                            str(entry.get("created_at") or _now().isoformat()),
                            str(entry.get("updated_at") or _now().isoformat()),
                        ),
                    )
            except Exception:
                pass


# Initialize database on module load
try:
    _init_db()
except Exception:
    pass


def _row_to_job_dict(row: sqlite3.Row) -> dict:
    """Convert a database row into the standard job dict expected by web.api."""
    created_at = row["created_at"]
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at)
        except Exception:
            created_at = _now()

    updated_at = row["updated_at"]
    if isinstance(updated_at, str):
        try:
            updated_at = datetime.fromisoformat(updated_at)
        except Exception:
            updated_at = _now()

    config = json.loads(row["config"]) if row["config"] else {}
    progress = json.loads(row["progress"]) if row["progress"] else None
    clips = json.loads(row["clips"]) if row["clips"] else []
    log = json.loads(row["log"]) if row["log"] else []
    tags = json.loads(row["tags"]) if ("tags" in row.keys() and row["tags"]) else []

    return {
        "id": row["id"],
        "status": row["status"],
        "created_at": created_at,
        "updated_at": updated_at,
        "url": row["url"],
        "upload_filename": row["upload_filename"],
        "source": row["source"],
        "config": config,
        "progress": progress,
        "clips": clips,
        "error": row["error"],
        "log": log,
        "tags": tags,
    }


def _persist() -> None:
    """Export SQLite snapshot to legacy jobs.json for backward compatibility."""
    try:
        jobs = list_jobs()
        serializable = {}
        for job in jobs:
            entry = dict(job)
            for key in ("created_at", "updated_at"):
                if isinstance(entry.get(key), datetime):
                    entry[key] = entry[key].isoformat()
            if entry.get("progress") and isinstance(entry["progress"], JobProgressEvent):
                entry["progress"] = entry["progress"].model_dump()
                if isinstance(entry["progress"].get("timestamp"), datetime):
                    entry["progress"]["timestamp"] = entry["progress"]["timestamp"].isoformat()
            if entry.get("clips"):
                entry["clips"] = [
                    c.model_dump() if isinstance(c, ClipDetail) else c
                    for c in entry["clips"]
                ]
            serializable[entry["id"]] = entry
        os.makedirs(os.path.dirname(PERSIST_PATH), exist_ok=True)
        with open(PERSIST_PATH, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2, default=str)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_job(
    url: Optional[str] = None,
    upload_filename: Optional[str] = None,
    source: str = "youtube",
    config: dict | None = None,
    job_id: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """Create a new job and return its ID."""
    job_id = job_id or uuid.uuid4().hex[:12]
    now_iso = _now().isoformat()
    config_json = json.dumps(config or {}, ensure_ascii=False)
    log_json = json.dumps([], ensure_ascii=False)
    clips_json = json.dumps([], ensure_ascii=False)
    tags_json = json.dumps(tags or [], ensure_ascii=False)

    with _lock:
        with _get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO jobs (
                    id, status, url, upload_filename, source,
                    config, progress, clips, error, log, tags,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, NULL, ?, ?, ?, ?);
                """,
                (
                    job_id,
                    JobStatus.QUEUED.value,
                    url,
                    upload_filename,
                    source,
                    config_json,
                    clips_json,
                    log_json,
                    tags_json,
                    now_iso,
                    now_iso,
                ),
            )
        _persist()
    return job_id


def get_job(job_id: str) -> Optional[dict]:
    """Return a job dict or None."""
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?;", (job_id,)).fetchone()
        if row is None:
            return None
        return _row_to_job_dict(row)


def list_jobs() -> list[dict]:
    """Return all jobs sorted by creation time (newest first)."""
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC;").fetchall()
        return [_row_to_job_dict(r) for r in rows]


def update_job(job_id: str, **kwargs) -> None:
    """Update arbitrary fields on a job."""
    with _lock:
        job = get_job(job_id)
        if job is None:
            return

        # Prepare updated values
        status = kwargs.get("status", job["status"])
        url = kwargs.get("url", job["url"])
        upload_filename = kwargs.get("upload_filename", job["upload_filename"])
        source = kwargs.get("source", job["source"])
        config = kwargs.get("config", job["config"])
        progress = kwargs.get("progress", job["progress"])
        clips = kwargs.get("clips", job["clips"])
        error = kwargs.get("error", job["error"])
        log = kwargs.get("log", job["log"])
        now_iso = _now().isoformat()

        # Serialize fields
        config_json = json.dumps(config, default=str, ensure_ascii=False) if config is not None else None
        
        if progress is not None:
            if hasattr(progress, "model_dump"):
                prog_dict = progress.model_dump()
            elif isinstance(progress, dict):
                prog_dict = progress
            else:
                prog_dict = str(progress)
            progress_json = json.dumps(prog_dict, default=str, ensure_ascii=False)
        else:
            progress_json = None

        if clips is not None:
            clips_list = [c.model_dump() if hasattr(c, "model_dump") else c for c in clips]
            clips_json = json.dumps(clips_list, default=str, ensure_ascii=False)
        else:
            clips_json = json.dumps([], ensure_ascii=False)

        log_json = json.dumps(log or [], default=str, ensure_ascii=False)

        with _get_conn() as conn:
            conn.execute(
                """
                UPDATE jobs SET
                    status = ?,
                    url = ?,
                    upload_filename = ?,
                    source = ?,
                    config = ?,
                    progress = ?,
                    clips = ?,
                    error = ?,
                    log = ?,
                    updated_at = ?
                WHERE id = ?;
                """,
                (
                    status,
                    url,
                    upload_filename,
                    source,
                    config_json,
                    progress_json,
                    clips_json,
                    error,
                    log_json,
                    now_iso,
                    job_id,
                ),
            )
        _persist()


def update_progress(
    job_id: str,
    step: str,
    step_number: int,
    total_steps: int,
    message: str,
    percent: float = 0.0,
) -> None:
    """Update progress on a running job."""
    event = JobProgressEvent(
        step=step,
        step_number=step_number,
        total_steps=total_steps,
        message=message,
        percent=percent,
    )
    job = get_job(job_id)
    if job is None:
        return

    log = job.get("log", [])
    log.append(f"[{step}] {message}")
    if len(log) > 500:
        log = log[-500:]

    update_job(job_id, progress=event, log=log)


def set_status(job_id: str, status: JobStatus) -> None:
    """Set job status."""
    update_job(job_id, status=status.value if hasattr(status, "value") else str(status))


def set_error(job_id: str, error: str) -> None:
    """Mark job as failed with an error message."""
    update_job(job_id, status=JobStatus.FAILED.value, error=error)


def set_clips(job_id: str, clips: list[ClipDetail]) -> None:
    """Store rendered clip details."""
    update_job(job_id, clips=clips, status=JobStatus.COMPLETED.value)


def delete_job(job_id: str) -> bool:
    """Delete a job. Returns True if found."""
    with _lock:
        with _get_conn() as conn:
            cur = conn.execute("DELETE FROM jobs WHERE id = ?;", (job_id,))
            found = cur.rowcount > 0
        if found:
            _persist()
        return found


def get_running_count() -> int:
    """Count jobs currently in processing states."""
    processing = (
        JobStatus.DOWNLOADING.value,
        JobStatus.TRANSCRIBING.value,
        JobStatus.ANALYZING.value,
        JobStatus.RENDERING.value,
    )
    with _get_conn() as conn:
        placeholders = ",".join("?" for _ in processing)
        cur = conn.execute(
            f"SELECT COUNT(*) FROM jobs WHERE status IN ({placeholders});",
            processing,
        )
        return cur.fetchone()[0]


def get_queued_count() -> int:
    """Count jobs waiting to start."""
    with _get_conn() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE status = ?;",
            (JobStatus.QUEUED.value,),
        )
        return cur.fetchone()[0]


def reconcile_orphan_jobs(error_message: str = "Interrupted by server restart") -> int:
    """
    Find jobs stuck in non-terminal states (queued, downloading, transcribing,
    analyzing, rendering) and mark them as failed.

    Returns the number of reconciled jobs.
    """
    non_terminal = (
        JobStatus.QUEUED.value,
        JobStatus.DOWNLOADING.value,
        JobStatus.TRANSCRIBING.value,
        JobStatus.ANALYZING.value,
        JobStatus.RENDERING.value,
    )
    now_iso = _now().isoformat()
    with _lock:
        with _get_conn() as conn:
            placeholders = ",".join("?" for _ in non_terminal)
            cur = conn.execute(
                f"""
                UPDATE jobs SET
                    status = ?,
                    error = ?,
                    updated_at = ?
                WHERE status IN ({placeholders});
                """,
                (JobStatus.FAILED.value, error_message, now_iso, *non_terminal),
            )
            count = cur.rowcount
        if count > 0:
            _persist()
        return count


# ---------------------------------------------------------------------------
# Advanced Job Search, Filters, Bulk Operations & Presets
# ---------------------------------------------------------------------------

def search_jobs(
    query: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """
    Search and filter jobs by status, search string, and tags with pagination.

    Returns:
        tuple of (list_of_job_dicts, total_matching_count)
    """
    with _get_conn() as conn:
        conditions = []
        params: list[object] = []

        if status:
            conditions.append("status = ?")
            params.append(status)

        if query:
            q_like = f"%{query}%"
            conditions.append("(url LIKE ? OR upload_filename LIKE ? OR error LIKE ? OR config LIKE ? OR id LIKE ?)")
            params.extend([q_like, q_like, q_like, q_like, q_like])

        if tag:
            t_like = f"%{tag}%"
            conditions.append("tags LIKE ?")
            params.append(t_like)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Total matching count
        count_cur = conn.execute(f"SELECT COUNT(*) FROM jobs {where_clause};", params)
        total = count_cur.fetchone()[0]

        # Paginated results
        query_sql = f"SELECT * FROM jobs {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?;"
        cur = conn.execute(query_sql, params + [limit, offset])
        jobs = [_row_to_job_dict(row) for row in cur.fetchall()]

        return jobs, total


def cancel_job(job_id: str) -> bool:
    """Mark a queued or running job as CANCELLED."""
    with _lock:
        with _get_conn() as conn:
            cur = conn.execute("SELECT status FROM jobs WHERE id = ?;", (job_id,))
            row = cur.fetchone()
            if not row:
                return False
            conn.execute(
                "UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?;",
                (JobStatus.CANCELLED.value, _now().isoformat(), job_id),
            )
        _persist()
    return True


def clone_job(job_id: str, config_overrides: Optional[dict] = None) -> Optional[str]:
    """Clone an existing job with optional config overrides and return new job_id."""
    existing = get_job(job_id)
    if not existing:
        return None

    cfg = dict(existing.get("config", {}))
    if config_overrides:
        cfg.update(config_overrides)

    return create_job(
        url=existing.get("url"),
        upload_filename=existing.get("upload_filename"),
        source=existing.get("source", "youtube"),
        config=cfg,
        tags=existing.get("tags", []),
    )


def update_job_tags(job_id: str, tags: list[str]) -> bool:
    """Update tags array for a job."""
    with _lock:
        with _get_conn() as conn:
            cur = conn.execute("SELECT id FROM jobs WHERE id = ?;", (job_id,))
            if not cur.fetchone():
                return False
            conn.execute(
                "UPDATE jobs SET tags = ?, updated_at = ? WHERE id = ?;",
                (json.dumps(tags, ensure_ascii=False), _now().isoformat(), job_id),
            )
        _persist()
    return True


def bulk_delete_jobs(job_ids: list[str]) -> int:
    """Delete multiple jobs in a single transaction."""
    if not job_ids:
        return 0
    with _lock:
        with _get_conn() as conn:
            placeholders = ",".join("?" for _ in job_ids)
            cur = conn.execute(f"DELETE FROM jobs WHERE id IN ({placeholders});", job_ids)
            deleted = cur.rowcount
        _persist()
    return deleted


def bulk_cancel_jobs(job_ids: list[str]) -> int:
    """Cancel multiple jobs in a single transaction."""
    if not job_ids:
        return 0
    with _lock:
        with _get_conn() as conn:
            placeholders = ",".join("?" for _ in job_ids)
            cur = conn.execute(
                f"UPDATE jobs SET status = ?, updated_at = ? WHERE id IN ({placeholders}) AND status NOT IN (?, ?);",
                [JobStatus.CANCELLED.value, _now().isoformat()] + job_ids + [JobStatus.COMPLETED.value, JobStatus.FAILED.value],
            )
            cancelled = cur.rowcount
        _persist()
    return cancelled


# ---------------------------------------------------------------------------
# Presets CRUD
# ---------------------------------------------------------------------------

def save_preset(name: str, config: dict, description: str = "") -> dict:
    """Save or update a named preset profile."""
    now_iso = _now().isoformat()
    with _lock:
        with _get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO presets (name, description, config, created_at, updated_at)
                VALUES (?, ?, ?, COALESCE((SELECT created_at FROM presets WHERE name = ?), ?), ?);
                """,
                (name, description, json.dumps(config, ensure_ascii=False), name, now_iso, now_iso),
            )
    return {"name": name, "description": description, "config": config, "updated_at": now_iso}


def get_preset(name: str) -> Optional[dict]:
    """Retrieve a preset by name."""
    with _get_conn() as conn:
        cur = conn.execute("SELECT * FROM presets WHERE name = ?;", (name,))
        row = cur.fetchone()
        if not row:
            return None
        return {
            "name": row["name"],
            "description": row["description"] or "",
            "config": json.loads(row["config"]) if row["config"] else {},
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }


def list_presets() -> list[dict]:
    """List all available presets."""
    with _get_conn() as conn:
        cur = conn.execute("SELECT * FROM presets ORDER BY name ASC;")
        return [
            {
                "name": row["name"],
                "description": row["description"] or "",
                "config": json.loads(row["config"]) if row["config"] else {},
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in cur.fetchall()
        ]


def delete_preset(name: str) -> bool:
    """Delete a preset by name."""
    with _lock:
        with _get_conn() as conn:
            cur = conn.execute("DELETE FROM presets WHERE name = ?;", (name,))
            return cur.rowcount > 0
