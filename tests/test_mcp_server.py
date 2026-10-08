"""MCP adapter tests, driven through the SDK's in-memory client/server session.

They prove (the SDK-free lint, config and docs checks are in test_agent_static.py): the exposed surface is exactly the agent surface; owner operations are absent and
unreachable; kernel domain errors and unexpected errors surface safely; consent and answers cannot be
supplied by an agent and networked calls are capped; sealed material does not leak; and the real stdio
entry point starts, answers and keeps stdout to JSON-RPC only.
"""
from __future__ import annotations

import asyncio
import errno
import json
import subprocess
import sys
import tempfile
import threading
from operator import attrgetter, methodcaller
from pathlib import Path

import pytest

pytest.importorskip("mcp", reason="install the agents extra: pip install -e '.[agents]'")

from mcp import Client, MCPError, StdioServerParameters
from mcp.server.mcpserver.exceptions import ToolError

from kernel_support import approve
from eija_studio.application.ports import ProviderResult
from eija_studio.domain.models import AGENT, OWNER, DomainError, Proposal, Alternative
from eija_studio.application.service import Studio
from eija_studio.interfaces import agent_policy
from eija_studio.interfaces.mcp_server import (
    AGENT_TOOLS, OWNER_ONLY_OPERATIONS, AgentPort, AgentSurface, StudioAgentPort, _owner_next, create_server)

ROOT = Path(__file__).resolve().parents[1]
REQUEST = "Let teachers sign off excursions."


def session(studio, **options):
    """Run an async block against an in-memory client of a server built around `studio`."""
    def run(block):
        async def main():
            async with Client(create_server(studio, **options)) as client:
                return await block(client)
        return asyncio.run(main())
    return run


def call(client, name, **arguments):
    return client.call_tool(name, arguments)


def payload(result) -> dict:
    assert not result.is_error, result.content
    return json.loads(result.content[0].text)


class NetworkedStub:
    """A networked provider double: exercises the consent path without any network."""
    name, networked = "stub-net", True

    def __init__(self):
        self.calls = 0

    def doctor(self):
        return {"provider": self.name, "ready": True}

    def propose(self, request, model):
        self.calls += 1
        proposal = Proposal(summary="stub", alternatives=(Alternative(interpretation="unsupported", explanation="stub"),), unknowns=())
        return ProviderResult(proposal, self.name, "stub", {}, False)


# ---- surface -----------------------------------------------------------------------------------
def test_tool_surface_is_exactly_the_agent_surface(studio):
    tools = session(studio)(lambda c: c.list_tools())
    names = [t.name for t in tools.tools]
    assert sorted(names) == sorted(AGENT_TOOLS)
    for forbidden in OWNER_ONLY_OPERATIONS:
        assert forbidden not in names, forbidden
    # An agent cannot smuggle consent, meaning or answers through a tool argument.
    smuggled = {"consent", "interpretation", "answers", "subject_hash", "acknowledge_unknowns", "principal"}
    for tool in tools.tools:
        assert not smuggled & set(tool.input_schema.get("properties", {})), tool.name
        assert ("proposal" in tool.input_schema.get("properties", {})) == (tool.name == "edit_check")
    hints = {t.name: t.annotations for t in tools.tools}
    assert all(h is not None and h.destructive_hint is False for h in hints.values())
    assert hints["view_case"].read_only_hint is True and hints["verify"].read_only_hint is False
    assert all(hints[name].read_only_hint is True for name in ("pack", "affordances", "edit_check", "repository_impact", "repository_source"))


def test_calling_an_owner_operation_is_an_error_not_a_dispatch(studio):
    async def block(client):
        for name in ("select", "select_meaning", "edit", "undo", "redo", "approve", "apply"):
            result = await client.call_tool(name, {"case_id": "0" * 32})
            assert result.is_error and "Unknown tool" in result.content[0].text, name
    session(studio)(block)


def test_surface_holds_no_principal_and_needs_only_the_five_member_port(studio):
    # The guarantee is that owner tools are absent (tests above and test_agent_static.py), not a principal check.
    surface = AgentSurface(StudioAgentPort(studio))
    assert not hasattr(surface, "principal") and not hasattr(surface, "studio")
    with pytest.raises(TypeError):
        AgentSurface(StudioAgentPort(studio), principal=OWNER)  # type: ignore[call-arg]

    class Fake:
        networked = False

        def list_cases(self):
            return []

        def create(self, request):
            return {"id": "a" * 32, "version": 0, "stage": "DRAFT"}

        def view(self, case_id):
            raise ToolError("not reached")

        propose = verify = view
    fake_surface = AgentSurface(Fake())  # a five-member fake is enough to drive it: nothing else can be reached
    assert fake_surface.list_cases() == {"cases": [], "count": 0}
    assert fake_surface.create_case(REQUEST)["stage"] == "DRAFT"
    # Assert against the REAL port, not the fake above (which was written without owner names and so proved nothing):
    # its public attributes are exactly the AgentPort members, and no owner operation is among them.
    real = StudioAgentPort(studio)
    public = {name for name in dir(real) if not name.startswith("_")}
    assert public == agent_policy.port_members(AgentPort)
    assert not public & set(OWNER_ONLY_OPERATIONS)


def _reachable_by_ordinary_names(root, depth=5):
    """Every object reachable from ``root`` through non-dunder attribute names, the way attrgetter/methodcaller or a
    dotted path can go. (Dunder walks such as __closure__ are the lint's job, not this test's.)"""
    seen, stack, found = set(), [(root, 0)], []
    while stack:
        obj, level = stack.pop()
        if id(obj) in seen or level > depth:
            continue
        seen.add(id(obj))
        found.append(obj)
        for name in dir(obj):
            if name.startswith("__"):
                continue
            try:
                stack.append((getattr(obj, name), level + 1))
            except Exception:  # noqa: S112  (a property that raises leads nowhere)
                continue
    return found


def test_the_narrowed_port_cannot_reach_an_owner_operation_by_any_ordinary_name(studio):
    """Review of PR #23: `attrgetter`, `methodcaller` and dotted paths must not find approve/apply on the narrowed port."""
    port = StudioAgentPort(studio)
    for name in (*OWNER_ONLY_OPERATIONS, "_studio", "studio", "_studio.approve", "studio.apply", "_studio.store.transaction"):
        with pytest.raises(AttributeError):
            attrgetter(name)(port)
    for name in OWNER_ONLY_OPERATIONS:
        with pytest.raises(AttributeError):
            methodcaller(name, "0" * 32, 0)(port)
    reachable = _reachable_by_ordinary_names(AgentSurface(port))
    assert not any(isinstance(obj, Studio) for obj in reachable), "an ordinary attribute path leads from the surface to the Studio"
    assert not any(getattr(obj, "__name__", "") in OWNER_ONLY_OPERATIONS for obj in reachable)
    # negative control: the walk really does find a Studio when one is stored on the port (the old design)

    class Leaky:
        def __init__(self, held):
            self._studio = held
    assert any(isinstance(obj, Studio) for obj in _reachable_by_ordinary_names(Leaky(studio)))


def test_the_kernel_still_refuses_an_authority_less_principal_below_the_adapter(studio, selected):
    """Kernel test, not an adapter test: the adapter is safe because it offers no such tool, not because of this."""
    with pytest.raises(DomainError) as raised:
        studio.select(selected["id"], selected["version"], "recommend_only", AGENT)
    assert raised.value.code == "AUTHORITY_REQUIRED"


def test_kernel_domain_errors_reach_the_agent_through_a_tool_path(studio, selected):
    async def block(client):
        # Studio refuses to reinterpret a case whose meaning the owner already selected.
        result = await call(client, "propose", case_id=selected["id"])
        assert result.is_error and "CASE_ALREADY_SELECTED" in result.content[0].text
        stale = await call(client, "propose", case_id=selected["id"], expected_version=selected["version"] + 9)
        assert stale.is_error and "STALE_VERSION" in stale.content[0].text
    session(studio)(block)


def test_guarded_translates_domain_errors_and_hides_unexpected_ones(studio):
    surface = AgentSurface(StudioAgentPort(studio))

    def domain():
        raise DomainError("MEANING_REQUIRED", "select first")

    def unexpected():
        raise RuntimeError("boom at C:/Users/owner/secret/receipt.key")
    with pytest.raises(ToolError, match="MEANING_REQUIRED: select first"):
        surface.guarded(domain)
    with pytest.raises(ToolError) as caught:
        surface.guarded(unexpected)
    text = str(caught.value)
    assert text.startswith("INTERNAL_ERROR") and "receipt.key" not in text and "boom" not in text


def test_unexpected_error_inside_a_tool_is_generic_over_the_wire(studio, monkeypatch):
    def explode(*_args, **_kwargs):
        raise RuntimeError("leaks C:/secret/path")
    monkeypatch.setattr(studio, "view", explode)

    async def block(client):
        result = await call(client, "view_case", case_id="0" * 32)
        assert result.is_error and "INTERNAL_ERROR" in result.content[0].text
        assert "secret" not in result.content[0].text
    session(studio)(block)


def test_unknown_stage_degrades_instead_of_raising_and_proposal_cannot_relabel_trust(studio, monkeypatch):
    assert "FUTURE_STAGE" in _owner_next("FUTURE_STAGE") and "Take no further action" in _owner_next("FUTURE_STAGE")
    real_view = studio.view
    case = studio.create(REQUEST)

    def fake_view(case_id):
        view = real_view(case_id)
        view["case"] = {**view["case"], "stage": "FUTURE_STAGE",
                        "proposal": {"summary": "s", "alternatives": [], "unknowns": [], "trust": "TRUSTED"}}
        return view
    monkeypatch.setattr(studio, "view", fake_view)

    async def block(client):
        view = payload(await call(client, "view_case", case_id=case["id"]))
        assert "FUTURE_STAGE" in view["owner_next"]
        assert view["proposal"]["trust"] == "UNTRUSTED_PROPOSAL"
    session(studio)(block)


# ---- behaviour ---------------------------------------------------------------------------------
def test_agent_workflow_and_owner_boundary(studio):
    async def block(client):
        created = payload(await call(client, "create_case", request=REQUEST))
        case_id = created["id"]
        assert (await call(client, "list_cases")).structured_content["count"] == 1

        proposed = payload(await call(client, "propose", case_id=case_id))
        assert proposed["stage"] == "PROPOSED" and proposed["proposal"]["trust"] == "UNTRUSTED_PROPOSAL"
        assert proposed["provider_run"]["live"] is False

        view = payload(await call(client, "view_case", case_id=case_id))
        assert view["case"]["selected_meaning"] is None and view["projection_subject"] == "baseline"
        assert "select" in view["owner_next"].lower()

        # No meaning selected: verify is a surfaced kernel error, impact is honestly unavailable.
        blocked = await call(client, "verify", case_id=case_id)
        assert blocked.is_error and "MEANING_REQUIRED" in blocked.content[0].text
        assert payload(await call(client, "impact", case_id=case_id))["available"] is False
        return case_id
    case_id = session(studio)(block)

    # The local owner (not the agent) selects a meaning, out of band.
    case = studio.view(case_id)["case"]
    studio.select(case_id, case["version"], "recommend_only", OWNER)

    async def after(client):
        verified = payload(await call(client, "verify", case_id=case_id))
        assert verified["technical_claims"]["runtime_matrix"] == "PASS"
        assert verified["human_understanding"] == "UNKNOWN" and "not approval" in verified["boundary"]
        view = payload(await call(client, "view_case", case_id=case_id))
        assert view["projection_subject"] == "candidate" and view["packet"]["eligible"] is True
        assert any(u.startswith("human_understanding") for u in view["unknowns"])
        assert payload(await call(client, "impact", case_id=case_id))["complete"] is True
        return view
    view = session(studio)(after)
    # The meaning-check questions are shown without their answers.
    assert view["questions"] and all(set(q) == {"id", "question"} for q in view["questions"])
    assert '"expected":' not in json.dumps(view)


def test_verify_is_refused_after_owner_approval_and_the_decision_survives(studio, verified):
    approved = approve(studio, verified)
    decision = approved["decision"]

    async def block(client):
        result = await call(client, "verify", case_id=approved["id"])
        assert result.is_error and "VERIFY_WOULD_INVALIDATE_DECISION" in result.content[0].text
        view = payload(await call(client, "view_case", case_id=approved["id"]))
        assert view["case"]["decision"] == {"present": True, "by": "local-owner", "scope": "local-demo", "kind": "local-owner-acknowledgement"}
        # The sealed decision never reaches the agent.
        assert decision["local_signature"] not in json.dumps(view)
    session(studio)(block)
    assert studio.view(approved["id"])["case"]["decision"] == decision


def test_stale_expected_version_and_bad_ids_surface(studio, selected):
    async def block(client):
        stale = await call(client, "verify", case_id=selected["id"], expected_version=selected["version"] + 5)
        assert stale.is_error and "STALE_VERSION" in stale.content[0].text
        assert "INVALID_CASE_ID" in (await call(client, "view_case", case_id="../../etc/passwd")).content[0].text
        assert "NOT_FOUND" in (await call(client, "view_case", case_id="0" * 32)).content[0].text
        assert "INVALID_REQUEST" in (await call(client, "create_case", request="   ")).content[0].text
    session(studio)(block)


def test_network_consent_belongs_to_the_owner_not_the_agent(studio):
    studio.provider, studio.allow_network = NetworkedStub(), True

    async def declined(client):
        case_id = payload(await call(client, "create_case", request=REQUEST))["id"]
        result = await call(client, "propose", case_id=case_id)
        assert result.is_error and "EGRESS_CONSENT_REQUIRED" in result.content[0].text
    session(studio)(declined)  # allow_network alone is not enough; no tool argument can add consent

    async def consented(client):
        case_id = payload(await call(client, "create_case", request=REQUEST))["id"]
        run = payload(await call(client, "propose", case_id=case_id))["provider_run"]
        assert run["egress"] is True and "no authority" in run["semantics"].lower()
    session(studio, egress_consent=True)(consented)


def test_live_provider_calls_are_capped_per_session(studio):
    stub = NetworkedStub()
    studio.provider, studio.allow_network = stub, True

    async def block(client):
        case_id = payload(await call(client, "create_case", request=REQUEST))["id"]
        for _ in range(2):
            payload(await call(client, "propose", case_id=case_id))
        refused = await call(client, "propose", case_id=case_id)
        assert refused.is_error and "PROVIDER_CALL_LIMIT" in refused.content[0].text
        assert "--max-provider-calls" in refused.content[0].text
        # A malformed id never spends budget and never reaches the provider.
        assert "INVALID_CASE_ID" in (await call(client, "propose", case_id="nope")).content[0].text
    session(studio, egress_consent=True, max_provider_calls=2)(block)
    assert stub.calls == 2  # the third call was refused BEFORE any provider request


def test_zero_cap_forbids_live_calls_and_a_negative_cap_is_invalid(studio):
    stub = NetworkedStub()
    studio.provider, studio.allow_network = stub, True

    async def zero(client):
        case_id = payload(await call(client, "create_case", request=REQUEST))["id"]
        result = await call(client, "propose", case_id=case_id)
        assert result.is_error and "PROVIDER_CALL_LIMIT" in result.content[0].text
    session(studio, egress_consent=True, max_provider_calls=0)(zero)
    assert stub.calls == 0
    with pytest.raises(ValueError):
        AgentSurface(StudioAgentPort(studio), max_provider_calls=-1)


def test_offline_proposals_do_not_consume_the_cap(studio):
    async def block(client):
        case_id = payload(await call(client, "create_case", request=REQUEST))["id"]
        for _ in range(4):
            assert payload(await call(client, "propose", case_id=case_id))["provider_run"]["live"] is False
    session(studio, max_provider_calls=1)(block)


def test_render_projections_and_diagram_extension_point(studio, selected):
    async def block(client):
        case_id = selected["id"]
        journeys = payload(await call(client, "render", case_id=case_id, view="journeys", format="text"))
        assert journeys["subject"] == "candidate" and "Registrar" in journeys["content"]
        rules = payload(await call(client, "render", case_id=case_id, view="rules", format="json"))
        assert isinstance(rules["content"], list) and "not a second source of truth" in rules["derived"]
        assert "states" in payload(await call(client, "render", case_id=case_id, view="states", format="text"))["view"]
        missing = await call(client, "render", case_id=case_id, view="journeys", format="mermaid")
        assert missing.is_error and "DIAGRAMS_NOT_AVAILABLE" in missing.content[0].text
    session(studio)(block)

    def fake(model, view, format):
        return f"{format}:{view}:{len(model.states)}"
    async def wired(client):
        got = payload(await call(client, "render", case_id=selected["id"], view="states", format="mermaid"))
        assert got["content"] == "mermaid:states:5"
    session(studio, diagram_renderer=fake)(wired)


def test_resources_language_and_adrs(studio):
    async def block(client):
        uris = {str(r.uri) for r in (await client.list_resources()).resources}
        assert {"eija://agent/contract", "eija://language", "eija://adr"} <= uris
        language = (await client.read_resource("eija://language")).contents[0].text
        assert "**Change Case:**" in language and "**Evidence Receipt:**" in language
        assert "0016" in (await client.read_resource("eija://adr")).contents[0].text
        assert "OSS first" in (await client.read_resource("eija://adr/0016")).contents[0].text
        assert "may not" in (await client.read_resource("eija://agent/contract")).contents[0].text.lower()
        for bad in ("eija://adr/9999", "eija://adr/..%2F..%2FAGENTS", "eija://adr/abc"):
            with pytest.raises(MCPError):
                await client.read_resource(bad)
    session(studio)(block)


# ---- sealed material: every tool -----------------------------------------------------------------
SEALED_KEYS = {"expected", "local_signature", "seal", "signature"}


def _walk(value, path=()):
    """Every (path, key, value) triple of nested dicts and lists."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield path, key, item
            yield from _walk(item, (*path, key))
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item, path)


def sealed_material_violations(outputs, studio, case_id) -> list[str]:
    """The real leak scan. Checks structure, not just strings: a substring scan misses a 9-character answer like
    "Registrar" or a re-labelled key (review of PR #23: `hint: expected` passed the old scan).

    1. no key anywhere is a sealed key (expected answers, seals, signatures);
    2. every `questions` item has exactly the keys {id, question};
    3. no dict pairs a question id with its expected value, and no long expected answer appears as text;
    4. the local signature, and the workspace path, appear nowhere."""
    decision = studio.view(case_id)["case"]["decision"] or {}
    expected = {q["id"]: q["expected"] for q in studio.view(case_id)["packet"]["questions"]}
    problems: list[str] = []
    for label, result in outputs:
        content = result.structured_content if result.structured_content is not None else {"text": result.content[0].text}
        text = json.dumps(content) + result.content[0].text
        for path, key, value in _walk(content):
            if key in SEALED_KEYS:
                problems.append(f"{label}: sealed key {key!r} at {'.'.join(map(str, path)) or '<root>'}")
            if key == "questions" and isinstance(value, list):
                problems += [f"{label}: question item has keys {sorted(q)}" for q in value if set(q) != {"id", "question"}]
            if isinstance(value, dict) and any(isinstance(v, str) and v in expected for v in value.values()):
                answered = [expected[v] for v in value.values() if isinstance(v, str) and v in expected]
                if any(v == answer for v in value.values() if isinstance(v, str) for answer in answered):
                    problems.append(f"{label}: a question id is paired with its expected answer")
        problems += [f"{label}: {secret!r} in output" for secret in
                     (decision.get("local_signature"), str(studio.store.directory), *(a for a in expected.values() if len(a) > 12))
                     if secret and secret in text]
    return problems


async def _all_outputs(client, case_id, created=None):
    outputs = [("list_cases", await call(client, "list_cases")),
               ("view_case", await call(client, "view_case", case_id=case_id)),
               ("impact", await call(client, "impact", case_id=case_id)),
               ("verify", await call(client, "verify", case_id=case_id))]
    outputs += [(f"render {view} {fmt}", await call(client, "render", case_id=case_id, view=view, format=fmt))
                for view in ("rules", "states", "journeys") for fmt in ("json", "text")]
    outputs += [("pack", await call(client, "pack")),
                ("affordances", await call(client, "affordances", case_id=case_id)),
                ("edit_check", await call(client, "edit_check", case_id=case_id,
                                          proposal={"kind": "retarget_transition", "transition": "TR-REJECT",
                                                       "end": "source", "state": "Submitted"})),
                ("repository_impact", await call(client, "repository_impact", term="unknown")),
                ("repository_source", await call(client, "repository_source", reference="repo://src/unknown.py"))]
    outputs.append(("create_case", await call(client, "create_case", request=REQUEST)))
    outputs.append(("propose", await call(client, "propose", case_id=created or case_id)))
    return outputs


def test_no_tool_leaks_sealed_material_after_owner_approval(studio, verified):
    """Every tool that returns case data, including create_case and propose, scanned after approval."""
    approved = approve(studio, verified)
    fresh = studio.create(REQUEST)  # a DRAFT case for propose (an approved case is past proposing)

    async def block(client):
        outputs = await _all_outputs(client, approved["id"], created=fresh["id"])
        assert sealed_material_violations(outputs, studio, approved["id"]) == []
    session(studio)(block)


def test_leak_scan_has_teeth(studio, verified, monkeypatch):
    """Negative control on the REAL scan: a view_case that hints the expected answers, and a render that returns the
    sealed decision, must each be reported. (The old scan passed the first one.)"""
    approved = approve(studio, verified)
    real_view, real_render = AgentSurface.view_case, AgentSurface.render

    def hinting(self, case_id):
        out = real_view(self, case_id)
        expected = {q["id"]: q["expected"] for q in self.port.view(case_id)["packet"]["questions"]}
        out["questions"] = [{**q, "hint": expected[q["id"]]} for q in out["questions"]]
        return out

    def sealing(self, case_id, view, fmt):
        return real_render(self, case_id, view, fmt) | {"x": self.port.view(case_id)["case"]["decision"]}

    async def scan(client):
        outputs = [("view_case", await call(client, "view_case", case_id=approved["id"])),
                   ("render", await call(client, "render", case_id=approved["id"], view="rules", format="json"))]
        return sealed_material_violations(outputs, studio, approved["id"])

    assert session(studio)(scan) == []  # the honest server is clean
    monkeypatch.setattr(AgentSurface, "view_case", hinting)
    leaked = session(studio)(scan)
    assert any("question item has keys" in v for v in leaked), leaked
    monkeypatch.setattr(AgentSurface, "render", sealing)
    leaked = session(studio)(scan)
    assert any("render" in v and ("sealed key" in v or "in output" in v) for v in leaked), leaked


def test_real_stdio_server_starts_lists_tools_and_answers(tmp_path):
    params = StdioServerParameters(command=sys.executable, args=["-m", "eija_studio", "mcp", "--workspace", str(tmp_path / "w")])

    async def main():
        async with Client(params) as client:
            tools = await client.list_tools()
            created = await client.call_tool("create_case", {"request": REQUEST})
            return sorted(t.name for t in tools.tools), created.is_error
    names, errored = asyncio.run(main())
    assert names == sorted(AGENT_TOOLS) and errored is False


def _rpc(identifier, method, params=None):
    message = {"jsonrpc": "2.0", "method": method}
    if identifier is not None:
        message["id"] = identifier
    if params is not None:
        message["params"] = params
    return json.dumps(message)


def _drive_raw_server(workspace, lines, expected_ids, timeout=90):
    """Run `eija mcp` as a raw subprocess, write JSON-RPC lines, collect EVERY stdout line until all replies arrive."""
    # A pipe left unread while collecting stdout can block the child before its next reply.
    with tempfile.TemporaryFile() as stderr_capture:
        process = subprocess.Popen([sys.executable, "-m", "eija_studio", "mcp", "--workspace", str(workspace)],  # noqa: S603 - fixed argv: this interpreter, no shell
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr_capture)
        watchdog = threading.Timer(timeout, process.kill)
        stdout_lines: list[str] = []
        try:
            watchdog.start()
            for line in lines:
                process.stdin.write((line + "\n").encode("utf-8"))
            process.stdin.flush()
            seen: set = set()
            while not expected_ids <= seen:
                raw = process.stdout.readline()
                if not raw:
                    break
                stdout_lines.append(raw.decode("utf-8"))
                try:
                    message = json.loads(stdout_lines[-1])
                except ValueError:
                    continue
                if isinstance(message, dict) and "id" in message:
                    seen.add(message["id"])
            process.stdin.close()
            rest = process.stdout.read().decode("utf-8")  # anything the server prints after the last reply counts too
            stdout_lines.extend(part + "\n" for part in rest.split("\n") if part)
            process.wait(timeout=30)
            stderr_capture.seek(0)
            stderr = stderr_capture.read().decode("utf-8", "replace")
        finally:
            watchdog.cancel()
            try:
                process.kill()
                process.wait(timeout=30)
            finally:
                try:
                    process.stdin.close()
                except OSError as error:
                    # Match Popen's stdin cleanup: Windows reports EINVAL when the child has closed its pipe.
                    if error.errno not in (errno.EPIPE, errno.EINVAL):
                        raise
                finally:
                    process.stdout.close()
    return stdout_lines, stderr


def _raw_driver_fixture(monkeypatch, workspace, script):
    """Substitute only the expected server argv with a disposable deterministic child."""
    popen = subprocess.Popen
    children, captures = [], []

    def start(argv, **kwargs):
        assert argv == [sys.executable, "-m", "eija_studio", "mcp", "--workspace", str(workspace)]
        assert kwargs["stdin"] == kwargs["stdout"] == subprocess.PIPE
        assert "shell" not in kwargs
        child = popen([sys.executable, "-u", "-c", script], **kwargs)  # Fixed disposable Python fixture, no shell.
        children.append(child)
        captures.append(kwargs["stderr"])
        return child

    monkeypatch.setattr(subprocess, "Popen", start)
    return children, captures


def test_raw_driver_collects_stderr_without_blocking_stdout(tmp_path, monkeypatch):
    """Exceed pipe capacity before the final reply; preserve all stdout and exact stderr."""
    workspace = tmp_path / "raw-fixture"
    first = '{"jsonrpc":"2.0","id":41,"result":{}}\n'
    last = '{"jsonrpc":"2.0","id":42,"result":{}}\n'
    noise, tail = "unrelated stdout before replies\n", "unrelated stdout after replies\n"
    marker = b"stderr fixture ready\n"
    script = (
        "import sys\n"
        "assert sys.stdin.buffer.readline()\n"
        f"sys.stderr.buffer.write({marker!r})\n"
        "sys.stderr.buffer.flush()\n"
        f"sys.stdout.buffer.write({(noise + first).encode('utf-8')!r})\n"
        "sys.stdout.flush()\n"
        "sys.stderr.buffer.write(b'stderr diagnostic\\n' * 131072 + b'\\xff\\n')\n"
        "sys.stderr.buffer.flush()\n"
        f"sys.stdout.buffer.write({last.encode('utf-8')!r})\n"
        "sys.stdout.flush()\n"
        "assert sys.stdin.buffer.read() == b''\n"
        f"sys.stdout.buffer.write({tail.encode('utf-8')!r})\n"
    )
    children, captures = _raw_driver_fixture(monkeypatch, workspace, script)
    stdout, stderr = _drive_raw_server(workspace, [_rpc(41, "fixture")], {41, 42}, timeout=3)

    assert stdout == [noise, first, last, tail]
    expected_stderr = marker + b"stderr diagnostic\n" * 131072 + b"\xff\n"
    assert stderr == expected_stderr.decode("utf-8", "replace")
    assert len(children) == len(captures) == 1
    assert children[0].poll() is not None
    assert children[0].stdin.closed and children[0].stdout.closed and captures[0].closed


def test_raw_driver_preserves_missing_reply_and_unrelated_stdout(tmp_path, monkeypatch):
    workspace = tmp_path / "raw-missing-reply"
    first = '{"jsonrpc":"2.0","id":41,"result":{}}\n'
    noise = "unrelated stdout before exit\n"
    script = "import sys\nassert sys.stdin.buffer.readline()\n" + f"sys.stdout.buffer.write({(noise + first).encode('utf-8')!r})\n"
    _raw_driver_fixture(monkeypatch, workspace, script)

    stdout, stderr = _drive_raw_server(workspace, [_rpc(41, "fixture")], {41, 42}, timeout=3)

    assert stdout == [noise, first]  # Missing replies and pollution remain visible to the protocol oracle.
    assert stderr == ""


def test_raw_driver_reaps_child_and_closes_streams_on_input_error(tmp_path, monkeypatch):
    workspace = tmp_path / "raw-input-error"
    children, captures = _raw_driver_fixture(monkeypatch, workspace, "import sys; sys.stdin.buffer.read()")

    def broken_lines():
        yield _rpc(41, "fixture")
        raise RuntimeError("fixture input failed")

    with pytest.raises(RuntimeError, match="fixture input failed"):
        _drive_raw_server(workspace, broken_lines(), {41}, timeout=3)

    assert len(children) == len(captures) == 1
    assert children[0].poll() is not None
    assert children[0].stdin.closed and children[0].stdout.closed and captures[0].closed


_INIT = [
    _rpc(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "raw-test", "version": "0"}}),
    _rpc(None, "notifications/initialized"),
]


def _call(identifier, name, **arguments):
    return _rpc(identifier, "tools/call", {"name": name, "arguments": arguments})


def _created_case_id(workspace) -> str:
    """A case created by a first raw server session, so the second can drive every tool on a real case."""
    lines, _ = _drive_raw_server(workspace, [*_INIT, _call(2, "create_case", request=REQUEST)], expected_ids={1, 2})
    reply = next(json.loads(line) for line in lines if json.loads(line).get("id") == 2)
    return json.loads(reply["result"]["content"][0]["text"])["id"]


def test_stdout_of_the_real_server_is_only_json_rpc(tmp_path):
    case = _created_case_id(tmp_path / "w")
    lines = [
        *_INIT,
        "this line is not json at all",                       # garbage must not make the server print to stdout
        _rpc(2, "tools/list", {}),
        _call(3, "create_case", request=REQUEST),
        _call(4, "view_case", case_id="../../etc/passwd"),   # tool error path
        _call(5, "propose", case_id="0" * 32),               # kernel error path
        _rpc(6, "resources/read", {"uri": "eija://adr/9999"}),                                        # protocol error path
        _rpc(7, "tools/call", {"name": "no_such_tool", "arguments": {}}),
        # the SUCCESS paths of every tool (a print planted in one of these once went unnoticed: review of PR #23)
        _call(8, "list_cases"), _call(9, "view_case", case_id=case), _call(10, "impact", case_id=case),
        _call(11, "verify", case_id=case), _call(12, "render", case_id=case, view="rules", format="text"),
        _call(13, "propose", case_id=case),
    ]
    ids_expected = set(range(1, 14))
    stdout_lines, _stderr = _drive_raw_server(tmp_path / "w", lines, expected_ids=ids_expected)
    ids = set()
    replies = {}
    for line in stdout_lines:
        message = json.loads(line)  # every single stdout line must parse
        assert isinstance(message, dict) and message.get("jsonrpc") == "2.0", line
        assert "result" in message or "error" in message or "method" in message, line
        ids.add(message.get("id"))
        replies[message.get("id")] = message
    assert ids_expected <= ids
    assert "Traceback" not in "".join(stdout_lines)
    assert all("result" in replies[i] and not replies[i]["result"].get("isError") for i in (8, 9, 10, 12)), "the read tools succeed on a real case"
    assert "Traceback" not in "".join(map(str, replies.values()))


def test_startup_refusal_of_the_real_server_writes_nothing_to_stdout(tmp_path):
    done = subprocess.run([sys.executable, "-m", "eija_studio", "mcp", "--workspace", str(tmp_path / "w"), "--provider", "openrouter"],  # noqa: S603 - fixed argv: this interpreter, no shell
                          capture_output=True, timeout=60, check=False)
    assert done.returncode == 2 and done.stdout == b""
    assert b"CONFIGURATION" in done.stderr


def test_unicode_huge_and_hostile_inputs_never_leak_paths_or_tracebacks(tmp_path):
    hostile_ids = ["../../etc/passwd", "..\\..\\Windows\\win.ini", "A" * 100_000, "\u202e\u0000\u00e9\U0001f600" * 40,
                   "0" * 31 + "g", "0" * 32 + "\n", "", "%2e%2e%2f", "C:\\Windows\\System32"]
    workspace = tmp_path / "w"
    params = StdioServerParameters(command=sys.executable, args=["-m", "eija_studio", "mcp", "--workspace", str(workspace)])
    forbidden = ("Traceback", str(tmp_path), str(ROOT), "site-packages", 'File "', "receipt.key", "sqlite")

    async def main():
        texts = []
        async with Client(params) as client:
            for case_id in hostile_ids:
                for tool in ("view_case", "impact", "verify", "propose"):
                    result = await client.call_tool(tool, {"case_id": case_id})
                    assert result.is_error, (tool, case_id[:20])
                    texts.append(result.content[0].text)
            for name in ("select", "approve", "apply", "edit", "nope", "../../x", "eija://adr"):
                result = await client.call_tool(name, {"case_id": "0" * 32})
                assert result.is_error and result.content[0].text == f"Unknown tool: {name}"
            for arguments in ({"request": "x" * 6001}, {"request": "x" * 3_000_000}, {"request": "   "}, {"request": "\U0001f600" * 6001}):
                result = await client.call_tool("create_case", arguments)
                assert result.is_error and "INVALID_REQUEST" in result.content[0].text
                texts.append(result.content[0].text)
            # Awkward but legitimate text is stored and returned as data, never interpreted.
            awkward = "\u202e\U0001f600 <script>alert(1)</script> \u00e9 \\..\\"
            ok = await client.call_tool("create_case", {"request": awkward})
            assert not ok.is_error
            created_id = json.loads(ok.content[0].text)["id"]
            view = json.loads((await client.call_tool("view_case", {"case_id": created_id})).content[0].text)
            assert view["case"]["request"] == awkward
            for bad in ("eija://adr/../../AGENTS", "eija://adr/00%2e%2e", "eija://adr/0016\n", "file:///C:/Windows/win.ini"):
                with pytest.raises(MCPError) as caught:
                    await client.read_resource(bad)
                texts.append(str(caught.value))
        return texts
    for text in asyncio.run(main()):
        for marker in forbidden:
            assert marker not in text, (marker, text[:200])


def test_studio_ui_renders_agent_authored_text_only_as_text():
    """Agent-authored request text reaches the owner's browser; the UI must never treat it as markup."""
    web = ROOT / "src/eija_studio/resources/web"
    script = (web / "app.js").read_text(encoding="utf-8")
    for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function", "setAttribute(\"on"):
        assert sink not in script, sink
    assert "textContent" in script and "script-src 'self'" in (ROOT / "src/eija_studio/interfaces/http.py").read_text(encoding="utf-8")
