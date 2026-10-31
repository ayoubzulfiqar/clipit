from datetime import datetime, timezone
import os
import shutil
import tempfile
import unittest

from clipping.scheduler import (
    export_schedule_csv,
    export_schedule_json,
    generate_posting_schedule,
    get_next_optimal_slot,
)


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_get_next_optimal_slot(self):
        # Starting at 05:00 UTC
        start = datetime(2026, 11, 1, 5, 0, 0, tzinfo=timezone.utc)
        # Next peak for tiktok (peaks at 7, 12, 19, 22) with min_gap 1 hour
        slot = get_next_optimal_slot(start, platform="tiktok", min_gap_hours=1.0)
        self.assertEqual(slot.hour, 7)
        self.assertEqual(slot.day, 1)

    def test_generate_posting_schedule(self):
        clips = [
            {
                "rank": 1,
                "title_inggris": "Hook Your Audience Fast",
                "hastag": "#growth #creators",
                "output_video": "outputs/clip_1.mp4",
            },
            {
                "rank": 2,
                "title_inggris": "The 3 Second Rule",
                "hastag": "#editing #tips",
                "output_video": "outputs/clip_2.mp4",
            },
        ]

        start = datetime(2026, 11, 1, 6, 0, 0, tzinfo=timezone.utc)
        schedule = generate_posting_schedule(
            clips=clips,
            platforms=["tiktok", "shorts"],
            start_time=start,
            clips_per_day=2,
        )

        # 2 clips * 2 platforms = 4 scheduled posts
        self.assertEqual(len(schedule), 4)
        for post in schedule:
            self.assertIn("scheduled_time_iso", post)
            self.assertIn("platform", post)
            self.assertIn("title", post)

        # Export test
        csv_path = os.path.join(self.tmp_dir, "calendar.csv")
        json_path = os.path.join(self.tmp_dir, "calendar.json")

        export_schedule_csv(schedule, csv_path)
        export_schedule_json(schedule, json_path)

        self.assertTrue(os.path.exists(csv_path))
        self.assertTrue(os.path.exists(json_path))
        self.assertGreater(os.path.getsize(csv_path), 0)
        self.assertGreater(os.path.getsize(json_path), 0)


if __name__ == "__main__":
    unittest.main()
