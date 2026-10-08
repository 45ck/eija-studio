# Agent workflow scripts

Saved so work can resume after a pause. They are Claude Code `Workflow` scripts (plain JavaScript) and reference local worktree paths in their headers (`C:/Dev/eija-wt/...`); edit those first.

| File | What it drives |
|---|---|
| `phase1.js` | Remaining Phase 1 (WBS 1.4 to 1.12): laws + vocabulary gate in parallel with weave-lite, evidence kinds, MCP/CLI, held-out pack, e2e, docs, one adversarial review, merge to main. Launch with `args: {"go": true}`. Steps already done (1.1 to 1.3, 1.4, 1.6) should be removed or skipped first; see the tracker. |
| `phase2.js` | Phases 2 and 3: workbench shell and option-D canvas in parallel with the landing queue and comparison harness, scenes as pack-parameterised scripts, recording, merge. |
| `mkissues.py` | Creates the labels, milestones and issues (idempotent by title). Already run once. |
| `LAND-BRIEF.md` | The standard brief for landing a branch. |

Rules baked into every script: single writer per worktree, commit and push each step, `nox -t fast` per step and `nox -t full` once at the milestone, negative control per gate, edge cases go to `FUTURE-WORK.md`, owner-only actions are never done by agents.
