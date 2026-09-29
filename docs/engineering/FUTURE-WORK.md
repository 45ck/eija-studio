# Future work

Items that were found, judged real, and deliberately not built yet. Each row says why it waits, what event makes it
worth doing, and a rough size. Anything that only tests a super-hard edge case goes here instead of into the code.

| Item | Why it waits | Trigger | Size |
|---|---|---|---|
| Refresh `verification/bend/evidence/bend.json` with the fixed Bend runner (per-law `--verdict`, archive pin, Dockerfile-hash image tag) | The snapshot is a real Docker run and this PC does not start Docker (Docker-backed sessions are NOT_RUN here). The strict xfail `test_the_snapshot_was_produced_by_the_current_gate_and_dockerfile` marks the gap and starts failing loudly (XPASS) once the snapshot is refreshed | A host with Docker: `nox -s formal_bend -- --build --snapshot`, then remove the xfail marker | S (one run, a few minutes, plus one commit) |
| Put `verification/` under the complexity ratchet (xenon roots and `DEFAULT_ROOTS`) | 32 functions in `verification/{smt,tla,bend,...}` are over the budget of 10 (the worst: `tla/run.py::main` 26, `smt/prove.py::build_report` 26). Recording them as debt would launder new debt; refactoring formal-lane code is a behaviour-risk change that needs its own tests | The formal lanes are next edited, or before Phase 1 exit | M (32 refactors, each with the lane's own regression tests) |
