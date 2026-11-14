"""The API contract of an app built from a workflow (ADR-0207): an OpenAPI 3.1 document of what the generated server
serves, written from the model, the pack and the data model rather than by hand.

The paths and status codes are those of the generated server (ADR-0150). Request bodies come from the same sources the
server checks against: the record fields from the record class (the schema says what `check_values` accepts), the
actions from the model's transitions and the actors from the pack's fixture directory. The kernel's refusal codes are
the documented error responses, grouped by the status the server sends them with: both read one table,
`eija_studio.domain.app_http` (ADR-0250). The drift check is in the tests: every route the generated server serves is in
the document, and every path in the document is served.

Pure: reads the pack, its model and its data model only.
"""
from __future__ import annotations

from typing import Any

from eija_studio.domain.app_http import REFUSALS
from eija_studio.domain.data import Attribute, DataModel, record_fields, references
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack

FORMAT = "3.1.0"
__all__ = ["REFUSALS", "api_contract"]


def _field(attribute: Attribute) -> dict[str, Any]:
    """What `check_values` accepts for one attribute. An empty or null value counts as missing."""
    types: dict[str, dict[str, Any]] = {
        "text": {"type": "string", "maxLength": attribute.max_length},
        "number": {"type": "number"},
        "boolean": {"type": "boolean"},
        "date": {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
        "choice": {"enum": list(attribute.choices)},
    }
    schema = types[attribute.type]
    if attribute.required and attribute.type == "text":
        schema = schema | {"minLength": 1}
    if not attribute.required:
        schema = {"anyOf": [schema, {"type": "null"}, {"const": ""}]}
    return schema | ({"description": attribute.description} if attribute.description else {})


def _fields(data: DataModel | None) -> dict[str, Any]:
    if data is None:
        return {"type": "object", "maxProperties": 0, "description": "This workflow has no record class, so a record has no fields."}
    fields = record_fields(data)  # attributes, then the id fields of built associations (ADR-0235)
    return {"type": "object", "additionalProperties": False, "description": f"The attributes of the {data.record} class (data.json).",
            "properties": {a.name: _field(a) for a in fields},
            "required": [a.name for a in fields if a.required]}


def _error(status: str) -> dict[str, Any]:
    description, codes = REFUSALS[status]
    return {"description": description, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Refusal"},
                                                                          "examples": {c: {"value": {"code": c, "message": "…"}} for c in codes}}}}


def _errors(*statuses: str) -> dict[str, Any]:
    """The error responses of an operation: its own, and those any request can get (a foreign Host header, a failure)."""
    return {s: _error(s) for s in sorted({*statuses, "403", "500"})}


ONCE = {"type": "string", "minLength": 1, "maxLength": 100,
        "description": "Optional. Send the same request again with the same id after a lost answer: the first result is "
                       "returned (200) instead of a second one being made. The id with any other request is OPERATION_CONFLICT."}


def _ok(description: str, schema: dict[str, Any]) -> dict[str, Any]:
    return {"description": description, "content": {"application/json": {"schema": schema}}}


def _body(ref: str) -> dict[str, Any]:
    return {"required": True, "content": {"application/json": {"schema": {"$ref": ref}}}}


def _objects(data: DataModel | None) -> dict[str, Any]:
    """The object store behind reference fields (ADR-0235): the classes a built association names, or none."""
    stored = sorted({r.target for r in references(data)})
    name = {"name": "class", "in": "path", "required": True,
            "description": f"A class a record refers to: {', '.join(stored)}" if stored else "This app stores no objects: every class is 404",
            "schema": {"enum": stored} if stored else {"type": "string", "pattern": "^[A-Z][A-Za-z0-9]{0,39}$"}}
    new = {"required": True, "content": {"application/json": {"schema": {
        "type": "object", "required": ["actor"], "properties": {"actor": {"$ref": "#/components/schemas/Actor"}, "fields": {"type": "object"},
                                                                "operation_id": ONCE}}}}}
    return {"get": {"operationId": "listObjects", "summary": "The stored objects of a class a record refers to", "parameters": [name],
                    "responses": {"200": _ok("The objects", {"type": "array", "items": {"type": "object"}}), **_errors("404")}},
            "post": {"operationId": "createObject", "summary": "Store an object a record can refer to; its values are checked",
                     "parameters": [name], "requestBody": new,
                     "responses": {"201": _ok("The new object and its id", {"type": "object"}),
                                   "200": _ok("The object this operation id made before", {"type": "object"}),
                                   **_errors("400", "404", "408", "409")}}}


def _signals() -> dict[str, Any]:
    """Another workflow's signal starts a record (ADR-0242); served only when the model receives one."""
    return {"post": {"operationId": "receiveSignal", "summary": "Start a record because another workflow sent a signal the model receives",
                     "requestBody": _body("#/components/schemas/Signal"),
                     "responses": {"201": _ok("The record the signal started", {"type": "object"}),
                                   "200": _ok("This operation id was delivered before: the record it started", {"type": "object"}),
                                   **_errors("400", "408", "409")}}}


def _paths(model: Workflow, data: DataModel | None) -> dict[str, Any]:
    record_id = {"name": "id", "in": "path", "required": True, "schema": {"type": "string", "pattern": "^[0-9a-f]{1,32}$"}}
    actor = {"name": "actor", "in": "query", "required": False, "description": "Whose options to list", "schema": {"$ref": "#/components/schemas/Actor"}}
    obj, many = {"type": "object"}, {"type": "array", "items": {"type": "object"}}
    return {
        "/api/app": {"get": {"operationId": "describeApp", "summary": "The workflow: states, roles, actions, actors and the record class",
                             "responses": {"200": _ok("The app's description", obj), **_errors()}}},
        "/api/records": {
            "get": {"operationId": "listRecords", "summary": "Every record, newest first", "responses": {"200": _ok("The records", many), **_errors()}},
            "post": {"operationId": "createRecord", "summary": f"Create a record in {model.initial_state}", "requestBody": _body("#/components/schemas/NewRecord"),
                     "responses": {"201": _ok("The new record", obj), "200": _ok("The record this operation id made before", obj),
                                   **_errors("400", "408", "409")}}},
        "/api/records/{id}": {"get": {"operationId": "viewRecord", "summary": "A record, its history and the actions the actor may take",
                                      "parameters": [record_id, actor], "responses": {"200": _ok("The record", obj), **_errors("404")}}},
        "/api/records/{id}/act": {"post": {"operationId": "act", "summary": "Take an action on a record; the kernel decides",
                                           "parameters": [record_id], "requestBody": _body("#/components/schemas/Act"),
                                           "responses": {"200": _ok("The step the kernel took", obj), **_errors("400", "404", "408", "409")}}},
        "/api/outbox": {"get": {"operationId": "outbox", "summary": "Notifications written by actions; nothing is sent",
                                "responses": {"200": _ok("The outbox", many), **_errors()}}},
        "/api/objects/{class}": _objects(data),
    } | ({"/api/signals": _signals()} if model.receives else {})


def api_contract(pack: Pack, model: Workflow, data: DataModel | None) -> dict[str, Any]:
    """The OpenAPI 3.1 document of the app this pack, model and data model build."""
    actions = sorted({t.action for t in model.transitions})
    by_action = {a: sorted({t.role for t in model.transitions if t.action == a}) for a in actions}
    return {
        "openapi": FORMAT,
        "info": {"title": f"{pack.pack.name} API", "version": pack.pack.version,
                 "description": f"Generated by EIJA Studio from model {model.semantic_hash[:12]}. The kernel decides every action; "
                                "the actor is chosen from the pack's fixture directory, which is not authentication."},
        "servers": [{"url": "http://127.0.0.1:8000", "description": "run.py's default address (--port or PORT change it)"}],
        "paths": _paths(model, data),
        "components": {"schemas": {
            "Actor": {"type": "string", "enum": sorted(a.id for a in pack.fixtures.actors)},
            "Action": {"type": "string", "enum": actions,
                       "description": "; ".join(f"{a}: {', '.join(by_action[a])}" for a in actions) or "The model has no actions."},
            "Fields": _fields(data),
            "NewRecord": {"type": "object", "additionalProperties": True, "required": ["title", "actor"],
                          "properties": {"title": {"type": "string", "minLength": 1, "maxLength": 200}, "actor": {"$ref": "#/components/schemas/Actor"},
                                         "fields": {"$ref": "#/components/schemas/Fields"}, "operation_id": ONCE}},
            "Act": {"type": "object", "additionalProperties": True, "required": ["actor", "action", "expected_version", "operation_id"],
                    "properties": {"actor": {"$ref": "#/components/schemas/Actor"}, "action": {"$ref": "#/components/schemas/Action"},
                                   "expected_version": {"type": "integer"},
                                   "operation_id": {"type": "string", "minLength": 1, "maxLength": 100,
                                                    "description": "Required. Repeat it to retry safely: the step is taken once"}}},
            "Signal": {"type": "object", "additionalProperties": True, "required": ["signal", "sender", "operation_id"],
                       "properties": {"signal": {"type": "string", "enum": sorted({r.signal for r in model.receives})},
                                      "sender": {"type": "string", "enum": sorted({r.sender for r in model.receives})},
                                      "operation_id": {"type": "string", "minLength": 1, "maxLength": 100,
                                                       "description": "Required. Delivering the signal again under it starts nothing new"},
                                      "fields": {"$ref": "#/components/schemas/Fields"}}},
            "Refusal": {"type": "object", "required": ["code", "message"], "properties": {"code": {"type": "string"}, "message": {"type": "string"}}},
        }},
    }
