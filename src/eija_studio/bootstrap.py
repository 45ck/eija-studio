"""The only composition root: wires application ports to concrete adapters."""
from functools import partial
from pathlib import Path
from .adapters.sqlite_store import SQLiteStore, sandbox_factory
from .adapters.receipts import ReceiptSigner
from .adapters.identity import identity
from .adapters.providers import create_provider, KEYED_PROVIDERS, PROVIDER_NAMES  # noqa: F401 - re-exported for interfaces
from .adapters.formal import FormalReports
from .application.service import Studio
from .domain.pack import Pack, default_pack, load_pack


def resolve_pack(pack: Pack | str | Path | None) -> Pack:
    """A pack object, a pack directory/file, or None for the configured default (``$EIJA_PACK`` or packs/default.json)."""
    if pack is None:
        return default_pack()
    return pack if isinstance(pack, Pack) else load_pack(pack)


def build_studio(workspace: Path, provider="offline", model="", allow_network=False, key=None, formal=False,
                 pack: Pack | str | Path | None = None) -> Studio:
    """``formal=True`` attaches formal-lane evidence (Bend, SMT, bounded model check) to ``verify``; off by default so library and test
    callers get exactly the runtime-matrix receipt. The CLI and the Studio turn it on; a missing tool then shows as NOT_RUN."""
    domain = resolve_pack(pack)
    proposal_provider = create_provider(provider, model, key, domain)  # raises ValueError for an unknown name
    store = SQLiteStore(workspace, pack=domain)
    return Studio(store, proposal_provider, ReceiptSigner(store.directory), partial(identity, domain), sandbox_factory(store.directory, domain),
                  allow_network=allow_network, formal=FormalReports() if formal else None, pack=domain)
