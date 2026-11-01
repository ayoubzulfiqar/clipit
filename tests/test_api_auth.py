import os
import unittest
from unittest.mock import AsyncMock, patch

try:
    from web.api.app import api_key_auth_middleware
    FASTAPI_AVAILABLE = True
except (ImportError, RuntimeError):
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI is not installed in current environment")
class TestApiAuth(unittest.IsolatedAsyncioTestCase):
    async def test_auth_bypassed_when_no_api_key_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            mock_request = AsyncMock()
            mock_call_next = AsyncMock(return_value="OK_NEXT")

            res = await api_key_auth_middleware(mock_request, mock_call_next)
            self.assertEqual(res, "OK_NEXT")
            mock_call_next.assert_called_once_with(mock_request)

    async def test_auth_allows_public_endpoints(self):
        with patch.dict(os.environ, {"CLIPIT_API_KEY": "secret123"}):
            for path in ["/api/health", "/api/health/ready", "/docs", "/openapi.json"]:
                mock_request = AsyncMock()
                mock_request.url.path = path
                mock_call_next = AsyncMock(return_value="PUBLIC_OK")

                res = await api_key_auth_middleware(mock_request, mock_call_next)
                self.assertEqual(res, "PUBLIC_OK")
                mock_call_next.assert_called_once()

    async def test_auth_rejects_missing_key_on_protected_endpoints(self):
        with patch.dict(os.environ, {"CLIPIT_API_KEY": "secret123"}):
            mock_request = AsyncMock()
            mock_request.url.path = "/api/jobs"
            mock_request.headers = {}
            mock_call_next = AsyncMock()

            res = await api_key_auth_middleware(mock_request, mock_call_next)
            self.assertEqual(res.status_code, 401)
            mock_call_next.assert_not_called()

    async def test_auth_accepts_valid_header_key(self):
        with patch.dict(os.environ, {"CLIPIT_API_KEY": "secret123"}):
            mock_request = AsyncMock()
            mock_request.url.path = "/api/jobs"
            mock_request.headers = {"X-API-Key": "secret123"}
            mock_call_next = AsyncMock(return_value="AUTH_OK")

            res = await api_key_auth_middleware(mock_request, mock_call_next)
            self.assertEqual(res, "AUTH_OK")
            mock_call_next.assert_called_once()


if __name__ == "__main__":
    unittest.main()
