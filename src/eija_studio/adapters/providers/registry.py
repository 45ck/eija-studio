"""Provider names and construction. The composition root (bootstrap.py) is the only caller."""
from __future__ import annotations
from typing import Callable
from eija_studio.application.ports import ProposalProvider
from eija_studio.domain.pack import Pack
from .anthropic_api import AnthropicApiProvider
from .claude_code import ClaudeCodeProvider
from .codex import CodexProvider
from .gemini import GeminiCliProvider
from .offline import OfflineProvider
from .opencode import OpenCodeProvider
from .openrouter import OpenRouterProvider

KEYED_PROVIDERS = frozenset({"openrouter", "anthropic"})  # providers that take a key held in memory only
_FACTORIES: dict[str, Callable[[str, str | None, Pack | None], ProposalProvider]] = {
    "offline": lambda model, key, pack: OfflineProvider(pack),
    "openrouter": lambda model, key, pack: OpenRouterProvider(model, key, pack=pack),
    "anthropic": lambda model, key, pack: AnthropicApiProvider(model, key, pack=pack),
    "codex": lambda model, key, pack: CodexProvider(model, pack=pack),
    "claude": lambda model, key, pack: ClaudeCodeProvider(model, pack=pack),
    "opencode": lambda model, key, pack: OpenCodeProvider(model, pack=pack),
    "gemini": lambda model, key, pack: GeminiCliProvider(model, pack=pack),
}
PROVIDER_NAMES = tuple(_FACTORIES)


def create_provider(name: str, model: str = "", key: str | None = None, pack: Pack | None = None) -> ProposalProvider:
    if name not in _FACTORIES:
        raise ValueError("Unknown provider")
    return _FACTORIES[name](model, key, pack)
