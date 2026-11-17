# The AI builds it. PlayIDE proves it. (17 November 2026)

This is a scripted recording of the real PlayIDE page (`/play`). Every click is a real browser action against a real `eija serve`, and every step asserts text the page actually rendered. `python -m demos run playide_ai_builds_proved --dry-run` repeats the same clicks and assertions without video. The take is **PASS**, with no act skipped. It runs 3 minutes 54 seconds, recorded from `main` at `1e93c33`.

[Watch the README copy](assets/playide-proved-20261117/playide-ai-builds-proved.mp4) (1280 wide).

## The AI in this video

There is no live model. The describer is the offline shape reader (`offline-describe-fixture-v1`) and the chat's proposer is the offline phrase reader (`offline-plan-fixture-v1`). The first title card and the first chat caption say so. Whatever proposes a change, live or offline, goes through the same kernel, laws and checks.

## What the run shows

| Chapter | What is real |
|---|---|
| The AI drafts the whole system | A coffee shop described in one sentence. The describer's check lists every view before anything is made. The state machine, the class diagram with the named fields, and a sequence diagram of a test the kernel recorded by running the model. |
| The AI changes it in plain words | "Add Pay from Placed to Paid for Customer then move Start source to Paid" becomes typed steps the policy allows. What's missing reports that the recorded way to `Collected` no longer holds; Update the tests records it again, and the sequence now pays first. |
| Built and checked across the stack | Build & run builds the app from the same model. Every conformance case matches the kernel: the options the app offers, its HTTP API answers and the records it stores ([ADR-0243](../adr/0243-conformance-that-catches-divergence.md)). The Components tab's Deployment lens draws the browser, the Python process and the SQLite file read from the built app. |
| Proved before it lands | On the library loan template, the AI's plan also removes `ReturnLate`. Before anything lands, To consider reports that the late-return scenario breaks, and Review ranks the removal high risk with the kernel's answer. Dropping the step leaves nothing high risk. |
| Every law, every run | The Laws tab searches every reachable configuration of the changed model and every law holds on every run the kernel allows. The app is rebuilt, its conformance cases match again, and simulated users run through it. |
| AI agents inside the guarantee | On the refund desk template, a change that would let the support agent (an AI agent actor) approve refunds is refused by a law. The rest of the plan goes through. |
| Behind it (closing cards) | The repository's formal gates, run on the recorded commit; see below. |

## The formal gates quoted on the closing cards

Run on the recorded commit (Linux, Python 3.13, z3 5.1.0):

| Gate | Result |
|---|---|
| `nox -s formal_smt` | Z3: 15 of 15 policy invariants UNSAT (proved), non-vacuous; 2,572 differential candidates against the real `check_policy`, 0 disagreements; 8 of 8 named negative controls give counterexamples. Per-pack law encodings PASS for all 11 packs. |
| `nox -s formal_tla` | TLC: baseline 5,520 states, candidate 3,600, candidate_reject_submitted 6,288 (15,408 in all), all PASS; all 4 negative controls produce the expected violation; runtime and spec agree on all three configurations. |
| `nox -s scxml_differential` | 12,256 cases across 11 packs give the same outcome on an independent SCXML engine as on the kernel; 0 disagreements. |
| `nox -s conformance_divergence` | 553 deliberately wrong apps (library loan, and the library-loan and refund-desk feature variants): 349 caught by behaviour, 204 refused; no law with a missed break. |
| `nox -s property` | 117 Hypothesis property and stateful differential tests pass. |

## What "proved" means here

The proofs and checks are against the model and its laws: the kernel's answers, the laws the person wrote, and the app built from that model. They show the app does what the model says, on every layer the checks reach. They do not show that the model is what the person meant; that is why changes are reviewed, laws are the person's, and the owner approves and applies. The TLA+ model is of the excursion workflow; the SMT invariants are of the change policy that every proposal passes through.

## Not shown

Nothing is approved or applied; that waits on the owner's source review and restamp (issue #80). The formal gates run in the repository, not inside the PlayIDE page; the cards quote their output.

## Reproduce the recording

```bash
pip install -e ".[demos]"
nox -s formal_smt formal_tla scxml_differential conformance_divergence property   # the numbers on the closing cards
python -m demos run playide_ai_builds_proved --dry-run
python -m demos run playide_ai_builds_proved
python -m demos finish playide_ai_builds_proved
ffmpeg -i demos/output/playide_ai_builds_proved.mp4 -vf scale=1280:-2 -crf 30 -an -movflags +faststart \
  docs/demos/assets/playide-proved-20261117/playide-ai-builds-proved.mp4
```

The poster is the frame at 1:42 (the deployment diagram of the built app, with 334 of 334 conformance cases matching).
