import unittest
from unittest.mock import patch

from clipping.scene_detect import (
    batch_snap_clips,
    detect_scene_changes,
    snap_clip_boundaries,
    snap_to_nearest_scene_cut,
)


class TestSceneDetect(unittest.TestCase):
    def test_snap_to_nearest_scene_cut_within_tolerance(self):
        cuts = [10.2, 18.5, 30.1, 44.8]

        # 10.5 is 0.3s away from 10.2 -> snaps to 10.2
        snapped = snap_to_nearest_scene_cut(10.5, cuts, max_distance=0.8)
        self.assertEqual(snapped, 10.2)

        # 12.0 is 1.8s away from 10.2 and 6.5s away from 18.5 -> outside tolerance, remains 12.0
        unchanged = snap_to_nearest_scene_cut(12.0, cuts, max_distance=1.0)
        self.assertEqual(unchanged, 12.0)

    def test_snap_clip_boundaries(self):
        cuts = [14.8, 45.2]
        clip = {
            "rank": 1,
            "start_time": 15.0,  # 0.2s from 14.8
            "end_time": 45.0,    # 0.2s from 45.2
            "viral_score": 90,
        }

        updated = snap_clip_boundaries(clip, cuts, max_distance=0.5, min_clip_duration=10.0)
        self.assertEqual(updated["start_time"], 14.8)
        self.assertEqual(updated["end_time"], 45.2)
        self.assertTrue(updated["scene_cut_snapped"])

    def test_snap_clip_boundaries_preserves_min_duration(self):
        cuts = [20.0, 22.0]
        clip = {
            "rank": 2,
            "start_time": 19.5,
            "end_time": 25.0,
        }
        # If snapping would reduce duration below min_clip_duration (e.g. 10.0), it does not snap
        snap_clip_boundaries(clip, cuts, max_distance=1.0, min_clip_duration=10.0)
        # Duration would be 22.0 - 20.0 = 2.0s < 10.0s -> boundaries should not be modified
        self.assertEqual(clip["start_time"], 19.5)
        self.assertEqual(clip["end_time"], 25.0)

    @patch("clipping.scene_detect.detect_scene_changes")
    def test_batch_snap_clips(self, mock_detect):
        mock_detect.return_value = [10.0, 40.0, 70.0, 100.0]

        clips = [
            {"rank": 1, "start_time": 10.4, "end_time": 39.8},
            {"rank": 2, "start_time": 70.2, "end_time": 99.5},
        ]

        batch_snap_clips(clips, "mock_video.mp4", max_distance=0.8)

        self.assertEqual(clips[0]["start_time"], 10.0)
        self.assertEqual(clips[0]["end_time"], 40.0)
        self.assertEqual(clips[1]["start_time"], 70.0)
        self.assertEqual(clips[1]["end_time"], 100.0)


if __name__ == "__main__":
    unittest.main()
