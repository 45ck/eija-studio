# ADR-0226: standard record navigation and a connected presentation map

* Status: accepted for generated local record apps
* Date: 2026-10-11

## Context

Generated applications should offer familiar navigation without requiring every project to design a shell from scratch. The default target is a record-based app. Screens, attributes and workflow actions already have canonical models; a separate frontend policy model would let the interface drift from the system being reviewed.

## Decision

Derive a frozen `eija.navigation.v1` model from the existing pack, workflow, data and screens. The default hierarchy is Records → New record / Record detail → workflow action screens. Destinations name real panels and focus targets, with explicit selected-record requirements. The generated app exports `app/navigation.json`, validates it against its loaded contracts and exposes it through `/api/app`. React renders the navigation from this model.

Create/read are executable. General record update/delete remain unsupported; workflow actions execute their existing state changes. Navigation grants no authority. A selected action still needs the current service response and its state, role, version and operation checks. Missing navigation bindings disable the affected control instead of guessing a destination.

The workbench presentation map reads the same immutable generated snapshot. Show a destination, its screen fields and controls, the linked UML attribute/use case and the declared action consequences. Label it checked design. A current app identity match is useful provenance, but rendered behavior and permission checks remain separate observations. Changed or absent subjects cannot be labelled a current runtime match.

This uses UWE's separation of content, navigation and presentation as a reference, not a claim of full UWE conformance. The initial destinations are in-page panels; no URL routes or generic CRUD permissions are invented. Authored routes, multiple record types and more complex navigation require a future versioned contract with runtime meaning.

## Verification

Refuse unknown screen actions/attributes, broken hierarchy, mismatched loaded navigation and fake CRUD capabilities. A label, field order/type or navigation change must produce a different generated subject. Observe actual React navigation/focus and screen controls, link selections back to UML and keep denied service actions denied without writes. Retain malformed and stale cases as explicit failures, not decorative successful maps.

## Reference

[UWE navigation tutorial](https://uwe.pst.ifi.lmu.de/teachingTutorialNavigation.html) and [presentation tutorial](https://uwe.pst.ifi.lmu.de/teachingTutorialPresentation.html).
