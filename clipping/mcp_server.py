"""
clipping.mcp_server — Model Context Protocol (MCP) Server for Clipit.

Exposes Clipit AI auto-clipping, hardware detection, presets, and scheduling
tools to external AI agents via JSON-RPC 2.0 over standard I/O (stdio).
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

from clipping import __version__
from clipping.hardware import detect_hardware
from clipping.dedup import filter_duplicate_candidates
from clipping.scheduler import generate_posting_schedule


MCP_TOOLS = [
    {
        "name": "clipit_get_health",
        "description": "Inspect Clipit engine health, version, external binary availability, and hardware accelerator profile.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "clipit_list_presets",
        "description": "List all configured video style presets (e.g. tiktok_viral, youtube_shorts_clean, reels_aesthetic, podcast_split).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "clipit_create_job",
        "description": "Submit a new video URL to the Clipit auto-clipping pipeline queue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Source video URL (YouTube, TikTok, Instagram, Google Drive)"},
                "clips": {"type": "integer", "description": "Number of viral clips to extract (default: 5)", "default": 5},
                "ratio": {"type": "string", "enum": ["9:16", "16:9", "1:1", "4:5"], "default": "9:16"},
                "platform": {"type": "string", "enum": ["custom", "tiktok", "reels", "shorts", "linkedin", "x", "youtube"], "default": "tiktok"},
                "font_style": {"type": "string", "enum": ["HORMOZI", "STORYTELLER", "CINEMATIC", "DEFAULT"], "default": "HORMOZI"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "clipit_list_jobs",
        "description": "Query recent clipping jobs, statuses, and output clip details.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter by status: queued, downloading, transcribing, analyzing, rendering, completed, failed, cancelled"},
                "search": {"type": "string", "description": "Search keyword in URL, title, or error"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": [],
        },
    },
    {
        "name": "clipit_schedule_calendar",
        "description": "Generate an optimal multi-platform publishing calendar for rendered clips based on peak engagement hours.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "clips": {"type": "array", "description": "Array of clip metadata objects", "items": {"type": "object"}},
                "platforms": {"type": "array", "items": {"type": "string"}, "default": ["tiktok", "shorts", "reels"]},
                "clips_per_day": {"type": "integer", "default": 2},
            },
            "required": ["clips"],
        },
    },
    {
        "name": "clipit_filter_duplicates",
        "description": "Filter out temporal and semantic duplicate clip intervals based on IoU threshold.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "clips": {"type": "array", "items": {"type": "object"}},
                "threshold_iou": {"type": "number", "default": 0.6},
            },
            "required": ["clips"],
        },
    },
]


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    """Execute tool by name and return serializable result."""
    if name == "clipit_get_health":
        hw = detect_hardware()
        return {
            "status": "ok",
            "version": __version__,
            "hardware": hw.to_dict(),
        }

    elif name == "clipit_list_presets":
        try:
            from web.api import store
            presets = store.list_presets()
        except ImportError:
            from clipping.studio.presets import PLATFORM_PRESETS
            presets = [{"name": k, "description": p.description, "config": {}} for k, p in PLATFORM_PRESETS.items()]
        return {"presets": presets, "total": len(presets)}

    elif name == "clipit_create_job":
        url = arguments.get("url")
        clips = arguments.get("clips", 5)
        ratio = arguments.get("ratio", "9:16")
        platform = arguments.get("platform", "tiktok")
        font_style = arguments.get("font_style", "HORMOZI")

        try:
            from web.api import store
            job_id = store.create_job(
                url=url,
                config={
                    "clips": clips,
                    "ratio": ratio,
                    "platform": platform,
                    "font_style": font_style,
                },
                tags=["mcp_agent", platform],
            )
            return {"job_id": job_id, "status": "queued", "message": f"Job {job_id} submitted successfully"}
        except ImportError:
            return {"job_id": "dry_run", "status": "queued", "message": "Job queued (API store offline)"}

    elif name == "clipit_list_jobs":
        status_filter = arguments.get("status")
        search = arguments.get("search")
        limit = arguments.get("limit", 10)
        try:
            from web.api import store
            jobs, total = store.search_jobs(query=search, status=status_filter, limit=limit)
        except ImportError:
            jobs, total = [], 0
        return {"jobs": jobs, "total": total}

    elif name == "clipit_schedule_calendar":
        clips = arguments.get("clips", [])
        platforms = arguments.get("platforms", ["tiktok", "shorts", "reels"])
        cpd = arguments.get("clips_per_day", 2)
        schedule = generate_posting_schedule(clips=clips, platforms=platforms, clips_per_day=cpd)
        return {"schedule": schedule, "total_posts": len(schedule)}

    elif name == "clipit_filter_duplicates":
        clips = arguments.get("clips", [])
        thresh = arguments.get("threshold_iou", 0.6)
        filtered = filter_duplicate_candidates(clips, threshold_iou=thresh)
        return {"deduplicated_clips": filtered, "kept_count": len(filtered), "original_count": len(clips)}

    else:
        raise ValueError(f"Unknown tool: '{name}'")


def process_jsonrpc_request(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process a single MCP JSON-RPC 2.0 request."""
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": {
                    "name": "clipit-mcp-server",
                    "version": __version__,
                },
            },
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": MCP_TOOLS,
            },
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        try:
            res_content = handle_tool_call(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(res_content, ensure_ascii=False, indent=2),
                        }
                    ]
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32000,
                    "message": str(exc),
                },
            }

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found",
                },
            }
        return None


def run_stdio_server():
    """Run interactive MCP server listening on stdin, responding on stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = process_jsonrpc_request(req)
            if resp:
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
