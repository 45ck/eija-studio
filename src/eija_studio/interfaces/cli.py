from __future__ import annotations
import argparse, getpass, importlib.util, json, os, secrets, sys
from pathlib import Path
from tempfile import TemporaryDirectory
from pydantic import ValidationError
from eija_studio import __version__
from eija_studio.bootstrap import build_studio, resolve_pack, source_identity, KEYED_PROVIDERS, PROVIDER_NAMES
from eija_studio.domain.models import Workflow, DomainError, OWNER, fingerprint
from eija_studio.domain.policy import check_policy, first_supported_meaning, projections
from eija_studio.domain.impact import model_impact
from eija_studio.application.compiler import subject_for
from eija_studio.application.verifier import verify_runtime
from eija_studio.application.diagram_catalog import FORMATS, VIEWS, VIEW_FORMATS, html_panels, render_view
from eija_studio.weave.cli import COMMANDS as WEAVE_COMMANDS, add_parsers as add_weave_parsers
from .agent_config import DEFAULT_MAX_PROVIDER_CALLS, snippet
from .app_build import add_parser as add_build_parser, build as build_app


def output(value, path: Path | None = None):
    text = json.dumps(value, indent=2, ensure_ascii=False)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(text + "\n", encoding="utf-8")
        temporary.replace(path)
    else:
        print(text)


def _render_workflows(args) -> tuple[Workflow, Workflow | None]:
    if (args.case_id is None) == (args.workflow is None):
        raise DomainError("CONFIGURATION", "Give exactly one of CASE_ID or --workflow FILE")
    if args.case_id is None:
        return resolve_pack(args.pack).model, Workflow.model_validate_json(args.workflow.read_text(encoding="utf-8"))
    if not args.workspace.is_dir():
        raise DomainError("NOT_FOUND", "Workspace does not exist; render never creates one")
    return build_studio(args.workspace, pack=args.pack).workflows(args.case_id)


def _render_text(args, before: Workflow, after: Workflow | None) -> str:
    if args.fmt == "html":
        from .render_html import html_page
        return html_page("EIJA diagrams: " + (args.case_id or args.workflow.name), html_panels(args.view, before, after, args.action))
    if args.view == "all":
        raise DomainError("CONFIGURATION", "--view all is only available with --format html")
    if args.fmt not in VIEW_FORMATS[args.view]:
        raise DomainError("FORMAT_UNSUPPORTED", f"{args.view} is not emitted as {args.fmt}; supported: {', '.join(VIEW_FORMATS[args.view])}")
    return render_view(args.view, args.fmt, before, after, args.action)


def _write_render(data: bytes, out: Path | None) -> None:
    if out is None:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(str(out))


def render_command(args) -> int:
    """Text on stdout is the diagram itself (no JSON wrapper) so it pipes into a renderer. A workflow the
    protected policy refuses is still drawn, with a POLICY BLOCKED marker, and the command exits 2 so a script
    cannot mistake it for a routine change. Read-only: it never creates a workspace or a receipt key."""
    before, after = _render_workflows(args)
    _write_render(_render_text(args, before, after).encode("utf-8"), args.out)
    blocked = check_policy(after if after is not None else before, resolve_pack(args.pack))
    if blocked:
        print("POLICY_BLOCKED: " + "; ".join(blocked) + " (drawn with a marker; the runtime would refuse this workflow)", file=sys.stderr)
        return 2
    return 0


def check_export_command(args) -> int:
    doc = json.loads(args.file.read_text(encoding="utf-8"))
    valid = doc.get("format") == "eija.change-case.export.v1" and doc.get("payload_hash") == fingerprint(doc.get("payload"))
    output({"payload_integrity": valid, "authority": "NOT_VERIFIED; exported evidence is not imported for approval"})
    return 0 if valid else 2


def _add_render_parser(subs) -> None:
    render = subs.add_parser("render", help="Generate UML (Mermaid, PlantUML, DOT or HTML) from a case's executable model")
    render.add_argument("case_id", nargs="?", help="Change Case id; alternatively pass --workflow")
    render.add_argument("--workflow", type=Path, help="Workflow JSON file, drawn as the candidate against the shipped baseline")
    render.add_argument("--workspace", type=Path, default=Path(".eija"))
    render.add_argument("--pack", type=Path, help="Domain pack directory or JSON file (defaults to EIJA_PACK or packs/default.json)")
    render.add_argument("--view", choices=(*VIEWS, "all"), default="state", help="'all' is for --format html only")
    render.add_argument("--format", choices=(*FORMATS, "html"), default="mermaid", dest="fmt")
    render.add_argument("--action", help="Action for --view sequence")
    render.add_argument("--out", type=Path, help="Write here instead of stdout (LF, UTF-8)")


def build_command(args) -> int:
    """Generate an app from the model and check it against the kernel (ADR-0150). Needs no workspace or key."""
    code, summary = build_app(args, resolve_pack(args.pack), source_identity)
    output(summary)
    return code


EARLY_COMMANDS = {"check-export": check_export_command, "render": render_command, "build": build_command, **WEAVE_COMMANDS}  # need no workspace, provider or key


def formal_table(evidence: list) -> str:
    """One line per formal evidence kind for a human reader (stderr); the full detail is in the JSON packet."""
    lines = ["formal evidence (recomputed by the kernel from raw artifacts; UNKNOWN and NOT_RUN are never rounded up):"]
    for e in evidence:
        why = "" if e["status"] == "PASS" else (e.get("reasons") or [""])[0]
        lines.append(f"  {e['kind']:<22} {e['status']:<8} {e['evidence_level']}" + (f"  {why}" if why else ""))
    return "\n".join(lines)


def _formal_for_compile(studio, model) -> dict:
    """Formal evidence and, if the policy blocks the model, the negative-control counterexamples that explain why."""
    if studio.formal is None:
        return {}
    view = studio.formal_view(model)
    return {"formal_evidence": view["evidence"], "formal_explanations": view["explanations"]}


def _report_failure(command: str, exc: Exception) -> None:
    if isinstance(exc, DomainError):
        failure = {"error": exc.code, "message": exc.message} | ({"details": exc.details} if exc.details else {})
    else:
        failure = {"error": "INPUT_OR_ENVIRONMENT_ERROR", "message": "Check the file, schema, permissions and configuration; no raw sensitive input is echoed"}
    if command == "mcp":
        # stdout is the MCP protocol channel: a startup error printed there would corrupt it. Use stderr.
        print(json.dumps(failure, indent=2, ensure_ascii=False), file=sys.stderr)
    else:
        output(failure)


def _run_mcp(args) -> int:
    """`eija mcp`: print client config, or serve the agent-facing MCP server on stdio. Errors here go to stderr."""
    if args.print_config:
        print(snippet(args.print_config, sys.executable, args.workspace, pack=args.pack, repository=args.repo), end="")
        return 0
    if args.ask_key or (args.provider != "offline" and not (args.allow_network and args.egress_consent)):
        # stdin/stdout are the protocol channel, and network use is the owner's decision made at startup.
        raise DomainError("CONFIGURATION", "mcp: --ask-key is unsupported; a networked provider needs --allow-network and --egress-consent")
    if args.max_provider_calls < 0:
        raise DomainError("CONFIGURATION", "mcp: --max-provider-calls must be 0 or more")
    try:
        from .mcp_server import serve_stdio
    except ImportError as error:
        if importlib.util.find_spec("mcp") is None:
            raise DomainError("MISSING_EXTRA", 'Install the MCP SDK: pip install -e ".[agents]"') from error
        # The SDK is there but unusable (for example mcp<2 has no mcp.server.mcpserver): say so, do not say "install".
        raise DomainError("MCP_SDK_INCOMPATIBLE", f"The installed MCP SDK cannot be used ({error}); this release expects "
                                                   'mcp==2.2.0: pip install -e ".[agents]"') from error
    studio = build_studio(args.workspace, args.provider, args.model, args.allow_network, None, formal=not args.no_formal,
                          pack=args.pack, repository_root=args.repo)
    serve_stdio(studio, egress_consent=args.egress_consent, max_provider_calls=args.max_provider_calls,
                diagram_renderer=_agent_diagram)
    return 0


def _agent_diagram(model: Workflow, view: str, fmt: str) -> str:
    """Reuse the reviewed diagram generators; SVG needs an external renderer and is not silently fabricated."""
    if fmt not in FORMATS:
        raise DomainError("FORMAT_UNSUPPORTED", "The built-in MCP renderer emits Mermaid, PlantUML or DOT text")
    return render_view("journey" if view == "journeys" else "state", fmt, model)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="eija", description="EIJA Studio — bounded local assurance POC")
    parser.add_argument("--version", action="version", version=__version__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--workspace", type=Path, default=Path(".eija"))
    common.add_argument("--pack", type=Path, help="Domain pack directory or JSON file (defaults to EIJA_PACK or packs/default.json)")
    common.add_argument("--provider", choices=PROVIDER_NAMES, default=os.getenv("EIJA_PROVIDER", "offline"))
    common.add_argument("--model", default=os.getenv("EIJA_MODEL", ""))
    common.add_argument("--allow-network", action="store_true", help="Allow explicit provider calls; per-request consent still required")
    common.add_argument("--ask-key", action="store_true", help="Prompt locally for the OpenRouter/Anthropic API key; never persist it")
    common.add_argument("--no-formal", action="store_true", help="Do not attach formal-lane evidence (Bend, SMT, bounded model check) when verifying")
    subs = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "doctor", "list"):
        subs.add_parser(command, parents=[common])
    serve = subs.add_parser("serve", parents=[common]); serve.add_argument("--port", type=int, default=8765); serve.add_argument("--open", action="store_true")
    serve.add_argument("--repo", type=Path, help="Explicit local repository to inspect read-only; never executes its code")
    demo = subs.add_parser("demo", parents=[common]); demo.add_argument("--out", type=Path, default=Path("demo-case.json"))
    propose = subs.add_parser("propose", parents=[common]); propose.add_argument("request"); propose.add_argument("--consent", action="store_true")
    verify = subs.add_parser("verify", parents=[common]); verify.add_argument("case_id"); verify.add_argument("--expected-version", type=int, required=True)
    export = subs.add_parser("export", parents=[common]); export.add_argument("case_id"); export.add_argument("--out", type=Path, required=True)
    backup = subs.add_parser("backup", parents=[common]); backup.add_argument("--out", type=Path, required=True)
    compile_p = subs.add_parser("compile", parents=[common]); compile_p.add_argument("file", type=Path); compile_p.add_argument("--out", type=Path, required=True); compile_p.add_argument("--verify", action="store_true")
    check = subs.add_parser("check-export"); check.add_argument("file", type=Path)
    _add_render_parser(subs)
    add_build_parser(subs)
    add_weave_parsers(subs)
    mcp = subs.add_parser("mcp", parents=[common], help="Serve the agent-facing MCP server on stdio (needs the agents extra)")
    mcp.add_argument("--repo", type=Path, help="Explicit local repository to inspect read-only; never executes its code")
    mcp.add_argument("--print-config", choices=["claude", "codex", "opencode", "gemini"], help="Print copy-paste client config for this MCP server and exit")
    mcp.add_argument("--egress-consent", action="store_true", help="Owner's STANDING consent: every propose call in this session may send the request to a networked provider; agents cannot grant it")
    mcp.add_argument("--max-provider-calls", type=int, default=DEFAULT_MAX_PROVIDER_CALLS, help="Cap on networked provider calls per MCP session (spend guard; 0 forbids them)")
    args = parser.parse_args(argv)
    try:
        if args.command in EARLY_COMMANDS:
            return EARLY_COMMANDS[args.command](args)
        if args.command == "mcp":
            return _run_mcp(args)
        key = None
        if args.ask_key:
            if args.provider not in KEYED_PROVIDERS:
                raise DomainError("CONFIGURATION", "--ask-key is only for the OpenRouter and Anthropic API providers")
            key = getpass.getpass(f"{args.provider} API key (not stored): ")
        studio = build_studio(args.workspace, args.provider, args.model, args.allow_network, key, formal=not args.no_formal,
                              pack=args.pack, repository_root=getattr(args, "repo", None))
        if args.command == "init":
            output({"workspace": str(studio.store.directory), "provider": args.provider, "state": "READY", "data": "synthetic only"})
        elif args.command == "doctor":
            identity = studio.identity_provider()
            result = {"python": sys.version.split()[0], "studio": __version__, "release_fixture_matches": identity["trusted_fixture"],
                      "network_enabled": args.allow_network, "provider": studio.provider.doctor(),
                      "live_inference": "NOT_RUN", "platform_validation": "See evidence/release-report.json"}
            output(result)
            return 0 if identity["trusted_fixture"] and result["provider"]["ready"] else 2
        elif args.command == "serve":
            if not 1024 <= args.port <= 65535:
                raise DomainError("CONFIGURATION", "Use an unprivileged port from 1024 through 65535")
            import uvicorn, webbrowser
            from .http import create_app
            token = secrets.token_urlsafe(32)
            url = f"http://127.0.0.1:{args.port}/#{token}"
            print("EIJA Studio — local single-owner session. Do not share these private links.\n" + url, flush=True)
            print(f"PlayIDE (visual model, Build & run): http://127.0.0.1:{args.port}/play#{token}", flush=True)
            if args.provider != "offline":
                print("External inference requires configured credentials and explicit per-request consent.", flush=True)
            if args.open:
                # Browser may briefly arrive before the listener; refresh if necessary.
                webbrowser.open(url)
            uvicorn.run(create_app(studio, token, args.port), host="127.0.0.1", port=args.port, access_log=False, log_level="warning")
        elif args.command == "list":
            output([{k: c[k] for k in ("id", "stage", "version", "request")} for c in studio.store.list_cases()])
        elif args.command == "propose":
            c = studio.create(args.request)
            output(studio.propose(c["id"], c["version"], consent=args.consent))
        elif args.command == "verify":
            studio.verify(args.case_id, args.expected_version)
            packet = studio.view(args.case_id)["packet"]
            output(packet)
            print(formal_table(packet.get("formal_evidence", [])), file=sys.stderr)
        elif args.command == "export":
            output(studio.export(args.case_id), args.out); print(str(args.out))
        elif args.command == "backup":
            if args.out.exists():
                raise DomainError("OUTPUT_EXISTS", "Choose a new backup filename")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            studio.store.backup(args.out)
            print("Database backup saved. Preserve receipt.key separately and securely to verify local seals.")
        elif args.command == "demo":
            if args.provider != "offline":
                raise DomainError("CONFIGURATION", "demo is deliberately offline; use propose for a live provider test")
            c = studio.create(studio.pack.fixtures.demo_request)
            c = studio.propose(c["id"], c["version"])
            # Explicit scripted fixture choice (the pack's first supported meaning), NOT an actual human authorisation.
            c = studio.select(c["id"], c["version"], first_supported_meaning(studio.pack), OWNER)
            c = studio.verify(c["id"], c["version"])
            data = studio.export(c["id"])
            data["demo_note"] = "Scripted fixture meaning selection. No human approval or baseline application occurred."
            output(data, args.out)
            output({"case_id": c["id"], "export": str(args.out), "packet": studio.view(c["id"])["packet"]["status"],
                    "baseline_applied": False, "human_understanding": "UNKNOWN"})
        elif args.command == "compile":
            model = Workflow.model_validate_json(args.file.read_text(encoding="utf-8"))
            errors = check_policy(model, studio.pack)
            identity = studio.identity_provider()
            compiled = {"format": "eija.compilation.v1", "semantic_hash": model.semantic_hash, "policy_errors": errors,
                        "pack": {"id": studio.pack.id, "version": studio.pack.pack.version, "digest": studio.pack.digest},
                        "source_review_required": not identity["trusted_fixture"], "projections": projections(model),
                        "impact": model_impact(studio.pack.model, model), "human_understanding": "UNKNOWN", "decision": "NONE"}
            if args.verify and not errors and identity["trusted_fixture"]:
                compiled["receipt"] = studio.signer.seal(verify_runtime(model, subject_for(model, {}, identity), studio.sandbox, studio.pack))
            compiled |= _formal_for_compile(studio, model)
            output(compiled, args.out / "compiled.json")
            output(model.model_dump(mode="json"), args.out / "model.json")
            print(str(args.out / "compiled.json"))
            return 2 if errors or not identity["trusted_fixture"] else 0
        return 0
    except (DomainError, ValidationError, OSError, ValueError, KeyError) as exc:
        _report_failure(args.command, exc)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
