"""Optional Anthropic Messages API provider: a key from the environment, held in memory only.

Use the Claude Code adapter for a subscription login; this one is the metered-API path. Raw HTTP through httpx
(already a dependency) because the task and ADR-0021 ask for a thin, mockable, header-controlled transport.
Contract-tested with a mock transport only; NOT live-verified (no API key was available), so the structured
output request shape is an assumption to re-check with ``scripts/live_provider_smoke.py``. No default model is
baked in: a model id goes stale, so the operator must name one (``--model`` / ``EIJA_MODEL``).
"""
from __future__ import annotations

import os
from typing import Any

import httpx

from eija_studio.application.ports import ProviderResult
from eija_studio.domain.models import DomainError, Workflow, canonical
from eija_studio.domain.pack import Pack, default_pack

from ._common import parse_proposal, proposal_schema, safe_usage, system_prompt, validate_model_name
from ._http import post_json

ENDPOINT = "https://api.anthropic.com/v1/messages"
USAGE_FIELDS = frozenset({"input_tokens", "output_tokens"})
_UNSUPPORTED = frozenset({"minLength", "maxLength", "minItems", "maxItems", "minimum", "maximum", "pattern"})


def _relax(node: Any) -> Any:
    """Drop JSON Schema keywords structured outputs may reject. The reply is still validated by Proposal."""
    if isinstance(node, dict):
        return {k: ({n: _relax(sub) for n, sub in v.items()} if k in ("properties", "$defs") else _relax(v))
                for k, v in node.items() if k not in _UNSUPPORTED}
    if isinstance(node, list):
        return [_relax(v) for v in node]
    return node


def _reply_text(payload: dict[str, Any]) -> str:
    """The single text block of a completed (``end_turn``) reply; refusals, truncation and tool use are rejected."""
    try:
        if payload["stop_reason"] != "end_turn":
            raise DomainError("PROVIDER_INCOMPLETE", "Truncated, refused or tool-request output is not accepted")
        blocks = payload["content"]
        texts = [b["text"] for b in blocks if b["type"] == "text"]
        if len(texts) != 1 or any(b["type"] == "tool_use" for b in blocks):
            raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid")
    except (KeyError, IndexError, TypeError, AttributeError):
        raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid") from None
    return str(texts[0])


class AnthropicApiProvider:
    name, networked = "anthropic", True

    def __init__(self, model: str = "", key: str | None = None, *, transport: httpx.BaseTransport | None = None, timeout: float = 120,
                 pack: Pack | None = None):
        self.model = validate_model_name(model)
        self.pack = pack if pack is not None else default_pack()
        self._key, self.transport, self.timeout = key or os.getenv("ANTHROPIC_API_KEY"), transport, timeout

    def doctor(self) -> dict:
        return {"provider": self.name, "ready": bool(self._key and self.model), "model": self.model or "(none: pass --model)",
                "key_present": bool(self._key), "live_test": "NOT_RUN"}

    def _body(self, request: str, model: Workflow) -> dict[str, Any]:
        data = canonical({"request": request, "baseline": model.model_dump(mode="json")})
        return {"model": self.model, "max_tokens": 8000, "system": system_prompt(model, self.pack),
                "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": _relax(proposal_schema())}},
                "messages": [{"role": "user", "content": "INPUT DATA:\n" + data}]}

    def propose(self, request: str, model: Workflow) -> ProviderResult:
        if not self._key or not self.model:
            raise DomainError("PROVIDER_NOT_CONFIGURED", "Set ANTHROPIC_API_KEY and name a model (--model / EIJA_MODEL); neither is stored")
        headers = {"x-api-key": self._key, "anthropic-version": "2023-06-01"}
        payload = post_json(ENDPOINT, self._body(request, model), headers, transport=self.transport, timeout=self.timeout,
                            label="Anthropic API")
        proposal = parse_proposal(_reply_text(payload), model, self.pack)
        return ProviderResult(proposal, self.name, str(payload.get("model", self.model)), safe_usage(payload.get("usage"), USAGE_FIELDS), True)
