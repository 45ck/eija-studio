"""MCP adapter tests, driven through the SDK's in-memory client/server session.

They prove: the exposed surface is exactly the agent surface; owner operations are absent and
unreachable; kernel authority errors surface; consent and answers cannot be supplied by an agent;
sealed material does not leak; and the real stdio entry point starts and answers.
"""
from __future__ import annotations

import ast
import asyncio
import json
import sys
import tomllib
from pathlib import Path

import pytest

pytest.importorskip("mcp", reason="install the agents extra: pip install -e '.[agents]'")

from mcp import Client, StdioServerParameters  # noqa: E402
from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402

from conftest import approve  # noqa: E402
from eija_studio.application.ports import ProviderResult  # noqa: E402
from eija_studio.domain.models import AGENT, OWNER, DomainError, Principal, Proposal, Alternative  # noqa: E402
from eija_studio.interfaces import agent_config  # noqa: E402
from eija_studio.interfaces.cli import main as cli_main  # noqa: E402
from eija_studio.interfaces.mcp_server import (  # noqa: E402
    AGENT_TOOLS, ALLOWED_STUDIO_CALLS, OWNER_ONLY_OPERATIONS, AgentSurface, create_server)

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

    def doctor(self):
        return {"provider": self.name, "ready": True}

    def propose(self, request, model):
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


def test_surface_runs_as_agent_and_refuses_an_owner_principal(studio):
    assert AgentSurface(studio).principal is AGENT and not AGENT.capabilities
    with pytest.raises(ValueError):
        AgentSurface(studio, principal=OWNER)
    with pytest.raises(ValueError):
        AgentSurface(studio, principal=Principal(id="x", capabilities=frozenset({"select"})))


def test_kernel_authority_errors_surface_as_tool_errors(studio, selected):
    surface = AgentSurface(studio)
    case = selected["id"], selected["version"]
    for attempt in (lambda: studio.select(case[0], case[1], "recommend_only", surface.principal),
                    lambda: studio.approve(case[0], case[1], "0" * 64, {}, True, surface.principal),
                    lambda: studio.apply(case[0], case[1], surface.principal)):
        with pytest.raises(ToolError, match="AUTHORITY_REQUIRED"):
            surface.guarded(attempt)


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
            with pytest.raises(Exception):
                await client.read_resource(bad)
    session(studio)(block)


# ---- CLI and docs ------------------------------------------------------------------------------
def test_cli_refuses_unsafe_mcp_configuration(tmp_path, capsys):
    base = ["mcp", "--workspace", str(tmp_path / "w")]
    assert cli_main(base + ["--provider", "openrouter"]) == 2                       # networked, no flags
    assert cli_main(base + ["--provider", "openrouter", "--allow-network"]) == 2    # needs owner consent too
    assert cli_main(base + ["--ask-key", "--provider", "openrouter", "--allow-network", "--egress-consent"]) == 2
    assert "CONFIGURATION" in capsys.readouterr().out
    assert not (tmp_path / "w").exists()  # refused before touching the workspace


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


def test_real_stdio_server_starts_lists_tools_and_keeps_stdout_clean(tmp_path):
    params = StdioServerParameters(command=sys.executable, args=["-m", "eija_studio", "mcp", "--workspace", str(tmp_path / "w")])

    async def main():
        async with Client(params) as client:
            tools = await client.list_tools()
            created = await client.call_tool("create_case", {"request": REQUEST})
            return sorted(t.name for t in tools.tools), created.is_error
    names, errored = asyncio.run(main())
    assert names == sorted(AGENT_TOOLS) and errored is False
