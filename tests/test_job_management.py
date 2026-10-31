import unittest

try:
    from web.api.models import JobStatus
    from web.api import store
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False


@unittest.skipUnless(API_AVAILABLE, "web.api dependencies (pydantic/fastapi) not installed")
class TestJobManagement(unittest.TestCase):
    def test_cancel_and_clone_job(self):
        job_id = store.create_job(
            url="https://youtube.com/watch?v=sample_mgmt",
            config={"clips": 5, "ratio": "9:16"},
            tags=["demo", "sports"],
        )

        job = store.get_job(job_id)
        self.assertEqual(job["status"], JobStatus.QUEUED.value)
        self.assertEqual(job["tags"], ["demo", "sports"])

        # 1. Cancel
        cancelled = store.cancel_job(job_id)
        self.assertTrue(cancelled)
        job_after = store.get_job(job_id)
        self.assertEqual(job_after["status"], JobStatus.CANCELLED.value)

        # 2. Clone with override
        cloned_id = store.clone_job(job_id, config_overrides={"clips": 10})
        self.assertIsNotNone(cloned_id)
        self.assertNotEqual(cloned_id, job_id)

        cloned_job = store.get_job(cloned_id)
        self.assertEqual(cloned_job["status"], JobStatus.QUEUED.value)
        self.assertEqual(cloned_job["config"]["clips"], 10)
        self.assertEqual(cloned_job["config"]["ratio"], "9:16")
        self.assertEqual(cloned_job["tags"], ["demo", "sports"])

    def test_update_tags_and_search(self):
        job_id = store.create_job(
            url="https://youtube.com/watch?v=unique_tag_search_target",
            config={"clips": 3},
        )

        # Update tags
        store.update_job_tags(job_id, ["tagA", "tagB"])
        updated = store.get_job(job_id)
        self.assertEqual(updated["tags"], ["tagA", "tagB"])

        # Search by tag
        jobs_tag, total_tag = store.search_jobs(tag="tagA")
        self.assertGreaterEqual(total_tag, 1)
        self.assertTrue(any(j["id"] == job_id for j in jobs_tag))

        # Search by query
        jobs_q, total_q = store.search_jobs(query="unique_tag_search_target")
        self.assertGreaterEqual(total_q, 1)
        self.assertTrue(any(j["id"] == job_id for j in jobs_q))

    def test_bulk_cancel_and_delete(self):
        j1 = store.create_job(url="https://example.com/bulk1")
        j2 = store.create_job(url="https://example.com/bulk2")

        # Bulk cancel
        cancelled_count = store.bulk_cancel_jobs([j1, j2])
        self.assertEqual(cancelled_count, 2)
        self.assertEqual(store.get_job(j1)["status"], JobStatus.CANCELLED.value)
        self.assertEqual(store.get_job(j2)["status"], JobStatus.CANCELLED.value)

        # Bulk delete
        deleted_count = store.bulk_delete_jobs([j1, j2])
        self.assertEqual(deleted_count, 2)
        self.assertIsNone(store.get_job(j1))
        self.assertIsNone(store.get_job(j2))


if __name__ == "__main__":
    unittest.main()
