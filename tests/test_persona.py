import unittest

from clipping.persona import (
    PERSONAS,
    get_persona,
    get_persona_prompt_instructions,
    list_personas,
)


class TestPersona(unittest.TestCase):
    def test_get_persona_default(self):
        p = get_persona("unknown_persona")
        self.assertEqual(p["name"], "General Audience")

    def test_get_persona_tech(self):
        p = get_persona("tech_founder")
        self.assertEqual(p["keyword_palette"], "neon_cyber")
        self.assertEqual(p["font_style"], "STORYTELLER")

    def test_get_persona_prompt_instructions(self):
        prompt = get_persona_prompt_instructions("finance_investor")
        self.assertIn("Finance & Wealth Builder", prompt)
        self.assertIn("asymmetric risk", prompt)

    def test_list_personas(self):
        lst = list_personas()
        self.assertGreaterEqual(len(lst), 5)
        ids = [x["id"] for x in lst]
        self.assertIn("general", ids)
        self.assertIn("tech_founder", ids)
        self.assertIn("finance_investor", ids)


if __name__ == "__main__":
    unittest.main()
