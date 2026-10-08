"""The component diagram (ADR-0155) is read from the generated files: every dependency is in the code, none is invented."""
from __future__ import annotations

from pathlib import Path

import pytest

from eija_studio.application.components import app_components
from eija_studio.domain.pack import load_pack
from eija_studio.interfaces.app_build import app_files

ROOT = Path(__file__).resolve().parents[1]


def files_of(name: str) -> dict[str, str]:
    pack = load_pack(ROOT / "packs" / name)
    return app_files(pack, pack.model)[0]


def uses(diagram: dict, source: str, target: str) -> list[str] | None:
    return next((d["names"] for d in diagram["dependencies"] if d["source"] == source and d["target"] == target), None)


def test_the_built_app_calls_the_kernel_and_has_no_rules_of_its_own():
    diagram = app_components(files_of("library-loan"))
    ids = {c["id"]: c["stereotype"] for c in diagram["components"]}
    assert ids["app.service"] == "component" and ids["eija_studio.application.runtime"] == "kernel"
    assert ids["sqlite3"] == "database" and ids["app/web"] == "browser" and ids["tests.test_conformance"] == "test"
    assert uses(diagram, "app.service", "eija_studio.application.runtime") == ["check_actor", "execute", "initialise"]
    assert "check_values" in uses(diagram, "app.service", "eija_studio.domain.data")
    assert uses(diagram, "app/web", "app.server") == ["/api/app", "/api/outbox", "/api/records"]
    assert uses(diagram, "app.service", "app/data.json") == ["reads"] and uses(diagram, "tests.test_conformance", "app.service")
    assert diagram["unserved_routes"] == [] and "json" in diagram["not_drawn"]


def test_a_pack_without_a_data_model_has_no_data_file_component():
    diagram = app_components(files_of("eija-review-slice"))
    assert "app/data.json" not in {c["id"] for c in diagram["components"]}


@pytest.mark.parametrize(("change", "check"), [
    # A dependency added to the code appears; one removed disappears. The diagram never needs editing by hand.
    (lambda f: f | {"app/service.py": f["app/service.py"] + "\nfrom eija_studio.domain.policy import check_policy\n"},
     lambda d: uses(d, "app.service", "eija_studio.domain.policy") == ["check_policy"]),
    (lambda f: f | {"app/service.py": f["app/service.py"].replace("import sqlite3\n", "")},
     lambda d: uses(d, "app.service", "sqlite3") is None),
    (lambda f: f | {"app/web/app.js": f["app/web/app.js"] + '\napi("/api/reports");\n'},
     lambda d: d["unserved_routes"] == ["/api/reports"]),
])
def test_the_diagram_follows_the_code(change, check):
    assert check(app_components(change(files_of("library-loan"))))


def test_interfaces_list_what_users_import():
    diagram = app_components(files_of("excursion"))
    runtime = next(i for i in diagram["interfaces"] if i["provider"] == "eija_studio.application.runtime")
    assert runtime["names"] == ["check_actor", "execute", "initialise"]


def test_only_imported_names_are_provided_interfaces():
    diagram = app_components(files_of("library-loan"))
    providers = {i["provider"] for i in diagram["interfaces"]}
    assert "app/data.json" not in providers and "app/web" not in providers  # read and served, not imported
    assert all("reads" not in i["names"] and "serves" not in i["names"] for i in diagram["interfaces"])
