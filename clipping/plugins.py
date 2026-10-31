"""
clipping.plugins — Plugin Architecture & Lifecycle Hook Manager

Provides an extensible hook system allowing developers and enterprise integrators
to hook into pipeline lifecycle events (e.g. video download, transcription,
clip scoring, rendering, publication).
"""

from __future__ import annotations

import functools
import importlib.util
import logging
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("clipit.plugins")

# Standard Pipeline Event Names
HOOK_DOWNLOAD_COMPLETE = "on_download_complete"
HOOK_TRANSCRIBE_COMPLETE = "on_transcribe_complete"
HOOK_CLIPS_SCORED = "on_clips_scored"
HOOK_RENDER_START = "on_render_start"
HOOK_RENDER_COMPLETE = "on_render_complete"
HOOK_JOB_FAILED = "on_job_failed"

VALID_HOOKS = {
    HOOK_DOWNLOAD_COMPLETE,
    HOOK_TRANSCRIBE_COMPLETE,
    HOOK_CLIPS_SCORED,
    HOOK_RENDER_START,
    HOOK_RENDER_COMPLETE,
    HOOK_JOB_FAILED,
}

# In-memory registry: event -> list of (priority, handler)
_HOOK_REGISTRY: Dict[str, List[Tuple[int, Callable[[Dict[str, Any]], Any]]]] = {}


def register_hook(event: str, handler: Callable[[Dict[str, Any]], Any], priority: int = 10) -> None:
    """
    Register a callable handler for a lifecycle event.
    Handlers with lower priority numbers run earlier (e.g. 0 before 10).
    """
    if event not in _HOOK_REGISTRY:
        _HOOK_REGISTRY[event] = []
    _HOOK_REGISTRY[event].append((priority, handler))
    _HOOK_REGISTRY[event].sort(key=lambda item: item[0])


def unregister_hook(event: str, handler: Callable[[Dict[str, Any]], Any]) -> bool:
    """Remove a previously registered handler."""
    if event not in _HOOK_REGISTRY:
        return False
    orig_len = len(_HOOK_REGISTRY[event])
    _HOOK_REGISTRY[event] = [item for item in _HOOK_REGISTRY[event] if item[1] != handler]
    return len(_HOOK_REGISTRY[event]) < orig_len


def clear_hooks(event: Optional[str] = None) -> None:
    """Clear registered hooks. If event is specified, clear only for that event."""
    if event:
        _HOOK_REGISTRY.pop(event, None)
    else:
        _HOOK_REGISTRY.clear()


def hook(event: str, priority: int = 10):
    """Decorator to register a function as a plugin hook."""
    def decorator(fn: Callable[[Dict[str, Any]], Any]):
        register_hook(event, fn, priority=priority)
        return fn
    return decorator


def trigger_hook(event: str, payload: Dict[str, Any], fail_fast: bool = False) -> Dict[str, Any]:
    """
    Trigger all registered hooks for an event in order of priority.
    Returns the potentially modified payload dictionary.
    """
    handlers = _HOOK_REGISTRY.get(event, [])
    for priority, handler in handlers:
        try:
            res = handler(payload)
            if isinstance(res, dict):
                payload.update(res)
        except Exception as e:
            logger.warning(f"Plugin handler {getattr(handler, '__name__', str(handler))} failed on '{event}': {e}")
            if fail_fast:
                raise
    return payload


def discover_plugins(plugin_dir: Optional[str] = None) -> int:
    """
    Scan a directory for Python plugin scripts and import them to register hooks.
    Returns count of loaded plugin files.
    """
    target_dir = plugin_dir or os.getenv("CLIPIT_PLUGIN_DIR", "plugins")
    if not os.path.isdir(target_dir):
        return 0

    loaded = 0
    for fname in sorted(os.listdir(target_dir)):
        if fname.endswith(".py") and not fname.startswith("__"):
            fpath = os.path.join(target_dir, fname)
            mod_name = f"clipit_plugin_{os.path.splitext(fname)[0]}"
            try:
                spec = importlib.util.spec_from_file_location(mod_name, fpath)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = mod
                    spec.loader.exec_module(mod)
                    loaded += 1
            except Exception as e:
                logger.error(f"Failed to load plugin from {fpath}: {e}")
    return loaded
