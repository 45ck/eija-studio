---
type: Architecture Decision Record
title: 'ADR-0024: Render Mermaid in a sandboxed frame so the Studio page keeps its strict CSP'
description: 'The Studio page ships `Content-Security-Policy: default-src ''none''; script-src ''self''; style-src ''self''; connect-src ''self''; img-src ''self'' data:; frame-ancestors ''none''; base-uri ''none''; form-action ''self''`.'
resource: repo://docs/adr/0024-sandboxed-frame-for-mermaid-rendering.md
tags:
- adr
- accepted
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0024-sandboxed-frame-for-mermaid-rendering.md
  title: 0024-sandboxed-frame-for-mermaid-rendering.md
  hash_method: lf-sha256-v1
  sha256: cb77aa31642c7f23c2c7b2636239c21e6726aeeb48f3e57d9569c2b1d809ed52
notes_baseline: d6f67eeb690ad60adf324ab30765594137ee091a554624578b3427da579cf9de
---

# ADR-0024: Render Mermaid in a sandboxed frame so the Studio page keeps its strict CSP

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | accepted |
| Date | 2026-09-29 |
| Lane | visual |
| Source | `repo://docs/adr/0024-sandboxed-frame-for-mermaid-rendering.md` |

## Decision outcome (verbatim)

> Chosen option: "sandboxed frame", because it relaxes styles only inside a document that has no route to the API or the token, and leaves the Studio page's `script-src`, `style-src` and `connect-src` unchanged.
>
> Precisely:
>
> * Studio page (`/`): the policy above gains exactly one directive, `frame-src 'self'`. `X-Frame-Options: DENY` and `frame-ancestors 'none'` are unchanged.
> * `/visual-frame` (static `visual-frame.html`): `default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src data:; connect-src 'none'; frame-ancestors 'self'; base-uri 'none'; form-action 'none'; sandbox allow-scripts`, plus `X-Frame-Options: SAMEORIGIN`. `script-src` has no `unsafe-inline` and no `unsafe-eval`. The document runs in an opaque origin (`sandbox` without `allow-same-origin`), cannot read `sessionStorage`, and `connect-src 'none'` forbids network calls.
> * The `<iframe>` also carries `sandbox="allow-scripts"`. The parent sends diagram text with `postMessage`; the frame accepts only messages whose `event.source` is its parent, and the parent accepts only messages from that frame's `contentWindow`. Text only crosses; no token, no HTML.
> * Static assets are an exact allowlist: `/assets/vendor/mermaid.min.js`, `/assets/visual-frame.js`, `/assets/visual-frame.css`. The vendored LICENSE and version record are not served.
> * Mermaid runs with `securityLevel: "strict"` (its own sanitiser), and every label is also escaped by the emitters.

## Sections

* Context and problem statement
* Decision drivers
* Considered options
* Decision outcome
* OSS check (required for any custom module)
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [ADR-0023: Generated UML and visual diff, with Mermaid as the primary renderer](/adrs/0023-generated-uml-and-visual-diff.md) - ADR-0019 decided that diagrams are generated projections of the executable model.
* [ADR-0195: Sequence diagrams are the pack's scenarios, drawn in UML and checked by the kernel step by step](/adrs/0195-sequence-diagrams-the-kernel-checks.md) - Engineers who read UML expect sequence diagrams beside the state machine, class, use case and component diagrams.
* [Visual model: UML/diagram generation and visual diff](/lanes/0023-visual-model-uml-diagram-generation.md) - Capability lane with ADR numbers 0023–0024 reserved.
<!-- okf:generated:end links -->
