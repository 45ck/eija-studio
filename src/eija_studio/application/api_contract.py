"""The API contract of an app built from a workflow (ADR-0207): an OpenAPI 3.1 document of what the generated server
serves, written from the model, the pack and the data model rather than by hand.

The paths and status codes are those of the generated server (ADR-0150). Request bodies come from the same sources the
server checks against: the record fields from the record class (the schema says what `check_values` accepts), the
actions from the model's transitions and the actors from the pack's fixture directory. The kernel's refusal codes are
the documented error responses, grouped by the status the server sends them with. The drift check is in the tests: every
route the generated server serves is in the document, and every path in the document is served.

Pure: reads the pack, its model and its data model only.
"""
from __future__ import annotations

from typing import Any

from eija_studio.domain.data import Attribute, DataModel
from eija_studio.domain.models import Workflow
from eija_studio.domain.pack import Pack

FORMAT = "3.1.0"
# The refusals the generated server sends, by status (app/server.py: FORBIDDEN, INVALID, NOT_FOUND, else 409).
REFUSALS = {
    "400": ("The request is malformed, or a field breaks the record class", ["BAD_REQUEST", "INVALID_TITLE", "FIELD_REQUIRED", "FIELD_TYPE",
                                                                           "FIELD_TOO_LONG", "FIELD_CHOICE", "UNKNOWN_FIELD"]),
    "403": ("The actor may not do this", ["UNKNOWN_ACTOR", "ACTOR_REVOKED", "ROLE_DENIED", "ASSIGNMENT_DENIED"]),
    "404": ("No such record", ["NOT_FOUND"]),
    "409": ("The kernel refused the step: the record is not in a state the action leaves, its version moved on, or it was "
            "made under another model or data model", ["STATE_DENIED", "STALE_VERSION", "STALE_INSTANCE", "STALE_DATA"]),
}


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
    record = data.entity(data.record)
    return {"type": "object", "additionalProperties": False, "description": f"The attributes of the {data.record} class (data.json).",
            "properties": {a.name: _field(a) for a in record.attributes},
            "required": [a.name for a in record.attributes if a.required]}


def _error(status: str) -> dict[str, Any]:
    description, codes = REFUSALS[status]
    return {"description": description, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Refusal"},
                                                                          "examples": {c: {"value": {"code": c, "message": "…"}} for c in codes}}}}


def _ok(description: str, schema: dict[str, Any]) -> dict[str, Any]:
    return {"description": description, "content": {"application/json": {"schema": schema}}}


def _body(ref: str) -> dict[str, Any]:
    return {"required": True, "content": {"application/json": {"schema": {"$ref": ref}}}}


def _paths(model: Workflow) -> dict[str, Any]:
    record_id = {"name": "id", "in": "path", "required": True, "schema": {"type": "string", "pattern": "^[0-9a-f]{1,32}$"}}
    actor = {"name": "actor", "in": "query", "required": False, "description": "Whose options to list", "schema": {"$ref": "#/components/schemas/Actor"}}
    obj, many = {"type": "object"}, {"type": "array", "items": {"type": "object"}}
    return {
        "/api/app": {"get": {"operationId": "describeApp", "summary": "The workflow: states, roles, actions, actors and the record class",
                             "responses": {"200": _ok("The app's description", obj)}}},
        "/api/records": {
            "get": {"operationId": "listRecords", "summary": "Every record, newest first", "responses": {"200": _ok("The records", many)}},
            "post": {"operationId": "createRecord", "summary": f"Create a record in {model.initial_state}", "requestBody": _body("#/components/schemas/NewRecord"),
                     "responses": {"201": _ok("The new record", obj), "400": _error("400"), "403": _error("403")}}},
        "/api/records/{id}": {"get": {"operationId": "viewRecord", "summary": "A record, its history and the actions the actor may take",
                                      "parameters": [record_id, actor], "responses": {"200": _ok("The record", obj), "404": _error("404")}}},
        "/api/records/{id}/act": {"post": {"operationId": "act", "summary": "Take an action on a record; the kernel decides",
                                           "parameters": [record_id], "requestBody": _body("#/components/schemas/Act"),
                                           "responses": {"200": _ok("The step the kernel took", obj), **{s: _error(s) for s in ("400", "403", "404", "409")}}}},
        "/api/outbox": {"get": {"operationId": "outbox", "summary": "Notifications written by actions; nothing is sent",
                                "responses": {"200": _ok("The outbox", many)}}},
    }


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
        "paths": _paths(model),
        "components": {"schemas": {
            "Actor": {"type": "string", "enum": sorted(a.id for a in pack.fixtures.actors)},
            "Action": {"type": "string", "enum": actions,
                       "description": "; ".join(f"{a}: {', '.join(by_action[a])}" for a in actions) or "The model has no actions."},
            "Fields": _fields(data),
            "NewRecord": {"type": "object", "additionalProperties": True, "required": ["title", "actor"],
                          "properties": {"title": {"type": "string", "minLength": 1, "maxLength": 200}, "actor": {"$ref": "#/components/schemas/Actor"},
                                         "fields": {"$ref": "#/components/schemas/Fields"}}},
            "Act": {"type": "object", "additionalProperties": True, "required": ["actor", "action", "expected_version"],
                    "properties": {"actor": {"$ref": "#/components/schemas/Actor"}, "action": {"$ref": "#/components/schemas/Action"},
                                   "expected_version": {"type": "integer"},
                                   "operation_id": {"type": "string", "maxLength": 100, "description": "Repeat it to retry safely"}}},
            "Refusal": {"type": "object", "required": ["code", "message"], "properties": {"code": {"type": "string"}, "message": {"type": "string"}}},
        }},
    }
