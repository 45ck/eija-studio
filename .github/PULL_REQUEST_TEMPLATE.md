## Why

<!-- The problem, and which lane or issue this belongs to. -->

## What

| Area | Change |
|---|---|
|  |  |

## Evidence

<!-- Commands and results verbatim, and the platform (OS, Python). -->

```text
```

## NOT_RUN

<!-- Every gate or check you could not run, with the missing prerequisite. Write "none" if none. -->

## Checklist

- [ ] `nox -t fast` and `nox -t full` pass locally (results above), or the failures are explained
- [ ] `python -m pytest -q` passes
- [ ] Missing prerequisites are reported as `NOT_RUN`, not `PASS`; nothing mocked is called live
- [ ] Kernel guards and protected policy are not weakened; providers and agents still cannot select meaning, approve or apply
- [ ] I did not run `scripts/stamp_release.py` or edit `trusted_build.json`
- [ ] OSS first: adopted tools and custom modules have rows in `docs/oss/REGISTER.md`
- [ ] Decisions are recorded in an ADR using only my lane's reserved numbers, and the ADR index is updated
- [ ] Generated files are deterministic and have a drift check
- [ ] LF line endings; no mass reformatting; shared files touched minimally
- [ ] `README.md` not edited (oss lane only) and `resources/web/*` not edited (visual lane only), unless this is that lane
- [ ] Docs and links updated; `nox -s docs_links` passes
