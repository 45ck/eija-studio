# Build an app from the model

`eija build` turns a workflow model into an app you can run: a local web page, an API and a SQLite database. The build also checks the app against EIJA's kernel. The diagram is the source. To change the app, change the model and build again. See [ADR-0150](adr/0150-build-apps-from-the-model-with-a-kernel-oracle.md) for the design.

```console
eija build --pack packs/excursion --out myapp
python myapp/run.py                 # http://127.0.0.1:8000
cd myapp && python -m unittest      # re-run the conformance check yourself
```

Use `--workflow FILE` to build a candidate workflow (for example one exported from a change case) instead of the pack's own model. The app needs Python 3.11 or newer and nothing else.

## What you get

| Path | What it is |
|---|---|
| `app/spec.py` | The model as Python literals: states, transitions (from, to, role, guards, effects), roles, actors and effects |
| `app/service.py` | The rules engine. It runs the same checks in the same order as the kernel, and each request commits in a single transaction. |
| `app/server.py`, `app/web/` | A local HTTP API and page: pick an actor, create records and take the actions the model allows, with reasons for those it refuses |
| `tests/oracle.json` | The kernel's answer for every state × action × actor × version, plus replays |
| `tests/test_conformance.py` | Checks the app against every oracle case |
| `BUILD.json` | Model and pack identity, file hashes, case count, the conformance result and the kernel's source-review status |

## Why you can trust it, and how far

The oracle is not the generator's reading of the model. The build asks EIJA's own runtime what should happen in every case, then runs the generated app's tests in a separate process. If the app commits or refuses anywhere the kernel does not, the build reports `FAIL` and exits 2. The repository's tests break the app on purpose five ways and require each break to be caught.

The build does **not** establish:

- correctness for actors or inputs outside the pack's fixture directory. The check is exhaustive for the modelled cases only.
- that the kernel itself is reviewed. While `kernel_source_review` is `SOURCE_REVIEW_REQUIRED`, the app agrees with unreviewed kernel source.
- anything about data the model does not describe. Records carry a title only, because entities and fields are not modelled yet.
- authentication. The actor picker selects from a fixture directory.
- delivery of notifications. They are written to an outbox table.

A model that the protected policy refuses is never built (`POLICY_BLOCKED`).

## Rebuilding

Building into a previous build's directory replaces only the files that build wrote and keeps `data/`. Records in a state the new model no longer has are flagged in the page, and every action on them is refused. Building into any other non-empty directory is refused with `OUTPUT_EXISTS`.
