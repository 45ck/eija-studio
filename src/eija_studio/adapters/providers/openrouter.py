"""OpenRouter over HTTPS with a key from the environment. Key is held in memory only, never persisted."""
from __future__ import annotations
import json, os
from math import isfinite
import httpx
from eija_studio.domain.models import Proposal, Workflow, DomainError, canonical
from eija_studio.application.ports import ProviderResult
from ._common import SYSTEM, parse_proposal


class OpenRouterProvider:
    name, networked = "openrouter", True
    def __init__(self, model: str, key: str | None = None, *, transport=None, timeout: float = 60):
        self.model, self._key, self.transport, self.timeout = model, key or os.getenv("OPENROUTER_API_KEY"), transport, timeout
    def doctor(self) -> dict:
        return {"provider": self.name, "ready": bool(self._key and self.model), "model": self.model,
                "key_present": bool(self._key), "live_test": "NOT_RUN"}
    def propose(self, request: str, model: Workflow) -> ProviderResult:
        if not self._key or not self.model:
            raise DomainError("PROVIDER_NOT_CONFIGURED", "Set OPENROUTER_API_KEY and EIJA_MODEL before starting")
        body = {"model": self.model, "messages": [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": canonical({"request": request, "baseline": model.model_dump(mode="json")})}],
                "max_tokens": 1600, "stream": False, "provider": {"require_parameters": True},
                "response_format": {"type": "json_schema", "json_schema": {"name": "eija_proposal", "strict": True,
                    "schema": Proposal.model_json_schema()}}}
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport, follow_redirects=False, trust_env=False) as client:
                with client.stream("POST", "https://openrouter.ai/api/v1/chat/completions", json=body,
                    headers={"Authorization": "Bearer " + self._key, "X-OpenRouter-Title": "EIJA Studio"}) as response:
                    if response.status_code != 200:
                        code = "PROVIDER_AUTH" if response.status_code in (401, 403) else "PROVIDER_RATE_LIMIT" if response.status_code == 429 else "PROVIDER_HTTP_ERROR"
                        raise DomainError(code, f"OpenRouter returned HTTP {response.status_code}; no automatic retry or fallback")
                    chunks, size = [], 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > 262144:
                            raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider envelope exceeds the size limit")
                        chunks.append(chunk)
            payload = json.loads(b"".join(chunks))
            choice = payload["choices"][0]
            if choice.get("finish_reason") != "stop" or choice["message"].get("tool_calls"):
                raise DomainError("PROVIDER_INCOMPLETE", "Truncated/tool-request output is not accepted")
            proposal = parse_proposal(choice["message"]["content"])
            usage = payload.get("usage", {})
            # Preserve only numeric accounting fields, never raw provider debug fields.
            safe_usage = {k: v for k, v in usage.items() if k in {"prompt_tokens", "completion_tokens", "total_tokens", "cost"} and type(v) in (int, float) and isfinite(v)}
            return ProviderResult(proposal, self.name, str(payload.get("model", self.model)), safe_usage, True)
        except (httpx.HTTPError, TimeoutError):
            raise DomainError("PROVIDER_TRANSPORT", "Provider request failed or timed out; it may still have been billed") from None
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as exc:
            if isinstance(exc, DomainError):
                raise
            raise DomainError("PROVIDER_OUTPUT_INVALID", "Provider response envelope was invalid") from None
