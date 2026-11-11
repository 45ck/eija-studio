"""Optional OpenAI Responses API provider: a key from the environment, held in memory only.

Use the Codex adapter for a ChatGPT sign-in; this one is the metered-API path for the OpenAI developer platform.
Raw HTTP through httpx, like the Anthropic and OpenRouter adapters (ADR-0021): thin, mockable, header-controlled.
Structured Outputs in strict mode constrain the reply to the proposal schema; the reply is still validated by
``Proposal`` and anything else fails closed. ``store`` is false so the request is not kept for later retrieval.
Contract-tested with a mock transport only; NOT live-verified until ``scripts/live_provider_smoke.py`` records a run.
No default model is baked in: a model id goes stale, so the operator must name one (``--model`` / ``EIJA_MODEL``).
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

ENDPOINT = "https://api.openai.com/v1/responses"
USAGE_FIELDS = frozenset({"input_tokens", "output_tokens", "total_tokens"})


def _message_parts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """The content parts of a completed reply's messages. Reasoning items are skipped; any other item (a tool call) is rejected."""
    if payload["status"] != "completed":
        raise DomainError("PROVIDER_INCOMPLETE", "Truncated, refused or tool-request output is not accepted")
    items = [item for item in payload["output"] if item["type"] != "reasoning"]
    if any(item["type"] != "message" for item in items):
        raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid")
    return [part for item in items for part in item["content"]]


def _reply_text(payload: dict[str, Any]) -> str:
    """The single output text of a completed reply; refusals, truncation and tool calls are rejected."""
    try:
        parts = _message_parts(payload)
        if any(part["type"] == "refusal" for part in parts):
            raise DomainError("PROVIDER_INCOMPLETE", "Truncated, refused or tool-request output is not accepted")
        texts = [part["text"] for part in parts if part["type"] == "output_text"]
    except (KeyError, IndexError, TypeError, AttributeError):
        raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid") from None
    if len(texts) != 1:
        raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid")
    return str(texts[0])


class OpenAiApiProvider:
    name, networked = "openai", True

    def __init__(self, model: str = "", key: str | None = None, *, transport: httpx.BaseTransport | None = None, timeout: float = 120,
                 pack: Pack | None = None):
        self.model = validate_model_name(model)
        self.pack = pack if pack is not None else default_pack()
        self._key, self.transport, self.timeout = key or os.getenv("OPENAI_API_KEY"), transport, timeout

    def doctor(self) -> dict:
        return {"provider": self.name, "ready": bool(self._key and self.model), "model": self.model or "(none: pass --model)",
                "key_present": bool(self._key), "live_test": "NOT_RUN"}

    def _body(self, request: str, model: Workflow) -> dict[str, Any]:
        data = canonical({"request": request, "baseline": model.model_dump(mode="json")})
        return {"model": self.model, "instructions": system_prompt(model, self.pack), "input": "INPUT DATA:\n" + data,
                "max_output_tokens": 8000, "store": False,
                "text": {"format": {"type": "json_schema", "name": "eija_proposal", "strict": True, "schema": proposal_schema()}}}

    def propose(self, request: str, model: Workflow) -> ProviderResult:
        if not self._key or not self.model:
            raise DomainError("PROVIDER_NOT_CONFIGURED", "Set OPENAI_API_KEY and name a model (--model / EIJA_MODEL); neither is stored")
        headers = {"Authorization": "Bearer " + self._key}
        payload = post_json(ENDPOINT, self._body(request, model), headers, transport=self.transport, timeout=self.timeout,
                            label="OpenAI API")
        proposal = parse_proposal(_reply_text(payload), model, self.pack)
        return ProviderResult(proposal, self.name, str(payload.get("model", self.model)), safe_usage(payload.get("usage"), USAGE_FIELDS), True)
