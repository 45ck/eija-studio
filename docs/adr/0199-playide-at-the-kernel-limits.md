# ADR-0199: PlayIDE at the kernel's limits: measured, and the kernel's repeated questions memoised

* Status: accepted
* Date: 2026-10-08
* Lane: PlayIDE (owner direction, 8 October 2026: stay fast on large models)

## Context and problem statement

The packs PlayIDE was built and demonstrated on have five or six states. Nobody had opened a large one. The kernel caps a model at 32 states and 64 transitions, a data model at 40 classes of up to 40 attributes and 80 associations, and screens at 80 (`domain/models.py`, `domain/data.py`, `domain/screens.py`), so the largest model PlayIDE can be asked to open is known. `scripts/large_pack.py --base packs/library-loan` writes one: the library-loan pack grown by a numbered workflow to those limits, with its laws still holding.

Measured on the cloud test machine (headless Chromium, `eija serve --provider offline`), a plan on that model took:

| Step | Before | After |
|---|---|---|
| Open the page | 0.4 s | 0.4 s |
| The plan's ripple (`/api/play/ripple`) | 118 s | 2.5 s |
| Laws tab (`/api/play/laws`) | 96 s | 1.8 s |
| Component diagram (`/api/play/components`) | 94 s | 1.6 s |
| Screens check with a plan (`/api/play/screens`) | 6.1 s | 0.4 s |
| Build & run (`/api/play/build`, 24,973 conformance cases) | 67 s | 11 s |
| Class diagram tab (drawing) | 1.5 s | 1.1 s |

## Decision drivers

* The kernel's answers do not change. A cache may only skip asking the same question of the same frozen objects again.
* No change to the limits, the laws or the evidence.
* Fix the measured bottlenecks, not guessed ones.

## Considered options

* **Memoise the kernel's answers for frozen contracts, in front of the kernel** (chosen for the server).
* **Memoise inside `domain/models.py` and `domain/policy.py`**: the same speed, but those files are protected and bound by source hash to the SMT proof's snapshot, so the owner would have to review and re-record it.
* **Raise the limits or make the oracle sample cases**: changes what is proved, so rejected.
* **Pass a pre-checked flag into `runtime.execute`**: changes the kernel's API and lets a caller skip the policy check, so rejected.

## Decision outcome

* **Where the time went.** Profiling (cProfile) showed that building the app's oracle and proving the laws each run the kernel tens of thousands of times on one unchanged model, and every run checked the whole model against the policy again (`ensure_policy`) and hashed it again (`Workflow.semantic_hash`). Those two were over 95 % of the time.
* **`application/memo.py`** keeps the answers in front of the kernel, not inside it: `runtime.execute` asks `ensure_conforms(model, pack, ensure_policy)` and `model_hash(model)` instead of calling the policy check and the hash directly, and the oracle and proof sessions use `model_hash` too. An `IdentityMemo` keeps the last 128 answers, keyed by the objects' identity. A `Workflow` and a `Pack` are frozen after validation, so the same objects always get the same answer; the memo holds the objects themselves, so an id cannot be reused for another object while its entry exists. A copy or an edit is a new object and is asked afresh. Only a pass is remembered: a model the policy refuses is refused by `ensure_policy` itself every time, with its own codes and refs, and the check is part of the key, so a test that replaces it is asked afresh. The protected domain files (`domain/models.py`, `domain/policy.py`) and the SMT snapshot bound to their source are unchanged. `tests/test_kernel_memo.py` checks the answers against the kernel's own.
* **The app is built once per version.** `interfaces/app_build.app_files` keeps the last eight builds by pack, exact model content (order included), data model digest and screens digest. The ripple builds the model in force beside the candidate on every edit, and the component diagram and Build & run build the candidate again; now each version is generated once. Callers get their own copies.
* **The class diagram.** Every vertex is placed at a fixed size, so the page tells maxGraph not to measure each shape and attribute row with `getBBox` (`lean()` in `play.js`).

### Consequences

* Good: the largest model PlayIDE accepts now answers a plan in about three seconds, not minutes.
* Good: no answer changed: the kernel, appgen, ripple, law-proof and play tests pass unchanged, including the negative controls that replace the policy check.
* Bad: a small amount of memory holds the last 128 models and 8 built apps.
* Known remaining cost: Build & run at the limits spends about 11 s, most of it the built app's own conformance tests opening a fresh SQLite database for each of 25,000 cases. Changing that changes the generated app and its golden files, so it is left for the appgen lane.
* Revisit when: the limits are raised, or Build & run at the limits matters (then reuse one schema per test run in the generated tests).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| `functools.lru_cache` / `cache` | Needs hashable arguments; a pydantic model hashes by value, which costs the dump the memo is meant to avoid | Use it if contracts gain a cheap identity hash |
| `functools.cached_property` | Pydantic's `model_copy` copies the instance dictionary, so an edited copy could keep a stale hash | Use it if copies stop carrying cached values |
| [cachetools](https://github.com/tkem/cachetools) (MIT) | A dependency for a 25-line identity-keyed LRU | Adopt if more caches are needed |
