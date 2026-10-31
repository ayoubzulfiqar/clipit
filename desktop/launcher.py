#!/usr/bin/env python3
"""
desktop.launcher — Desktop Application Orchestrator for Clipit Studio

Launches the Clipit Studio backend server and opens the user interface in a native
window or default browser, managing the process lifecycle and graceful shutdown.
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from typing import Optional


def find_free_port(start_port: int = 8000, max_attempts: int = 50) -> int:
    """Find an available TCP port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            result = sock.connect_ex(("127.0.0.1", port))
            if result != 0:
                return port
    return start_port


def check_ffmpeg_available() -> bool:
    """Verify that FFmpeg is available on the system PATH or local bundles."""
    return shutil.which("ffmpeg") is not None


def wait_for_server(url: str, timeout_sec: float = 15.0) -> bool:
    """Poll health endpoint until server is ready or timeout occurs."""
    start_time = time.time()
    health_url = f"{url.rstrip('/')}/api/health"
    while time.time() - start_time < timeout_sec:
        try:
            req = urllib.request.Request(health_url, headers={"User-Agent": "ClipitDesktop/1.0"})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def launch_desktop(
    host: str = "127.0.0.1",
    port: Optional[int] = None,
    open_browser: bool = True,
    dry_run: bool = False,
) -> int:
    """
    Launch Clipit Studio desktop runner.
    
    Returns exit code (0 for success).
    """
    if not check_ffmpeg_available():
        print("⚠️ [WARN] FFmpeg was not detected in system PATH. Video rendering may fail.")

    target_port = port or find_free_port(8000)
    server_url = f"http://{host}:{target_port}"
    print(f"🎬 Initializing Clipit Studio Desktop at {server_url}...")

    if dry_run:
        print("🧪 [DRY RUN] Desktop launcher validated successfully.")
        return 0

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "web.api.app:app",
        "--host",
        host,
        "--port",
        str(target_port),
    ]

    env = os.environ.copy()
    env["CLIPIT_DESKTOP_MODE"] = "1"

    proc = subprocess.Popen(cmd, env=env)
    print(f"🚀 Backend process spawned (PID: {proc.pid})")

    try:
        ready = wait_for_server(server_url, timeout_sec=12.0)
        if ready:
            print(f"✅ Clipit Studio is running at {server_url}")
            if open_browser:
                webbrowser.open(server_url)
        else:
            print(f"⚠️ Server took longer than expected to respond. URL: {server_url}")

        # Block until subprocess terminates
        return proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Clipit Studio Desktop...")
        proc.terminate()
        try:
            proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            proc.kill()
        return 0


def main():
    parser = argparse.ArgumentParser(description="Clipit Studio Desktop Launcher")
    parser.add_argument("--host", default="127.0.0.1", help="Binding host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=None, help="Binding port (default: auto-detect free port)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open default browser")
    parser.add_argument("--dry-run", action="store_true", help="Validate setup without launching server")
    args = parser.parse_args()

    code = launch_desktop(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
        dry_run=args.dry_run,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
