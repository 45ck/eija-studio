---
type: Function
title: domain.pack.default_location
description: '``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.'
resource: repo://src/eija_studio/domain/pack.py#default_location
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/pack.py#default_location
  title: domain/pack.py
  hash_method: ast-v2
  sha256: bfb22dd27d011375d49e8184b619f91ac40d4040e23799e184099e61074d8001
notes_baseline: 2643e36637c0a40e9faa5bfaefd6321a0a3bc312ec34ab38cb4c0030b20c3877
---

# domain.pack.default_location

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/pack`](/modules/domain/pack.md) |
| Signature | `def default_location() -> Path` |
| Code | `repo://src/eija_studio/domain/pack.py#default_location` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
``$EIJA_PACK`` if set, else the pack named by ``packs/default.json``.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.pack.DEFAULT_FILE](/symbols/domain/pack/DEFAULT_FILE.md) - Constant `DEFAULT_FILE` in `domain/pack`.
* [domain.pack.ENV_PACK](/symbols/domain/pack/ENV_PACK.md) - Constant `ENV_PACK` in `domain/pack`.
* [domain.pack.PACKS_ROOT](/symbols/domain/pack/PACKS_ROOT.md) - Constant `PACKS_ROOT` in `domain/pack`.
* [domain.pack.PackError](/symbols/domain/pack/PackError.md) - A pack that cannot be used.

## Referenced by

* [domain.pack.default_pack](/symbols/domain/pack/default_pack.md) - The configured pack, reread on every call and validated from a content-keyed cache.
<!-- okf:generated:end links -->
