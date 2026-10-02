"""Agent-lane checks that need no MCP SDK: the owner-operation lint (with negative controls), the client
config snippets, the docs and the skills.

They run whether or not the `agents` extra is installed. The SDK-driven behaviour is in test_mcp_server.py.
"""
from __future__ import annotations

import ast
import json
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from eija_studio.domain.models import DomainError
from eija_studio.interfaces import agent_config, agent_policy
from eija_studio.interfaces.cli import main as cli_main
from quality.sessions import agents as agents_sessions

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src/eija_studio/interfaces/mcp_server.py"

#: `Studio` attributes the port factory may read; `store` only as `store.list_cases`, `provider` only as `provider.networked`.
ALLOWED_STUDIO = {"store", "create", "propose", "verify", "view", "provider", "workbench", "affordances", "edit_check", "repository_impact", "repository_source"}
#: The methods AgentSurface may call on its port.
ALLOWED_PORT = {"list_cases", "create", "propose", "verify", "view", "networked", "workbench", "affordances", "edit_check", "repository_impact", "repository_source"}
#: Builtins and helpers that reach an attribute by a computed name and so defeat the name checks.
DYNAMIC = {"getattr", "setattr", "delattr", "eval", "exec", "__import__", "vars", "globals", "locals", "attrgetter", "methodcaller"}
#: Modules that give computed attribute access or introspection; the adapter has no use for them.
BLOCKED_MODULES = {"operator", "importlib", "inspect", "ctypes", "gc"}
#: Attributes that walk from an object to its class, function internals or namespace.
DUNDER_BLOCKED = {"__dict__", "__class__", "__closure__", "__func__", "__self__", "__globals__", "__getattribute__",
                  "__subclasses__", "__mro__", "__bases__", "__wrapped__", "__code__", "__defaults__", "__reduce__", "__reduce_ex__"}
RULES = ("owner-name", "owner-principal", "studio-reach", "studio-class", "port-member", "dynamic-access", "dunder")


def module_constant(name: str):
    """Read a literal module-level constant of the adapter without importing it (the SDK may be absent)."""
    for node in ast.parse(ADAPTER.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", None) == name:
            return ast.literal_eval(node.value)
    raise AssertionError(name)


AGENT_TOOLS = module_constant("AGENT_TOOLS")
OWNER_ONLY = module_constant("OWNER_ONLY_OPERATIONS")
STORE_WRITES = agent_policy.STORE_WRITE_NAMES  # derived from the persistence ports, SDK-free


def owner_operation_violations(source: str) -> list[tuple[str, str]]:
    """Best-effort lint of the adapter source: ``(rule, message)`` pairs, empty when none of the patterns occurs.

    Establishes: none of the listed patterns occurs. Does NOT prove the adapter cannot reach an owner operation
    (a determined author can always evade a lint). The structural narrowing is that AgentSurface holds a
    five-member port whose Studio lives only in a closure; the lint covers the common spellings of reaching past it.
    Every rule has a negative control that only it catches (test_every_rule_has_a_control_only_it_catches)."""
    tree = ast.parse(source)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    problems: list[tuple[str, str]] = []
    owner_names = set(OWNER_ONLY) | set(STORE_WRITES)

    def ancestors(node: ast.AST):
        while node in parents:
            child, node = node, parents[node]
            yield child, node

    def in_annotation(node: ast.AST) -> bool:
        return any(
            (isinstance(p, ast.arg) and p.annotation is c)
            or (isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)) and p.returns is c)
            or (isinstance(p, ast.AnnAssign) and p.annotation is c)
            for c, p in ancestors(node)
        )

    def inside_function(node: ast.AST, name: str) -> bool:
        return any(isinstance(p, ast.FunctionDef) and p.name == name for _, p in ancestors(node))

    def report(rule: str, node: ast.AST, message: str) -> None:
        problems.append((rule, f"line {getattr(node, 'lineno', '?')}: {message}"))

    def studio_use_allowed(node: ast.Name) -> bool:
        parent = parents[node]
        if isinstance(parent, ast.keyword):  # `create_server(studio=studio)`
            parent = parents[parent]
        if isinstance(parent, ast.Call) and getattr(parent.func, "id", None) in {"StudioAgentPort", "create_server"}:
            return True
        if not (inside_function(node, "StudioAgentPort") and isinstance(parent, ast.Attribute) and parent.value is node
                and parent.attr in ALLOWED_STUDIO):
            return False
        follower = {"store": "list_cases", "provider": "networked"}.get(parent.attr)
        grand = parents[parent]
        return follower is None or (isinstance(grand, ast.Attribute) and grand.value is parent and grand.attr == follower)

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if node.attr in owner_names:
                report("owner-name", node, f"attribute {node.attr!r} names an owner or store-write operation")
            if node.attr == "OWNER":
                report("owner-principal", node, "OWNER referenced")
            if node.attr in DUNDER_BLOCKED:
                report("dunder", node, f"{node.attr} reaches object internals")
            on_port = (isinstance(node.value, ast.Attribute) and node.value.attr == "port") or (
                isinstance(node.value, ast.Name) and node.value.id == "port")
            if on_port and node.attr not in ALLOWED_PORT:
                report("port-member", node, f"port.{node.attr} is not part of AgentPort")
        elif isinstance(node, ast.Name):
            if node.id in owner_names and isinstance(node.ctx, ast.Load):
                report("owner-name", node, f"name {node.id!r} names an owner or store-write operation")
            if node.id == "OWNER":
                report("owner-principal", node, "OWNER referenced")
            if node.id == "studio" and isinstance(node.ctx, ast.Load) and not studio_use_allowed(node):
                report("studio-reach", node, "`studio` used other than to build the port or inside the port factory's delegations")
            if node.id == "Studio" and isinstance(node.ctx, ast.Load) and not in_annotation(node):
                report("studio-class", node, "the Studio class used as a value (alias, class attribute access)")
            if node.id in DYNAMIC and isinstance(node.ctx, ast.Load):
                report("dynamic-access", node, f"dynamic attribute/eval builtin {node.id!r}")
        elif isinstance(node, ast.alias) and node.name == "OWNER":
            report("owner-principal", node, "OWNER imported")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            roots = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for name in roots:
                if name.split(".")[0] in BLOCKED_MODULES:
                    report("dynamic-access", node, f"import of {name!r} (computed attribute access or introspection)")
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


FACTORY = "port = StudioAgentPort(studio)"
#: (label, after-line, inserted line, the rule that must fire). Each is a way an edit could give the adapter owner power.
CONTROLS = [
    ("bare-name owner call", FACTORY, '_f = lambda: studio.approve("x", 0, "h", {}, True, None)', "studio-reach"),
    ("bare-name alias", FACTORY, "_s = studio", "studio-reach"),
    ("studio passed by keyword to an arbitrary call", FACTORY, "_x = dict(s=studio)", "studio-reach"),
    ("Studio class aliased", FACTORY, "_S = Studio", "studio-class"),
    ("Studio class attribute", FACTORY, "_f = Studio.list_cases", "studio-class"),
    ("private studio on the port", FACTORY, "_f = port._studio", "port-member"),
    ("undeclared port member", "self.port = port", "_f = self.port.nonexistent", "port-member"),
    ("owner method on any receiver", "self.port = port", "_f = service.approve", "owner-name"),
    ("owner method on a class", FACTORY, "_f = SomeService.apply", "owner-name"),
    ("store write on any receiver", FACTORY, "_f = SomeRepo(1).set_active", "owner-name"),
    ("store write missed by the old hand list (insert_case)", FACTORY, "_f = repo.insert_case", "owner-name"),
    ("bare owner name", FACTORY, "_f = select_meaning", "owner-name"),
    ("computed attribute name", FACTORY, '_f = getattr(port, "app" + "rove")', "dynamic-access"),
    ("operator.attrgetter import", "from pathlib import Path", "from operator import attrgetter as _ag", "dynamic-access"),
    ("methodcaller by name", FACTORY, '_f = methodcaller("apply")', "dynamic-access"),
    ("object internals", FACTORY, "_f = create_server.__globals__", "dunder"),
    ("class walk", FACTORY, "_f = port.__class__", "dunder"),
    ("owner principal imported", "from eija_studio.domain.policy import projections", "from eija_studio.domain.models import OWNER", "owner-principal"),
    ("owner principal by attribute", FACTORY, "_p = models.OWNER", "owner-principal"),
]


def _rules_found(after: str, insertion: str) -> set[str]:
    return {rule for rule, _ in owner_operation_violations(mutated(after, insertion))}


@pytest.mark.parametrize(("label", "after", "insertion", "rule"), CONTROLS, ids=[c[0] for c in CONTROLS])
def test_lint_catches_owner_reach_mutations(label, after, insertion, rule):
    """Negative controls. Leaking data is a redaction question, not an owner-operation one; test_mcp_server.py scans
    every tool's output for that."""
    assert rule in _rules_found(after, insertion), f"lint missed: {label}"


@pytest.mark.parametrize("rule", RULES)
def test_every_rule_has_a_control_only_it_catches(rule):
    """A rule that can be deleted with every control still green protects nothing (review of PR #23: the owner-name
    rule was exactly that). Some control must be caught by this rule alone."""
    assert any(_rules_found(after, insertion) == {rule} for _, after, insertion, expected in CONTROLS if expected == rule), rule


def test_the_store_write_names_come_from_the_ports_and_name_only_real_members():
    real = {name for proto in agent_policy.PERSISTENCE_PORTS for name in agent_policy.port_members(proto)}
    assert set(STORE_WRITES) <= real, set(STORE_WRITES) - real  # `put_case` once named a method that exists nowhere
    for writer in ("transaction", "save_case", "insert_case", "set_active", "event", "backup", "seal",
                   "create_instance", "update_instance", "record_operation", "enqueue"):
        assert writer in STORE_WRITES, writer
    assert not set(STORE_WRITES) & agent_policy.READ_ONLY_PORT_MEMBERS
    assert set(STORE_WRITES) == set(agent_policy.derive_store_write_names())


def test_studio_agent_port_exposes_exactly_the_agent_port():
    tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
    factory = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "StudioAgentPort")
    inner = next(n for n in factory.body if isinstance(n, ast.ClassDef))
    public = {n.name for n in inner.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")}
    assert public == ALLOWED_PORT, public ^ ALLOWED_PORT
    assert not any(isinstance(n, ast.Assign) for n in inner.body), "the port keeps no state: the Studio lives only in the closure"
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


@pytest.mark.parametrize("name", ["R&D", "a;b", "x|y", "a<b>c", "x^y", "it's", "plain"])
def test_claude_windows_snippet_double_quotes_every_argument_so_shell_metacharacters_stay_literal(name):
    r"""Review of PR #23: list2cmdline quotes only whitespace, so `C:\R&D\ws` split at `&` in cmd.exe and `;` in PowerShell."""
    argv = [r"C:\Python312\python.exe", "-m", "eija_studio", "mcp", "--workspace", rf"C:\{name}\ws"]
    text = agent_config._shell_join(argv, windows=True)
    assert text == " ".join(f'"{a}"' for a in argv), text


@pytest.mark.parametrize("hostile", ["$HOME", "a`b", "50%off", 'say"hi'])
def test_claude_windows_snippet_refuses_what_a_shell_would_still_expand_inside_quotes(hostile):
    """`$`, a backtick, `%` and `"` expand or end the quote in PowerShell / cmd.exe even inside double quotes: refuse
    (pointing at the JSON/TOML config forms) instead of printing a line that does something else."""
    with pytest.raises(DomainError) as refused:
        agent_config._shell_join(["py", rf"C:\{hostile}\ws"], windows=True)
    assert refused.value.code == "CONFIGURATION" and "codex" in refused.value.message
    assert agent_config._shell_join(["py", rf"/srv/{hostile}/ws"], windows=False)  # POSIX quoting handles them (shlex)


def test_a_workspace_path_ending_in_a_backslash_does_not_escape_the_closing_quote():
    assert agent_config._shell_join(["py", "C:\\ws\\"], windows=True) == '"py" "C:\\ws\\\\"'


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


# ---- the nox session must not read as a pass when the SDK tests did not run --------------------------------------
class _RecordingSession:
    posargs: list[str] = []  # noqa: RUF012

    class Skipped(Exception):
        pass

    def __init__(self):
        self.commands, self.skipped, self.logged = [], None, []

    def run(self, *args, **kwargs):
        self.commands.append(args)

    def log(self, message):
        self.logged.append(message)

    def skip(self, reason):
        self.skipped = reason
        raise self.Skipped(reason)


def _sdk(monkeypatch, present: bool):
    monkeypatch.setattr(agents_sessions.subprocess, "run", lambda argv, **kwargs: subprocess.CompletedProcess(argv, 0 if present else 1))


def test_agents_session_is_skipped_as_not_run_when_the_mcp_sdk_is_missing(monkeypatch):
    """nox reads a plain success as a pass: without the SDK the static checks run, then the session is SKIPPED (NOT_RUN)."""
    _sdk(monkeypatch, present=False)
    session = _RecordingSession()
    with pytest.raises(_RecordingSession.Skipped):
        agents_sessions.agents.func(session)
    assert session.skipped.startswith("NOT_RUN") and "static checks passed" in session.skipped
    assert any("tests/test_agent_static.py" in cmd for cmd in session.commands), "the SDK-free checks still ran"
    assert not any("tests/test_mcp_server.py" in cmd for cmd in session.commands)


def test_agents_session_runs_the_sdk_tests_and_succeeds_when_the_sdk_is_present(monkeypatch):
    _sdk(monkeypatch, present=True)
    session = _RecordingSession()
    agents_sessions.agents.func(session)
    assert session.skipped is None and any("tests/test_mcp_server.py" in cmd for cmd in session.commands)
