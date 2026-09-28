"""Untrusted proposal adapters. No implementation, evidence or governance tools are exposed.

Import compatibility: ``from eija_studio.adapters.providers import OfflineProvider, OpenRouterProvider,
CodexProvider`` keeps working. Structure: ``cli_base`` (isolation for every agent CLI), ``process``
(bounded run + tree kill), one thin module per vendor, ``registry`` (names and construction).
"""
from ._common import MAX_OUTPUT_BYTES, SYSTEM, parse_proposal
from .anthropic_api import AnthropicApiProvider
from .claude_code import ClaudeCodeProvider
from .cli_base import CliProposalProvider
from .codex import CodexProvider
from .gemini import GeminiCliProvider
from .offline import OfflineProvider
from .opencode import OpenCodeProvider
from .openrouter import OpenRouterProvider
from .registry import KEYED_PROVIDERS, PROVIDER_NAMES, create_provider

__all__ = ["MAX_OUTPUT_BYTES", "SYSTEM", "parse_proposal", "AnthropicApiProvider", "ClaudeCodeProvider", "CliProposalProvider",
           "CodexProvider", "GeminiCliProvider", "OfflineProvider", "OpenCodeProvider", "OpenRouterProvider",
           "KEYED_PROVIDERS", "PROVIDER_NAMES", "create_provider"]
