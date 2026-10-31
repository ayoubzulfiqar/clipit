import json
import logging
import unittest
from unittest.mock import patch

from clipping.logger import JsonFormatter, StandardFormatter, current_job_id, get_logger


class TestLogger(unittest.TestCase):
    def test_standard_formatter_with_and_without_job_id(self):
        formatter = StandardFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg="Pipeline step completed",
            args=(),
            exc_info=None,
        )

        # Without job_id
        current_job_id.set(None)
        output = formatter.format(record)
        self.assertIn("ℹ️ [INFO]", output)
        self.assertIn("Pipeline step completed", output)

        # With job_id in contextvar
        current_job_id.set("job_abc_123")
        output_with_job = formatter.format(record)
        self.assertIn("[job_abc_123]", output_with_job)
        self.assertIn("Pipeline step completed", output_with_job)

    def test_json_formatter(self):
        formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%SZ")
        record = logging.LogRecord(
            name="test_json",
            level=logging.WARNING,
            pathname=__file__,
            lineno=25,
            msg="Pexels rate limit near threshold",
            args=(),
            exc_info=None,
        )

        current_job_id.set("job_xyz_789")
        formatted_str = formatter.format(record)
        parsed = json.loads(formatted_str)

        self.assertEqual(parsed["level"], "WARNING")
        self.assertEqual(parsed["logger"], "test_json")
        self.assertEqual(parsed["message"], "Pexels rate limit near threshold")
        self.assertEqual(parsed["job_id"], "job_xyz_789")
        self.assertIn("timestamp", parsed)

    def test_get_logger_factory(self):
        logger = get_logger("clipit.test_module")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "clipit.test_module")


if __name__ == "__main__":
    unittest.main()
