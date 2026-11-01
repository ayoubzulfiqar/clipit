import unittest

try:
    from web.api.routes.tools import (
        CalendarRequest,
        ChaptersRequest,
        CopyrightCheckRequest,
        MarketplaceExportRequest,
        check_copyright_safety,
        export_marketplace_pack,
        generate_calendar,
        generate_chapters,
    )
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False


@unittest.skipUnless(TOOLS_AVAILABLE, "Tools API dependencies (FastAPI/Pydantic) not installed")
class TestToolsAPI(unittest.IsolatedAsyncioTestCase):
    async def test_copyright_check(self):
        req = CopyrightCheckRequest(
            transcript="This is an original tech commentary video explaining neural network attention.",
            title="AI Explainer",
            has_commercial_bgm=False,
            duration=25.0,
        )
        res = await check_copyright_safety(req)
        self.assertEqual(res.risk_level, "low")
        self.assertTrue(res.is_safe_for_monetization)

    async def test_generate_chapters(self):
        req = ChaptersRequest(
            title="Episode 10",
            clips=[
                {"start_time": 0.0, "title_en": "Intro Hook"},
                {"start_time": 45.0, "title_en": "Deep Architecture"},
            ],
        )
        res = await generate_chapters(req)
        self.assertEqual(len(res.chapters), 2)
        self.assertIn("00:00 - Intro Hook", res.youtube_block)
        self.assertIn("## Chapters", res.show_notes_markdown)

    async def test_generate_calendar(self):
        req = CalendarRequest(
            clips=[
                {"rank": 1, "title_en": "Viral Clip 1"},
                {"rank": 2, "title_en": "Viral Clip 2"},
            ],
            platforms=["tiktok", "shorts"],
            clips_per_day=1,
        )
        res = await generate_calendar(req)
        self.assertGreaterEqual(res.total_slots, 2)
        self.assertEqual(len(res.schedule), res.total_slots)

    async def test_marketplace_export(self):
        req = MarketplaceExportRequest(
            pack_name="Test Pack",
            preset_data={"pilihan_rasio": "9:16", "font_style": "HORMOZI"},
            author="Tester",
        )
        res = await export_marketplace_pack(req)
        self.assertEqual(res["pack_name"], "Test Pack")
        self.assertTrue(res["download_url"].startswith("/api/files/download_pack/"))


if __name__ == "__main__":
    unittest.main()
