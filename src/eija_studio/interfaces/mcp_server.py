"""MCP (Model Context Protocol) adapter: the agent-facing face of EIJA Studio.

Design in one paragraph. "AI proposes. The kernel checks. The local owner decides." The server exposes
only the operations an agent is allowed to perform: create a case, ask the configured provider for an
UNTRUSTED proposal, read derived views, and run the technical runtime verifier. It deliberately has no
tool that selects a meaning, edits the model, approves, applies, discards or previews-with-state. Those
are owner capabilities and stay in the browser Studio (``eija serve``).

The guarantee is ABSENCE, not a role check, in three layers: (1) the tool registry is asserted equal to
``AGENT_TOOLS``; (2) ``AgentSurface`` holds an ``AgentPort`` (five members) and never the whole ``Studio``:
the typed surface has no owner method, and the port keeps the ``Studio`` only in a closure, so no chain of
ordinary attribute names (``port._studio.approve``, ``attrgetter``, ``methodcaller``) reaches it (a test walks
every non-dunder attribute path); (3) an AST lint (tests/test_agent_static.py, with a negative control that
only each rule catches) rejects owner-operation and store-write names on any receiver, ``OWNER``, dynamic
attribute access, object-internals dunders, ``operator``/``importlib``/``inspect`` imports, and the ``Studio``
class or instance used outside the port factory. Reaching past the port needs dunder or introspection
access, which layer 3 catches in the common spellings: it is a best-effort lint, not a proof, and the
adapter is not a sandbox. Nothing here "runs as" the AGENT principal: ``Studio.create``,
``propose`` and ``verify`` take no principal, so the kernel cannot tell an MCP caller from any other and the
audit log does not attribute these actions to an agent (kernel follow-up). If a new tool ever needed a
principal, that would be a governance change to ADR-0041, not an implementation detail.

Spend guard: ``--egress-consent`` is a STANDING consent set once at startup, so it covers every
``propose`` call in the session. ``max_provider_calls`` caps how many networked provider calls one
server session may make; the agent cannot change it.

What this module does NOT establish: it is a convenience and a guard rail, not a sandbox. An agent
with the same OS permissions as the owner can still read the workspace directly (see AGENTS.md).

The module is an interface adapter: it may import the application and domain layers and the vendor
SDK; nothing in ``domain`` or ``application`` imports it.
"""
from __future__ import annotations

import logging
import platform
import re
import threading
from pathlib import Path
from typing import Any, Callable, Literal, Protocol

import anyio.to_thread
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.types import ToolAnnotations

from eija_studio import __version__
from eija_studio.application.service import Studio
from eija_studio.domain.models import DomainError, Workflow
from eija_studio.domain.policy import projections
from eija_studio.interfaces.agent_config import DEFAULT_MAX_PROVIDER_CALLS
from eija_studio.interfaces.agent_policy import STORE_WRITE_NAMES  # noqa: F401  (re-exported for the lint and the docs)

#: The complete agent tool surface. Adding a name here is a governance decision (ADR-0041).
AGENT_TOOLS: tuple[str, ...] = ("list_cases", "create_case", "propose", "view_case", "impact", "verify", "render")

#: Owner-only operations. Tests assert none of these is registered as a tool, and that no identifier in this
#: module names them on any receiver.
OWNER_ONLY_OPERATIONS: tuple[str, ...] = ("select", "select_meaning", "edit", "layout", "approve", "apply",
                                          "discard", "save", "reset_preview", "execute", "export")

# STORE_WRITE_NAMES (persistence operations an adapter must never touch; any use fails the lint in
# tests/test_agent_static.py) is derived from the ports in the SDK-free ``agent_policy`` module.

INSTRUCTIONS = (
    "EIJA Studio assurance kernel. You are an AGENT: you may create cases, request UNTRUSTED proposals, "
    "read derived views (projections, impact, packet), and run technical runtime verification. You may NOT "
    "select a meaning, edit, approve or apply; those belong to the local owner in the browser Studio. "
    "Never claim human understanding, approval or production readiness: the kernel reports "
    "human_understanding=UNKNOWN and lists limitations; repeat them. A NOT_RUN or UNKNOWN result is not a pass. "
    "Requests must be synthetic text (no secrets, no personal data). Read resource eija://agent/contract first."
)

_CASE_ID = re.compile(r"^[a-f0-9]{32}$")
_ADR_NUMBER = re.compile(r"^\d{4}$")

# Case stage -> what remains for the LOCAL OWNER (never for the agent).
OWNER_NEXT: dict[str, str] = {
    "DRAFT": "Ask for a proposal (agent may do this); then the owner selects a supported meaning in Studio.",
    "PROPOSED": "The owner must select one supported meaning in Studio. Agents cannot select.",
    "PREVIEW": "Run technical verification (agent may do this), then the owner reviews the packet in Studio.",
    "SAVED": "Run technical verification (agent may do this), then the owner reviews the packet in Studio.",
    "VERIFIED": "The owner reviews the packet, answers the meaning questions and decides in Studio.",
    "APPROVED": "The owner may apply the approved subject in Studio. Do not re-verify: it clears the decision.",
    "APPLIED": "Closed. Create a new case for further change.",
    "DISCARDED": "Closed. Create a new case for further change.",
}

_LOG = logging.getLogger("eija_studio.mcp")  # stderr only: stdout is the protocol channel


def _owner_next(stage: str) -> str:
    """Owner guidance for a stage; a stage this adapter does not know yet degrades to a safe default, never a KeyError."""
    return OWNER_NEXT.get(stage, f"Unrecognised case stage {stage!r}: ask the local owner to inspect this case in Studio. "
                                 "Take no further action on it.")


DIAGRAM_FORMATS = ("mermaid", "plantuml", "svg")
PROJECTION_VIEWS = ("rules", "states", "journeys")

#: EXTENSION POINT (visual lane, ADR-0019/0023). ``(workflow, view, format) -> text``. Until the diagrams
#: module lands on main and is wired by ``serve_stdio(diagram_renderer=...)``, diagram formats return
#: DIAGRAMS_NOT_AVAILABLE. This adapter deliberately does not generate diagrams itself.
DiagramRenderer = Callable[[Workflow, str, str], str]


def _docs_root() -> Path | None:
    """Repository ``docs/`` directory when running from a checkout; None for a bare wheel install."""
    root = Path(__file__).resolve().parents[3] / "docs"
    return root if (root / "architecture" / "ARCHITECTURE.md").is_file() else None


def _read_doc(relative: str, *, section: str | None = None) -> str:
    root = _docs_root()
    if root is None:
        return ("Documentation is not bundled with this installation. Install EIJA from a git checkout "
                "(pip install -e \".[agents]\") or read https://github.com/45ck/eija-studio/tree/main/docs")
    text = (root / relative).read_text(encoding="utf-8")
    if section is None:
        return text
    match = re.search(rf"^## {re.escape(section)}\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
    return f"## {section}\n{match.group(1)}" if match else text


def _tool_error(error: DomainError) -> ToolError:
    return ToolError(f"{error.code}: {error.message}")


def _case_id(value: str) -> str:
    if not isinstance(value, str) or not _CASE_ID.fullmatch(value):
        raise DomainError("INVALID_CASE_ID", "case_id must be the 32-character hex id returned by list_cases/create_case")
    return value


def _decision_summary(decision: dict | None) -> dict[str, Any]:
    """Presence and scope only: the sealed decision body and its seal never reach an agent."""
    if not decision:
        return {"present": False}
    return {"present": True, "by": decision.get("by"), "scope": decision.get("scope"), "kind": decision.get("kind")}


def _provider_run_summary(run: dict | None) -> dict | None:
    if not run:
        return None
    keys = ("provider", "model", "live", "egress", "elapsed_seconds", "timestamp", "semantics")
    return {k: run.get(k) for k in keys}


class AgentPort(Protocol):
    """The narrow slice of ``Studio`` an agent may use. It has no owner operation to call by construction."""

    @property
    def networked(self) -> bool: ...

    def list_cases(self) -> list[dict]: ...
    def create(self, request: str) -> dict: ...
    def propose(self, case_id: str, expected: int, *, consent: bool = False) -> dict: ...
    def verify(self, case_id: str, expected: int) -> dict: ...
    def view(self, case_id: str) -> dict: ...


def StudioAgentPort(studio: Studio) -> AgentPort:  # a class-like factory: the Studio lives only in a closure
    """``AgentPort`` over a composed ``Studio``. The only place in this module that holds a ``Studio``.

    Establishes: the adapter's reachable ``Studio`` surface is these five delegations, and the returned object has
    no attribute that leads to the ``Studio`` (it is captured by the methods' closure, not stored on the port), so
    ``attrgetter``/``methodcaller``/dotted paths by ordinary names cannot reach an owner operation. It does NOT
    stop dunder or introspection access (``__closure__``): the lint in tests/test_agent_static.py forbids those
    in this module. It does NOT establish identity: ``Studio`` takes no principal for these operations, so the
    kernel cannot tell this caller apart.
    """

    class _StudioAgentPort:
        @property
        def networked(self) -> bool:
            return bool(studio.provider.networked)

        def list_cases(self) -> list[dict]:
            return list(studio.store.list_cases())

        def create(self, request: str) -> dict:
            return studio.create(request)

        def propose(self, case_id: str, expected: int, *, consent: bool = False) -> dict:
            return studio.propose(case_id, expected, consent=consent)

        def verify(self, case_id: str, expected: int) -> dict:
            return studio.verify(case_id, expected)

        def view(self, case_id: str) -> dict:
            return studio.view(case_id)

    return _StudioAgentPort()


class AgentSurface:
    """The operations exposed to an agent, as plain synchronous methods returning JSON-able dicts.

    Separated from the MCP registration so it is unit-testable and so the exposed surface is one
    reviewable class. It holds an ``AgentPort``, never a ``Studio``: it cannot call an owner operation.
    """

    def __init__(self, port: AgentPort, *, egress_consent: bool = False, diagram_renderer: DiagramRenderer | None = None,
                 max_provider_calls: int = DEFAULT_MAX_PROVIDER_CALLS):
        if max_provider_calls < 0:
            raise ValueError("max_provider_calls must not be negative")
        self.port = port
        # Standing consent is a property of how the OWNER started the server. No tool argument can set it.
        self.egress_consent, self.diagram_renderer = egress_consent, diagram_renderer
        self.max_provider_calls, self._provider_calls, self._budget = max_provider_calls, 0, threading.Lock()

    def _reserve_provider_call(self) -> None:
        """Spend guard: count a networked attempt BEFORE it is made (a started request may bill even if it fails)."""
        if not self.port.networked:
            return
        with self._budget:
            if self._provider_calls >= self.max_provider_calls:
                raise DomainError("PROVIDER_CALL_LIMIT",
                                  f"This server session allows {self.max_provider_calls} live provider call(s) and they are used. "
                                  "Ask the owner to restart it with a higher --max-provider-calls if more are needed.")
            self._provider_calls += 1

    # ---- read ---------------------------------------------------------------------------------
    def list_cases(self) -> dict[str, Any]:
        cases = [{"id": c["id"], "version": c["version"], "stage": c["stage"], "created_at": c["created_at"],
                  "request": c["request"][:200]} for c in self.port.list_cases()]
        return {"cases": cases, "count": len(cases)}

    def view_case(self, case_id: str) -> dict[str, Any]:
        view = self.port.view(_case_id(case_id))
        case, packet = view["case"], view["packet"]
        proposal = case.get("proposal")
        unknowns = [f"human_understanding: {packet.get('human_understanding', 'UNKNOWN')}"]
        unknowns += list((proposal or {}).get("unknowns", []))
        claims = packet.get("technical_claims", {})
        unknowns += [f"{name}: {value}" for name, value in claims.items() if value != "PASS"]
        model = Workflow.model_validate(case["candidate"] if case["candidate"] else case["baseline"])
        return {
            "case": {"id": case["id"], "version": case["version"], "stage": case["stage"], "request": case["request"],
                     "created_at": case["created_at"], "baseline_version": case["baseline_version"],
                     "selected_meaning": case["selected_meaning"], "selected_by": case["selected_by"],
                     "transactions": [t["kind"] for t in case["transactions"]], "receipt_count": len(case["receipts"]),
                     "decision": _decision_summary(case["decision"]), "provider_run": _provider_run_summary(case["provider_run"])},
            "proposal": None if proposal is None else {**proposal, "trust": "UNTRUSTED_PROPOSAL"},
            "packet": {k: packet.get(k) for k in ("status", "eligible", "blockers", "policy_errors", "technical_claims",
                       "human_understanding", "core_status", "subject_hash", "receipt_applicability", "limitations")},
            # Question text only. The expected answers are the owner's meaning check, never shown to an agent.
            "questions": [{"id": q["id"], "question": q["question"]} for q in packet.get("questions", [])],
            "projection_subject": "candidate" if case["candidate"] else "baseline",
            "projections": projections(model),
            "unknowns": unknowns,
            "owner_next": _owner_next(case["stage"]),
        }

    def impact(self, case_id: str) -> dict[str, Any]:
        packet = self.port.view(_case_id(case_id))["packet"]
        if "impact" not in packet:
            return {"available": False, "blockers": packet.get("blockers", []),
                    "reason": "Impact needs a selected meaning; only the local owner selects one."}
        return {"available": True, "impact": packet["impact"], "complete": packet["impact"].get("complete"),
                "boundary": "Covers this model's explicit mapping, not all real-world dependencies."}

    def render(self, case_id: str, view: str, fmt: str) -> dict[str, Any]:
        _case_id(case_id)
        if view not in PROJECTION_VIEWS:
            raise DomainError("INVALID_VIEW", f"view must be one of {', '.join(PROJECTION_VIEWS)}")
        if fmt in DIAGRAM_FORMATS:
            return self._diagram(case_id, view, fmt)
        if fmt not in ("json", "text"):
            raise DomainError("INVALID_FORMAT", "format must be json, text, " + ", ".join(DIAGRAM_FORMATS))
        case = self.port.view(case_id)["case"]
        subject = "candidate" if case["candidate"] else "baseline"
        projected = projections(Workflow.model_validate(case["candidate"] or case["baseline"]))
        body: Any = projected[view]
        if fmt == "text":
            body = self._text(view, body)
        return {"view": view, "format": fmt, "subject": subject, "content": body,
                "derived": "Generated from the executable Workflow; not a second source of truth. Do not edit."}

    def _diagram(self, case_id: str, view: str, fmt: str) -> dict[str, Any]:
        if self.diagram_renderer is None:
            raise DomainError("DIAGRAMS_NOT_AVAILABLE",
                              "No diagram renderer is wired into this server (extension point for the visual lane). "
                              "Use format json or text for projections.")
        case = self.port.view(case_id)["case"]
        model = Workflow.model_validate(case["candidate"] or case["baseline"])
        return {"view": view, "format": fmt, "subject": "candidate" if case["candidate"] else "baseline",
                "content": self.diagram_renderer(model, view, fmt),
                "derived": "Generated from the executable Workflow; not a second source of truth."}

    @staticmethod
    def _text(view: str, body: Any) -> str:
        if view == "journeys":
            return "\n".join(body)
        if view == "rules":
            return "\n".join(f"{t['role']} may {t['action']}: {t['from_state']} -> {t['to_state']}" for t in body)
        return "\n".join(f"{s['id']}: " + (", ".join(f"{a['role']}:{a['action']}->{a['target']}" for a in s["next_actions"]) or "(terminal)")
                         for s in body)

    # ---- act as AGENT ---------------------------------------------------------------------------
    def create_case(self, request: str) -> dict[str, Any]:
        case = self.port.create(request)
        return {"id": case["id"], "version": case["version"], "stage": case["stage"], "owner_next": _owner_next(case["stage"])}

    def _version(self, case_id: str, expected_version: int | None) -> int:
        current = self.port.view(_case_id(case_id))["case"]["version"]
        if expected_version is not None and expected_version != current:
            raise DomainError("STALE_VERSION", "Case changed; reload with view_case before acting")
        return current

    def propose(self, case_id: str, expected_version: int | None = None) -> dict[str, Any]:
        expected = self._version(case_id, expected_version)
        self._reserve_provider_call()
        case = self.port.propose(case_id, expected, consent=self.egress_consent)
        return {"id": case["id"], "version": case["version"], "stage": case["stage"],
                "proposal": {**case["proposal"], "trust": "UNTRUSTED_PROPOSAL"},
                "provider_run": _provider_run_summary(case["provider_run"]), "owner_next": _owner_next(case["stage"])}

    def verify(self, case_id: str, expected_version: int | None = None) -> dict[str, Any]:
        expected = self._version(case_id, expected_version)
        stage = self.port.view(case_id)["case"]["stage"]
        if stage == "APPROVED":
            # Studio.verify clears an existing owner decision. An agent must not be able to do that.
            raise DomainError("VERIFY_WOULD_INVALIDATE_DECISION",
                              "The owner has approved this subject; re-verifying would clear that decision. Ask the owner.")
        self.port.verify(case_id, expected)
        view = self.view_case(case_id)
        packet = view["packet"]
        return {"id": case_id, "version": view["case"]["version"], "stage": view["case"]["stage"],
                "technical_claims": packet["technical_claims"], "receipt_applicability": packet["receipt_applicability"],
                "blockers": packet["blockers"], "human_understanding": packet["human_understanding"],
                "boundary": "Technical runtime verification only: a bounded matrix checked by a same-author oracle. "
                            "It is not approval, not human understanding and not a proof.",
                "owner_next": view["owner_next"]}

    # ---- error translation (also used by tests to prove authority errors surface) ---------------
    def guarded(self, call: Callable[[], Any]) -> Any:
        """Run ``call``; surface a kernel DomainError as a tool error ``CODE: message``."""
        try:
            return call()
        except DomainError as error:
            raise _tool_error(error) from None
        except ToolError:
            raise
        except Exception:
            # Never return raw exception text: it can carry file paths or workspace internals. Log to stderr only.
            _LOG.exception("unexpected error in an MCP tool")
            raise ToolError("INTERNAL_ERROR: the server hit an unexpected error; details are in the server's stderr log "
                            "for the owner. Do not retry in a loop.") from None

    async def guarded_async(self, call: Callable[[], Any]) -> Any:
        return await anyio.to_thread.run_sync(lambda: self.guarded(call))


def create_server(studio: Studio, *, egress_consent: bool = False, diagram_renderer: DiagramRenderer | None = None,
                  max_provider_calls: int = DEFAULT_MAX_PROVIDER_CALLS) -> MCPServer:
    """Build the MCP server around an already composed ``Studio`` (composition happens in bootstrap.py)."""
    # The first platform.system() call runs a WMI query on Windows (it can fail under memory pressure and
    # fall back, printing a faulthandler dump under pytest). Make it here at start-up, not on a worker thread.
    platform.uname()
    port = StudioAgentPort(studio)
    surface = AgentSurface(port, egress_consent=egress_consent, diagram_renderer=diagram_renderer,
                           max_provider_calls=max_provider_calls)
    server = MCPServer("eija-studio", instructions=INSTRUCTIONS, version=__version__)
    read = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
    write = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False)
    reach = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False,
                            open_world_hint=port.networked)

    @server.tool(annotations=read)
    async def list_cases() -> dict[str, Any]:
        """List Change Cases in this workspace (id, version, stage, first 200 chars of the request)."""
        return await surface.guarded_async(surface.list_cases)

    @server.tool(annotations=write)
    async def create_case(request: str) -> dict[str, Any]:
        """Create a Change Case from a synthetic plain-language request (1-6000 chars; no secrets or personal data).
        Returns the new case id and what the local owner must do next."""
        return await surface.guarded_async(lambda: surface.create_case(request))

    @server.tool(annotations=reach)
    async def propose(case_id: str, expected_version: int | None = None) -> dict[str, Any]:
        """Ask the configured provider for an UNTRUSTED interpretation of the case request. The default provider is
        an offline deterministic fixture, not a model. The result is a proposal only: it selects nothing and
        proves nothing. Only the local owner selects a meaning."""
        return await surface.guarded_async(lambda: surface.propose(case_id, expected_version))

    @server.tool(annotations=read)
    async def view_case(case_id: str) -> dict[str, Any]:
        """Read a case: stage, proposal (untrusted), review-packet summary, projections (rules/states/journeys),
        the meaning-check questions (without answers), the UNKNOWNs and what the local owner must do next."""
        return await surface.guarded_async(lambda: surface.view_case(case_id))

    @server.tool(annotations=read)
    async def impact(case_id: str) -> dict[str, Any]:
        """Modelled impact closure of the candidate versus the baseline. Needs a meaning selected by the local owner."""
        return await surface.guarded_async(lambda: surface.impact(case_id))

    @server.tool(annotations=write)
    async def verify(case_id: str, expected_version: int | None = None) -> dict[str, Any]:
        """Run the technical runtime verification (bounded actor x state x action matrix, same-author oracle) and
        attach the receipt. This is not approval and not human evidence. Refused once the owner has approved."""
        return await surface.guarded_async(lambda: surface.verify(case_id, expected_version))

    @server.tool(annotations=read)
    async def render(case_id: str, view: Literal["rules", "states", "journeys"] = "journeys",
                     format: Literal["json", "text", "mermaid", "plantuml", "svg"] = "text") -> dict[str, Any]:
        """Render a derived view of the executable model. json/text are projections. mermaid/plantuml/svg need a
        diagram renderer wiring that is not installed unless the response says otherwise (DIAGRAMS_NOT_AVAILABLE)."""
        return await surface.guarded_async(lambda: surface.render(case_id, view, format))

    @server.resource("eija://agent/contract", name="agent-contract", mime_type="text/markdown",
                     description="What an agent may and may not do with EIJA (mirrors AGENTS.md).")
    def agent_contract() -> str:
        return _read_doc("agents/contract.md")

    @server.resource("eija://language", name="ubiquitous-language", mime_type="text/markdown",
                     description="The ubiquitous language: precise meanings of Change Case, Meaning Selection, Evidence Receipt, ...")
    def ubiquitous_language() -> str:
        return _read_doc("architecture/ARCHITECTURE.md", section="Ubiquitous language")

    @server.resource("eija://adr", name="adr-index", mime_type="text/markdown", description="Architecture decision record index.")
    def adr_index() -> str:
        return _read_doc("adr/README.md")

    @server.resource("eija://adr/{number}", name="adr", mime_type="text/markdown",
                     description="One architecture decision record by four-digit number, e.g. 0016.")
    def adr(number: str) -> str:
        root = _docs_root()
        if not _ADR_NUMBER.fullmatch(number):
            raise ResourceNotFoundError("ADR numbers are four digits, e.g. 0016")
        if root is None:
            raise ResourceNotFoundError("Documentation is not bundled with this installation; read eija://adr for the notice")
        matches = sorted((root / "adr").glob(f"{number}-*.md"))
        if not matches:
            raise ResourceNotFoundError(f"No ADR {number}")
        return matches[0].read_text(encoding="utf-8")

    return server


def serve_stdio(studio: Studio, *, egress_consent: bool = False, diagram_renderer: DiagramRenderer | None = None,
                max_provider_calls: int = DEFAULT_MAX_PROVIDER_CALLS) -> None:
    """Serve over stdio. stdout is the protocol channel: nothing else may write to it."""
    create_server(studio, egress_consent=egress_consent, diagram_renderer=diagram_renderer,
                  max_provider_calls=max_provider_calls).run("stdio")
