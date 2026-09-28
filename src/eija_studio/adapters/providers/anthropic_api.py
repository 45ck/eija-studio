"""Optional Anthropic Messages API provider: a key from the environment, held in memory only.

Use the Claude Code adapter for a subscription login; this one is the metered-API path. Raw HTTP through httpx
(already a dependency) because the task and ADR-0021 ask for a thin, mockable, header-controlled transport.
Contract-tested with a mock transport only; NOT live-verified (no API key was available), so the structured
output request shape is an assumption to re-check with ``scripts/live_provider_smoke.py``.
"""
from __future__ import annotations
import json
import os
from typing import Any
import httpx
from eija_studio.application.ports import ProviderResult
from eija_studio.domain.models import DomainError, Workflow, canonical
from ._common import MAX_ENVELOPE_BYTES, SYSTEM, parse_proposal, proposal_schema, safe_usage, validate_model_name

ENDPOINT = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-opus-5-5"
_UNSUPPORTED = frozenset({"minLength", "maxLength", "minItems", "maxItems", "minimum", "maximum", "pattern"})


def _relax(node: Any) -> Any:
    """Drop JSON Schema keywords structured outputs may reject. The reply is still validated by Proposal."""
    if isinstance(node, dict):
        return {k: ({n: _relax(sub) for n, sub in v.items()} if k in ("properties", "$defs") else _relax(v))
                for k, v in node.items() if k not in _UNSUPPORTED}
    if isinstance(node, list):
        return [_relax(v) for v in node]
    return node


class AnthropicApiProvider:
    name, networked = "anthropic", True

    def __init__(self, model: str = "", key: str | None = None, *, transport=None, timeout: float = 120):
        self.model = validate_model_name(model) or DEFAULT_MODEL
        self._key, self.transport, self.timeout = key or os.getenv("ANTHROPIC_API_KEY"), transport, timeout

    def doctor(self) -> dict:
        return {"provider": self.name, "ready": bool(self._key), "model": self.model, "key_present": bool(self._key), "live_test": "NOT_RUN"}

    def propose(self, request: str, model: Workflow) -> ProviderResult:
        if not self._key:
            raise DomainError("PROVIDER_NOT_CONFIGURED", "Set ANTHROPIC_API_KEY before starting (it is never stored)")
        body = {"model": self.model, "max_tokens": 8000, "system": SYSTEM, "output_config": {"effort": "low",
                "format": {"type": "json_schema", "schema": _relax(proposal_schema())}},
                "messages": [{"role": "user", "content": "INPUT DATA:\n" + canonical({"request": request, "baseline": model.model_dump(mode="json")})}]}
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport, follow_redirects=False, trust_env=False) as client:
                with client.stream("POST", ENDPOINT, json=body, headers={"x-api-key": self._key, "anthropic-version": "2023-06-01"}) as response:
                    if response.status_code != 200:
                        code = "PROVIDER_AUTH" if response.status_code in (401, 403) else "PROVIDER_RATE_LIMIT" if response.status_code == 429 else "PROVIDER_HTTP_ERROR"
                        raise DomainError(code, f"Anthropic API returned HTTP {response.status_code}; no automatic retry or fallback")
                    chunks, size = [], 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > MAX_ENVELOPE_BYTES:
                            raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider envelope exceeds the size limit")
                        chunks.append(chunk)
            payload = json.loads(b"".join(chunks))
            if payload["stop_reason"] != "end_turn":
                raise DomainError("PROVIDER_INCOMPLETE", "Truncated, refused or tool-request output is not accepted")
            texts = [b["text"] for b in payload["content"] if b["type"] == "text"]
            if len(texts) != 1 or any(b["type"] == "tool_use" for b in payload["content"]):
                raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid")
            usage = safe_usage(payload.get("usage"), frozenset({"input_tokens", "output_tokens"}))
            return ProviderResult(parse_proposal(texts[0]), self.name, str(payload.get("model", self.model)), usage, True)
        except (httpx.HTTPError, TimeoutError):
            raise DomainError("PROVIDER_TRANSPORT", "Provider request failed or timed out; it may still have been billed") from None
        except DomainError:
            raise
        except (KeyError, IndexError, TypeError, ValueError, AttributeError):
            raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid") from None
