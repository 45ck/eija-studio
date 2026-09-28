"""Loopback-only local adapter. No public hosting, CORS, remote provider proxy or raw file endpoint."""
from __future__ import annotations
import hmac
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import Field
from eija_studio.domain.models import Contract, DomainError, OWNER, SemanticTransaction, LayoutChange, ExecuteCommand

class NewCase(Contract):
    request: str = Field(min_length=1, max_length=6000)
class Version(Contract):
    expected_version: int = Field(ge=0, strict=True)
class Propose(Version):
    consent: bool = Field(default=False, strict=True)
class Select(Version):
    interpretation: Literal["recommend_only", "final_approval", "confirm_only", "unsupported"]
class Edit(Version):
    transaction: SemanticTransaction
class Layout(Version):
    change: LayoutChange
class Preview(Version):
    state: str | None = None
class Approval(Version):
    subject_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    answers: dict[str, str]
    acknowledge_unknowns: bool = Field(strict=True)
    scope: Literal["local-demo", "field-use"] = "local-demo"


def create_app(studio, token: str, port: int = 8765) -> FastAPI:
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
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"})
        return response

    @app.exception_handler(DomainError)
    async def domain_error(request, exc):
        status = 404 if exc.code == "NOT_FOUND" else 403 if exc.code in {"AUTHORITY_REQUIRED", "EGRESS_CONSENT_REQUIRED"} else 409
        return JSONResponse({"code": exc.code, "message": exc.message}, status_code=status)

    @app.exception_handler(RequestValidationError)
    async def contract_error(request, exc):
        # Do not echo rejected input, which might contain a mistakenly pasted key.
        return JSONResponse({"code": "CONTRACT_REJECTED", "message": "Invalid fields/types for this command"}, status_code=422)

    @app.get("/")
    def index():
        return FileResponse(web / "index.html")

    @app.get("/assets/{name}")
    def asset(name: str):
        if name not in {"app.js", "app.css"}:
            return JSONResponse({"code": "NOT_FOUND"}, status_code=404)
        return FileResponse(web / name)

    @app.get("/api/status")
    def status():
        with studio.store.transaction() as u:
            active = u.active()
        identity = studio.identity_provider()
        return {"version": "0.2.0", "provider": studio.provider.name, "network_enabled": studio.allow_network,
            "provider_networked": studio.provider.networked, "baseline_version": active["version"], "baseline": active["model"],
            "trusted_fixture": identity["trusted_fixture"], "identity_boundary": "Single local owner; synthetic actors only"}

    @app.get("/api/doctor")
    def doctor():
        return studio.provider.doctor()

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

    @app.post("/api/cases/{case_id}/layout")
    def layout(case_id: str, body: Layout):
        return studio.layout(case_id, body.expected_version, body.change, OWNER)

    @app.post("/api/cases/{case_id}/save")
    def save(case_id: str, body: Version):
        return studio.save(case_id, body.expected_version)

    @app.post("/api/cases/{case_id}/verify")
    def verify(case_id: str, body: Version):
        return studio.verify(case_id, body.expected_version)

    @app.post("/api/cases/{case_id}/approve")
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

    @app.get("/api/cases/{case_id}/export")
    def export(case_id: str):
        return JSONResponse(studio.export(case_id), headers={"Content-Disposition": f'attachment; filename="eija-{case_id}.json"'})

    return app
