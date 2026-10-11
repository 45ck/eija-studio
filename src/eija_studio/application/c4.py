"""Read-only C4 views of generated source and declared model contracts.

Containers and component dependencies reuse the existing source projections. A
role is a fixture contract, never an authenticated person or connected provider.
This module generates neither executable meaning nor runtime observations.
"""
from __future__ import annotations

from typing import Any

from eija_studio.application.components import app_components
from eija_studio.application.deployment import app_deployment
from eija_studio.application.class_build import class_build
from eija_studio.application.build_subject import checked_build_subject, snapshot_contracts
from eija_studio.domain.data import DataModel
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack, Role

FORMAT = "eija.c4.v1"
SYSTEM = "system:generated-app"
LIMITS = [
    "Structural projection of the generated source; no runtime observation or deployment proof is supplied.",
    "Actors are fixture roles, not authenticated people. Agent, timer and external-system roles have no generated connector or scheduler.",
    "Notification effects enqueue locally; external delivery, cloud deployment and cross-workflow messaging are unsupported.",
    "Only the designated record class is stored. Other classes and relationships remain design.",
]


def _node(cid: str, name: str, kind: str, technology: str, summary: str,
          sources: list[str], *, support: str = "generated_structure", drill: str | None = None,
          details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"id": cid, "name": name, "kind": kind, "technology": technology, "summary": summary,
            "support": support, "sources": sources, "drill": drill, "details": details or {}}


def _relation(source: str, target: str, label: str, mechanism: str, sources: list[str],
              *, support: str = "generated_structure") -> dict[str, Any]:
    return {"source": source, "target": target, "label": label, "mechanism": mechanism,
            "sources": sources, "support": support}


def _actor(pack: Pack, role: Role, actions: list[str]) -> dict[str, Any]:
    return _node("actor:" + role.id, role.id, "person" if role.kind == "human" else "external_actor",
                 role.kind, role.description or "Declared fixture role", ["app/pack.json"],
                 support="fixture_contract", details={"actions": actions, "kind": role.kind,
                 "fixture_actors": [a.id for a in pack.fixtures.actors if a.role == role.id],
                 "authentication": "UNSUPPORTED", "external_connection": "NOT_IMPLEMENTED"})


def _context(pack: Pack, model: Workflow) -> dict[str, Any]:
    system = _node(SYSTEM, pack.pack.name, "software_system", "Generated local application",
                   f"{len(model.states)} states · {len(model.transitions)} actions in one workflow",
                   ["app/model.json", "app/pack.json"], drill="containers",
                   details={"states": list(model.states), "actions": [t.model_dump(mode="json") for t in model.transitions]})
    nodes, relations = [], []
    for role in pack.roles:
        actions = [t.action for t in model.transitions if t.role == role.id]
        cid = "actor:" + role.id
        nodes.append(_actor(pack, role, actions))
        if actions:
            relations.append(_relation(cid, SYSTEM, ", ".join(actions), "Declared action authority",
                                       ["app/model.json", "app/pack.json"], support="fixture_contract"))
    return {"name": "System context", "boundary": "One local software system",
            "nodes": [*nodes, system], "relationships": relations}


def _containers(deployment: dict[str, Any]) -> dict[str, Any]:
    names = {"node:browser": ("Web application", "HTML · JavaScript · CSS", "Renders screens and calls the local API"),
             "node:process": ("Application server", "Python · HTTP", "Executes the installed kernel against this workflow"),
             "node:database": ("Record store", "SQLite", "Local workflow records, operation replay, audit and outbox")}
    nodes = []
    for item in deployment["nodes"]:
        name, technology, summary = names[item["id"]]
        sources = [path for artifact in item["artifacts"] for path in artifact["files"]]
        if item["id"] == "node:database":
            sources = ["app/service.py", "run.py"]
        nodes.append(_node(item["id"], name, "database" if item["id"] == "node:database" else "container",
                           technology, summary, sources, drill="components" if item["id"] == "node:process" else None,
                           details={"address_default": item["address"], "configuration": item["set_by"],
                                    "artifacts": item["artifacts"]}))
    relationships = [_relation(path["source"], path["target"], ", ".join(path["names"]) or "Local database connection",
                                path["protocol"], ["app/web/app.js", "app/server.py"] if path["protocol"] == "HTTP"
                                else ["app/service.py"])
                     for path in deployment["paths"]]
    return {"name": "Containers", "boundary": SYSTEM, "nodes": nodes, "relationships": relationships}


def _inside_server(component: dict[str, Any]) -> bool:
    cid = component["id"]
    return (cid.startswith("app.") or component["stereotype"] in {"kernel", "database"}
            or (cid.startswith("app/") and cid.endswith(".json")))


def _component(item: dict[str, Any], summaries: dict[str, str], imports: dict[str, list[str]]) -> dict[str, Any]:
    titles = {"app.server": "HTTP adapter", "app.service": "Record service", "app/web": "Web application",
              "sqlite3": "SQLite driver"}
    cid = item["id"]
    sources = item["files"] or ["repo://src/" + cid.replace(".", "/") + ".py"]
    if cid == "sqlite3":
        sources = ["app/service.py"]
    return _node(cid, titles.get(cid, item["name"]), item["stereotype"],
                 "JSON contract" if cid.endswith(".json") else "Python", summaries.get(cid, item["name"]), sources,
                 details={"imports": imports.get(cid, []), "files": item["files"], "lines": item["lines"]})


def _component_links(dependencies: list[dict[str, Any]], nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = {node["id"]: node["sources"] for node in nodes}
    relationships = [_relation(link["source"], link["target"], ", ".join(link["names"]) or "imports",
                                "Generated source dependency", sources[link["source"]])
                     for link in dependencies if link["source"] in sources and link["target"] in sources]
    return relationships


def _components(diagram: dict[str, Any], model: Workflow, data: DataModel | None) -> dict[str, Any]:
    summaries = {"app.server": "Serves the page and dispatches its API requests",
                 "app.service": "Loads model contracts and supplies atomic storage to the installed kernel",
                 "app/model.json": f"{len(model.states)} states · {len(model.transitions)} actions; policy lives in the kernel",
                 "app/data.json": f"Stored record: {data.record}" if data else "No record data contract",
                 "sqlite3": "Embedded database driver in the application server process"}
    imports = {item["provider"]: item["names"] for item in diagram["interfaces"]}
    nodes = [_component(item, summaries, imports) for item in diagram["components"] if _inside_server(item)]
    relationships = _component_links(diagram["dependencies"], nodes)
    return {"name": "Server components", "boundary": "node:process", "nodes": nodes, "relationships": relationships}


def app_c4(files: dict[str, str], *, kernel_version: str = "unknown") -> dict[str, Any]:
    """Current generated-source architecture, plus explicit fixture and data-design limits."""
    subject = checked_build_subject(files)
    pack, model, data, _ = snapshot_contracts(files)
    components, deployment = app_components(files), app_deployment(files, kernel_version)
    return {"format": FORMAT,
            "subject": subject,
            "levels": {"context": _context(pack, model), "containers": _containers(deployment),
                       "components": _components(components, model, data)},
            "data_support": class_build(data) if data else None,
            "effects": [{"id": effect.id, "kind": effect.kind, "recipient": effect.recipient,
                         "delivery": "LOCAL_OUTBOX_ONLY" if effect.kind == "notification" else "LOCAL_AUDIT_ONLY"}
                        for effect in pack.effects.catalog],
            "limits": list(LIMITS), "unserved_routes": components["unserved_routes"],
            "observation": {"runtime": "NOT_OBSERVED", "deployment": "UNSUPPORTED", "policy_change": False}}
