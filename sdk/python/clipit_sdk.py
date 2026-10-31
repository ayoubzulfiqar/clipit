"""
clipit_sdk — Official Typed Python Client for Clipit API.

Enables headless scripts, agents, and external services to create clipping jobs,
poll status, download rendered zip bundles, and manage presets.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Callable, Dict, List, Optional
import urllib.error
import urllib.parse
import urllib.request


class ClipitError(Exception):
    """Base exception for Clipit SDK errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, detail: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class ClipitClient:
    """
    Lightweight, dependency-free typed Python SDK for Clipit Web API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("CLIPIT_API_KEY", "")
        self.timeout = timeout

    def _headers(self, content_type: Optional[str] = "application/json") -> Dict[str, str]:
        headers = {
            "User-Agent": "Clipit-Python-SDK/1.15.0",
        }
        if content_type:
            headers["Content-Type"] = content_type
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            if query:
                url = f"{url}?{query}"

        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(
            url,
            data=body,
            headers=self._headers(content_type="application/json" if data is not None else None),
            method=method,
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_bytes = resp.read()
                if not resp_bytes:
                    return None
                return json.loads(resp_bytes.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8")
            try:
                detail = json.loads(err_body)
            except Exception:
                detail = err_body
            raise ClipitError(f"HTTP {exc.code}: {detail}", status_code=exc.code, detail=detail) from exc
        except urllib.error.URLError as exc:
            raise ClipitError(f"Connection failed: {exc.reason}") from exc

    def health(self) -> Dict[str, Any]:
        """Check system health probe."""
        return self._request("GET", "/api/health")

    def ready(self) -> Dict[str, Any]:
        """Check hardware readiness and encoder status."""
        return self._request("GET", "/api/health/ready")

    def list_jobs(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """List jobs with optional search and status filtering."""
        return self._request("GET", "/api/jobs", params={"search": search, "status": status, "page": page, "limit": limit})

    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get detail and clips for a job."""
        return self._request("GET", f"/api/jobs/{job_id}")

    def create_job(
        self,
        url: Optional[str] = None,
        upload_filename: Optional[str] = None,
        clips: int = 7,
        ratio: str = "9:16",
        ai_provider: str = "gemini",
        whisper_model: str = "large-v3",
        whisper_device: str = "auto",
        font_style: str = "HORMOZI",
        semantic_emojis: bool = False,
        use_sfx: bool = False,
        snap_scene_cuts: bool = False,
        silence_trim: bool = False,
        normalize_audio: bool = True,
        webhook_url: Optional[str] = None,
        **extra_config: Any,
    ) -> Dict[str, Any]:
        """Submit a new clipping job."""
        payload: Dict[str, Any] = {
            "clips": clips,
            "ratio": ratio,
            "ai_provider": ai_provider,
            "whisper_model": whisperModel if (whisperModel := whisper_model) else "large-v3",
            "whisper_device": whisper_device,
            "font_style": font_style,
            "semantic_emojis": semantic_emojis,
            "use_sfx": use_sfx,
            "snap_scene_cuts": snap_scene_cuts,
            "silence_trim": silence_trim,
            "normalize_audio": normalize_audio,
        }
        if url:
            payload["url"] = url
        if upload_filename:
            payload["upload_filename"] = upload_filename
        if webhook_url:
            payload["webhook_url"] = webhook_url
        payload.update(extra_config)

        return self._request("POST", "/api/jobs", data=payload)

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a running or queued job."""
        return self._request("POST", f"/api/jobs/{job_id}/cancel")

    def retry_job(self, job_id: str) -> Dict[str, Any]:
        """Retry a failed or cancelled job."""
        return self._request("POST", f"/api/jobs/{job_id}/retry")

    def clone_job(self, job_id: str) -> Dict[str, Any]:
        """Clone an existing job into a new run."""
        return self._request("POST", f"/api/jobs/{job_id}/clone")

    def delete_job(self, job_id: str) -> Dict[str, Any]:
        """Delete a job and its outputs."""
        return self._request("DELETE", f"/api/jobs/{job_id}")

    def list_presets(self) -> List[Dict[str, Any]]:
        """List available pipeline presets."""
        res = self._request("GET", "/api/presets")
        return res.get("presets", []) if isinstance(res, dict) else []

    def wait_for_job(
        self,
        job_id: str,
        poll_interval: float = 3.0,
        timeout: float = 600.0,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Poll job until completed, failed, or timed out.
        """
        start = time.time()
        while time.time() - start < timeout:
            job = self.get_job(job_id)
            status = job.get("status")

            if on_progress and job.get("progress"):
                on_progress(job["progress"])

            if status == "completed":
                return job
            elif status in ("failed", "cancelled"):
                raise ClipitError(f"Job finished with status '{status}': {job.get('error')}", detail=job)

            time.sleep(poll_interval)

        raise ClipitError(f"Timed out after {timeout} seconds waiting for job {job_id}")

    def download_zip(self, job_id: str, destination_path: str) -> str:
        """Download all rendered outputs as a zip file."""
        url = f"{self.base_url}/api/outputs/{job_id}/zip"
        req = urllib.request.Request(url, headers=self._headers(content_type=None))

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            with open(destination_path, "wb") as f:
                while chunk := resp.read(65536):
                    f.write(chunk)

        return os.path.abspath(destination_path)
