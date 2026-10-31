import unittest

from clipping.engine import get_analysis_prompt
from clipping.metadata import normalize_and_validate


class TestViralityFactors(unittest.TestCase):
    def test_analysis_prompt_contains_virality_factors(self):
        prompt = get_analysis_prompt(
            transkrip_lengkap="[0.0 - 5.0] Test transcript",
            jumlah_clip=3,
            durasi_hook=3,
        )
        self.assertIn("virality_factors", prompt)
        self.assertIn("hook_strength", prompt)
        self.assertIn("engagement_potential", prompt)
        self.assertIn("emotional_intensity", prompt)
        self.assertIn("pacing_score", prompt)

    def test_normalize_and_validate_preserves_explicit_virality_factors(self):
        raw = [
            {
                "rank": 1,
                "viral_score": 95,
                "start_time": 10.0,
                "end_time": 40.0,
                "title_indonesia": "Judul Indonesia",
                "title_inggris": "English Title",
                "hastag": "#viral #trend",
                "description_hook": "Hook description.",
                "description_context": "Context description.",
                "virality_factors": {
                    "hook_strength": 98,
                    "engagement_potential": 94,
                    "emotional_intensity": 90,
                    "pacing_score": 96,
                    "virality_explanation": "Extremely punchy intro hook with strong payoff.",
                },
            }
        ]

        normalized = normalize_and_validate(raw)
        self.assertEqual(len(normalized), 1)
        vf = normalized[0].get("virality_factors")
        self.assertIsInstance(vf, dict)
        self.assertEqual(vf["hook_strength"], 98)
        self.assertEqual(vf["engagement_potential"], 94)
        self.assertEqual(vf["emotional_intensity"], 90)
        self.assertEqual(vf["pacing_score"], 96)
        self.assertEqual(vf["virality_explanation"], "Extremely punchy intro hook with strong payoff.")

    def test_normalize_and_validate_derives_fallback_virality_factors(self):
        # Legacy response without virality_factors field
        raw = [
            {
                "rank": 1,
                "viral_score": 85,
                "start_time": 5.0,
                "end_time": 25.0,
                "title_indonesia": "Judul Sederhana",
                "title_inggris": "Simple Title",
                "hastag": "#simple #clip",
                "description_hook": "Hook description.",
                "description_context": "Context description.",
                "alasan": "Topik sangat relate dengan banyak orang.",
            }
        ]

        normalized = normalize_and_validate(raw)
        self.assertEqual(len(normalized), 1)
        vf = normalized[0].get("virality_factors")
        self.assertIsInstance(vf, dict)
        self.assertGreaterEqual(vf["hook_strength"], 80)
        self.assertGreaterEqual(vf["engagement_potential"], 80)
        self.assertGreaterEqual(vf["emotional_intensity"], 80)
        self.assertGreaterEqual(vf["pacing_score"], 80)
        self.assertIn("Topik sangat relate", vf["virality_explanation"])


if __name__ == "__main__":
    unittest.main()
