"""The only composition root: wires application ports to concrete adapters."""
from pathlib import Path
from .adapters.sqlite_store import SQLiteStore, sandbox_factory
from .adapters.receipts import ReceiptSigner
from .adapters.identity import identity
from .adapters.providers import OfflineProvider, OpenRouterProvider, CodexProvider
from .adapters.formal import FormalReports
from .application.service import Studio


def build_studio(workspace: Path, provider="offline", model="", allow_network=False, key=None, formal=False) -> Studio:
    """``formal=True`` attaches formal-lane evidence (Bend, SMT, bounded model check) to ``verify``; off by default so library and test
    callers get exactly the runtime-matrix receipt. The CLI and the Studio turn it on; a missing tool then shows as NOT_RUN."""
    choices = {"offline": lambda: OfflineProvider(), "openrouter": lambda: OpenRouterProvider(model, key), "codex": lambda: CodexProvider(model)}
    if provider not in choices:
        raise ValueError("Unknown provider")
    store = SQLiteStore(workspace)
    return Studio(store, choices[provider](), ReceiptSigner(store.directory), identity, sandbox_factory(store.directory), allow_network=allow_network,
                  formal=FormalReports() if formal else None)
