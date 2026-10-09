"""Loopback-only local adapter. No public hosting, CORS, remote provider proxy or raw file endpoint."""
from __future__ import annotations
import hmac
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import Field
from eija_studio.application.diagram_catalog import case_diagrams
from eija_studio.application.edit_preview import EditPreview
from eija_studio.application.edit_proposal import TypedEditProposal
from eija_studio.application.plan import example_passes
from eija_studio.application.repository import COMMIT_OID_PATTERN
from eija_studio.domain.models import MEANING_ID, Contract, DomainError, OWNER, LayoutChange, ExecuteCommand, Workflow
from eija_studio.domain.pack import Pack
from eija_studio.domain.transactions import Transaction
from .play import register as register_play
from .play_systems import register as register_systems

# The Studio page keeps this policy. Only /visual-frame, a static document with no API access, relaxes styles
# (Mermaid writes inline style attributes) and is sandboxed; docs/SECURITY_AND_TRUST.md and ADR-0023 record why.
PAGE_CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-src 'self'; "
            "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
FRAME_CSP = ("default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src data:; connect-src 'none'; "
             "frame-ancestors 'self'; base-uri 'none'; form-action 'none'; sandbox allow-scripts")
WEB_ASSETS = frozenset({"app.js", "app.css", "canvas.js", "tree.js", "review.js", "compare.js", "compare.css", "repository-review.js", "repository-review.css", "source.js", "shell.js", "agent-edit.js", "visual-frame.js", "visual-frame.css", "play.js", "play-run.js", "play.css", "play-laws.js", "play-assist.js", "play-assist.css", "play-review.js", "play-review.css", "play-access.js", "play-access.css", "play-shell.js", "play-shell.css", "play-diff.js", "play-diff.css", "play-tests.js", "play-tests.css", "play-interop.js", "play-interop.css", "play-systems.js", "play-systems.css", "play-sequence.js", "play-sequence.css", "play-game.js", "play-game.css"})
# PlayIDE frames the app built from the model, which runs as a separate process on its own loopback port (ADR-0151).
PLAY_CSP = PAGE_CSP.replace("frame-src 'self'", "frame-src 'self' http://127.0.0.1:*")


class NewCase(Contract):
    request: str = Field(min_length=1, max_length=6000)
class Version(Contract):
    expected_version: int = Field(ge=0, strict=True)
class Propose(Version):
    consent: bool = Field(default=False, strict=True)
class Select(Version):
    interpretation: str = Field(pattern=MEANING_ID)  # a meaning id of the active pack; the service checks it
class EditPropose(Version):
    request: str = Field(min_length=1, max_length=6000)
class EditCheck(Contract):
    transaction: Transaction
class Edit(Version):
    transaction: Transaction
class Layout(Version):
    change: LayoutChange
class Preview(Version):
    state: str | None = None
class Approval(Version):
    subject_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    answers: dict[str, str]
    acknowledge_unknowns: bool = Field(strict=True)
    scope: Literal["local-demo", "field-use"] = "local-demo"


def _set_security_headers(response, path: str) -> None:
    framed = path == "/visual-frame"
    # The vendored renderer is a 5 MB public, versioned file with no user data: let the browser keep it for an hour.
    cache = "private, max-age=3600" if path == "/assets/vendor/mermaid.min.js" and response.status_code == 200 else "no-store"
    response.headers.update({"Cache-Control": cache, "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer", "X-Frame-Options": "SAMEORIGIN" if framed else "DENY",
        "Content-Security-Policy": FRAME_CSP if framed else PLAY_CSP if path == "/play" else PAGE_CSP})


def pack_summary(pack: Pack) -> dict[str, object]:
    """What the page needs to name the domain without hardcoding it: the pack's name, demo request, declared actions
    (in declaration order), declared roles and synthetic fixture actors."""
    return {"id": pack.id, "name": pack.pack.name, "version": pack.pack.version, "demo_request": pack.fixtures.demo_request,
            "actions": [a.id for a in pack.actions], "roles": [r.id for r in pack.roles],
            "actors": [{"id": a.id, "role": a.role, "active": a.active, "assigned": a.assigned} for a in pack.fixtures.actors]}


def create_app(studio, token: str, port: int = 8765, systems=None) -> FastAPI:
    """`systems` (ADR-0185), when given, lets PlayIDE start and open systems; `studio` is then its `StudioHandle`."""
    app = FastAPI(title="EIJA Studio", version="0.2.0", docs_url=None, redoc_url=None, openapi_url=None)
    web = Path(__file__).resolve().parents[1] / "resources" / "web"
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    allowed_origins = {"http://" + host for host in allowed_hosts}

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        if request.headers.get("host", "") not in allowed_hosts:
            return JSONResponse({"code": "HOST_DENIED", "message": "Loopback host required"}, status_code=403)
        if request.url.path.startswith("/api/"):
            supplied = request.headers.get("authorization", "")
            if not hmac.compare_digest(supplied, "Bearer " + token):
                return JSONResponse({"code": "SESSION_REQUIRED", "message": "Use the private launch link"}, status_code=401)
            if request.method not in {"GET", "HEAD"}:
                if request.headers.get("origin") not in allowed_origins:
                    return JSONResponse({"code": "ORIGIN_DENIED", "message": "Same-origin local browser required"}, status_code=403)
                if request.headers.get("content-type", "").split(";")[0] != "application/json":
                    return JSONResponse({"code": "CONTENT_TYPE", "message": "JSON required"}, status_code=415)
                # ASGI streaming body cap; Content-Length alone is not trustworthy.
                data, size = [], 0
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > 32768:
                        return JSONResponse({"code": "BODY_TOO_LARGE", "message": "32 KiB request limit"}, status_code=413)
                    data.append(chunk)
                request._body = b"".join(data)
        response = await call_next(request)
        _set_security_headers(response, request.url.path)
        return response

    @app.exception_handler(DomainError)
    async def domain_error(request, exc):
        status = 404 if exc.code == "NOT_FOUND" else 403 if exc.code in {"AUTHORITY_REQUIRED", "EGRESS_CONSENT_REQUIRED"} else 409
        body = {"code": exc.code, "message": exc.message} | ({"details": exc.details} if exc.details else {})
        return JSONResponse(body, status_code=status)

    @app.exception_handler(RequestValidationError)
    async def contract_error(request, exc):
        # Do not echo rejected input, which might contain a mistakenly pasted key.
        return JSONResponse({"code": "CONTRACT_REJECTED", "message": "Invalid fields/types for this command"}, status_code=422)

    @app.get("/")
    def index():
        return FileResponse(web / "index.html")

    @app.get("/assets/{name}")
    def asset(name: str):
        if name not in WEB_ASSETS or not (web / name).is_file():
            return JSONResponse({"code": "NOT_FOUND"}, status_code=404)
        return FileResponse(web / name)

    @app.get("/assets/vendor/{name}")
    def vendored(name: str):
        if name not in {"mermaid.min.js", "dagre.min.js", "maxgraph.min.js"}:  # exact allowlist; licenses are kept with the assets
            return JSONResponse({"code": "NOT_FOUND"}, status_code=404)
        return FileResponse(web / "vendor" / name)

    own = (lambda: systems.library.contains(Path(systems.current["pack"]))) if systems is not None else (lambda: False)
    app.state.play = register_play(app, studio, web, own)
    if systems is not None:
        systems.on_switch = app.state.play.stop
        register_systems(app, systems)

    @app.get("/visual-frame")
    def visual_frame():
        return FileResponse(web / "visual-frame.html")

    @app.get("/api/status")
    def status():
        with studio.store.transaction() as u:
            active = u.active()
        identity = studio.identity_provider()
        return {"version": "0.2.0", "provider": studio.provider.name, "network_enabled": studio.allow_network,
            "provider_networked": studio.provider.networked, "baseline_version": active["version"], "baseline": active["model"],
            "trusted_fixture": identity["trusted_fixture"], "identity_boundary": "Single local owner; synthetic actors only",
            "pack": pack_summary(studio.pack) | {"demo_modelled": example_passes(
                studio.pack.fixtures.demo_request, Workflow.model_validate(active["model"]), studio.pack, studio.plan_proposer)}}

    @app.get("/api/doctor")
    def doctor():
        return studio.provider.doctor()

    @app.get("/api/workbench")
    def workbench():
        return studio.workbench()

    @app.get("/api/repository/impact")
    def repository_impact(term: str = Query(min_length=1, max_length=400),
                          expected_source_hash: str | None = Query(default=None, pattern="^sha256:[0-9a-f]{64}$")):
        return studio.repository_impact(term, expected_source_hash=expected_source_hash)

    @app.get("/api/repository/source")
    def repository_source(reference: str = Query(min_length=1, max_length=800),
                          expected_source_hash: str | None = Query(default=None, pattern="^sha256:[0-9a-f]{64}$")):
        return studio.repository_source(reference, expected_source_hash=expected_source_hash)

    @app.get("/api/repository/freshness")
    def repository_freshness(expected_source_hash: str = Query(pattern="^sha256:[0-9a-f]{64}$")):
        return studio.repository_freshness(expected_source_hash)

    @app.get("/api/repository/change")
    def repository_change(base: str = Query(pattern=COMMIT_OID_PATTERN, max_length=64),
                          head: str = Query(pattern=COMMIT_OID_PATTERN, max_length=64)):
        return studio.repository_change(base, head)

    @app.get("/api/repository/change/file")
    def repository_change_file(base: str = Query(pattern=COMMIT_OID_PATTERN, max_length=64),
                               head: str = Query(pattern=COMMIT_OID_PATTERN, max_length=64),
                               path: str = Query(min_length=1, max_length=1024),
                               reference: str | None = Query(default=None, min_length=1, max_length=800)):
        return studio.repository_change_file(base, head, path, reference)

    @app.get("/api/cases")
    def cases():
        return [{k: c[k] for k in ("id", "version", "request", "stage", "created_at")} for c in studio.store.list_cases()]

    @app.post("/api/cases")
    def new_case(body: NewCase):
        return studio.create(body.request)

    @app.get("/api/cases/{case_id}")
    def get_case(case_id: str):
        return studio.view(case_id)

    @app.post("/api/cases/{case_id}/propose")
    def propose(case_id: str, body: Propose):
        return studio.propose(case_id, body.expected_version, consent=body.consent)

    @app.post("/api/cases/{case_id}/select")
    def select(case_id: str, body: Select):
        return studio.select(case_id, body.expected_version, body.interpretation, OWNER)

    @app.post("/api/cases/{case_id}/edit")
    def edit(case_id: str, body: Edit):
        return studio.edit(case_id, body.expected_version, body.transaction, OWNER)

    @app.post("/api/cases/{case_id}/edit/propose", response_model=TypedEditProposal)
    def propose_edit(case_id: str, body: EditPropose):
        return studio.propose_edit(case_id, body.expected_version, body.request)

    @app.post("/api/cases/{case_id}/edit/check")
    def edit_check(case_id: str, body: EditCheck):
        return studio.edit_check(case_id, body.transaction)

    @app.post("/api/cases/{case_id}/edit/preview", response_model=EditPreview)
    def edit_preview(case_id: str, body: EditCheck):
        return studio.edit_preview(case_id, body.transaction)

    @app.post("/api/cases/{case_id}/undo")
    def undo(case_id: str, body: Version):
        return studio.undo(case_id, body.expected_version, OWNER)

    @app.post("/api/cases/{case_id}/redo")
    def redo(case_id: str, body: Version):
        return studio.redo(case_id, body.expected_version, OWNER)

    @app.get("/api/cases/{case_id}/history")
    def history(case_id: str):
        return studio.history(case_id)

    @app.get("/api/cases/{case_id}/affordances")
    def affordances(case_id: str):
        return studio.affordances(case_id)

    @app.post("/api/cases/{case_id}/layout")
    def layout(case_id: str, body: Layout):
        return studio.layout(case_id, body.expected_version, body.change, OWNER)

    @app.post("/api/cases/{case_id}/save")
    def save(case_id: str, body: Version):
        return studio.save(case_id, body.expected_version)

    @app.post("/api/cases/{case_id}/verify")
    def verify(case_id: str, body: Version):
        return studio.verify(case_id, body.expected_version)

    @app.post("/api/cases/{case_id}/approve", summary="Owner decision on the exact revision")
    def approve(case_id: str, body: Approval):
        return studio.approve(case_id, body.expected_version, body.subject_hash, body.answers, body.acknowledge_unknowns, OWNER, body.scope)

    @app.post("/api/cases/{case_id}/apply")
    def apply(case_id: str, body: Version):
        return studio.apply(case_id, body.expected_version, OWNER)

    @app.post("/api/cases/{case_id}/discard")
    def discard(case_id: str, body: Version):
        return studio.discard(case_id, body.expected_version)

    @app.post("/api/cases/{case_id}/preview")
    def preview(case_id: str, body: Preview):
        return studio.reset_preview(case_id, body.expected_version, body.state)

    @app.post("/api/cases/{case_id}/execute")
    def execute(case_id: str, body: ExecuteCommand):
        return studio.execute(case_id, body)

    @app.get("/api/cases/{case_id}/diagrams")
    def diagrams(case_id: str, fmt: Literal["mermaid", "plantuml", "dot"] = Query("mermaid", alias="format")):
        before, after = studio.workflows(case_id)
        return case_diagrams(before, after, fmt)

    @app.get("/api/cases/{case_id}/export")
    def export(case_id: str):
        return JSONResponse(studio.export(case_id), headers={"Content-Disposition": f'attachment; filename="eija-{case_id}.json"'})

    return app
