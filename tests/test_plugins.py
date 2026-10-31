import os
import tempfile
import unittest

from clipping.plugins import (
    HOOK_CLIPS_SCORED,
    HOOK_DOWNLOAD_COMPLETE,
    HOOK_RENDER_COMPLETE,
    clear_hooks,
    discover_plugins,
    hook,
    register_hook,
    trigger_hook,
    unregister_hook,
)


class TestPlugins(unittest.TestCase):
    def setUp(self):
        clear_hooks()

    def tearDown(self):
        clear_hooks()

    def test_register_and_trigger_hook(self):
        calls = []

        def my_handler(payload):
            calls.append(payload.get("video_path"))
            return {"tagged": True}

        register_hook(HOOK_DOWNLOAD_COMPLETE, my_handler)

        result = trigger_hook(HOOK_DOWNLOAD_COMPLETE, {"video_path": "/tmp/test.mp4"})
        self.assertEqual(calls, ["/tmp/test.mp4"])
        self.assertTrue(result.get("tagged"))

    def test_hook_priority_ordering(self):
        order = []

        register_hook(HOOK_RENDER_COMPLETE, lambda p: order.append("second"), priority=20)
        register_hook(HOOK_RENDER_COMPLETE, lambda p: order.append("first"), priority=5)

        trigger_hook(HOOK_RENDER_COMPLETE, {})
        self.assertEqual(order, ["first", "second"])

    def test_decorator_registration(self):
        called = []

        @hook(HOOK_CLIPS_SCORED, priority=1)
        def score_filter(p):
            called.append(p.get("count", 0))

        trigger_hook(HOOK_CLIPS_SCORED, {"count": 4})
        self.assertEqual(called, [4])

    def test_unregister_hook(self):
        fn = lambda p: p
        register_hook(HOOK_DOWNLOAD_COMPLETE, fn)
        removed = unregister_hook(HOOK_DOWNLOAD_COMPLETE, fn)
        self.assertTrue(removed)

        not_removed = unregister_hook(HOOK_DOWNLOAD_COMPLETE, fn)
        self.assertFalse(not_removed)

    def test_plugin_error_isolation(self):
        def buggy_handler(payload):
            raise RuntimeError("Intentional error in plugin")

        register_hook(HOOK_RENDER_COMPLETE, buggy_handler)

        # By default fail_fast=False, so error is swallowed and logged
        payload = {"status": "ok"}
        out = trigger_hook(HOOK_RENDER_COMPLETE, payload, fail_fast=False)
        self.assertEqual(out, {"status": "ok"})

        # With fail_fast=True, it re-raises
        with self.assertRaises(RuntimeError):
            trigger_hook(HOOK_RENDER_COMPLETE, payload, fail_fast=True)

    def test_discover_plugins_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_code = """
from clipping.plugins import hook, HOOK_CLIPS_SCORED

@hook(HOOK_CLIPS_SCORED)
def sample_plugin(payload):
    payload["plugin_loaded"] = True
"""
            plugin_path = os.path.join(tmpdir, "my_plugin.py")
            with open(plugin_path, "w") as f:
                f.write(plugin_code)

            count = discover_plugins(tmpdir)
            self.assertEqual(count, 1)

            res = trigger_hook(HOOK_CLIPS_SCORED, {})
            self.assertTrue(res.get("plugin_loaded"))


if __name__ == "__main__":
    unittest.main()
