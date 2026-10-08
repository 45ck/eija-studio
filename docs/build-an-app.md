# Build an app from the model

`eija build` turns a workflow model into an app you can run: a local web page, an API and a SQLite database. The build also checks the app against EIJA's kernel. The diagram is the source. To change the app, change the model and build again. See [ADR-0150](adr/0150-build-apps-from-the-model-with-a-kernel-oracle.md) for the design.

```console
eija build --pack packs/excursion --out myapp
python myapp/run.py                 # http://127.0.0.1:8000
cd myapp && python -m unittest      # re-run the conformance check yourself
```

Use `--workflow FILE` to build a candidate workflow (for example one exported from a change case) instead of the pack's own model. Run the app with a Python that has `eija-studio` installed: the app calls EIJA's kernel for every decision, so there is no second copy of the rules.

## What you get

| Path | What it is |
|---|---|
| `app/model.json`, `app/pack.json` | The canonical workflow model (states, transitions, roles, guards, effects) and pack (actors, policy) the app was built from |
| `app/data.json` | The pack's data model, when it has a `data.json`: the record class's attributes become the app's form, and every value is checked by EIJA's `check_values` |
| `app/service.py` | SQLite storage for the kernel. Creating a record calls `runtime.initialise` and each action calls `runtime.execute`; each request commits in a single transaction. |
| `app/server.py`, `app/web/` | A local HTTP API and page: pick an actor, create records and take the actions the model allows, with reasons for those it refuses |
| `tests/oracle.json` | The kernel's answer for every state × action × actor × version, plus replays |
| `tests/test_conformance.py` | Checks the app against every oracle case |
| `BUILD.json` | Model and pack identity, file hashes, case count, the conformance result and the kernel's source-review status |

## Why you can trust it, and how far

The oracle is not the generator's reading of the model. The build asks EIJA's own runtime what should happen in every case, then runs the generated app's tests in a separate process. If the app commits or refuses anywhere the kernel does not, the build reports `FAIL` and exits 2. The repository's tests break the app on purpose five ways (operations not recorded, audit not written, notifications not queued, a role changed in `app/model.json`, an assignment changed in `app/pack.json`) and two more for the data model (values stored unchecked, a required attribute made optional), and require each break to be caught.

The build does **not** establish:

- correctness for actors or inputs outside the pack's fixture directory. The check is exhaustive for the modelled cases only.
- that the kernel itself is reviewed. While `kernel_source_review` is `SOURCE_REVIEW_REQUIRED`, the app agrees with unreviewed kernel source.
- anything about data the model does not describe. Without a `data.json`, records carry a title only. With one, only the record class is stored; other classes are drawn but not stored yet.
- authentication. The actor picker selects from a fixture directory.
- delivery of notifications. They are written to an outbox table.

A model that the protected policy refuses is never built (`POLICY_BLOCKED`).

## Rebuilding

Building into a previous build's directory replaces only the files that build wrote and keeps `data/`. Records created under a different model are flagged in the page, and the kernel refuses every action on them with `STALE_INSTANCE`. Building into any other non-empty directory is refused with `OUTPUT_EXISTS`.
