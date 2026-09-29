"""SDK-free policy data for the agent adapter: which persistence operations an agent adapter must never touch.

Kept out of ``mcp_server`` so the static lint (tests/test_agent_static.py) can import it without the MCP SDK.
"""
from __future__ import annotations

from typing import Any

from eija_studio.application import ports

#: Port members that only read. Everything else on a persistence port counts as a write, so a NEW port member is
#: treated as a store write (the safe direction) until someone classifies it here, deliberately.
READ_ONLY_PORT_MEMBERS: frozenset[str] = frozenset({
    "load_case", "active", "actor", "find_instance", "find_operation", "observations", "effect_counts",
    "list_cases", "directory", "authentic",
})

#: The persistence ports a write can go through (the unit of work, the repository, the receipt sealer).
PERSISTENCE_PORTS: tuple[Any, ...] = (ports.UnitOfWork, ports.Repository, ports.ReceiptAuthenticator)


def port_members(protocol: Any) -> set[str]:
    """Public methods, properties and annotated attributes declared on a Protocol class."""
    methods = {name for name, value in vars(protocol).items() if (callable(value) or isinstance(value, property)) and not name.startswith("_")}
    return methods | {name for name in getattr(protocol, "__annotations__", {}) if not name.startswith("_")}


def derive_store_write_names() -> tuple[str, ...]:
    """Every member of the persistence ports except the read-only ones, sorted."""
    members: set[str] = set()
    for protocol in PERSISTENCE_PORTS:
        members |= port_members(protocol)
    return tuple(sorted(members - READ_ONLY_PORT_MEMBERS))


#: Persistence operations an adapter must never touch; any use fails the lint in tests/test_agent_static.py.
#: Derived from the ports, not typed by hand (a hand list once named a method that does not exist and missed five
#: real writers).
STORE_WRITE_NAMES: tuple[str, ...] = derive_store_write_names()
