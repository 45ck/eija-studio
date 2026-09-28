"""One bounded HTTPS POST for the metered API providers. Establishes transport limits, not correctness.

No redirects, no proxy or netrc from the environment, the response size capped while it streams, one attempt
only, and a stable ``DomainError`` for every failure. The response body of a failed request is never read.
"""
from __future__ import annotations
from typing import Any, Mapping
import httpx
from eija_studio.domain.models import DomainError
from ._common import MAX_ENVELOPE_BYTES


def post_json_bounded(url: str, *, body: Mapping[str, Any], headers: Mapping[str, str], label: str, timeout: float, transport: Any = None,
                      max_bytes: int = MAX_ENVELOPE_BYTES) -> bytes:
    """POST ``body`` as JSON and return the raw response bytes (at most ``max_bytes``) of a 200 reply."""
    try:
        with httpx.Client(timeout=timeout, transport=transport, follow_redirects=False, trust_env=False) as client:
            with client.stream("POST", url, json=body, headers=dict(headers)) as response:
                if response.status_code != 200:
                    code = "PROVIDER_AUTH" if response.status_code in (401, 403) else "PROVIDER_RATE_LIMIT" if response.status_code == 429 else "PROVIDER_HTTP_ERROR"
                    raise DomainError(code, f"{label} returned HTTP {response.status_code}; no automatic retry or fallback")
                chunks, size = [], 0
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    if size > max_bytes:
                        raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider envelope exceeds the size limit")
                    chunks.append(chunk)
                return b"".join(chunks)
    except (httpx.HTTPError, TimeoutError):
        raise DomainError("PROVIDER_TRANSPORT", "Provider request failed or timed out; it may still have been billed") from None
