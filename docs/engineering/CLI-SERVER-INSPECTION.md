# Fagan inspection: the `eija` command and the local server

On 13 November 2026 the `eija` command and the loopback server behind PlayIDE were inspected line by line against a
checklist, then probed with the real command and a test client. This note is the inspection record: what was read,
the checklist, every defect with its severity and location, what was fixed, and what was left. The boundary decisions
are [ADR-0244](../adr/0244-built-app-environment-and-bind-before-links.md).

## Scope

| Read in full | Lines |
|---|---|
| `src/eija_studio/interfaces/cli.py` (argument parsing, exit codes, failure reports) | 403 |
| `src/eija_studio/interfaces/http.py` (host, token, origin and body guards; security headers; routes) | 306 |
| `src/eija_studio/interfaces/play.py` (PlayIDE routes, Build & run's app process) | 496 |
| `src/eija_studio/interfaces/play_systems.py` (open, start and save systems; `eija new`) | 300 |
| `src/eija_studio/adapters/system_library.py` (systems home, recent list, draft files) | 148 |
| `src/eija_studio/interfaces/app_build.py`, `uml_interop.py`, `play_interop.py`, `agent_config.py` | 400 |
| `src/eija_studio/weave/cli.py`, the file-reading parts of `mcp_server.py`, `play_assurance.py` and `adapters/repository.py` | 350 |
| The generated app's `server.py.tmpl` and `run.py.tmpl` (what PlayIDE starts on the network) | 180 |

Out of scope (other inspections the same day): the kernel, the generator's output, diagram editing, chat plan mode,
persistence logic and Simulate.

## Checklist

1. Every command and route validates its input before any side effect (no workspace, key or file is made for a request that is then refused).
2. Every failure is one JSON object with a stable code and exit 2; no traceback and no echo of file content (ADR-0236).
3. Exit codes mean the same thing across commands: 0 clean, 2 refused or failed, and a model the protected policy refuses is never exit 0.
4. Defaults taken from the environment are validated as strictly as the flags they stand for.
5. Paths from a request never leave their root (`..`, absolute paths, symlinks); writes are atomic or into a folder the command owns.
6. The protected-files policy: no route or command writes a pack's law file or tests (`pack.json`, `scenarios.json`) without the person asking.
7. The server answers only on loopback, to the loopback Host, with the session token, and to same-origin JSON for writes; unauthenticated input never causes a 500.
8. A link with the session token can only point at this server.
9. Child processes get only what they need: no provider key or other secret in their environment.
10. Secrets never reach stdout, logs or error bodies.

## Defects

Severity: **Major** is a security or data boundary crossed, or a wrong result a script would act on; **Minor** is a
wrong message, a side effect before a refusal, or an inconsistency a person would notice.

| # | Severity | Where | Defect | Status |
|---|---|---|---|---|
| D1 | Major | `interfaces/cli.py` `serve` | Private links printed and `--open` run before the port was bound. With the port taken, the browser opened another program's page with the session token in its address; the command printed a raw uvicorn error and exited 1. | Fixed: bind and listen first (`_listen`), `PORT_IN_USE`, exit 2 |
| D2 | Major | `interfaces/play.py` `AppRunner._start` | Build & run passed the IDE's whole environment, including `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` and `OPENROUTER_API_KEY`, to the generated app process. | Fixed: `APP_ENVIRONMENT` allowlist |
| D3 | Minor | `interfaces/http.py` `boundary` | An `Authorization` header with a non-ASCII byte made `hmac.compare_digest` raise: an unauthenticated request got 500 and a traceback in the log, not 401. | Fixed: compare bytes |
| D4 | Minor | `interfaces/cli.py` `serve` | `--port 80` was refused only after the workspace and `receipt.key` were created. | Fixed: port checked before the studio is built |
| D5 | Minor | `interfaces/cli.py` `main` | argparse does not check a default against `choices`, so `EIJA_PROVIDER=bogus` gave the generic `INPUT_OR_ENVIRONMENT_ERROR`. | Fixed: `CONFIGURATION` naming the variable and the choices |
| D6 | Minor | `interfaces/uml_interop.py` `export_command` | `eija uml export` of a model the protected policy refuses exited 0 with no marker, where `render`, `scxml`, `build` and `laws` exit 2. | Fixed: written, `POLICY_BLOCKED` on stderr, exit 2 |
| D7 | Minor | `interfaces/cli.py` `_FILE_ERRORS`; `adapters/system_library.py` `create` | `--systems` naming a file gave the generic message on the command line and a 500 from PlayIDE's New system. | Fixed: `SYSTEMS_HOME_INVALID`; `PATH_EXISTS` and `NOT_A_DIRECTORY` codes |
| D8 | Minor | `interfaces/play_systems.py` `start_system` | `eija new` with a name over 80 characters said "The file does not match the expected schema", though no file was given. | Fixed: the argument and the problem |
| D9 | Minor | `interfaces/play_systems.py` `start_system` | `eija new --from describe` answered "No describer is configured"; describing an app is a PlayIDE form with no command-line input. | Fixed: says where it lives |
| D10 | Minor | `resources/appgen/server.py.tmpl` | The generated app's server checks no `Host` header, so a page using DNS rebinding could drive a running generated app on loopback. Its data is synthetic and it holds no secrets (after D2). | Left: generator lane; [#249](https://github.com/45ck/eija-studio/issues/249) |

## Checked and clean

* Host, token and origin guards; the 32 KiB streamed body cap; JSON-only writes; CSP and `nosniff` on every response; 500s carry no exception text.
* Static files: `/assets/{name}` and `/assets/vendor/{name}` serve exact allowlists; `..%2F` and `//api/` are 404.
* Opening a system takes only the launched pack, one in the systems home, or one on the recent list; `/etc` is refused. New system ids are slugs (`../../evil` becomes `evil`), and a system is never written over an existing folder.
* `eija build --out` only replaces a folder that is exactly a previous build; BUILD.json paths with `..` or absolute paths are ignored.
* The protected-files policy holds: no route writes `pack.json` or `scenarios.json`. The server writes only the systems home (new systems, `recent.json`), a system's `draft.json`, the workspace database and built apps under `<workspace>/apps`.
* The repository source view takes references, not paths, and refuses excluded ones; the mirror is a temp folder outside the checkout.
* MCP doc resources read fixed paths and four-digit ADR numbers only.
* No secret is printed: provider keys come from the environment or a non-echoing prompt, and error bodies never echo input.

## Observations (not defects)

* `eija list` and `eija doctor` create a workspace and `receipt.key` when none exists. `render` explicitly does not.
* `eija export --out` replaces an existing file; `eija backup --out` refuses one.
* `eija lint` uses exit 1 for FAIL and 2 for NOT_RUN, so a command error (also 2) reads as NOT_RUN to a script.

## What keeps it fixed

`tests/test_cli_server_inspection.py` (fast tier) has one test per fixed defect, named D1 to D9.

## Second pass (14 November 2026)

A principal-engineer pass went where the first did not: every route and subcommand run against a live `eija serve`,
a fuller security review (token handling, CSRF and Origin, Host and DNS rebinding on the IDE server, file and path
handling, every child process), concurrency between browser tabs, shutdown, and design-level limits. The boundary
decisions are [ADR-0251](../adr/0251-server-boundaries-second-inspection.md).

### Extra checklist items

11. A limit a person is told (the page's "2 MB" for a UML file) is the limit the server applies.
12. Reading a repository runs nothing the repository or its configuration names (filters, fsmonitor, hooks, external diff).
13. No process the IDE starts outlives it, whichever way the IDE is stopped (Ctrl+C, SIGTERM, closing the terminal).
14. The session token is never anywhere another local user can read it (process arguments, world-readable files).
15. A request that runs while another tab opens a different system reads and writes one system, not half of each.
16. Two of the same action at once (a double click) give two results or a clear refusal, never a 500.
17. Files the IDE writes about the workspace are no more readable than the workspace database (0600).

### Defects

| # | Severity | Where | Defect | Status |
|---|---|---|---|---|
| S1 | Major | `adapters/repository_capture.py` `_metadata` | `eija serve --repo` and `eija mcp --repo` ran a command named in the repository's own `.git/config`: `git status` runs a file's clean filter to compare a stat-dirty file, and `.gitattributes` picks the filter. The module says Git metadata commands never run filters. | Fixed: every configured filter driver is switched off for `status` (`_without_filters`) |
| S2 | Major | `interfaces/http.py` `boundary` | One 32 KiB body cap for every write. The UML import contract and the page allow 2 MB, so PlayIDE refused its own XMI export of 7 of the 11 shipped packs (`BODY_TOO_LARGE`); the plan, ripple and draft routes hit the cap within their own contracts (64 steps, twice). | Fixed: caps per route family (`body_limit`): 32 KiB default, 1 MiB for `/api/play/`, 4.5 MB for the two UML upload routes |
| S3 | Major | `interfaces/play.py` `AppRunner`; `http.py` | SIGTERM to `eija serve` left the built app running on its port: only `atexit` stopped it, and uvicorn re-raises SIGTERM after shutdown so `atexit` never runs. | Fixed: the app is stopped by the server's shutdown event |
| S4 | Minor | `interfaces/cli.py` `_serve_command` | `--open` gave the browser the private link as a command-line argument, which every local user can read (`ps`, `/proc`); the loopback port is open to all of them. | Fixed: the browser opens `<workspace>/open.html` (0600), which forwards to the link and is removed on exit |
| S5 | Minor | `interfaces/play.py` `AppRunner._start` | The app's port is picked free, closed, then bound by the app. A program that took it in between was framed and reported as this model's app, since "something listens" was the only check. | Fixed: the server on the port must name this build's subject at `/api/app` (`_serves`) |
| S6 | Minor | `interfaces/play_systems.py` `StudioHandle`, draft routes | A request still running when another tab opened a different system switched studio halfway (model from one system, pack from the other), and a Save could pass the "same system" check and then write its draft into the other system's workspace. | Fixed: each request is pinned to its studio (`StudioHandle.pinned`); draft save and clear check and write under the switch lock |
| S7 | Minor | `adapters/system_library.py` `create`; `play_new_system` | Two New system requests of one name at once (a double click) both chose the same id; the second rename failed with a bare OSError, a 500. | Fixed: one create at a time with the id chosen again (`x`, `x-2`); a folder made by another process is `SYSTEM_EXISTS` |
| S8 | Minor | `adapters/sqlite_store.py` `backup` | `eija backup` wrote the database copy as 0644 (the database is 0600), and checked for an existing file before, not when, it created it. | Fixed: created with `O_EXCL` as 0600; a file there is `OUTPUT_EXISTS` |

### Checked and clean

* Host allowlist on the IDE server itself: a DNS-rebinding page sends its own name as Host and is refused before the token is looked at; `%61pi` paths are decoded before the `/api/` check, `//api/` and `/API/` are 404.
* Writes need the exact Origin (`null` and absent are refused), JSON content type, and the token; GET routes change nothing. No CORS, no cookies: the token lives in the tab's `sessionStorage` and the link's fragment, which is never sent to a server.
* The built app is a separate origin (another port): it cannot read the IDE's token or pass its Origin check.
* Every Git command passes `-C`, `--no-optional-locks` and `core.fsmonitor=false`, clears `GIT_*` from the environment, uses `--` before paths, and `diff` runs with `--no-ext-diff --no-textconv`. `cat-file`, `ls-tree`, `ls-files` and `check-ignore --no-index` run no filters.
* Ctrl+C (SIGINT) already stopped the app; only SIGTERM did not.
* Conformance runs (`eija build`, Build & run) get an empty environment apart from the Windows system variables, `-I` and a fresh bytecode cache.

### Observations (not defects)

* `eija serve` holds every system opened in this session in memory (`Systems.studios`) until it stops.
* Built apps are kept under `<workspace>/apps/<key>` for every model built; nothing prunes them.
* A Build & run holds the runner's lock for the whole conformance run (up to 600 s); Stop and opening another system wait for it.
* A SIGKILL'd IDE still leaves its app running; only a parent-death signal (Linux only) or a job object (Windows) would stop that.

### What keeps it fixed

`tests/test_cli_server_deeper.py` (fast tier) has one test per defect, named S1 to S8. Each fails on main before the
fix (S1: the marker file the filter writes appears; S2: 413; S3: the child outlives shutdown; S4: the token is in
the argument; S5: no refusal; S6: the request's second read is the other system; S7: an OSError, three requests give
500, 500, 200; S8: mode 0644).
