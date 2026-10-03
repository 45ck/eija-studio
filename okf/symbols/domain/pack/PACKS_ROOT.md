---
type: Constant
title: domain.pack.PACKS_ROOT
description: Constant `PACKS_ROOT` in `domain/pack`.
resource: repo://src/eija_studio/domain/pack.py#PACKS_ROOT
tags:
- symbol
- domain
- constant
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#PACKS_ROOT
  title: domain/pack.py
  hash_method: ast-v2
  sha256: bcd58e4fd50c6ec753873698a933eedfba987dc6fa53aa6b15ff61166d4e55a2
notes_baseline: 8873e838f49775937e10e034aab31a75dda217870c317e0182a2f15debe4409b
verified:
- by: process:codex-packaging-integration
  at: '2026-10-03T03:27:08Z'
  notes_sha256: ef9f78fa44a8af0aa2833ffe3ec878e5a9d5c488fd24b9cabfa1c46566aa2878
  sources_sha256: 0f2ed1d2e9ba30770a2c96ab757ec39e60a91f0c3835a776e4244f9c41bdee4e
- by: process:codex-integrated-pack-resolution
  at: '2026-10-03T03:49:04Z'
  notes_sha256: d0ac96f5f9f00b472bb1f410011e535a6de9480640ce283779486f696e2ef009
  sources_sha256: 8873e838f49775937e10e034aab31a75dda217870c317e0182a2f15debe4409b
---

# domain.pack.PACKS_ROOT

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | constant |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `PACKS_ROOT = _packs_root(Path(__file__).resolve().parents[1])` |
| Code | `repo://src/eija_studio/domain/pack.py#PACKS_ROOT` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

_The source carries no docstring._
<!-- okf:generated:end facts -->

## Notes

The shared root prefers an existing bundled `resources/packs` location. Without a
bundle, only the canonical `src/eija_studio` layout with readable TOML project
metadata naming `eija-studio` may use authored top-level packs. This permits source
distributions and editable installs without Git. Other layouts or missing, invalid
or unrelated metadata keep the bundled path, so a missing installed bundle cannot
silently adopt valid adjacent packs. A present but incomplete or malformed bundle
is not rescued by another root. Explicit `EIJA_PACK` precedence and pack-content
validation remain in `default_location` and `load_pack`; this root grants no trust
or authority.

<!-- okf:generated:begin links -->
## Referenced by

* [domain.pack.default_location](/symbols/domain/pack/default_location.md) - ``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.
<!-- okf:generated:end links -->
