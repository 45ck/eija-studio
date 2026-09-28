"""The only composition root: wires application ports to concrete adapters."""
from pathlib import Path
from .adapters.sqlite_store import SQLiteStore, sandbox_factory
from .adapters.receipts import ReceiptSigner
from .adapters.identity import identity
from .adapters.providers import create_provider, KEYED_PROVIDERS, PROVIDER_NAMES  # noqa: F401 - re-exported for interfaces
from .application.service import Studio


def build_studio(workspace: Path, provider="offline", model="", allow_network=False, key=None) -> Studio:
    proposal_provider = create_provider(provider, model, key)  # raises ValueError for an unknown name
    store = SQLiteStore(workspace)
    return Studio(store, proposal_provider, ReceiptSigner(store.directory), identity, sandbox_factory(store.directory), allow_network=allow_network)
