"""A bounded presentation/navigation lens over one exact generated snapshot.

This is a checked design projection, not a second UI contract, policy interpreter
or runtime observation. Existing Screens, DataModel and Workflow own its meaning.
"""
from __future__ import annotations

from typing import Any

from eija_studio.application.build_subject import checked_build_subject, snapshot_contracts
from eija_studio.domain.data import Attribute, DataModel
from eija_studio.domain.models import DomainError, Transition, Workflow
from eija_studio.domain.navigation import Destination, Navigation, navigation_for
from eija_studio.domain.pack import Pack
from eija_studio.domain.screens import Screen, Screens, require_buildable

FORMAT = "eija.presentation-map.v1"
LIMITS = (
    "UWE-inspired content, navigation and presentation projection; not a full UWE metamodel or conformance claim.",
    "These cards describe generated design. A matching app identity does not prove rendered accessibility or runtime behaviour.",
    "Action fields display existing record values. Typed action inputs and record updates are not implemented.",
    "Roles are local fixtures. The application service checks current authority, state and version for every action.",
)


def _control(attribute: Attribute, editable: bool, react: bool) -> dict[str, Any]:
    if not editable:
        return {"component": "Values" if react else "Description list", "native_type": "read-only text"}
    component = {"boolean": "Checkbox", "choice": "NativeSelect"}.get(attribute.type, "TextInput")
    native = {"boolean": "checkbox", "choice": "select"}.get(attribute.type, attribute.type)
    return {"component": component if react else "Native HTML", "native_type": native,
            "browser_required": attribute.required and attribute.type != "boolean"}


def _fields(screen: Screen, data: DataModel | None, *, editable: bool, react: bool) -> list[dict[str, Any]]:
    if data is None:
        if screen.fields:
            raise DomainError("SCREEN_UNKNOWN_ATTRIBUTE", "A screen without a data model cannot declare record fields")
        return []
    attributes = {a.name: a for a in data.entity(data.record).attributes}
    return [{"attribute": field.attribute, "label": field.label or field.attribute, "order": order,
             "type": attributes[field.attribute].type, "required": attributes[field.attribute].required,
             "choices": list(attributes[field.attribute].choices), "max_length": attributes[field.attribute].max_length,
             "editable": editable, "control": _control(attributes[field.attribute], editable, react),
             "class_ref": "class:" + data.record, "source": "app/data.json"}
            for order, field in enumerate(screen.fields)]


def _authority(transition: Transition | None, model: Workflow) -> dict[str, Any]:
    if transition is None:
        detail = {"role": "Any active fixture actor", "guards": ["actor_active"], "from_state": None,
                  "to_state": model.initial_state, "required_effects": [], "forbidden_effects": []}
    else:
        detail = {"role": transition.role, "guards": list(transition.guards), "from_state": transition.from_state,
                  "to_state": transition.to_state, "required_effects": list(transition.required_effects),
                  "forbidden_effects": list(transition.forbidden_effects)}
    return detail | {"status": "SERVICE_CHECKED_AT_ACTION", "checker": "eija_studio.application.runtime"}


def _transition(screen: Screen, model: Workflow) -> Transition | None:
    transition = next((t for t in model.transitions if t.action == screen.use_case), None)
    if screen.use_case is not None and transition is None:
        raise DomainError("NAVIGATION_ACTION_MISSING", "The screen's action is absent from this workflow")
    return transition


def _screen(screen: Screen | None, destination: Destination, data: DataModel | None,
            model: Workflow, react: bool) -> dict[str, Any]:
    if screen is None:
        raise DomainError("NAVIGATION_SCREEN_MISSING", "The navigation destination has no supported screen")
    transition = _transition(screen, model)
    create = screen.use_case is None
    return {"id": destination.id, "kind": destination.kind, "panel": destination.panel,
            "title": screen.title, "button": screen.button or screen.use_case or "Create", "use_case": screen.use_case,
            "use_case_ref": "usecase:create" if create else destination.transition_ref,
            "class_ref": "class:" + data.record if data else None,
            "fields": _fields(screen, data, editable=create, react=react),
            "component": "Records" if create else "ActionScreen", "sources": ["app/screens.json", "app/model.json"],
            "authority": _authority(transition, model)}


def _navigation(files: dict[str, str], pack: Pack, model: Workflow,
                data: DataModel | None, screens: Screens) -> Navigation:
    try:
        navigation = Navigation.model_validate_json(files["app/navigation.json"])
    except (KeyError, ValueError) as error:
        raise DomainError("NAVIGATION_INVALID", "The generated navigation model is missing or invalid") from error
    if navigation != navigation_for(pack, model, data, screens):
        raise DomainError("NAVIGATION_MODEL_MISMATCH", "Generated navigation differs from this workflow, data or screens")
    return navigation


def _frontend(files: dict[str, str]) -> dict[str, str]:
    react = "frontend/main.jsx" in files
    return {"framework": "React" if react else "HTML / JavaScript", "library": "Mantine" if react else "Native controls",
            "source": "frontend/main.jsx" if react else "app/web/app.js"}


def _record(data: DataModel | None) -> dict[str, Any]:
    if data is None:
        return {"name": "Record", "class_ref": None, "fields": []}
    return {"name": data.record, "class_ref": "class:" + data.record,
            "fields": [a.name for a in data.entity(data.record).attributes]}


def app_presentation(files: dict[str, str]) -> dict[str, Any]:
    """Link declared screens, controls and action consequences from validated generated bytes."""
    subject = checked_build_subject(files)
    pack, model, data, screens = snapshot_contracts(files)
    require_buildable(screens, model, data)
    navigation = _navigation(files, pack, model, data, screens)
    frontend = _frontend(files)
    react = frontend["framework"] == "React"
    projected = [_screen(screens.screen(destination.use_case), destination, data, model, react)
                 for destination in navigation.destinations if destination.kind in {"create", "action"}]
    create = next(screen for screen in projected if screen["kind"] == "create")
    actions = [screen for screen in projected if screen["kind"] == "action"]
    return {"format": FORMAT, "support": "CHECKED_DESIGN", "subject": subject,
            "name": pack.pack.name, "frontend": frontend, "record": _record(data),
            "create": create, "actions": actions, "navigation": navigation.model_dump(mode="json"),
            "observation": {"runtime": "NOT_OBSERVED", "rendered_ui": "NOT_OBSERVED", "policy_change": False},
            "limits": list(LIMITS)}
