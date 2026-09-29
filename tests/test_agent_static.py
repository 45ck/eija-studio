"""Agent-lane checks that need no MCP SDK: the owner-operation lint (with negative controls), the client
config snippets, the docs and the skills.

They run whether or not the `agents` extra is installed. The SDK-driven behaviour is in test_mcp_server.py.
"""
from __future__ import annotations

import ast
import json
import re
import shlex
import sys
import tomllib
from pathlib import Path

import pytest

from eija_studio.interfaces import agent_config
from eija_studio.interfaces.cli import main as cli_main

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src/eija_studio/interfaces/mcp_server.py"

#: `Studio` attributes StudioAgentPort may read; `store` only as `store.list_cases`.
ALLOWED_STUDIO = {"store", "create", "propose", "verify", "view", "provider"}
#: The methods AgentSurface may call on its port.
ALLOWED_PORT = {"list_cases", "create", "propose", "verify", "view", "networked"}
#: Builtins that could reach an attribute by a computed name and so defeat the name checks.
DYNAMIC = {"getattr", "setattr", "delattr", "eval", "exec", "__import__", "vars", "globals"}


def module_constant(name: str):
    """Read a literal module-level constant of the adapter without importing it (the SDK may be absent)."""
    for node in ast.parse(ADAPTER.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == name:
            return ast.literal_eval(node.value)
    raise AssertionError(name)


AGENT_TOOLS = module_constant("AGENT_TOOLS")
OWNER_ONLY = module_constant("OWNER_ONLY_OPERATIONS")
STORE_WRITES = module_constant("STORE_WRITE_NAMES")


def owner_operation_violations(source: str) -> list[str]:
    """Best-effort lint of the adapter source. Establishes: none of the listed patterns occurs. Does NOT
    prove the adapter cannot reach an owner operation (a determined author can always evade a lint); the
    structural guarantee is that AgentSurface holds a five-method port, not the Studio."""
    tree = ast.parse(source)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    problems: list[str] = []

    def enclosing_class(node: ast.AST) -> str | None:
        while node in parents:
            node = parents[node]
            if isinstance(node, ast.ClassDef):
                return node.name
        return None

    for node in ast.walk(tree):
        where = f"line {getattr(node, 'lineno', '?')}"
        if isinstance(node, ast.Attribute):
            if node.attr in set(OWNER_ONLY) | set(STORE_WRITES):
                problems.append(f"{where}: attribute {node.attr!r} names an owner or store-write operation")
            if node.attr == "OWNER":
                problems.append(f"{where}: OWNER referenced")
            if node.attr == "_studio" and isinstance(node.ctx, ast.Load):
                parent = parents[node]
                if enclosing_class(node) != "StudioAgentPort":
                    problems.append(f"{where}: _studio read outside StudioAgentPort")
                elif not (isinstance(parent, ast.Attribute) and parent.value is node and parent.attr in ALLOWED_STUDIO):
                    problems.append(f"{where}: _studio aliased or used beyond {sorted(ALLOWED_STUDIO)}")
                elif parent.attr == "store":
                    grand = parents[parent]
                    if not (isinstance(grand, ast.Attribute) and grand.value is parent and grand.attr == "list_cases"):
                        problems.append(f"{where}: only store.list_cases is allowed")
            if isinstance(node.value, ast.Attribute) and node.value.attr == "port" and node.attr not in ALLOWED_PORT:
                problems.append(f"{where}: port.{node.attr} is not part of AgentPort")
        elif isinstance(node, ast.Name):
            if node.id == "OWNER":
                problems.append(f"{where}: OWNER referenced")
            if node.id == "studio" and isinstance(node.ctx, ast.Load):
                parent = parents[node]
                is_port_ctor = isinstance(parent, ast.Call) and getattr(parent.func, "id", None) in {"StudioAgentPort", "create_server"}
                is_port_field = isinstance(parent, ast.Assign) and enclosing_class(node) == "StudioAgentPort"
                is_keyword = isinstance(parent, ast.keyword)
                if not (is_port_ctor or is_port_field or is_keyword):
                    problems.append(f"{where}: bare `studio` used other than to construct the port")
            if node.id in DYNAMIC and isinstance(node.ctx, ast.Load):
                problems.append(f"{where}: dynamic attribute/eval builtin {node.id!r}")
        elif isinstance(node, ast.alias) and node.name == "OWNER":
            problems.append(f"{where}: OWNER imported")
    return problems


def mutated(after: str, insertion: str) -> str:
    """The real adapter source with `insertion` (one line, indented like `after`) added after the first `after` line."""
    lines = ADAPTER.read_text(encoding="utf-8").splitlines()
    index = next(i for i, line in enumerate(lines) if line.strip() == after.strip())
    indent = re.match(r"\s*", lines[index]).group(0)
    return "\n".join([*lines[: index + 1], indent + insertion, *lines[index + 1:]])


# ---- the lint itself ---------------------------------------------------------------------------
def test_adapter_source_passes_the_owner_operation_lint():
    assert owner_operation_violations(ADAPTER.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize(("label", "after", "insertion"), [
    ("bare-name owner call", "port = StudioAgentPort(studio)", '_f = lambda: studio.approve("x", 0, "h", {}, True, None)'),
    ("bare-name alias", "port = StudioAgentPort(studio)", "_s = studio"),
    ("private studio in the factory", "port = StudioAgentPort(studio)", "_f = lambda: port._studio.select"),
    ("store write via the port", "port = StudioAgentPort(studio)", "_f = lambda: port._studio.store.transaction()"),
    ("store write via a surface", "self.port = port", "_f = self.port.store.set_active"),
    ("owner method on the port", "self.port = port", "_f = self.port.approve"),
    ("computed attribute name", "port = StudioAgentPort(studio)", '_f = getattr(port, "app" + "rove")'),
    ("owner principal imported", "from eija_studio.domain.policy import projections", "from eija_studio.domain.models import OWNER"),
    ("owner principal by attribute", "port = StudioAgentPort(studio)", "_p = models.OWNER"),
])
def test_lint_catches_owner_reach_mutations(label, after, insertion):
    """Negative controls: each mutation is a way an edit could give the adapter owner power. Leaking data is
    a redaction question, not an owner-operation one; test_mcp_server.py scans every tool's output for that."""
    assert owner_operation_violations(mutated(after, insertion)), f"lint missed: {label}"


def test_studio_agent_port_exposes_exactly_the_agent_port():
    tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
    port = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "StudioAgentPort")
    public = {n.name for n in port.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")}
    assert public == ALLOWED_PORT, public ^ ALLOWED_PORT
    protocol = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "AgentPort")
    declared = {n.name for n in protocol.body if isinstance(n, ast.FunctionDef)} | {
        n.target.id for n in protocol.body if isinstance(n, ast.AnnAssign)}
    assert declared == ALLOWED_PORT


# ---- CLI ---------------------------------------------------------------------------------------
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


def test_non_mcp_commands_still_report_errors_on_stdout(tmp_path, capsys):
    assert cli_main(["verify", "0" * 32, "--expected-version", "0", "--workspace", str(tmp_path / "w")]) == 2
    captured = capsys.readouterr()
    assert "NOT_FOUND" in captured.out and captured.err == ""


def _hide_sdk(monkeypatch, *names):
    """Make `import mcp...` fail as if the SDK (or one of its submodules) were absent, even if tests imported it before."""
    for name in [n for n in sys.modules if n == "mcp" or n.startswith(("mcp.", "eija_studio.interfaces.mcp_server"))]:
        monkeypatch.delitem(sys.modules, name)
    for name in names:
        monkeypatch.setitem(sys.modules, name, None)


def test_missing_sdk_reports_missing_extra_on_stderr_before_creating_the_workspace(tmp_path, capsys, monkeypatch):
    _hide_sdk(monkeypatch, "mcp")
    assert cli_main(["mcp", "--workspace", str(tmp_path / "w")]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "MISSING_EXTRA" in captured.err
    assert not (tmp_path / "w").exists()


def test_a_wrong_sdk_version_is_not_reported_as_a_missing_extra(tmp_path, capsys, monkeypatch):
    """`mcp<2` has no `mcp.server.mcpserver`: a version fault with its own code and cause, not 'install the extra'."""
    pytest.importorskip("mcp", reason="needs the installed SDK, only its submodule is faked as missing")
    _hide_sdk(monkeypatch, "mcp.server.mcpserver")
    assert cli_main(["mcp", "--workspace", str(tmp_path / "w")]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "MCP_SDK_INCOMPATIBLE" in captured.err and "mcpserver" in captured.err
    assert "MISSING_EXTRA" not in captured.err and not (tmp_path / "w").exists()


# ---- config snippets ---------------------------------------------------------------------------
@pytest.mark.parametrize("client", agent_config.CLIENTS)
def test_print_config_is_valid_for_each_client(client, tmp_path, capsys):
    assert cli_main(["mcp", "--workspace", str(tmp_path / "w"), "--print-config", client]) == 0
    text = capsys.readouterr().out
    workspace = str((tmp_path / "w").resolve())
    assert text.endswith("\n")
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


def test_claude_snippet_is_quoted_for_the_target_shell(tmp_path):
    workspace = tmp_path / "My Docs" / "ws"
    windows = agent_config.snippet("claude", "C:\\Py thon\\python.exe", workspace, windows=True)
    assert '"C:\\Py thon\\python.exe"' in windows and "'" not in windows  # cmd.exe passes single quotes literally
    posix = agent_config.snippet("claude", "/opt/py thon/python", workspace, windows=False)
    assert "'/opt/py thon/python'" in posix and '"' not in posix


def test_toml_snippet_survives_hostile_workspace_paths(tmp_path):
    """Non-BMP characters (JSON would emit surrogate-pair escapes, invalid in TOML), quotes and DEL round-trip."""
    workspace = tmp_path / ("a\U0001F600b\x7f" + '"q\\')
    server = tomllib.loads(agent_config.snippet("codex", "py", workspace))["mcp_servers"]["eija"]
    assert server["args"][-1] == str(workspace.resolve())


# ---- docs and skills ---------------------------------------------------------------------------
def test_docs_name_every_tool_and_forbid_every_owner_operation():
    contract = (ROOT / "docs/agents/contract.md").read_text(encoding="utf-8")
    quickstart = (ROOT / "docs/agents/quickstart.md").read_text(encoding="utf-8")
    for tool in AGENT_TOOLS:
        assert f"`{tool}`" in contract, tool
    for operation in ("select", "edit", "approve", "apply"):
        assert f"`{operation}`" in contract.split("## What an agent may not do")[1], operation
    for client in ("claude mcp add", "[mcp_servers.eija]", '"mcp"', '"mcpServers"'):
        assert client in quickstart, client
    assert "--max-provider-calls" in quickstart and "--max-provider-calls" in contract


def test_quickstart_snippets_match_the_generated_config():
    """Drift check: the placeholder snippets in the quickstart are what `--print-config` generates, PY/WS filled in."""
    quickstart = (ROOT / "docs/agents/quickstart.md").read_text(encoding="utf-8")
    workspace = str(Path("WS").resolve())

    def normalised(client: str) -> str:
        text = agent_config.snippet(client, "PY", Path("WS"), windows=False)
        # json.dumps doubles Windows backslashes; shlex may quote the path. Undo both to reach the placeholder.
        for spelling in (json.dumps(workspace)[1:-1], shlex.quote(workspace), workspace):
            text = text.replace(spelling, "WS")
        return text

    for line in normalised("codex").splitlines():
        assert line in quickstart, line
    assert json.dumps(json.loads(normalised("opencode"))["mcp"]["eija"]["command"]) in quickstart
    gemini = json.loads(normalised("gemini"))["mcpServers"]["eija"]
    assert json.dumps(gemini["args"]) in quickstart and f'"timeout": {gemini["timeout"]}, "trust": false' in quickstart
    assert normalised("claude").strip() in quickstart


SKILLS = [".agents/skills/eija-studio/SKILL.md", ".claude/skills/eija-studio/SKILL.md"]


@pytest.mark.parametrize("path", SKILLS)
def test_skills_name_every_tool_and_pre_approve_none(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    assert text.startswith("---\nname: eija-studio\n")
    for tool in AGENT_TOOLS:
        assert tool in text, tool
    assert "allowed-tools" not in text  # a skill must not silently pre-approve tool calls (some reach networked providers)
    assert "no select, edit, approve or apply tool" in text


def test_the_two_skills_differ_only_by_the_claude_code_tool_name_note():
    generic, claude = ((ROOT / p).read_text(encoding="utf-8") for p in SKILLS)
    note = " (in Claude Code they appear as `mcp__eija__<tool>`)"
    assert claude.replace(note, "") == generic and note in claude
