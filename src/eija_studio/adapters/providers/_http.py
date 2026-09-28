"""One bounded HTTPS POST for the API providers (OpenRouter, Anthropic): no redirect, no retry, size cap.

Establishes: the key travels only in the request header, the response is read under a byte cap, HTTP and
transport failures map to stable codes whose text never includes the response body, and there is exactly one
attempt. Does not interpret the payload; each provider validates its own envelope.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

import httpx

from eija_studio.domain.models import DomainError

from ._common import MAX_ENVELOPE_BYTES, status_failure_code

_INVALID_ENVELOPE = "Provider response envelope was invalid"


def _read_capped(response: httpx.Response) -> bytes:
    chunks: list[bytes] = []
    size = 0
    for chunk in response.iter_bytes():
        size += len(chunk)
        if size > MAX_ENVELOPE_BYTES:
            raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider envelope exceeds the size limit")
        chunks.append(chunk)
    return b"".join(chunks)


def post_json(url: str, body: Mapping[str, Any], headers: Mapping[str, str], *, transport: httpx.BaseTransport | None,
              timeout: float, label: str) -> dict[str, Any]:
    """POST ``body`` once and return the JSON object reply, or raise a sanitised DomainError."""
    try:
        with (httpx.Client(timeout=timeout, transport=transport, follow_redirects=False, trust_env=False) as client,
              client.stream("POST", url, json=body, headers=dict(headers)) as response):
            if response.status_code != 200:
                code = status_failure_code(response.status_code, "PROVIDER_HTTP_ERROR")
                raise DomainError(code, f"{label} returned HTTP {response.status_code}; no automatic retry or fallback")
            raw = _read_capped(response)
    except (httpx.HTTPError, TimeoutError):
        raise DomainError("PROVIDER_TRANSPORT", "Provider request failed or timed out; it may still have been billed") from None
    try:
        payload = json.loads(raw)
    except ValueError:
        raise DomainError("PROVIDER_OUTPUT_INVALID", _INVALID_ENVELOPE) from None
    if not isinstance(payload, dict):
        raise DomainError("PROVIDER_OUTPUT_INVALID", _INVALID_ENVELOPE)
    return payload
