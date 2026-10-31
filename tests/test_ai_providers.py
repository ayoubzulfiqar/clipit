import unittest
from unittest.mock import MagicMock, patch

from clipping.ai import (
    AIResult,
    AnthropicProvider,
    BaseAIProvider,
    FallbackChainProvider,
    GeminiProvider,
    NvidiaProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
    UsageMetadata,
    get_ai_provider,
)
from clipping.config import ClipitConfig


class TestAIProviders(unittest.TestCase):
    def test_factory_returns_expected_classes(self):
        self.assertIsInstance(get_ai_provider("gemini"), GeminiProvider)
        self.assertIsInstance(get_ai_provider("nvidia"), NvidiaProvider)
        self.assertIsInstance(get_ai_provider("openai"), OpenAICompatibleProvider)
        self.assertIsInstance(get_ai_provider("ollama"), OllamaProvider)
        self.assertIsInstance(get_ai_provider("anthropic"), AnthropicProvider)
        self.assertIsInstance(get_ai_provider("auto"), FallbackChainProvider)

    def test_cost_estimation(self):
        gemini = GeminiProvider()
        # 1M prompt tokens at $0.075 + 1M completion at $0.30 = $0.375
        cost = gemini.estimate_cost(1_000_000, 1_000_000, "gemini-1.5-flash")
        self.assertAlmostEqual(cost, 0.375, places=3)

        ollama = OllamaProvider()
        # Local offline Ollama is completely free
        self.assertEqual(ollama.estimate_cost(500_000, 200_000, "llama3.2"), 0.0)

    def test_is_configured_logic(self):
        cfg_empty = ClipitConfig(api_key_gemini="", api_key_nvidia="placeholder_key")
        cfg_valid = ClipitConfig(api_key_gemini="AIzaSyValidGeminiKey", api_key_nvidia="nvapi-valid")

        gemini = GeminiProvider()
        self.assertFalse(gemini.is_configured(cfg_empty))
        self.assertTrue(gemini.is_configured(cfg_valid))

        ollama = OllamaProvider()
        # Local Ollama is always configured (defaults to local daemon)
        self.assertTrue(ollama.is_configured(cfg_empty))

    def test_fallback_chain_failover(self):
        """Verify that FallbackChainProvider fails over to the secondary provider on error."""
        cfg = ClipitConfig(jumlah_clip=1, durasi_hook=3)

        mock_p1 = MagicMock(spec=BaseAIProvider)
        mock_p1.name = "failing_primary"
        mock_p1.is_configured.return_value = True
        mock_p1.analyze.side_effect = RuntimeError("503 Service Unavailable / Rate Limit")

        mock_p2 = MagicMock(spec=BaseAIProvider)
        mock_p2.name = "healthy_secondary"
        mock_p2.is_configured.return_value = True
        expected_clips = [{"rank": 1, "title": "Fallback Clip", "viral_score": 90}]
        mock_p2.analyze.return_value = AIResult(
            clips=expected_clips,
            provider_name="healthy_secondary",
            model_name="mock_model",
            usage=UsageMetadata(prompt_tokens=100, completion_tokens=50, estimated_cost_usd=0.001),
        )

        chain = FallbackChainProvider([mock_p1, mock_p2])
        result = chain.analyze("dummy transcript", cfg)

        self.assertEqual(result.provider_name, "healthy_secondary")
        self.assertEqual(len(result.clips), 1)
        self.assertEqual(result.clips[0]["title"], "Fallback Clip")
        mock_p1.analyze.assert_called_once()
        mock_p2.analyze.assert_called_once()

    def test_fallback_chain_all_fail_raises_runtime_error(self):
        cfg = ClipitConfig(jumlah_clip=1, durasi_hook=3)

        mock_p1 = MagicMock(spec=BaseAIProvider)
        mock_p1.name = "primary"
        mock_p1.is_configured.return_value = True
        mock_p1.analyze.side_effect = ValueError("Primary parse error")

        chain = FallbackChainProvider([mock_p1])
        with self.assertRaises(RuntimeError) as ctx:
            chain.analyze("dummy transcript", cfg)
        self.assertIn("All AI providers in fallback chain failed", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
