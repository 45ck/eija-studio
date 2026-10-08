# ADR-0150: Build runnable apps from the model, checked against the kernel as oracle

* Status: accepted for the local workflow-app slice
* Date: 2026-10-08
* Lane: app generation (owner direction, 8 October 2026)

## Context and problem statement

The owner's goal, stated on 8 October 2026, is "UML you can trust to build apps". Until now EIJA checked and simulated a workflow model, but nothing a user drew became software they could run. The [mission](../engineering/MISSION.md) warns against implying general code generation. This record adds a bounded generator. It turns the workflow model (states, transitions, roles, guards and declared effects) into a runnable app, and the app is trusted only as far as an exhaustive comparison with the kernel shows.

## Decision drivers

* The model stays the single source of behaviour. The app must not become a second, hand-edited rule source.
* Trust comes from evidence, not from the generator's author. The generated app is compared against the existing kernel (`application/runtime.execute`), not against the generator's own reading of the model.
* A model the protected policy refuses is never built.
* The app runs anywhere EIJA's users are: Python 3.11+ with no extra dependencies, bound to 127.0.0.1.
* The limits are stated in every build: no entities or fields yet, fixture actors rather than authentication, and an outbox rather than sent notifications.

## Considered options

* Template engines (Jinja2, Cookiecutter, Copier) generating a framework app (FastAPI, Django).
* Model-driven tools (Eclipse Sirius/Acceleo, Xtext, JHipster JDL).
* Interpreting the model at runtime inside EIJA (`eija serve` hosting user apps).
* A fixed standard-library runtime template plus a generated `spec.py` and a kernel-computed oracle (chosen).

## Decision outcome

Chosen option: a fixed runtime template plus generated spec and oracle.

`eija build --pack P [--workflow F] --out DIR` writes these files:

* `app/spec.py`: the model as plain Python literals, readable next to the diagram.
* `app/service.py`, `app/server.py`, `app/web/*`, `run.py`: the fixed runtime. It runs the same checks in the same order as the kernel: record, action, actor, authority, replay, version, state, then the declared effects in one SQLite transaction.
* `tests/oracle.json`: for every state, every action (plus one undeclared action), every fixture actor (plus one unknown actor) and expected versions 0 and 1, the kernel's own answer. Committed cases also record the answer to an exact replay.
* `tests/test_conformance.py`: replays every oracle case against the generated service, and checks that each committed effect is written exactly once.
* `BUILD.json`: pack and model identity, the oracle hash and case count, the hash of every file, the conformance result (`PASS`, `FAIL` or `NOT_RUN` with `--no-test`), and whether the kernel source matches the owner-stamped fixture (`kernel_source_review`).

The build runs the generated tests in a separate process, the way a user of the app would, and exits 2 on `FAIL`. Negative controls in `tests/test_appgen.py` mutate five rules in a generated app and require the conformance run to fail for each. The rules are the assignment guard, the role check, the version check, an effect write and a role in the spec.

The generator is pure (`application/appgen.py`). Writing files, reading templates and running the tests live in `interfaces/app_build.py`. A non-empty output directory is written only if it holds a previous build's `BUILD.json`. A rebuild replaces only the files that build listed, so `data/` survives.

### Consequences

* Good: a user can draw or edit a workflow, build it and use it in a browser. The app's behaviour is exhaustively compared with the kernel for every modelled case.
* Good: the generated app has no dependency on EIJA at runtime and can be copied anywhere.
* Bad: records carry only a title, because the model has no entities or fields yet. That is the next model extension and needs its own ADR.
* Bad: the trust chain ends at the kernel. While `kernel_source_review` is `SOURCE_REVIEW_REQUIRED`, conformance shows agreement with unreviewed kernel source, not with an owner-reviewed one.
* Deliberate difference: the kernel refuses a preview instance created under an older model (`STALE_INSTANCE`). The app keeps its records across rebuilds instead. A record in a state the new model lacks is flagged in the UI, and every action on it is refused with `STATE_DENIED`.
* Revisit when: the model gains entities or fields, when apps need real authentication, or when a framework target (FastAPI or similar) is wanted for deployment.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Jinja2, Cookiecutter, Copier | Each needs a template engine dependency, but the output here is one fixed runtime plus Python literals, so `pprint` and file copy suffice. Templating adds no checking. | Move the templates to Copier if users need project variants or update merges |
| FastAPI or Django as the generated app's framework | They add install steps and a framework to the generated app. The standard library serves a local single-user app. | Add a second runtime template behind the same spec and oracle |
| Sirius/Acceleo, Xtext, JHipster JDL | They bring their own metamodels and would create a parallel rule source next to the `Workflow` contract | None planned. The `Workflow` contract is the metamodel. |
| Hosting user apps inside `eija serve` | That would mix the owner's review workbench with the user's running app and its data | — |
