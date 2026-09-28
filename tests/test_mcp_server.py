"""MCP adapter tests, driven through the SDK's in-memory client/server session.

They prove: the exposed surface is exactly the agent surface; owner operations are absent and
unreachable; kernel domain errors and unexpected errors surface safely; consent and answers cannot be
supplied by an agent and networked calls are capped; sealed material does not leak; and the real stdio
entry point starts, answers and keeps stdout to JSON-RPC only.
"""
from __future__ import annotations

import ast
import asyncio
import json
import subprocess
import sys
import threading
import tomllib
from pathlib import Path

import pytest

pytest.importorskip("mcp", reason="install the agents extra: pip install -e '.[agents]'")

from mcp import Client, MCPError, StdioServerParameters
from mcp.server.mcpserver.exceptions import ToolError

from conftest import approve
from eija_studio.application.ports import ProviderResult
from eija_studio.domain.models import OWNER, DomainError, Proposal, Alternative
from eija_studio.interfaces import agent_config
from eija_studio.interfaces.cli import main as cli_main
from eija_studio.interfaces.mcp_server import (
    AGENT_TOOLS, ALLOWED_STUDIO_CALLS, OWNER_ONLY_OPERATIONS, AgentSurface, _owner_next, create_server)

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
        assert not any(forbidden in name for name in names), forbidden
    # An agent cannot smuggle consent, meaning or answers through a tool argument.
    smuggled = {"consent", "interpretation", "answers", "subject_hash", "acknowledge_unknowns", "transaction", "principal"}
    for tool in tools.tools:
        assert not smuggled & set(tool.input_schema.get("properties", {})), tool.name
    hints = {t.name: t.annotations for t in tools.tools}
    assert all(h is not None and h.destructive_hint is False for h in hints.values())
    assert hints["view_case"].read_only_hint is True and hints["verify"].read_only_hint is False


def test_calling_an_owner_operation_is_an_error_not_a_dispatch(studio):
    async def block(client):
        for name in ("select", "select_meaning", "edit", "approve", "apply"):
            result = await client.call_tool(name, {"case_id": "0" * 32})
            assert result.is_error and "Unknown tool" in result.content[0].text, name
    session(studio)(block)


def test_mcp_never_calls_owner_operations_on_studio():
    source = (ROOT / "src/eija_studio/interfaces/mcp_server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    called = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Attribute)
              and n.value.attr == "studio"}
    assert called <= ALLOWED_STUDIO_CALLS, called - ALLOWED_STUDIO_CALLS
    assert not called & set(OWNER_ONLY_OPERATIONS)
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert "OWNER" not in names, "the MCP adapter must never hold the owner principal"


def test_surface_holds_no_principal_so_nothing_pretends_to_enforce_authority(studio):
    # The guarantee is that owner tools are absent (tests above), not a principal check: the adapter has none.
    assert not hasattr(AgentSurface(studio), "principal")
    with pytest.raises(TypeError):
        AgentSurface(studio, principal=OWNER)  # type: ignore[call-arg]


def test_kernel_domain_errors_reach_the_agent_through_a_tool_path(studio, selected):
    async def block(client):
        # Studio refuses to reinterpret a case whose meaning the owner already selected.
        result = await call(client, "propose", case_id=selected["id"])
        assert result.is_error and "CASE_ALREADY_SELECTED" in result.content[0].text
        stale = await call(client, "propose", case_id=selected["id"], expected_version=selected["version"] + 9)
        assert stale.is_error and "STALE_VERSION" in stale.content[0].text
    session(studio)(block)


def test_guarded_translates_domain_errors_and_hides_unexpected_ones(studio):
    surface = AgentSurface(studio)

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
        AgentSurface(studio, max_provider_calls=-1)


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


# ---- CLI and docs ------------------------------------------------------------------------------
def test_cli_refuses_unsafe_mcp_configuration_on_stderr_never_stdout(tmp_path, capsys):
    base = ["mcp", "--workspace", str(tmp_path / "w")]
    unsafe = ([*base, "--provider", "openrouter"],                                        # networked, no flags
              [*base, "--provider", "openrouter", "--allow-network"],                       # needs owner consent too
              [*base, "--ask-key", "--provider", "openrouter", "--allow-network", "--egress-consent"],
              [*base, "--max-provider-calls", "-1"])
    for argv in unsafe:
        assert cli_main(argv) == 2
        captured = capsys.readouterr()
        assert captured.out == "", "stdout is the MCP protocol channel; startup errors must not go there"
        assert "CONFIGURATION" in captured.err
    assert not (tmp_path / "w").exists()  # refused before touching the workspace


def test_missing_extra_is_reported_on_stderr_in_mcp_mode(tmp_path, capsys, monkeypatch):
    monkeypatch.setitem(sys.modules, "eija_studio.interfaces.mcp_server", None)  # makes the import fail
    assert cli_main(["mcp", "--workspace", str(tmp_path / "w")]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "MISSING_EXTRA" in captured.err


def test_non_mcp_commands_still_report_errors_on_stdout(tmp_path, capsys):
    assert cli_main(["verify", "0" * 32, "--expected-version", "0", "--workspace", str(tmp_path / "w")]) == 2
    captured = capsys.readouterr()
    assert "NOT_FOUND" in captured.out and captured.err == ""


@pytest.mark.parametrize("client", agent_config.CLIENTS)
def test_print_config_is_valid_for_each_client(client, tmp_path, capsys):
    assert cli_main(["mcp", "--workspace", str(tmp_path / "w"), "--print-config", client]) == 0
    text = capsys.readouterr().out
    workspace = str((tmp_path / "w").resolve())
    if client == "codex":
        server = tomllib.loads(text)["mcp_servers"]["eija"]
        assert server["command"] == sys.executable and server["args"][:3] == ["-m", "eija_studio", "mcp"] and server["args"][-1] == workspace
    elif client == "opencode":
        server = json.loads(text)["mcp"]["eija"]
        assert server["type"] == "local" and server["command"][0] == sys.executable and server["command"][-1] == workspace
    elif client == "gemini":
        server = json.loads(text)["mcpServers"]["eija"]
        assert server["command"] == sys.executable and server["args"][-1] == workspace and server["trust"] is False
    else:
        assert text.startswith("claude mcp add --scope project eija -- ") and workspace in text
    assert not (tmp_path / "w").exists()  # printing config creates nothing
    with pytest.raises(ValueError):
        agent_config.snippet("unknown", sys.executable, tmp_path)


def test_docs_name_every_tool_and_forbid_every_owner_operation():
    contract = (ROOT / "docs/agents/contract.md").read_text(encoding="utf-8")
    quickstart = (ROOT / "docs/agents/quickstart.md").read_text(encoding="utf-8")
    for tool in AGENT_TOOLS:
        assert f"`{tool}`" in contract, tool
    for operation in ("select", "edit", "approve", "apply"):
        assert f"`{operation}`" in contract.split("## What an agent may not do")[1], operation
    for client in ("claude mcp add", "[mcp_servers.eija]", '"mcp"', '"mcpServers"'):
        assert client in quickstart, client


@pytest.mark.parametrize("path", [".agents/skills/eija-studio/SKILL.md", ".claude/skills/eija-studio/SKILL.md"])
def test_skills_name_every_tool_and_pre_approve_none(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    assert text.startswith("---\nname: eija-studio\n")
    for tool in AGENT_TOOLS:
        assert tool in text, tool
    assert "allowed-tools" not in text  # a skill must not silently pre-approve tool calls (some reach networked providers)
    assert "no select, edit, approve or apply tool" in text


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
    process = subprocess.Popen([sys.executable, "-m", "eija_studio", "mcp", "--workspace", str(workspace)],  # noqa: S603 - fixed argv: this interpreter, no shell
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    watchdog = threading.Timer(timeout, process.kill)
    watchdog.start()
    stdout_lines: list[str] = []
    try:
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
        stderr = process.stderr.read().decode("utf-8", "replace")
    finally:
        watchdog.cancel()
        process.kill()
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()
    return stdout_lines, stderr


def test_stdout_of_the_real_server_is_only_json_rpc(tmp_path):
    lines = [
        _rpc(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "raw-test", "version": "0"}}),
        _rpc(None, "notifications/initialized"),
        "this line is not json at all",                       # garbage must not make the server print to stdout
        _rpc(2, "tools/list", {}),
        _rpc(3, "tools/call", {"name": "create_case", "arguments": {"request": REQUEST}}),
        _rpc(4, "tools/call", {"name": "view_case", "arguments": {"case_id": "../../etc/passwd"}}),   # tool error path
        _rpc(5, "tools/call", {"name": "propose", "arguments": {"case_id": "0" * 32}}),               # kernel error path
        _rpc(6, "resources/read", {"uri": "eija://adr/9999"}),                                        # protocol error path
        _rpc(7, "tools/call", {"name": "no_such_tool", "arguments": {}}),
    ]
    stdout_lines, _stderr = _drive_raw_server(tmp_path / "w", lines, expected_ids={1, 2, 3, 4, 5, 6, 7})
    ids = set()
    for line in stdout_lines:
        message = json.loads(line)  # every single stdout line must parse
        assert isinstance(message, dict) and message.get("jsonrpc") == "2.0", line
        assert "result" in message or "error" in message or "method" in message, line
        ids.add(message.get("id"))
    assert {1, 2, 3, 4, 5, 6, 7} <= ids
    assert "Traceback" not in "".join(stdout_lines)


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
