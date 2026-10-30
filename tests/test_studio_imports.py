import unittest


class TestStudioImports(unittest.TestCase):
    def test_studio_package_can_be_imported_directly(self):
        """Test that clipping.studio can be imported as a standard package."""
        import clipping.studio as studio

        self.assertTrue(hasattr(studio, "proses_klip"))
        self.assertTrue(hasattr(studio, "detect_video_encoder"))
        self.assertTrue(hasattr(studio, "format_seconds"))
        self.assertTrue(hasattr(studio, "escape_ffmpeg_filter_value"))
        self.assertTrue(hasattr(studio, "_is_vertical_ratio"))
        self.assertTrue(hasattr(studio, "_get_render_dims"))
        self.assertTrue(hasattr(studio, "siapkan_glitch_video"))
        self.assertTrue(hasattr(studio, "buat_file_ass"))
        self.assertTrue(hasattr(studio, "buat_thumbnail"))
        self.assertTrue(hasattr(studio, "get_face_detector"))
        self.assertTrue(hasattr(studio, "estimate_speaker_count_from_video"))

    def test_studio_submodules_can_be_imported(self):
        """Test that submodules inside clipping.studio can be imported directly."""
        from clipping.studio import helpers
        from clipping.studio import ffmpeg_utils
        from clipping.studio import utils
        from clipping.studio import typography
        from clipping.studio import audio_bgm
        from clipping.studio import broll
        from clipping.studio import subtitles
        from clipping.studio import effects
        from clipping.studio import transitions
        from clipping.studio import thumbnail
        from clipping.studio import watermark

        self.assertTrue(callable(helpers.format_seconds))
        self.assertTrue(callable(ffmpeg_utils.detect_video_encoder))
        self.assertTrue(callable(utils._is_vertical_ratio))
        self.assertTrue(callable(typography.download_google_font))
        self.assertTrue(callable(audio_bgm.build_bgm_filter))
        self.assertTrue(callable(subtitles.buat_file_ass))
        self.assertTrue(callable(thumbnail.buat_thumbnail))
        self.assertTrue(callable(watermark.apply_watermark))


if __name__ == "__main__":
    unittest.main()
