import unittest
from unittest.mock import AsyncMock, patch

try:
    from fastapi import HTTPException
    from web.api.routes.batch import (
        BatchJobCreateRequest,
        BatchJobItem,
        cancel_batch_jobs,
        create_batch_jobs,
        get_batch_status,
    )
    from web.api import store
    BATCH_AVAILABLE = True
except (ImportError, RuntimeError):
    BATCH_AVAILABLE = False


@unittest.skipUnless(BATCH_AVAILABLE, "web.api dependencies (fastapi/pydantic) not installed")
class TestBatchAPI(unittest.IsolatedAsyncioTestCase):
    @patch("web.api.worker.submit_job", new_callable=AsyncMock)
    async def test_create_and_query_batch(self, mock_submit):
        req = BatchJobCreateRequest(
            items=[
                BatchJobItem(url="https://www.youtube.com/watch?v=batch1", pilihan_rasio="9:16"),
                BatchJobItem(url="https://www.youtube.com/watch?v=batch2", pilihan_rasio="1:1"),
            ],
            default_config={"font_style": "the_bold_font"},
            batch_webhook_url="https://api.example.com/webhook",
        )

        res = await create_batch_jobs(req)
        self.assertTrue(res.batch_id.startswith("batch_"))
        self.assertEqual(res.total_jobs, 2)
        self.assertEqual(len(res.jobs), 2)
        batch_id = res.batch_id

        # Query batch status
        status = await get_batch_status(batch_id)
        self.assertEqual(status.batch_id, batch_id)
        self.assertEqual(status.total, 2)
        self.assertEqual(len(status.jobs), 2)

        # Cancel batch
        cancel_res = await cancel_batch_jobs(batch_id)
        self.assertEqual(cancel_res["batch_id"], batch_id)
        self.assertEqual(cancel_res["total"], 2)

    async def test_batch_not_found(self):
        with self.assertRaises(HTTPException) as ctx:
            await get_batch_status("non_existent_batch")
        self.assertEqual(ctx.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
