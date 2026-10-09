"""The API contract of a built app (#144, ADR-0207): an OpenAPI 3.1 document written from the model, the pack and the
data model. It cannot drift from the generated server (each route is in both), its field schema accepts only what
`check_values` accepts, and it is valid OpenAPI where the validator is installed (NOT_RUN otherwise)."""
from __future__ import annotations

import ast
import re

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from hypothesis_jsonschema import from_schema

from eija_studio.application.api_contract import REFUSALS, api_contract
from eija_studio.domain.data import check_values, data_for
from eija_studio.domain.models import DomainError
from eija_studio.domain.pack import PACKS_ROOT, load_pack
from eija_studio.interfaces.app_build import app_files

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
            if literal := re.fullmatch(r"url\.path == '(/api/[a-z/]+)'", text):
                routes.add((method, literal.group(1)))
            elif text == "match and (not match.group(2))":
                routes.add((method, "/api/records/{id}"))
            elif text == "match and match.group(2)":
                routes.add((method, "/api/records/{id}/act"))
    return routes


def test_every_route_the_server_serves_is_in_the_contract_and_no_other():
    pack, document = contract()
    server = app_files(pack, pack.model)[0]["app/server.py"]
    documented = {(method, path) for path, item in document["paths"].items() for method in item}
    assert served(server) == documented and len(documented) == 6


def test_the_refusal_codes_are_the_servers_by_status():
    pack, _ = contract()
    server = app_files(pack, pack.model)[0]["app/server.py"]
    sets = {name: set(ast.literal_eval(re.search(rf"^{name} = (\{{.*\}})$", server, re.M).group(1))) for name in ("FORBIDDEN", "INVALID")}
    assert set(REFUSALS["403"][1]) == sets["FORBIDDEN"] and set(REFUSALS["400"][1]) == sets["INVALID"]


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
    record = data_for(pack).entity(data_for(pack).record)
    schema = {**document["components"]["schemas"]["Fields"], "$defs": {}}

    @settings(max_examples=60, deadline=None, suppress_health_check=list(HealthCheck))
    @given(from_schema(schema))
    def allowed(values):
        check_values(record, values)

    allowed()


@settings(max_examples=60, deadline=None, suppress_health_check=list(HealthCheck))
@given(st.sampled_from(["memberCard", "dueDate", "format", "renewals"]), st.sampled_from([True, 3, "x" * 21, "2026-13-40", "Scroll"]))
def test_a_value_the_schema_refuses_is_refused_by_check_values_too(name, value):
    import jsonschema

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
    validator = pytest.importorskip("openapi_spec_validator", reason="NOT_RUN: install the interop-api extra")
    for pack_id in PACKS:
        validator.validate(contract(pack_id)[1])
