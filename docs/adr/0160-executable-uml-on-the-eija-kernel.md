# ADR-0160: Executable UML on the EIJA kernel: one interpreter, a closed action vocabulary, SCXML as the standard cross-check

* Status: accepted for the state-machine slice
* Date: 2026-10-08
* Lane: executable UML (owner direction, 8 October 2026: "how UML is executable and then runnable, with EIJA as the system underneath")

## Context and problem statement

PlayIDE draws six UML views (state machine, class, use case, screens, component, sequence) over one model (ADR-0093), and `eija build` turns the model into a running app checked against the kernel (ADR-0150). What was missing was one written answer to "what does each diagram *mean* when it runs, who decides that, and how do we know?", and any evidence that the meaning is the standard one rather than an EIJA invention.

Executable UML has been tried before. xtUML/BridgePoint (Mellor and Balcer) and OMG's fUML with the Alf action language gave UML precise execution semantics. Model-driven architecture then stalled on expressiveness: once the action language can say anything, the model is a program in a different syntax, and teams go back to code (Fowler, "Model Driven Architecture and language workbenches"). The owner asked whether AI changes that. The full write-up is [docs/architecture/executable-uml.md](../architecture/executable-uml.md).

## Decision drivers

* One interpreter. The repository rules forbid a second rule source or a second interpreter. The kernel (`runtime.execute`) is the only thing that decides what a model does, in PlayIDE, in Simulate and in a built app.
* Explicit supported semantics (mission). Every executable construct has a stated meaning, a refusal when its resolver is missing, and a negative oracle. Anything else is refused, not guessed.
* AI proposes, the kernel decides. Typing less is the point, so the AI writes and edits the model, but only through typed transactions the policy checks.
* Standard over home-grown. Where a standard with a normative execution algorithm exists, the model should be expressible in it, and an independent implementation should agree with the kernel.
* OSS first (ADR-0016) and Apache-2.0 compatible dependencies.

## Considered options

* **A. Adopt fUML and Alf** (fUML reference implementation, Java, CPL-1.0 and Apache-2.0 per its repository page; Papyrus Moka, EPL). Precise semantics for activities and actions; a general action language. It would replace the kernel with a second, larger interpreter, needs a JVM, and puts back the expressiveness that made models into code.
* **B. Adopt xtUML/BridgePoint** (Apache-2.0, LICENSE opened 2026-10-08). The closest match to the idea: class model, one state machine per class, an action language (OAL) and model compilers. It is an Eclipse application with its own metamodel, so EIJA's `Workflow` contract would become a translation target rather than the source; kept as the conceptual reference.
* **C. Adopt Umple** (MIT, LICENSE opened 2026-10-08). Textual UML with state machines that generates code. Its state machines compile to Java or other languages with arbitrary embedded code, so meaning moves into generated code; kept as inspiration for textual round-tripping.
* **D. Keep the kernel as the only interpreter, with a closed, typed action vocabulary, and project the state machine to W3C SCXML so an independent engine can run it and be compared case by case** (chosen).
* **E. Run models on an SCXML engine instead of the kernel** (python-statemachine, MIT; Apache Commons SCXML, Apache-2.0; XState, MIT). Standard semantics, but the engine knows nothing of the protected policy, typed effects, optimistic versions or idempotent replays, which would have to be rebuilt around it as a second rule source.
* **F. Sismic** (Python statechart interpreter with contracts, LGPL-3.0 per its LICENSE). Close in spirit to D's cross-check, but LGPL is reference-only for this repository.

## Decision outcome

Chosen option: **D**, because it keeps one interpreter and one source per fact, makes the meaning of the state diagram checkable against a W3C standard by code EIJA did not write, and grows expressiveness one typed operator at a time rather than through a general action language.

1. **Each UML view has one of three standings** (table in the architecture doc): *executable* (the kernel runs it: states, transitions, guards, effects, the record class's attributes), *checked design* (the kernel or a design check refuses it when it disagrees with the executable part: screens and use cases), or *derived* (generated from the executable model or a run and never edited as a source: sequence diagrams from the commit algorithm and from Simulate traces, component diagrams from the generated code).
2. **The action vocabulary is closed and typed.** Guards are the `Guard` literals, effects are declared `audit` or `notification` effects with typed adapters, and changes are the `domain.transactions` kinds. There is no action language. A new construct enters only with executable semantics, a missing-resolver refusal, projection rules, identity effects, a negative oracle and an evidence policy (repository rule). A test (`tests/test_executable_uml_profile.py`) fails if a guard or transaction kind is added without a row in the semantics table.
3. **AI is the author, not the interpreter.** Chat plan mode (ADR-0156) and drawn edits (ADR-0157) produce typed transactions; the policy refuses what breaks a law; the person accepts. The expressiveness gap that stalled MDA was the cost of writing precise models by hand. AI lowers that cost while the vocabulary stays small enough to check.
4. **SCXML export.** `eija scxml --pack P [--workflow F] [--out F]` (`application/scxml.py`, pure) writes the state machine as a W3C SCXML statechart: atomic states, one event per action, a `cond` holding the actor and version checks, and executable content that bumps `version` and appends each effect in order. The actor is resolved by the sender, as the kernel's `UnitOfWork.actor` port does. A model the policy blocks is not exported (`POLICY_BLOCKED`). Committed charts for every pack live in `verification/scxml/generated/` and the `scxml_drift` gate (fast, full) keeps them fresh.
5. **Differential check.** `python -m verification.scxml.differential` runs every app-oracle case (`appgen.oracle_cases`: state x action x fixture actor x expected version, plus an undeclared action and an unknown actor) on python-statemachine 3.2.1 and compares state, version and effects with the kernel's answer. Measured 2026-10-08 on linux, Python 3.13: 960 cases over three packs (360, 240, 360), 18 commits, 0 disagreements. Nine negative controls each break the chart one way (drop the role, assignment or version check; retarget a transition; drop, reorder or skip effects; move the initial state; add a transition) and each must produce a disagreement. The `scxml_differential` gate (full, release) reports NOT_RUN without the engine, never PASS.

### Consequences

* Good: the state diagram's meaning is checked against a W3C standard by an independent implementation. Agreement on every modelled case means the kernel's step is the standard statechart step for this subset.
* Good: no lock-in. Any SCXML engine with a Python datamodel can run the exported chart; an ECMAScript engine needs only the `cond` and `expr` strings rewritten.
* Good: the AI's freedom is bounded by the vocabulary, so every proposal is checkable, and a refusal names the law it breaks.
* Bad: the vocabulary is small on purpose. Hierarchical and orthogonal states, history, timers, computed guards over record values and cross-record actions are not executable yet; each needs its own operator ADR. This is the expressiveness risk, accepted and made explicit rather than hidden behind a general action language.
* Bad: the SCXML projection leaves out idempotent replay (`operation_binding`), which the app's own conformance run checks, and refusal codes, which an SCXML engine does not have.
* Bad: python-statemachine's Python datamodel is its own, not one of the W3C datamodels; the differential relies on that engine's reading of SCXML. A second engine (Apache Commons SCXML or XState through ECMAScript) would remove the single-engine assumption.
* Bad: `start_value` restores a machine in a given state without running entry from the initial state. That is how a stored record is restored, and a separate check covers the initial state, but paths through the chart are not walked.
* Revisit when: an operator beyond the current vocabulary is wanted (it extends both the kernel and the SCXML projection, with new differential cases); a second SCXML engine is adopted; or record-value guards make the Python datamodel expressions larger than the kernel's own checks.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| [python-statemachine](https://github.com/fgmacedo/python-statemachine) 3.2.1 (MIT, wheel METADATA read 2026-10-08) | Adopted as the independent SCXML engine for the differential, secure by default (`trusted=False`). Not the runtime: it has no protected policy, typed effects or storage port | Any SCXML engine behind `differential.compare` |
| xtUML BridgePoint (Apache-2.0), Umple (MIT), fUML/Alf reference implementations, Papyrus Moka | Each brings its own metamodel and interpreter or code generator, so it would be a second interpreter beside the kernel or move meaning into generated code | Export to them as targets if a user needs their tooling; the `Workflow` contract stays the source |
| Apache Commons SCXML (Apache-2.0), XState (MIT) | JVM or JavaScript; ECMAScript datamodel. Usable as a second differential engine later | Add an ECMAScript expression writer to `application/scxml.py` and a runner |
| Sismic (LGPL-3.0) | LGPL is reference-only in this repository | — |
| `xml.etree.ElementTree` (standard library) | Used for writing the document; no templating needed | — |
