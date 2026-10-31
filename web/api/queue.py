"""
web.api.queue — Pluggable task queue abstraction (Local ThreadPool & Distributed Redis/ARQ).
"""

from __future__ import annotations

import asyncio
import json
import os
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

from clipping.logger import get_logger

logger = get_logger("web.api.queue")


class BaseTaskQueue(ABC):
    """Abstract base class for background job task execution."""

    @abstractmethod
    async def submit_job(self, job_id: str, payload: dict, runner_fn: Callable[[str, dict], None]) -> None:
        """Enqueue or execute a pipeline job."""
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Return status and queue metrics."""
        pass


class LocalTaskQueue(BaseTaskQueue):
    """In-process thread-pool executor bounded by asyncio semaphore."""

    def __init__(self, max_concurrent: Optional[int] = None):
        concurrency = max_concurrent or int(os.environ.get("MAX_CONCURRENT_JOBS", "1"))
        self._semaphore = asyncio.Semaphore(concurrency)
        self._executor = ThreadPoolExecutor(max_workers=concurrency)
        self._max_concurrent = concurrency
        self._active_tasks: Dict[str, asyncio.Task] = {}

    async def submit_job(self, job_id: str, payload: dict, runner_fn: Callable[[str, dict], None]) -> None:
        async def _wrapped_runner():
            async with self._semaphore:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self._executor, runner_fn, job_id, payload)

        task = asyncio.create_task(_wrapped_runner())
        self._active_tasks[job_id] = task

        def _cleanup(_):
            self._active_tasks.pop(job_id, None)

        task.add_done_callback(_cleanup)

    def cancel_task(self, job_id: str) -> bool:
        task = self._active_tasks.get(job_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

    def get_info(self) -> Dict[str, Any]:
        return {
            "type": "local",
            "distributed": False,
            "max_concurrent": self._max_concurrent,
            "active_tasks": len(self._active_tasks),
        }


class RedisTaskQueue(BaseTaskQueue):
    """
    Distributed Redis queue for external multi-worker architectures.
    Pushes job payloads to a Redis list (`clipit:queue`) and publishes
    job notification events (`clipit:events`).
    """

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis_client = None

    def _get_client(self):
        if self._redis_client is None:
            import redis
            self._redis_client = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis_client

    async def submit_job(self, job_id: str, payload: dict, runner_fn: Callable[[str, dict], None]) -> None:
        try:
            r = self._get_client()
            job_data = {
                "job_id": job_id,
                "payload": payload,
            }
            # Push onto the FIFO task list
            r.rpush("clipit:queue", json.dumps(job_data))
            # Publish event
            r.publish("clipit:jobs", json.dumps({"event": "job_submitted", "job_id": job_id}))
            logger.info("Dispatched job %s to distributed Redis queue at %s", job_id, self.redis_url)
        except Exception as exc:
            logger.error("Failed to enqueue job %s to Redis: %s. Falling back to local execution.", job_id, exc)
            # Fallback to direct threadpool execution if Redis connection fails
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, runner_fn, job_id, payload)

    def get_info(self) -> Dict[str, Any]:
        queue_len = 0
        try:
            r = self._get_client()
            queue_len = r.llen("clipit:queue")
        except Exception:
            pass
        return {
            "type": "redis",
            "distributed": True,
            "redis_url": self.redis_url,
            "queue_length": queue_len,
        }


_global_queue: Optional[BaseTaskQueue] = None


def get_task_queue() -> BaseTaskQueue:
    """Singleton getter returning configured TaskQueue (Redis if configured, else Local)."""
    global _global_queue
    if _global_queue is None:
        redis_url = os.environ.get("CLIPIT_REDIS_URL") or os.environ.get("REDIS_URL")
        if redis_url:
            _global_queue = RedisTaskQueue(redis_url.strip())
        else:
            _global_queue = LocalTaskQueue()
    return _global_queue
