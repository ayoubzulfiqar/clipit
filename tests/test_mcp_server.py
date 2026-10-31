import json
import unittest

from clipping.mcp_server import process_jsonrpc_request, MCP_TOOLS


class TestMcpServer(unittest.TestCase):
    def test_initialize_handshake(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }
        resp = process_jsonrpc_request(req)
        self.assertEqual(resp["id"], 1)
        self.assertEqual(resp["result"]["serverInfo"]["name"], "clipit-mcp-server")

    def test_tools_list(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        resp = process_jsonrpc_request(req)
        self.assertEqual(resp["id"], 2)
        tools = resp["result"]["tools"]
        self.assertGreaterEqual(len(tools), 5)
        names = [t["name"] for t in tools]
        self.assertIn("clipit_get_health", names)
        self.assertIn("clipit_list_presets", names)
        self.assertIn("clipit_create_job", names)
        self.assertIn("clipit_schedule_calendar", names)

    def test_tools_call_health(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "clipit_get_health",
                "arguments": {},
            },
        }
        resp = process_jsonrpc_request(req)
        self.assertEqual(resp["id"], 3)
        content = resp["result"]["content"]
        self.assertEqual(len(content), 1)
        data = json.loads(content[0]["text"])
        self.assertEqual(data["status"], "ok")
        self.assertIn("hardware", data)

    def test_tools_call_schedule_calendar(self):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "clipit_schedule_calendar",
                "arguments": {
                    "clips": [
                        {"rank": 1, "title_inggris": "Hook fast", "output_video": "clip_1.mp4"}
                    ],
                    "platforms": ["tiktok", "shorts"],
                },
            },
        }
        resp = process_jsonrpc_request(req)
        self.assertEqual(resp["id"], 4)
        data = json.loads(resp["result"]["content"][0]["text"])
        self.assertEqual(data["total_posts"], 2)


if __name__ == "__main__":
    unittest.main()
