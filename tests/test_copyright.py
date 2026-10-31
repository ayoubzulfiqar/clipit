import unittest

from clipping.copyright import (
    analyze_content_safety,
    check_text_copyright_signals,
    recommend_originality_transforms,
)


class TestCopyrightSafety(unittest.TestCase):
    def test_clean_content_low_risk(self):
        transcript = "In this tutorial we are learning how to write clean Python unit tests."
        report = analyze_content_safety(transcript, title="Python Tutorial", continuous_duration_sec=20.0)
        self.assertEqual(report["risk_level"], "low")
        self.assertTrue(report["is_safe_for_monetization"])
        self.assertLess(report["risk_score"], 30.0)

        transforms = recommend_originality_transforms(report)
        self.assertEqual(len(transforms), 0)

    def test_copyright_flag_commercial_music(self):
        transcript = "Here is the new hit track performed by Taylor Swift under Universal Music."
        signals = check_text_copyright_signals(transcript)
        self.assertGreaterEqual(len(signals), 2)

        report = analyze_content_safety(
            transcript,
            has_commercial_bgm=True,
            continuous_duration_sec=60.0,
        )
        self.assertEqual(report["risk_level"], "high")
        self.assertFalse(report["is_safe_for_monetization"])

        transforms = recommend_originality_transforms(report)
        types = [t["type"] for t in transforms]
        self.assertIn("audio_pitch_shift", types)
        self.assertIn("audio_tempo_ramp", types)
        self.assertIn("broll_cutaway_cadence", types)
        self.assertIn("voiceover_sidechain_ducking", types)


if __name__ == "__main__":
    unittest.main()
