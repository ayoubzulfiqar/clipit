"""
clipping.gpu_offload — Serverless GPU Offload Interface

Provides pluggable remote GPU execution adapters for high-throughput video rendering,
whisper transcription, and face-tracking inference targeting serverless backends
such as Modal, RunPod, Replicate, or custom HTTP GPU endpoints.
"""

from __future__ import annotations

import abc
import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


class GPUOffloadProvider(abc.ABC):
    """Abstract base class for GPU offload providers."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Provider identifier name."""
        pass

    @abc.abstractmethod
    def is_configured(self) -> bool:
        """Check whether the provider has required credentials and configuration."""
        pass

    @abc.abstractmethod
    def submit_task(self, task_type: str, payload: Dict[str, Any]) -> str:
        """Submit a GPU rendering/inference task and return a unique task_id."""
        pass

    @abc.abstractmethod
    def get_status(self, task_id: str) -> Dict[str, Any]:
        """
        Poll task status.
        
        Returns dict with keys:
          - status: "QUEUED", "PROCESSING", "COMPLETED", "FAILED"
          - result: Any (if COMPLETED)
          - error: Optional[str] (if FAILED)
        """
        pass

    def cancel_task(self, task_id: str) -> bool:
        """Attempt to cancel an in-flight remote task."""
        return False


class LocalGPUProvider(GPUOffloadProvider):
    """Default local provider (no-op remote offload; processes on host machine)."""

    @property
    def name(self) -> str:
        return "local"

    def is_configured(self) -> bool:
        return True

    def submit_task(self, task_type: str, payload: Dict[str, Any]) -> str:
        task_id = f"local_{os.urandom(4).hex()}"
        return task_id

    def get_status(self, task_id: str) -> Dict[str, Any]:
        return {
            "status": "COMPLETED",
            "provider": "local",
            "task_id": task_id,
            "result": {"message": "Local execution handled inline."},
        }


class ModalOffloadProvider(GPUOffloadProvider):
    """
    Modal serverless GPU offload provider.
    Requires MODAL_ENDPOINT_URL and optional MODAL_AUTH_TOKEN.
    """

    def __init__(self, endpoint_url: Optional[str] = None, auth_token: Optional[str] = None):
        self.endpoint_url = endpoint_url or os.getenv("MODAL_ENDPOINT_URL", "")
        self.auth_token = auth_token or os.getenv("MODAL_AUTH_TOKEN", "")

    @property
    def name(self) -> str:
        return "modal"

    def is_configured(self) -> bool:
        return bool(self.endpoint_url)

    def submit_task(self, task_type: str, payload: Dict[str, Any]) -> str:
        if not self.is_configured():
            raise ValueError("ModalOffloadProvider is not configured with MODAL_ENDPOINT_URL.")

        body = json.dumps({"task_type": task_type, "payload": payload}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        req = urllib.request.Request(self.endpoint_url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return str(data.get("task_id", data.get("id", "modal_task")))

    def get_status(self, task_id: str) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("ModalOffloadProvider is not configured with MODAL_ENDPOINT_URL.")

        url = f"{self.endpoint_url.rstrip('/')}/status/{task_id}"
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=15.0) as resp:
            return json.loads(resp.read().decode("utf-8"))


class RunPodOffloadProvider(GPUOffloadProvider):
    """
    RunPod Serverless GPU provider.
    Requires RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID.
    """

    def __init__(self, api_key: Optional[str] = None, endpoint_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("RUNPOD_API_KEY", "")
        self.endpoint_id = endpoint_id or os.getenv("RUNPOD_ENDPOINT_ID", "")

    @property
    def name(self) -> str:
        return "runpod"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.endpoint_id)

    def submit_task(self, task_type: str, payload: Dict[str, Any]) -> str:
        if not self.is_configured():
            raise ValueError("RunPodOffloadProvider requires RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID.")

        url = f"https://api.runpod.ai/v2/{self.endpoint_id}/run"
        body = json.dumps({"input": {"task_type": task_type, **payload}}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return str(data.get("id", ""))

    def get_status(self, task_id: str) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError("RunPodOffloadProvider requires RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID.")

        url = f"https://api.runpod.ai/v2/{self.endpoint_id}/status/{task_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=15.0) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            # Normalize RunPod status codes
            runpod_status = raw.get("status", "UNKNOWN").upper()
            status_map = {
                "IN_QUEUE": "QUEUED",
                "IN_PROGRESS": "PROCESSING",
                "COMPLETED": "COMPLETED",
                "FAILED": "FAILED",
            }
            return {
                "status": status_map.get(runpod_status, runpod_status),
                "result": raw.get("output"),
                "error": raw.get("error"),
                "raw": raw,
            }


def get_gpu_offload_provider(provider_type: Optional[str] = None) -> GPUOffloadProvider:
    """
    Factory function returning the configured GPU offload provider.
    Defaults to 'local' if unset or invalid.
    """
    selected = (provider_type or os.getenv("CLIPIT_GPU_OFFLOAD_PROVIDER", "local")).strip().lower()

    if selected == "modal":
        return ModalOffloadProvider()
    elif selected == "runpod":
        return RunPodOffloadProvider()
    else:
        return LocalGPUProvider()
