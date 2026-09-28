# Scripted demos

Hand-authored, scripted recordings of EIJA Studio ([ADR-0047](../docs/adr/0047-hardcoded-scripted-demos-not-demo-machine.md)).
Each scenario is a short Python module that drives a real, ephemeral `eija serve` (offline provider, throwaway
workspace) in the installed Google Chrome, so every step asserts text the Studio really renders.

**What exists and what is still blocked on other lanes: [`scenarios/REGISTRY.md`](scenarios/REGISTRY.md)** (generated
from `scenarios/registry.py`; not copied here so it cannot go stale; see
[ADR-0048](../docs/adr/0048-scenario-dependency-gating.md)).

## Run

```
pip install -e ".[demos]"                        # Playwright; it drives the installed Chrome, no browser download
python -m demos list                             # scenarios and their status
python -m demos registry --check                 # catalogue, REGISTRY.md and manifests agree (no browser needed)
python -m demos registry --write                # regenerate REGISTRY.md after editing registry.py
python -m demos run assurance_loop --dry-run     # same real clicks and assertions, no video, no delays
python -m demos run assurance_loop               # record demos/output/assurance_loop.webm + its manifest
```

Exit codes: `0` PASS or PARTIAL, `1` failure, `2` usage, `3` NOT_RUN (a blocked scenario, Playwright not
installed, or Chrome cannot be launched; never reported as a pass). `--seed` only fixes the typing cadence;
recordings are not otherwise repeatable.

## Statuses

| Status | Meaning |
|---|---|
| `recorded` | a take exists and no act was skipped |
| `recorded-partial` | a take exists but an act could not run; the manifest lists it |
| `scripted-not-recorded` | the scenario module exists but has not been recorded |
| `blocked` | waits for other lanes; there is deliberately no module, only a registry row |

The video is a large binary and stays out of git (`demos/output/`, gitignored). What is committed is a small manifest
under `recordings/` (video sha256 and size, platform, skipped acts, and the sha256 of the scenario source at
recording time). `python -m demos registry --check` fails on a malformed manifest, a missing key or a local video
whose hash differs, and warns when the scenario source has changed since the recording.

## The assurance loop and act 4

`assurance_loop` is the shipped v0.2 flow. Its last act (verify, approve, apply) needs the release fixture to match
the current source, and only the **owner** can restamp that; agents never stamp. Until then the scenario records
acts 1-3, clicks Verify to show the Studio refusing with `SOURCE_REVIEW_REQUIRED` (the gate is exercised, never
bypassed), reports act 4 as skipped, and prints a `PARTIAL` line. The take is therefore `recorded-partial`.

The committed recording predates the current script and the planned Studio UI redesign; it will be re-recorded after
that. Its manifest says so.
