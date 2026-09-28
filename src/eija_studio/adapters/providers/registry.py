"""Provider names and construction. The composition root (bootstrap.py) is the only caller."""
from __future__ import annotations
from typing import Callable
from eija_studio.application.ports import ProposalProvider
from .anthropic_api import AnthropicApiProvider
from .claude_code import ClaudeCodeProvider
from .codex import CodexProvider
from .gemini import GeminiCliProvider
from .offline import OfflineProvider
from .opencode import OpenCodeProvider
from .openrouter import OpenRouterProvider

KEYED_PROVIDERS = frozenset({"openrouter", "anthropic"})  # providers that take a key held in memory only
_FACTORIES: dict[str, Callable[[str, str | None], ProposalProvider]] = {
    "offline": lambda model, key: OfflineProvider(),
    "openrouter": OpenRouterProvider,
    "anthropic": AnthropicApiProvider,
    "codex": lambda model, key: CodexProvider(model),
    "claude": lambda model, key: ClaudeCodeProvider(model),
    "opencode": lambda model, key: OpenCodeProvider(model),
    "gemini": lambda model, key: GeminiCliProvider(model),
}
PROVIDER_NAMES = tuple(_FACTORIES)


def create_provider(name: str, model: str = "", key: str | None = None) -> ProposalProvider:
    if name not in _FACTORIES:
        raise ValueError("Unknown provider")
    return _FACTORIES[name](model, key)
