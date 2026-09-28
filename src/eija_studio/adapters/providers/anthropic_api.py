"""Optional Anthropic Messages API provider: a key from the environment, held in memory only.

Use the Claude Code adapter for a subscription login; this one is the metered-API path. Raw HTTP through httpx
(already a dependency, shared with OpenRouter via ``_http``) rather than the official ``anthropic`` SDK: one
bounded, mockable, header-controlled transport and no second HTTP stack; see the register row in docs/oss/REGISTER.md.
A model must be named explicitly (``--model`` / EIJA_MODEL); there is no default.
Contract-tested with a mock transport only; NOT live-verified (no API key was available), so the structured
output request shape is an assumption to re-check with ``scripts/live_provider_smoke.py``.
"""
from __future__ import annotations
import json
import os
from typing import Any
from eija_studio.application.ports import ProviderResult
from eija_studio.domain.models import DomainError, Workflow, canonical
from ._common import SYSTEM, parse_proposal, proposal_schema, safe_usage, validate_model_name
from ._http import post_json_bounded

ENDPOINT = "https://api.anthropic.com/v1/messages"
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
        self.model = validate_model_name(model)  # no default: a metered call never silently picks a model (and its price)
        self._key, self.transport, self.timeout = key or os.getenv("ANTHROPIC_API_KEY"), transport, timeout

    def doctor(self) -> dict:
        return {"provider": self.name, "ready": bool(self._key and self.model), "model": self.model, "key_present": bool(self._key), "live_test": "NOT_RUN"}

    def propose(self, request: str, model: Workflow) -> ProviderResult:
        if not self._key or not self.model:
            raise DomainError("PROVIDER_NOT_CONFIGURED", "Set ANTHROPIC_API_KEY and EIJA_MODEL before starting (the key is never stored)")
        body = {"model": self.model, "max_tokens": 8000, "system": SYSTEM, "output_config": {"effort": "low",
                "format": {"type": "json_schema", "schema": _relax(proposal_schema())}},
                "messages": [{"role": "user", "content": "INPUT DATA:\n" + canonical({"request": request, "baseline": model.model_dump(mode="json")})}]}
        raw = post_json_bounded(ENDPOINT, body=body, headers={"x-api-key": self._key, "anthropic-version": "2023-06-01"}, label="Anthropic API",
                                timeout=self.timeout, transport=self.transport)
        try:
            payload = json.loads(raw)
            if payload["stop_reason"] != "end_turn":
                raise DomainError("PROVIDER_INCOMPLETE", "Truncated, refused or tool-request output is not accepted")
            texts = [b["text"] for b in payload["content"] if b["type"] == "text"]
            if len(texts) != 1 or any(b["type"] == "tool_use" for b in payload["content"]):
                raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid")
            usage = safe_usage(payload.get("usage"), frozenset({"input_tokens", "output_tokens"}))
            return ProviderResult(parse_proposal(texts[0]), self.name, str(payload.get("model", self.model)), usage, True)
        except DomainError:
            raise
        except (KeyError, IndexError, TypeError, ValueError, AttributeError):
            raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid") from None
