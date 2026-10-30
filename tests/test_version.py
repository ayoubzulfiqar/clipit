import json
import re
import unittest
from pathlib import Path

import clipping


class TestVersionConsistency(unittest.TestCase):
    def test_clipping_version_defined(self):
        """Test that clipping package defines __version__ as 1.15.0."""
        self.assertTrue(hasattr(clipping, "__version__"))
        self.assertEqual(clipping.__version__, "1.15.0")

    def test_pyproject_version_matches(self):
        """Test that pyproject.toml matches clipping.__version__."""
        pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        content = pyproject_path.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        self.assertIsNotNone(match, "version not found in pyproject.toml")
        self.assertEqual(match.group(1), clipping.__version__)

    def test_package_json_version_matches(self):
        """Test that web/dashboard/package.json matches clipping.__version__."""
        pkg_json_path = Path(__file__).resolve().parent.parent / "web" / "dashboard" / "package.json"
        with open(pkg_json_path, "r", encoding="utf-8") as f:
            pkg = json.load(f)
        self.assertEqual(pkg.get("version"), clipping.__version__)


if __name__ == "__main__":
    unittest.main()
