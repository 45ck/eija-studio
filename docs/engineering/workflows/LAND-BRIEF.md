# Landing brief v2: take one item to MERGED on main

EIJA Studio (https://github.com/45ck/eija-studio, local main clone C:\Dev\eija-studio) is an open-source, Apache-2.0,
IDE-style assurance kernel. AI proposes, a deterministic kernel checks, the owner decides. The owner has delegated
review and merging to us ("i am not reviewing anything"). You land ONE item and MERGE it yourself once every
condition below holds. Landings are serialised by the coordinator, so nobody else merges to main while you work.

## Non-negotiables
- Owner-only (never do): run scripts/stamp_release.py; edit src/eija_studio/resources/trusted_build.json; let an
  agent or provider approve or apply; weaken kernel guards; read auth or token files; print secrets; start live
  paid provider calls. `SOURCE_REVIEW_REQUIRED` on a modified checkout is expected until the owner restamps.
- Honesty: MEASUREMENT vs PREDICTION; a proof about a model is not a proof about the code; a missing prerequisite
  (Docker, Java, Chrome, CLI login, network) is NOT_RUN, never PASS; mocked is never "live".
- Never: `rm -rf`, `git worktree remove --force`, force-push, `--no-verify`, or touching another lane's worktree.
- Machine: Windows 11, 16 GB RAM shared with other sessions; D: is a slow HDD and is TEMP. Set TMP and TEMP to
  `<worktree>/.tmp` for every command. Run commands serially. Use at most one Chrome at a time. Do not start
  Docker Desktop; if Docker is already running and the lane needs it, use it and say so, and otherwise the
  Docker-backed result is NOT_RUN. Kill any process of yours that goes above 3 GB. Never run the calvin-ops
  epistemic validator.
- pip: always pass `--no-cache-dir`. Venv `.venv-gates` inside the worktree (`py -3.12 -m venv .venv-gates`), then
  `pip install --no-cache-dir -e ".[dev,lint,<lane extras>]"`. If the install is stuck for more than 5 minutes,
  kill it and use a new venv directory name.
- Write files with the file tools, not backslash-heavy heredocs (the shell wrapper mangles escapes).

## Steps
1. Work in the lane's existing worktree if it is given to you; otherwise
   `git -C /c/Dev/eija-studio worktree add --detach /c/Dev/eija-wt/land-<lane> origin/<branch>`.
   Then run `git fetch origin && git merge --no-edit origin/main`. The merge drivers are configured: `pyproject.toml`
   merges per key. If `docs/adr/README.md` conflicts, run `git checkout origin/main -- docs/adr/README.md` and then
   `python -m quality.tools.adr_index --write`. When `cli.py` or `service.py` conflict, keep both sides' additions.
2. Apply the review findings you were given. Fix every blocker and major finding, and the cheap minor ones. Confirm
   each finding against the code first; a refuted finding goes in the record as "no change needed" with the evidence.
3. Run the gates on the merge result: `nox -s lint typecheck typecheck_win32 architecture complexity dependencies
   adr_index tests` plus the lane's own sessions (`nox -l`). Everything must pass. Do not weaken shared config for
   a lane problem. Complexity: refactor first; new ratchet debt only when a refactor is unreasonable, and list it.
4. GIF, required by docs/engineering/PR-STANDARD.md. If `python -m demos pr-gif` exists on main, use it (browser
   for a visible change, terminal for a non-visual change, showing the real behaviour including a negative control).
   Publish it to the orphan `pr-media` branch under `pr/<number>/` as the tool documents, and embed the raw URL.
   If the tool is not on main yet (only item 1 builds it), record the GIF with ffmpeg (on PATH) and publish it the
   same way. Keep it under 5 MB, 1280 px wide at most and 20 s long at most.
5. Commit with conventional messages ending with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`,
   then push to the PR branch (not force). Rewrite the PR description with `gh pr edit <n> -R 45ck/eija-studio
   --body-file <file>` so it meets docs/engineering/PR-STANDARD.md exactly: Summary, See it (GIF), What changed and
   why, Evidence (gates verbatim), Review record table, Risk and rollback, Owner actions. Write as a principal
   engineer: outcome first, concrete, short, honest about limits. End with a blank line and
   `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
6. Merge: `gh pr merge <n> -R 45ck/eija-studio --merge` ONLY if the gates pass on the merge result, no blocker or
   major finding is open, and the GIF is embedded. If main moved in the meantime (it should not), merge it in again
   and re-run the gates. If you cannot meet the bar, do NOT merge: leave a PR comment that says exactly what is
   blocking.
7. Update the tracker. In `/c/Dev/eija-wt/prstd` (branch `poc/tracker`), run `git pull --ff-only`, set your row's State
   in `docs/engineering/POC-STATUS.md` to `merged` or `blocked: <reason>` and fill in its PR number, commit, then push.
   Regenerate the body of draft PR #27 from that file: the intro line, the `## Landing queue` section onward, and the
   Claude Code footer. Apply it with `gh pr edit 27`.
8. Return the structured summary you are asked for.
