"""OpenRouter over HTTPS with a key from the environment. Key is held in memory only, never persisted."""
from __future__ import annotations

import os
from typing import Any

import httpx

from eija_studio.application.ports import ProviderResult
from eija_studio.domain.models import DomainError, Workflow, canonical

from ._common import SYSTEM, parse_proposal, proposal_schema, safe_usage
from ._http import post_json

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
USAGE_FIELDS = frozenset({"prompt_tokens", "completion_tokens", "total_tokens", "cost"})


def _reply_content(payload: dict[str, Any]) -> str:
    """The single completed assistant message text, or a sanitised DomainError. No tool calls are accepted."""
    try:
        choice = payload["choices"][0]
        if choice.get("finish_reason") != "stop" or choice["message"].get("tool_calls"):
            raise DomainError("PROVIDER_INCOMPLETE", "Truncated/tool-request output is not accepted")
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError, AttributeError):
        raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid") from None
    return content if isinstance(content, str) else ""


def _reply_usage(payload: dict[str, Any]) -> dict[str, Any]:
    """Numeric accounting fields only. A ``usage`` that is present but not an object marks a malformed envelope."""
    usage = payload.get("usage", {})
    if not isinstance(usage, dict):
        raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid")
    return safe_usage(usage, USAGE_FIELDS)


class OpenRouterProvider:
    name, networked = "openrouter", True

    def __init__(self, model: str, key: str | None = None, *, transport: httpx.BaseTransport | None = None, timeout: float = 60):
        self.model, self._key, self.transport, self.timeout = model, key or os.getenv("OPENROUTER_API_KEY"), transport, timeout

    def doctor(self) -> dict:
        return {"provider": self.name, "ready": bool(self._key and self.model), "model": self.model,
                "key_present": bool(self._key), "live_test": "NOT_RUN"}

    def _body(self, request: str, model: Workflow) -> dict[str, Any]:
        user = canonical({"request": request, "baseline": model.model_dump(mode="json")})
        return {"model": self.model, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                "max_tokens": 1600, "stream": False, "provider": {"require_parameters": True},
                "response_format": {"type": "json_schema", "json_schema": {"name": "eija_proposal", "strict": True,
                                                                            "schema": proposal_schema()}}}

    def propose(self, request: str, model: Workflow) -> ProviderResult:
        if not self._key or not self.model:
            raise DomainError("PROVIDER_NOT_CONFIGURED", "Set OPENROUTER_API_KEY and EIJA_MODEL before starting")
        headers = {"Authorization": "Bearer " + self._key, "X-OpenRouter-Title": "EIJA Studio"}
        payload = post_json(ENDPOINT, self._body(request, model), headers, transport=self.transport, timeout=self.timeout,
                            label="OpenRouter")
        proposal = parse_proposal(_reply_content(payload))
        return ProviderResult(proposal, self.name, str(payload.get("model", self.model)), _reply_usage(payload), True)
