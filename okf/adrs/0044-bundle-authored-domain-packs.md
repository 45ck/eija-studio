---
type: Architecture Decision Record
title: 'ADR-0044: Bundle authored domain packs during distribution builds'
description: The source checkout loads its top-level `packs/` directory.
resource: repo://docs/adr/0044-bundle-authored-domain-packs.md
tags:
- adr
- proposed
status: draft
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/adr/0044-bundle-authored-domain-packs.md
  title: 0044-bundle-authored-domain-packs.md
  hash_method: lf-sha256-v1
  sha256: 69695e3dd63b14c3ba852d5d74b23e325f0bc44352d1e51f2d08b03d67b19e42
notes_baseline: 16cfdaf736bc651c60e51d96d301406be1e4e6993ff70770b3e473d5dc633e67
verified:
- by: process:codex-packaging-integration
  at: '2026-10-03T03:27:08Z'
  notes_sha256: 24c70ded7405755dfc2f30551982e918a45adbf417b7f32d25e566fc3890d2f5
  sources_sha256: 2061cc3a148dd5fc9150dcaa93dc2cb5ead14e517aa12418fbf8172d1075dc5f
- by: process:codex-integrated-pack-resolution
  at: '2026-10-03T03:49:04Z'
  notes_sha256: 24c70ded7405755dfc2f30551982e918a45adbf417b7f32d25e566fc3890d2f5
  sources_sha256: abb63a811cec6cb7d6eb09e5c81616125b28c9b8c8b91c245b500c0df407358b
- by: process:codex-installation-fixture-layout
  at: '2026-10-03T04:28:28Z'
  notes_sha256: 24c70ded7405755dfc2f30551982e918a45adbf417b7f32d25e566fc3890d2f5
  sources_sha256: 16cfdaf736bc651c60e51d96d301406be1e4e6993ff70770b3e473d5dc633e67
---

# ADR-0044: Bundle authored domain packs during distribution builds

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Status | proposed |
| Date | 2026-10-03 |
| Lane | OSS community, documentation and release |
| Source | `repo://docs/adr/0044-bundle-authored-domain-packs.md` |

## Decision outcome (verbatim)

> Use the existing setuptools backend and a `build_py` adapter in `setup.py`. Copy the authored
> JSON pack files into `build_lib/eija_studio/resources/packs`, replacing that generated subtree
> on each build so removed policies do not survive in reused output. The source tree receives
> no generated pack copy. `MANIFEST.in` retains the hook and authoritative packs in an sdist.
> No build dependency requirement is lowered and no new runtime dependency is introduced.
>
> One shared `PACKS_ROOT` prefers bundled package data whenever present. Only the canonical
> `src/eija_studio` layout with a readable `pyproject.toml` declaring project name `eija-studio`
> may use authored top-level packs when no bundle exists. This supports source distributions
> and editable installs without requiring Git. Other layouts and absent, malformed or unrelated
> project metadata keep the bundled path, so a missing entire installed bundle fails closed
> instead of silently adopting valid adjacent packs. Both default loading and pack-id lookup
> use that root. An explicit `EIJA_PACK` retains precedence. Missing or invalid configured data
> and malformed bundled data fail closed; no fallback substitutes another policy after an error.
> Pack digests, content refresh and same-id ambiguity rules are unchanged. This is resource
> resolution, with no new operator, interpreter, authority, receipt or source conformance claim.

## Sections

* Context and problem statement
* Decision outcome
* Verification and limits
* OSS check

## Code and docs mentioned

Existence-checked by the gate; not hashed (an ADR is a decision record, not a description of current code).

* `repo://pyproject.toml`
* `repo://scripts/candidate_wheel_smoke.py`
* `repo://scripts/wheel_smoke.py`
* `repo://setup.py`
* `repo://tests/installation/candidate_wheel_probe.py`
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Referenced by

* [OSS community, documentation and release](/lanes/0043-oss-community-documentation-and-release.md) - Capability lane with ADR numbers 0043–0044 reserved.
<!-- okf:generated:end links -->
