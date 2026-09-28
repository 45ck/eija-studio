"""The only composition root: wires application ports to concrete adapters."""
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator
from .adapters.sqlite_store import SQLiteStore
from .adapters.receipts import ReceiptSigner
from .adapters.identity import identity
from .adapters.providers import OfflineProvider, OpenRouterProvider, CodexProvider
from .application.service import Studio


def build_studio(workspace: Path, provider="offline", model="", allow_network=False, key=None) -> Studio:
    choices = {"offline": lambda: OfflineProvider(), "openrouter": lambda: OpenRouterProvider(model, key), "codex": lambda: CodexProvider(model)}
    if provider not in choices:
        raise ValueError("Unknown provider")
    store = SQLiteStore(workspace)
    return Studio(store, choices[provider](), ReceiptSigner(store.directory), identity, sandbox_factory(store.directory), allow_network=allow_network)


def sandbox_factory(workspace: Path):
    """Disposable verification sandboxes live beside the workspace (same disk, not the system temp
    directory, which may be a slow drive) and use the ephemeral profile: same unit-of-work semantics,
    no per-commit flush."""
    root = workspace / "sandboxes"

    @contextmanager
    def sandbox() -> Iterator[SQLiteStore]:
        root.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix="eija-check-", dir=root) as directory:
            yield SQLiteStore(Path(directory), durability="ephemeral")

    return sandbox
