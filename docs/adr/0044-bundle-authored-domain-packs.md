# ADR-0044: Bundle authored domain packs during distribution builds

* Status: proposed
* Date: 2026-10-03
* Lane: OSS community, documentation and release

## Context and problem statement

The source checkout loads its top-level `packs/` directory. The wheel currently discovers
only `src/` packages and their resources, leaving the default pointer and domain packs out.
An outside-checkout installation reproduced `PackError` for missing `default.json`;
the baseline wheel (`8568e592b9ef804bfd13444051088c676e29f7016ded681f0dddfa385d5f33b9`)
contained no pack entries. The new typed-edit modules and browser asset were present with
exact source hashes. Validation of the proposed fix remains required before acceptance.

## Decision outcome

Use the existing setuptools backend and a `build_py` adapter in `setup.py`. Copy the authored
JSON pack files into `build_lib/eija_studio/resources/packs`, replacing that generated subtree
on each build so removed policies do not survive in reused output. The source tree receives
no generated pack copy. `MANIFEST.in` retains the hook and authoritative packs in an sdist.
No build dependency requirement is lowered and no new runtime dependency is introduced.

One shared `PACKS_ROOT` prefers bundled package data whenever present. Only the canonical
`src/eija_studio` layout with a readable `pyproject.toml` declaring project name `eija-studio`
may use authored top-level packs when no bundle exists. This supports source distributions
and editable installs without requiring Git. Other layouts and absent, malformed or unrelated
project metadata keep the bundled path, so a missing entire installed bundle fails closed
instead of silently adopting valid adjacent packs. Both default loading and pack-id lookup
use that root. An explicit `EIJA_PACK` retains precedence. Missing or invalid configured data
and malformed bundled data fail closed; no fallback substitutes another policy after an error.
Pack digests, content refresh and same-id ambiguity rules are unchanged. This is resource
resolution, with no new operator, interpreter, authority, receipt or source conformance claim.

## Verification and limits

Regressions cover bundled precedence, recognized source checkout fallback, missing entire
installed bundles beside valid alternate packs, malformed project metadata, explicit
configuration failures and exact build-output bytes, including obsolete-output removal. A separate candidate
smoke installs an explicit wheel outside the checkout with reused environment dependencies,
checks bundled/source byte identity, missing-entire-bundle refusal beside valid alternate
packs, asset delivery and read-only typed proposal/refusal.
The generic installer stays in `scripts/candidate_wheel_smoke.py`; its fixed, explicit
fixture and independent domain-specific oracles live in
`tests/installation/candidate_wheel_probe.py`. The runner reads only that repository
fixture path. This remains an explicitly invoked installation check, not an automatically
collected pytest result, and adds no vocabulary exemption or weakened oracle.
It must preserve the expected untrusted-source boundary. A direct build and a wheel rebuilt
from its sdist must contain identical authored pack bytes. These checks are not a clean-room
dependency install, live provider run, human study or release approval.

`scripts/wheel_smoke.py` keeps its existing strict release-fixture and eligibility assertions.
No trusted fixture is stamped or relaxed to pass the candidate installation check.

## OSS check

| OSS checked | Why adapter/dependency use was insufficient | Replacement path |
|---|---|---|
| Setuptools build backend and `build_py`; Python `shutil` | The authored packs are intentionally outside the import package, so normal package-data globs cannot include them without a duplicate source tree | Remove the small build adapter if the canonical project layout moves packs into package resources; retain the same install and identity checks |
