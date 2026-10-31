import asyncio
import os
import unittest
from unittest.mock import MagicMock, patch

from web.api.queue import (
    BaseTaskQueue,
    LocalTaskQueue,
    RedisTaskQueue,
    get_task_queue,
)


class TestTaskQueue(unittest.IsolatedAsyncioTestCase):
    async def test_local_task_queue_executes_runner(self):
        queue = LocalTaskQueue(max_concurrent=2)
        executed_jobs = []

        def mock_runner(job_id, payload):
            executed_jobs.append((job_id, payload.get("test")))

        await queue.submit_job("job_1", {"test": "val1"}, mock_runner)
        await asyncio.sleep(0.05)

        self.assertEqual(len(executed_jobs), 1)
        self.assertEqual(executed_jobs[0], ("job_1", "val1"))

        info = queue.get_info()
        self.assertEqual(info["type"], "local")
        self.assertFalse(info["distributed"])
        self.assertEqual(info["max_concurrent"], 2)

    def test_get_task_queue_defaults_to_local(self):
        with patch.dict(os.environ, {}, clear=True):
            import web.api.queue as q_mod
            q_mod._global_queue = None
            tq = get_task_queue()
            self.assertIsInstance(tq, LocalTaskQueue)

    def test_get_task_queue_uses_redis_when_configured(self):
        with patch.dict(os.environ, {"CLIPIT_REDIS_URL": "redis://localhost:6379/0"}):
            import web.api.queue as q_mod
            q_mod._global_queue = None
            tq = get_task_queue()
            self.assertIsInstance(tq, RedisTaskQueue)
            self.assertEqual(tq.redis_url, "redis://localhost:6379/0")
            # Reset
            q_mod._global_queue = None


if __name__ == "__main__":
    unittest.main()
