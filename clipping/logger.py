"""
clipping.logger — Structured, leveled logging for Clipit.

Supports:
- Console-friendly human formatting with level colors/emojis.
- JSON-formatted structured logging for production/cloud log aggregators (CLIPIT_LOG_FORMAT=json).
- Contextual correlation via `job_id` contextvars.
"""

from __future__ import annotations

import contextvars
import json
import logging
import os
import sys
import time
from typing import Any, Dict, Optional

# Context variable for correlating logs to specific job IDs
current_job_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "current_job_id", default=None
)


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        job_id = getattr(record, "job_id", None) or current_job_id.get()
        if job_id:
            log_obj["job_id"] = job_id

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


class StandardFormatter(logging.Formatter):
    """Clean human-readable console formatter."""

    LEVEL_PREFIXES = {
        logging.DEBUG: "🔍 [DEBUG]",
        logging.INFO: "ℹ️ [INFO]",
        logging.WARNING: "⚠️ [WARN]",
        logging.ERROR: "❌ [ERROR]",
        logging.CRITICAL: "🚨 [CRIT]",
    }

    def format(self, record: logging.LogRecord) -> str:
        prefix = self.LEVEL_PREFIXES.get(record.levelno, f"[{record.levelname}]")
        job_id = getattr(record, "job_id", None) or current_job_id.get()
        job_str = f" [{job_id}]" if job_id else ""
        msg = record.getMessage()
        return f"{prefix}{job_str} {msg}"


def get_logger(name: str = "clipit") -> logging.Logger:
    """
    Get or configure a leveled logger for the given module name.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    log_level_str = os.environ.get("CLIPIT_LOG_LEVEL", os.environ.get("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    format_style = os.environ.get("CLIPIT_LOG_FORMAT", "text").lower()
    if format_style == "json":
        handler.setFormatter(JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ"))
    else:
        handler.setFormatter(StandardFormatter())

    logger.addHandler(handler)
    logger.propagate = False
    return logger
