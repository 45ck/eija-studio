---
type: Module
title: interfaces.render_html
description: 'Self-contained HTML for `eija render --format html`: generated Mermaid text plus the vendored renderer.'
resource: repo://src/eija_studio/interfaces/render_html.py
tags:
- module
- interfaces
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/interfaces/render_html.py
  title: interfaces/render_html.py
  hash_method: ast-api-v1
  sha256: 10bef972e27804dbff60dae18a6641847772e3f0d7a08612adb1f8487712c344
notes_baseline: bcab3ca8536c83a0780f2a0983dbd915c3ed143b3a1571245eb63823376e2ab4
---

# interfaces.render_html

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Layer | interfaces |
| Code | `repo://src/eija_studio/interfaces/render_html.py` |
| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |

## Module docstring

~~~text
Self-contained HTML for `eija render --format html`: generated Mermaid text plus the vendored renderer.

The page embeds the pinned mermaid.min.js (resources/web/vendor) inline, so it needs no network and no
CDN. It carries no timestamp: equal diagrams give equal bytes. The Mermaid source stays visible under
each figure, because the text, not the picture, is what the drift check compares.
~~~

## Public symbols

_Symbol pages are generated for the domain and application layers only._
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
