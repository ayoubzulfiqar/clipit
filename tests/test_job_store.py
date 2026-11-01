import os
import tempfile
import unittest
from unittest.mock import patch

try:
    from web.api.models import JobStatus, ClipDetail
    STORE_AVAILABLE = True
except (ImportError, RuntimeError):
    STORE_AVAILABLE = False


@unittest.skipUnless(STORE_AVAILABLE, "web.api dependencies (pydantic/fastapi) not installed")
class TestJobStore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.persist_path = os.path.join(self.test_dir.name, "jobs.json")
        self.db_path = os.path.join(self.test_dir.name, "jobs.sqlite3")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_job_crud_lifecycle(self):
        from web.api import store

        with patch("web.api.store.PERSIST_PATH", self.persist_path), \
             patch("web.api.store.DB_PATH", self.db_path):
            store._init_db()

            # 1. Create job
            job_id = store.create_job(
                url="https://youtube.com/watch?v=123",
                source="youtube",
                config={"clips": 5},
            )
            self.assertIsNotNone(job_id)

            # 2. Get job
            job = store.get_job(job_id)
            self.assertIsNotNone(job)
            self.assertEqual(job["status"], JobStatus.QUEUED.value)
            self.assertEqual(job["url"], "https://youtube.com/watch?v=123")
            self.assertEqual(store.get_queued_count(), 1)
            self.assertEqual(store.get_running_count(), 0)

            # 3. Update status & progress
            store.set_status(job_id, JobStatus.DOWNLOADING)
            self.assertEqual(store.get_running_count(), 1)
            self.assertEqual(store.get_queued_count(), 0)

            store.update_progress(
                job_id,
                step="download",
                step_number=1,
                total_steps=5,
                message="Downloading video",
                percent=20.0,
            )
            job = store.get_job(job_id)
            self.assertEqual(job["progress"]["step"], "download")
            self.assertEqual(len(job["log"]), 1)

            # 4. Set clips (completion)
            clip = ClipDetail(
                rank=1,
                title="Best Clip",
                filename="clip_1.mp4",
                duration_seconds=30.0,
                start_time=0.0,
                end_time=30.0,
                download_url="/api/outputs/test/clip_1.mp4",
            )
            store.set_clips(job_id, [clip])
            job = store.get_job(job_id)
            self.assertEqual(job["status"], JobStatus.COMPLETED.value)
            self.assertEqual(len(job["clips"]), 1)
            self.assertEqual(store.get_running_count(), 0)

            # 5. List jobs
            jobs = store.list_jobs()
            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0]["id"], job_id)

            # 6. Delete job
            deleted = store.delete_job(job_id)
            self.assertTrue(deleted)
            self.assertIsNone(store.get_job(job_id))
            self.assertEqual(len(store.list_jobs()), 0)

    def test_legacy_jobs_json_migration(self):
        import json
        from web.api import store

        legacy_data = {
            "legacy_job_99": {
                "id": "legacy_job_99",
                "status": "completed",
                "url": "https://youtube.com/watch?v=legacy",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:05:00+00:00",
                "config": {"clips": 3},
                "log": ["[test] done"],
            }
        }
        with open(self.persist_path, "w", encoding="utf-8") as f:
            json.dump(legacy_data, f)

        with patch("web.api.store.PERSIST_PATH", self.persist_path), \
             patch("web.api.store.DB_PATH", self.db_path):
            store._init_db()
            migrated_job = store.get_job("legacy_job_99")
            self.assertIsNotNone(migrated_job)
            self.assertEqual(migrated_job["status"], "completed")
            self.assertEqual(migrated_job["config"]["clips"], 3)

    def test_reconcile_orphan_jobs(self):
        from web.api import store
        from web.api.models import JobStatus

        with patch("web.api.store.PERSIST_PATH", self.persist_path), \
             patch("web.api.store.DB_PATH", self.db_path):
            store._init_db()
            j1 = store.create_job(url="https://youtube.com/watch?v=1")
            j2 = store.create_job(url="https://youtube.com/watch?v=2")
            j3 = store.create_job(url="https://youtube.com/watch?v=3")
            j4 = store.create_job(url="https://youtube.com/watch?v=4")

            store.set_status(j2, JobStatus.RENDERING)
            store.set_status(j3, JobStatus.COMPLETED)
            store.set_error(j4, "Prior failure")

            reconciled = store.reconcile_orphan_jobs("Server restarted")
            self.assertEqual(reconciled, 2)

            # j1 (was queued) -> now failed
            res_j1 = store.get_job(j1)
            self.assertEqual(res_j1["status"], JobStatus.FAILED.value)
            self.assertIn("Server restarted", res_j1["error"])

            # j2 (was rendering) -> now failed
            res_j2 = store.get_job(j2)
            self.assertEqual(res_j2["status"], JobStatus.FAILED.value)
            self.assertIn("Server restarted", res_j2["error"])

            # j3 (was completed) -> untouched
            res_j3 = store.get_job(j3)
            self.assertEqual(res_j3["status"], JobStatus.COMPLETED.value)

            # j4 (was already failed) -> untouched
            res_j4 = store.get_job(j4)
            self.assertEqual(res_j4["status"], JobStatus.FAILED.value)
            self.assertEqual(res_j4["error"], "Prior failure")


if __name__ == "__main__":
    unittest.main()
