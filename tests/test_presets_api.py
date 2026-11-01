import unittest

try:
    from web.api import store
    API_AVAILABLE = True
except (ImportError, RuntimeError):
    API_AVAILABLE = False


@unittest.skipUnless(API_AVAILABLE, "web.api dependencies (pydantic/fastapi) not installed")
class TestPresetsStore(unittest.TestCase):
    def test_default_presets_seeded(self):
        presets = store.list_presets()
        self.assertGreaterEqual(len(presets), 5)
        names = [p["name"] for p in presets]
        self.assertIn("tiktok_viral", names)
        self.assertIn("youtube_shorts_clean", names)
        self.assertIn("reels_aesthetic", names)
        self.assertIn("podcast_split", names)
        self.assertIn("linkedin_square", names)

    def test_preset_crud(self):
        name = "custom_test_preset"
        cfg = {"pilihan_rasio": "9:16", "font_style": "HORMOZI", "test_key": 123}
        desc = "A custom preset for testing"

        # 1. Save
        saved = store.save_preset(name, cfg, desc)
        self.assertEqual(saved["name"], name)
        self.assertEqual(saved["description"], desc)
        self.assertEqual(saved["config"]["test_key"], 123)

        # 2. Get
        retrieved = store.get_preset(name)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], name)
        self.assertEqual(retrieved["config"]["pilihan_rasio"], "9:16")

        # 3. List
        all_p = store.list_presets()
        self.assertTrue(any(p["name"] == name for p in all_p))

        # 4. Delete
        del_ok = store.delete_preset(name)
        self.assertTrue(del_ok)
        self.assertIsNone(store.get_preset(name))


if __name__ == "__main__":
    unittest.main()
