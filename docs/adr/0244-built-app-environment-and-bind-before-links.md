# ADR-0244: The built app gets no secrets, and `eija serve` binds its port before it prints a link

* Status: accepted
* Date: 2026-11-13
* Lane: interfaces / security (Fagan inspection of the command line and server)

## Context and problem statement

A Fagan inspection of the `eija` command and the local server ([CLI-SERVER-INSPECTION](../engineering/CLI-SERVER-INSPECTION.md)) found two boundary defects.

* **Build & run handed the IDE's whole environment to the built app.** `AppRunner._start` removed only `PYTHONPATH`, `PYTHONHOME` and `PYTHONSTARTUP`. A person who starts PlayIDE with `OPENAI_API_KEY` (ADR-0229/0230), `ANTHROPIC_API_KEY` or `OPENROUTER_API_KEY` set passed that key to every generated app process. The generated app never needs it. The conformance run (ADR-0150) already used an allowlist, so the two child processes disagreed.
* **`eija serve` printed its private links before it owned the port.** The links (with the session token in the fragment) were printed, and `--open` opened the browser, before uvicorn tried to bind. When another program held the port, the browser opened that program's page with the token in its address, the command printed a raw uvicorn error and exited 1, not the JSON failure every other command prints. An invalid port was refused only after the workspace and its `receipt.key` had been created.

## Decision drivers

* Least privilege at every child-process boundary (docs/SECURITY_AND_TRUST.md: keys stay in the process that needs them).
* A link to the private session must only ever point at this server.
* Every `eija` failure is one JSON object with a stable code and exit 2 (ADR-0236).

## Considered options

* Keep the deny-list and add the known key names to it. Any key we do not know about (a cloud token, a database URL) still leaks.
* An allowlist for the built app's environment, as the conformance run has.
* For the port: check it with a probe connect before printing. Racy, and a probe cannot tell a closed port from a filtered one.
* Bind and listen on the socket first, print and open the browser, then hand that socket to uvicorn (`Server.run(sockets=[...])`).

## Decision outcome

Chosen options: the allowlist (`interfaces.play.APP_ENVIRONMENT`: `PATH`, the Windows system variables, home, locale, time zone, temp folders and `VIRTUAL_ENV`, plus `PORT`), and bind-then-print. `eija serve` validates the port and binds `127.0.0.1:<port>` before it builds the studio, so a bad or busy port (`CONFIGURATION`, `PORT_IN_USE`) leaves no workspace behind and prints no link. The socket is already listening when the browser opens, so the old "refresh if necessary" race is gone too.

### Consequences

* Good: no provider key reaches a generated app; a busy port is a clear, early, JSON failure.
* Bad: a generated app that someone edits to read another environment variable no longer sees it when PlayIDE starts it. `python run.py` from a shell still passes the shell's environment.
* Revisit when: the generated app needs configuration from the environment (add the variable to the allowlist with a test).

## OSS check (required for any custom module)

| OSS checked | Why adapter/dependency use was insufficient | Replacement or fork path |
|---|---|---|
| uvicorn `Server.run(sockets=...)` | Used as is; no custom server code | none needed |
