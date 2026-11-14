# ADR-0251: Request caps per route, no repository filters, and a server that cleans up after itself

* Status: accepted
* Date: 2026-11-14
* Lane: interfaces / security (second Fagan inspection of the command line and server)

## Context and problem statement

A second, deeper inspection of the `eija` command and the local server ([CLI-SERVER-INSPECTION](../engineering/CLI-SERVER-INSPECTION.md), "Second pass") found eight defects (S1 to S8). Four of them needed a boundary decision rather than a line fix.

* **One body cap for every route (S2).** The server refused any write over 32 KiB. The UML import contract (ADR-0190) takes a file of up to 2,000,000 characters and the page checks for 2 MB, so the limit the person was told was never the limit applied. For 7 of the 11 shipped packs the XMI export, sent back as an import request, is over 32 KiB (34 KB to 39 KB), so PlayIDE could not import its own export of them. PlayIDE's other routes carry the model shown, up to 64 plan steps twice, edited screens and a tests draft, and reach the cap well inside their contracts.
* **`--repo` ran a command named by the repository's Git configuration (S1).** `git status` runs a file's clean filter (`filter.<driver>.clean` or `.process`, selected by `.gitattributes`) to compare a stat-dirty file with the index. A checkout whose own `.git/config` names such a command (a downloaded repository, say) had it run by `eija serve --repo` and `eija mcp --repo`, though the capture module says it never runs project code or filters.
* **SIGTERM left the built app running (S3).** The app was stopped only by `atexit`. uvicorn handles SIGTERM, shuts down and then re-raises the signal, whose default handler ends the process without running `atexit`. The generated app went on serving on its port after the IDE had gone.
* **`--open` put the private link on the browser's command line (S4).** `webbrowser.open(url)` starts the browser with the URL as an argument, and every local user can read another process's arguments (`ps`, `/proc`). The loopback port is reachable by every local user, and the token is the only thing that tells the owner apart.

## Decision drivers

* A limit the person is told is the limit applied, and each route's cap follows from its contract.
* "Never executes its code" holds for the repository's configuration as well as its files.
* No process the IDE starts outlives it, however it is stopped.
* The session token is never in a place another local user can read.

## Considered options

* Raise the single cap to the largest contract (about 4.5 MB) for every route. Simple, but the Change Case routes and the page's plan transfer check (play-activation.js) are built on 32 KiB, and nothing there needs more.
* A cap per route family: 32 KiB by default, 1 MiB for PlayIDE's `/api/play/` routes, `2 × MAX_CHARS + 512 KiB` for the two routes that take a UML file. Chosen.
* For S1: stop running `git status` (the `dirty` flag is metadata only), or switch off filters for that one command. A switch-off keeps the flag and the behaviour; Git has no single option for it, so each filter driver the configuration names gets an empty `clean`, `smudge` and `process` and `required=false` through `-c`.
* For S3: a signal handler of our own (it would fight uvicorn's), or the ASGI shutdown event, which uvicorn runs on Ctrl+C and SIGTERM before it re-raises. Chosen: `app.router.add_event_handler("shutdown", runner.stop)`.
* For S4: print the link only and drop `--open` (a regression for every user), or open an owner-only launcher page, as Jupyter does. Chosen: `<workspace>/open.html`, mode 0600 in the 0700 workspace, forwarding to the private link; it is removed when the server stops.

## Decision outcome

All four chosen options above, plus line fixes for S5 to S8 (recorded in the inspection log): the IDE confirms that the server on the built app's port is that build (its `/api/app` names the build subject) before it frames it; a request is pinned to the system it began on (`StudioHandle.pinned`), and a draft is checked and written with no system switch in between; new systems are created one at a time so a double click makes `x` and `x-2`; a backup is a new 0600 file.

### Consequences

* Good: PlayIDE round-trips its own UML exports; a repository's configuration cannot make the IDE run a command; stopping the IDE stops its app; the token stays out of the process table.
* Bad: with filters switched off, a Git LFS file that is stat-dirty compares as its raw bytes, so the read-only `dirty` flag can say true where `git status` with LFS would not. A PlayIDE route may now read up to 1 MiB (4.5 MB for a UML file) into memory per request; the server is single-owner and loopback-only.
* Revisit when: a route's contract grows past its family's cap (give it its own entry in `interfaces.http.body_limit`), or the server stops being single-owner.

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| Starlette lifespan / FastAPI shutdown event | Used as is | none needed |
| Jupyter Server's browser launcher file (pattern only, not code) | No library exposes it; it is a few lines | none needed |
| Git `-c` configuration overrides | Used as is; Git has no single switch that disables every filter | none needed |
