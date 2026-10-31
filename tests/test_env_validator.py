import unittest

from clipping.env_validator import validate_environment


class TestEnvValidator(unittest.TestCase):
    def test_missing_or_placeholder_keys_rejected(self):
        env = {
            "GOOGLE_API_KEY": "your-gemini-api-key-here",
            "PEXELS_API_KEY": "",
            "HF_TOKEN": "placeholder",
        }
        report = validate_environment(env, require_ai=True, ai_provider="gemini")
        self.assertFalse(report.is_valid)
        self.assertTrue(any("GOOGLE_API_KEY" in err for err in report.errors))
        self.assertTrue(any("PEXELS_API_KEY" in w for w in report.warnings))
        self.assertTrue(any("HF_TOKEN" in w for w in report.warnings))
        self.assertEqual(len(report.active_providers), 0)

    def test_valid_keys_accepted(self):
        env = {
            "GOOGLE_API_KEY": "AIzaSyD-valid-mock-key-12345",
            "PEXELS_API_KEY": "valid_pexels_token_98765",
            "HF_TOKEN": "hf_valid_token_555",
        }
        report = validate_environment(
            env,
            require_ai=True,
            require_broll=True,
            require_podcast=True,
            ai_provider="gemini",
        )
        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.errors), 0)
        self.assertIn("gemini", report.active_providers)
        self.assertIn("pexels", report.active_providers)
        self.assertIn("pyannote", report.active_providers)

    def test_nvidia_provider_validation(self):
        env = {
            "NVIDIA_API_KEY": "nvapi-valid-key-9999",
        }
        report = validate_environment(env, require_ai=True, ai_provider="nvidia")
        self.assertTrue(report.is_valid)
        self.assertIn("nvidia", report.active_providers)


if __name__ == "__main__":
    unittest.main()
