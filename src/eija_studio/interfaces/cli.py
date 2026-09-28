from __future__ import annotations
import argparse, getpass, json, os, secrets, sys
from pathlib import Path
from tempfile import TemporaryDirectory
from pydantic import ValidationError
from eija_studio import __version__
from eija_studio.bootstrap import build_studio
from eija_studio.domain.models import Workflow, SemanticTransaction, DomainError, OWNER, fingerprint
from eija_studio.domain.policy import baseline, apply_transaction, check_policy, projections
from eija_studio.domain.impact import model_impact
from eija_studio.application.compiler import subject_for
from eija_studio.application.verifier import verify_runtime
from eija_studio.application.diagram_catalog import FORMATS, VIEWS, VIEW_FORMATS, html_panels, render_view


def output(value, path: Path | None = None):
    text = json.dumps(value, indent=2, ensure_ascii=False)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(text + "\n", encoding="utf-8")
        temporary.replace(path)
    else:
        print(text)


def render_command(args) -> int:
    """Text on stdout is the diagram itself (no JSON wrapper) so it pipes into a renderer. A workflow the
    protected policy refuses is still drawn, with a POLICY BLOCKED marker, and the command exits 2 so a script
    cannot mistake it for a routine change. Read-only: it never creates a workspace or a receipt key."""
    if (args.case_id is None) == (args.workflow is None):
        raise DomainError("CONFIGURATION", "Give exactly one of CASE_ID or --workflow FILE")
    if args.case_id is not None:
        if not args.workspace.is_dir():
            raise DomainError("NOT_FOUND", "Workspace does not exist; render never creates one")
        before, after = build_studio(args.workspace).workflows(args.case_id)
    else:
        before, after = baseline(), Workflow.model_validate_json(args.workflow.read_text(encoding="utf-8"))
    if args.fmt == "html":
        from .render_html import html_page
        text = html_page("EIJA diagrams: " + (args.case_id or args.workflow.name), html_panels(args.view, before, after, args.action))
    else:
        if args.view == "all":
            raise DomainError("CONFIGURATION", "--view all is only available with --format html")
        if args.fmt not in VIEW_FORMATS[args.view]:
            raise DomainError("FORMAT_UNSUPPORTED", f"{args.view} is not emitted as {args.fmt}; supported: {', '.join(VIEW_FORMATS[args.view])}")
        text = render_view(args.view, args.fmt, before, after, args.action)
    data = text.encode("utf-8")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(data)
        print(str(args.out))
    else:
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    blocked = check_policy(after if after is not None else before)
    if blocked:
        print("POLICY_BLOCKED: " + "; ".join(blocked) + " (drawn with a marker; the runtime would refuse this workflow)", file=sys.stderr)
        return 2
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="eija", description="EIJA Studio — bounded local assurance POC")
    parser.add_argument("--version", action="version", version=__version__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--workspace", type=Path, default=Path(".eija"))
    common.add_argument("--provider", choices=["offline", "openrouter", "codex"], default=os.getenv("EIJA_PROVIDER", "offline"))
    common.add_argument("--model", default=os.getenv("EIJA_MODEL", ""))
    common.add_argument("--allow-network", action="store_true", help="Allow explicit provider calls; per-request consent still required")
    common.add_argument("--ask-key", action="store_true", help="Prompt locally for OpenRouter key; never persist it")
    subs = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "doctor", "list"):
        subs.add_parser(command, parents=[common])
    serve = subs.add_parser("serve", parents=[common]); serve.add_argument("--port", type=int, default=8765); serve.add_argument("--open", action="store_true")
    demo = subs.add_parser("demo", parents=[common]); demo.add_argument("--out", type=Path, default=Path("demo-case.json"))
    propose = subs.add_parser("propose", parents=[common]); propose.add_argument("request"); propose.add_argument("--consent", action="store_true")
    verify = subs.add_parser("verify", parents=[common]); verify.add_argument("case_id"); verify.add_argument("--expected-version", type=int, required=True)
    export = subs.add_parser("export", parents=[common]); export.add_argument("case_id"); export.add_argument("--out", type=Path, required=True)
    backup = subs.add_parser("backup", parents=[common]); backup.add_argument("--out", type=Path, required=True)
    compile_p = subs.add_parser("compile", parents=[common]); compile_p.add_argument("file", type=Path); compile_p.add_argument("--out", type=Path, required=True); compile_p.add_argument("--verify", action="store_true")
    check = subs.add_parser("check-export"); check.add_argument("file", type=Path)
    render = subs.add_parser("render", help="Generate UML (Mermaid, PlantUML, DOT or HTML) from a case's executable model")
    render.add_argument("case_id", nargs="?", help="Change Case id; alternatively pass --workflow")
    render.add_argument("--workflow", type=Path, help="Workflow JSON file, drawn as the candidate against the shipped baseline")
    render.add_argument("--workspace", type=Path, default=Path(".eija"))
    render.add_argument("--view", choices=(*VIEWS, "all"), default="state", help="'all' is for --format html only")
    render.add_argument("--format", choices=(*FORMATS, "html"), default="mermaid", dest="fmt")
    render.add_argument("--action", help="Action for --view sequence")
    render.add_argument("--out", type=Path, help="Write here instead of stdout (LF, UTF-8)")
    args = parser.parse_args(argv)
    try:
        if args.command == "check-export":
            doc = json.loads(args.file.read_text(encoding="utf-8"))
            valid = doc.get("format") == "eija.change-case.export.v1" and doc.get("payload_hash") == fingerprint(doc.get("payload"))
            output({"payload_integrity": valid, "authority": "NOT_VERIFIED; exported evidence is not imported for approval"})
            return 0 if valid else 2
        if args.command == "render":
            return render_command(args)
        key = None
        if args.ask_key:
            if args.provider != "openrouter":
                raise DomainError("CONFIGURATION", "--ask-key is only for OpenRouter")
            key = getpass.getpass("OpenRouter key (not stored): ")
        studio = build_studio(args.workspace, args.provider, args.model, args.allow_network, key)
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
            print("EIJA Studio — local single-owner session. Do not share this private link.\n" + url, flush=True)
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
            studio.verify(args.case_id, args.expected_version); output(studio.view(args.case_id)["packet"])
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
            c = studio.create("Let teachers sign off excursions.")
            c = studio.propose(c["id"], c["version"])
            # Explicit scripted fixture choice, NOT an actual human authorisation.
            c = studio.select(c["id"], c["version"], "recommend_only", OWNER)
            c = studio.verify(c["id"], c["version"])
            data = studio.export(c["id"])
            data["demo_note"] = "Scripted fixture meaning selection. No human approval or baseline application occurred."
            output(data, args.out)
            output({"case_id": c["id"], "export": str(args.out), "packet": studio.view(c["id"])["packet"]["status"],
                    "baseline_applied": False, "human_understanding": "UNKNOWN"})
        elif args.command == "compile":
            model = Workflow.model_validate_json(args.file.read_text(encoding="utf-8"))
            errors = check_policy(model)
            identity = studio.identity_provider()
            compiled = {"format": "eija.compilation.v1", "semantic_hash": model.semantic_hash, "policy_errors": errors,
                        "source_review_required": not identity["trusted_fixture"], "projections": projections(model),
                        "impact": model_impact(baseline(), model), "human_understanding": "UNKNOWN", "decision": "NONE"}
            if args.verify and not errors and identity["trusted_fixture"]:
                compiled["receipt"] = studio.signer.seal(verify_runtime(model, subject_for(model, {}, identity), studio.sandbox))
            output(compiled, args.out / "compiled.json")
            output(model.model_dump(mode="json"), args.out / "model.json")
            print(str(args.out / "compiled.json"))
            return 2 if errors or not identity["trusted_fixture"] else 0
        return 0
    except (DomainError, ValidationError, OSError, ValueError, KeyError) as exc:
        if isinstance(exc, DomainError):
            output({"error": exc.code, "message": exc.message})
        else:
            output({"error": "INPUT_OR_ENVIRONMENT_ERROR", "message": "Check the file, schema, permissions and configuration; no raw sensitive input is echoed"})
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
