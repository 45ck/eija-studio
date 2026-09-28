# Contributing to EIJA Studio

Thank you for helping. EIJA is an open-source (Apache-2.0) assurance kernel: "AI proposes. The kernel checks. The local owner decides." Contributions from people and from agents are welcome under the same rules. By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Set up

```bash
git clone https://github.com/45ck/eija-studio.git && cd eija-studio
python3 -m venv .venv && source .venv/bin/activate   # Windows: py -3 -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
```

Python 3.11 or later. If your system temp directory is slow, keep temporary data inside the checkout (`.tmp/`, `.pytest-tmp/`; both are gitignored).

## Read first

[AGENTS.md](AGENTS.md), [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md), [docs/TECHNICAL_LEAD_REVIEW.md](docs/TECHNICAL_LEAD_REVIEW.md), [docs/SECURITY_AND_TRUST.md](docs/SECURITY_AND_TRUST.md), [docs/adr/README.md](docs/adr/README.md) and [docs/oss/REGISTER.md](docs/oss/REGISTER.md).

## How work is organised: lanes

Work is split into capability lanes. Each has a branch `lane/<name>`, a reserved ADR number block and its own files (see [docs/ROADMAP.md](docs/ROADMAP.md) and the reserved blocks in [docs/adr/README.md](docs/adr/README.md)). Pick a lane, or propose a new one with the "new domain or lane" issue template, then:

* Keep to your lane's files. Do not edit another lane's `quality/sessions/*.py` module or `noxfile.py`.
* Touch shared files (`pyproject.toml`, `cli.py`, `bootstrap.py`, `AGENTS.md`, `docs/oss/REGISTER.md`) minimally and only where the lane needs it.
* `README.md` is edited only by the oss lane, and `src/eija_studio/resources/web/` only by the visual lane. Put your detail in `docs/` and ask for a link.
* Pin dependencies with `==` in your lane's extra in `pyproject.toml`; tool configuration goes in its own `[tool.x]` section.
* Files use LF line endings. On Windows write with `newline="\n"`. Do not mass-reformat existing files.

## Quality gates (local, tiered)

Hosted CI is unavailable ([ADR-0017](docs/adr/0017-local-quality-gates.md)), so the gates run on your machine and the results you report are local evidence.

| Tier | Command | When |
|---|---|---|
| fast | `nox -t fast` | before every commit; seconds |
| full | `nox -t full` | before opening a PR |
| release | `nox -t release` | maintainers; may need Docker, Java or Chromium |

A gate whose prerequisite is missing must report `NOT_RUN`, never `PASS`. Add a gate as a session in your own `quality/sessions/<lane>.py` with `python=False`, calling `sys.executable`. Heavy commands run one at a time; never start more than one Docker container or one browser from your lane.

## OSS first (ADR-0016)

Adopt a mature open-source tool before writing code, and write only EIJA-specific generators, adapters and glue ([ADR-0016](docs/adr/0016-oss-first-adapters-not-engines.md)). For every tool adopted and every custom module, add a row to [docs/oss/REGISTER.md](docs/oss/REGISTER.md) naming the alternatives you checked and the replacement path.

## Architecture decisions (ADRs)

Use only your lane's reserved numbers, copy [docs/adr/template.md](docs/adr/template.md) (MADR), and add the record to the index in [docs/adr/README.md](docs/adr/README.md). An accepted ADR is never rewritten; supersede it with a new one. Kernel changes need a regression test and an ADR.

## Evidence honesty

These rules apply to people and to agents:

* A missing prerequisite (Docker, Java, Chrome, a CLI login, network) is `NOT_RUN`, never `PASS`.
* Do not call a mocked result live, a model proof a code proof, a synthetic test a human study, or a hash a proof of correctness.
* Never weaken a kernel guard or the protected policy to make a test pass. Providers and agents never select meaning, approve or apply.
* Never run `scripts/stamp_release.py` or edit `src/eija_studio/resources/trusted_build.json`. Only the maintainer re-stamps the release fixture. Do not edit generated receipts, expected outcomes or evidence labels to hide a failure.
* Generated artefacts are deterministic (sorted, no timestamps unless passed in). If you commit a generated file, add a drift check.

## Code quality

Typed, small functions; ports for external boundaries; domain and application code never import adapters or vendor libraries. Docstrings say what a function does and does **not** establish. Tests include negative controls, not tautologies. Every new workflow operator needs executable semantics, missing-resolver rejection, projection rules, identity effects, a negative oracle and an evidence policy.

## Commits and pull requests

* Conventional commit messages (`feat(visual): ...`, `fix(sqlite): ...`, `docs(oss): ...`).
* Sign-off is optional. If you want it, `git commit -s` adds a `Signed-off-by:` line under the [Developer Certificate of Origin](https://developercertificate.org/). Contributions are licensed under Apache-2.0, as in [LICENSE](LICENSE).
* Push a lane branch and open a PR against `main` using the template. State the evidence (commands and results), the platform, and every `NOT_RUN` with its reason. Never force-push someone else's branch and never push to `main`.
* If an AI agent helped, say so in the PR, and read every line you submit. An agent's summary is not evidence; command output is.

## Reporting problems

Bugs and feature requests use the issue templates. Vulnerabilities go through [SECURITY.md](SECURITY.md), never a public issue.
