"""
clipping.webhook — Webhook Notification Dispatcher & Signature Verification.

Allows external platforms (Make, Zapier, custom backend services) to receive
real-time HMAC-SHA256 signed event notifications when jobs complete, fail, or progress.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional
import urllib.request
import urllib.error

from clipping.logger import get_logger

logger = get_logger("clipping.webhook")


def compute_signature(payload_bytes: bytes, secret: str) -> str:
    """
    Compute an HMAC-SHA256 signature over raw payload bytes.
    """
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


def verify_webhook_signature(
    payload_bytes: bytes,
    signature_header: str,
    secret: str,
) -> bool:
    """
    Verify an incoming webhook HMAC-SHA256 signature.
    Matches formats like 'sha256=<hex>' or raw '<hex>'.
    """
    if not signature_header or not secret:
        return False

    raw_sig = signature_header.replace("sha256=", "").strip()
    expected = compute_signature(payload_bytes, secret)
    return hmac.compare_digest(raw_sig, expected)


def dispatch_webhook(
    url: str,
    event: str,
    data: Dict[str, Any],
    secret: Optional[str] = None,
    timeout: float = 5.0,
) -> bool:
    """
    Dispatch an HTTP POST webhook notification to the target URL.

    Args:
        url: Destination HTTPS/HTTP endpoint.
        event: Event name (e.g. 'job.completed', 'job.failed').
        data: Arbitrary payload dictionary.
        secret: Optional secret key for HMAC-SHA256 signature header.
        timeout: Network timeout in seconds.

    Returns:
        True if dispatched and status code is 2xx, False otherwise.
    """
    if not url:
        return False

    envelope = {
        "event": event,
        "timestamp": int(time.time()),
        "data": data,
    }
    payload_bytes = json.dumps(envelope, ensure_ascii=False).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Clipit-Webhook/1.15.0",
    }
    if secret:
        sig = compute_signature(payload_bytes, secret)
        headers["X-Clipit-Signature"] = f"sha256={sig}"

    req = urllib.request.Request(url, data=payload_bytes, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.getcode()
            if 200 <= status < 300:
                logger.info("Webhook '%s' delivered to %s (status: %d)", event, url, status)
                return True
            else:
                logger.warning("Webhook delivery returned status %d from %s", status, url)
                return False
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, Exception) as exc:
        logger.warning("Webhook dispatch failed to %s: %s", url, exc)
        return False
