import unittest

from clipping.ctr_optimizer import (
    generate_ctr_variants,
    recommend_thumbnail_text,
    score_title_ctr,
)


class TestCTROptimizer(unittest.TestCase):
    def test_score_title_ctr_high_performing(self):
        title = "Why This Insane Money Secret Shocked Everyone"
        res = score_title_ctr(title)
        self.assertGreaterEqual(res["ctr_score"], 80)
        self.assertIn(res["grade"], ("A", "A+"))
        self.assertTrue(len(res["matched_power_words"]) >= 2)

    def test_score_title_ctr_low_performing(self):
        title = "video clip"
        res = score_title_ctr(title)
        self.assertLess(res["ctr_score"], 60)
        self.assertIn(res["grade"], ("D", "F"))

    def test_recommend_thumbnail_text(self):
        text = recommend_thumbnail_text("How this secret AI tool works")
        self.assertIsInstance(text, str)
        self.assertTrue(text.isupper())
        self.assertIn("SECRET", text)

    def test_generate_ctr_variants(self):
        variants = generate_ctr_variants("Scaling a SaaS Business")
        self.assertEqual(len(variants), 3)
        angles = [v["angle"] for v in variants]
        self.assertIn("Curiosity Gap", angles)
        self.assertIn("Mistake & FOMO", angles)
        self.assertIn("Direct High-Value", angles)
        for v in variants:
            self.assertGreaterEqual(v["score"], 60)


if __name__ == "__main__":
    unittest.main()
