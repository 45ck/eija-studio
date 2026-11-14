"""The API contract of a built app (#144, ADR-0207): an OpenAPI 3.1 document written from the model, the pack and the
data model. It cannot drift from the generated server (each route is in both), its field schema accepts only what
`check_values` accepts, and it is valid OpenAPI where the validator is installed (NOT_RUN otherwise)."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import jsonschema
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from hypothesis_jsonschema import from_schema

from eija_studio.application.api_contract import api_contract
from eija_studio.application import runtime
from eija_studio.bootstrap import source_identity
from eija_studio.domain.app_http import STATUS
from eija_studio.domain import data as data_module
from eija_studio.domain.data import check_record, check_values, data_for
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.interfaces.app_build import app_files

try:  # the interop-api extra: the oracle that the document is valid OpenAPI 3.1
    import openapi_spec_validator
except ImportError:  # pragma: no cover - NOT_RUN without the extra
    openapi_spec_validator = None

PACKS = sorted(p.parent.name for p in PACKS_ROOT.glob("*/data.json"))


def contract(pack_id: str = "library-loan"):
    pack = load_pack(PACKS_ROOT / pack_id)
    return pack, api_contract(pack, pack.model, data_for(pack))


def served(server: str) -> set[tuple[str, str]]:
    """(method, path) for each route the generated server answers, read from its do_GET and do_POST."""
    routes = set()
    for function in (n for n in ast.walk(ast.parse(server)) if isinstance(n, ast.FunctionDef) and n.name in ("do_GET", "do_POST")):
        method = function.name.removeprefix("do_").lower()
        for test in (n.test for n in ast.walk(function) if isinstance(n, ast.If)):
            text = ast.unparse(test)
            if literal := re.fullmatch(r"url\.path == '(/api/[a-z/]+)'( and MODEL\.receives)?", text):
                routes.add((method, literal.group(1)))
            elif text == "stored":
                routes.add((method, "/api/objects/{class}"))
            elif text == "match and (not match.group(2))":
                routes.add((method, "/api/records/{id}"))
            elif text == "match and match.group(2)":
                routes.add((method, "/api/records/{id}/act"))
    return routes


@pytest.mark.parametrize(("pack_id", "routes"), [("library-loan", 8), ("library-fines", 9)])
def test_every_route_the_server_serves_is_in_the_contract_and_no_other(pack_id, routes):
    """The signals route is served, and documented, only for a model that receives a signal (ADR-0254: it was missing,
    and the route parser could not see it, so this test could not fail for it)."""
    pack, document = contract(pack_id)
    server = app_files(pack, pack.model, identity_provider=source_identity)[0]["app/server.py"]
    documented = {(method, path) for path, item in document["paths"].items() for method in item}
    server_routes = served(server) - (set() if pack.model.receives else {("post", "/api/signals")})
    assert server_routes == documented and len(documented) == routes


def test_the_server_and_the_contract_read_one_status_table():
    """No status table of its own in the server: it answers each refusal with `status_of`, which the contract documents."""
    pack, document = contract()
    server = app_files(pack, pack.model, identity_provider=source_identity)[0]["app/server.py"]
    assert "from eija_studio.domain.app_http import status_of" in server
    assert not re.search(r"^(FORBIDDEN|INVALID) = ", server, re.M) and not re.search(r"self\._json\((4|5)\d\d,", server)
    documented = {c for responses in (op["responses"] for item in document["paths"].values() for op in item.values())
                  for status, response in responses.items() if status >= "400"
                  for c in response["content"]["application/json"]["examples"]}
    assert documented == set(STATUS)


def raised_codes() -> set[str]:
    """Every refusal code the built app can answer with: what the kernel, the data model's checks and the app raise."""
    templates = Path(runtime.__file__).resolve().parents[1] / "resources" / "appgen"
    sources = [Path(runtime.__file__).read_text(), Path(data_module.__file__).read_text()]
    sources += [(templates / name).read_text() for name in ("service.py.tmpl", "server.py.tmpl")]  # what answers requests
    codes = {m for text in sources for m in re.findall(r'(?:DomainError|Refused)\(\s*"([A-Z_]+)"', text)}
    codes |= {m for text in sources for m in re.findall(r'"code": "([A-Z_]+)"', text)}
    return codes - {"DATA_INVALID", "DATA_PACK_MISMATCH"}  # build-time checks of the data model, never a request's


def test_every_code_the_app_can_refuse_with_has_a_documented_status():
    assert raised_codes() - set(STATUS) == set()
    assert {"ROLE_CANNOT_START", "SEPARATION_DENIED", "HOST_DENIED", "INTERNAL_ERROR", "OPERATION_CONFLICT"} <= raised_codes()


def test_an_act_must_carry_an_operation_id_and_a_create_may():
    _, document = contract()
    schemas = document["components"]["schemas"]
    assert "operation_id" in schemas["Act"]["required"] and schemas["Act"]["properties"]["operation_id"]["minLength"] == 1
    assert "operation_id" not in schemas["NewRecord"]["required"] and "operation_id" in schemas["NewRecord"]["properties"]


def test_the_actions_and_actors_come_from_the_model_and_the_pack():
    pack, document = contract()
    schemas = document["components"]["schemas"]
    assert schemas["Action"]["enum"] == sorted({t.action for t in pack.model.transitions})
    assert schemas["Actor"]["enum"] == sorted(a.id for a in pack.fixtures.actors)
    assert schemas["Fields"]["required"] == ["itemTitle", "memberCard", "dueDate", "format"]
    assert document["info"]["title"] == "Library loan API" and document["openapi"] == "3.1.0"


@pytest.mark.parametrize("pack_id", PACKS)
def test_every_record_the_field_schema_allows_passes_check_values(pack_id):
    pack, document = contract(pack_id)
    data = data_for(pack)
    schema = {**document["components"]["schemas"]["Fields"], "$defs": {}}

    @settings(max_examples=60, deadline=None, suppress_health_check=list(HealthCheck))
    @given(from_schema(schema))
    def allowed(values):
        check_record(data, values, lambda _cls, _id: True)  # a reference field names a stored object (ADR-0235)

    allowed()


@settings(max_examples=60, deadline=None, suppress_health_check=list(HealthCheck))
@given(st.sampled_from(["memberCard", "dueDate", "format", "renewals"]), st.sampled_from([True, 3, "x" * 21, "2026-13-40", "Scroll"]))
def test_a_value_the_schema_refuses_is_refused_by_check_values_too(name, value):
    pack, document = contract()
    record = data_for(pack).entity(data_for(pack).record)
    values = {"itemTitle": "Dune", "memberCard": "M-1", "dueDate": "2026-11-01", "format": "Book", name: value}
    schema_ok = jsonschema.Draft202012Validator(document["components"]["schemas"]["Fields"],
                                                format_checker=jsonschema.FormatChecker()).is_valid(values)
    try:
        check_values(record, values)
        kernel_ok = True
    except DomainError:
        kernel_ok = False
    assert schema_ok == kernel_ok, (name, value)


def test_the_document_is_valid_openapi_3_1():
    if openapi_spec_validator is None:
        pytest.skip("NOT_RUN: install the interop-api extra (openapi-spec-validator)")
    for pack_id in PACKS:
        openapi_spec_validator.validate(contract(pack_id)[1])
