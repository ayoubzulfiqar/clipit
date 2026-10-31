import unittest

from clipping.dedup import (
    calculate_temporal_iou,
    calculate_text_similarity,
    filter_duplicate_candidates,
)


class TestClipDedup(unittest.TestCase):
    def test_calculate_temporal_iou(self):
        # Exact match
        self.assertAlmostEqual(calculate_temporal_iou(10.0, 30.0, 10.0, 30.0), 1.0)
        # Disjoint
        self.assertAlmostEqual(calculate_temporal_iou(0.0, 10.0, 20.0, 30.0), 0.0)
        # 50% overlap: [10, 30] vs [20, 40] -> intersection [20, 30] = 10, union [10, 40] = 30 -> 10/30 = 0.333
        iou = calculate_temporal_iou(10.0, 30.0, 20.0, 40.0)
        self.assertAlmostEqual(iou, 10.0 / 30.0, places=3)

    def test_calculate_text_similarity(self):
        text_a = "How to build an AI agent from scratch"
        text_b = "how to build an AI agent easily"
        sim = calculate_text_similarity(text_a, text_b)
        self.assertGreater(sim, 0.6)

    def test_filter_duplicate_candidates_drops_lower_rank_overlap(self):
        candidates = [
            {
                "rank": 1,
                "viral_score": 95,
                "start_time": 10.0,
                "end_time": 40.0,
                "title_inggris": "The secret to massive wealth",
            },
            {
                "rank": 2,
                "viral_score": 88,
                "start_time": 12.0,
                "end_time": 39.0,  # 90%+ overlap with rank 1
                "title_inggris": "Secrets of massive wealth",
            },
            {
                "rank": 3,
                "viral_score": 82,
                "start_time": 80.0,
                "end_time": 110.0,  # completely independent clip
                "title_inggris": "Why discipline beats motivation",
            },
        ]

        filtered = filter_duplicate_candidates(candidates, threshold_iou=0.60)
        self.assertEqual(len(filtered), 2)
        # Rank 1 should be kept, rank 2 dropped, rank 3 kept
        self.assertEqual(filtered[0]["rank"], 1)
        self.assertEqual(filtered[1]["rank"], 3)


if __name__ == "__main__":
    unittest.main()
