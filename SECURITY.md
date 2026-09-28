# Security policy

## Reporting a vulnerability

Please report suspected vulnerabilities **privately** using GitHub private vulnerability reporting: <https://github.com/45ck/eija-studio/security/advisories/new>. Do not open a public issue or pull request for an unpatched vulnerability, and do not post exploit details in discussions.

Include the affected version or commit, your platform, the smallest steps that reproduce it, and what an attacker gains. Please do not include real personal data, provider keys or `receipt.key` contents in a report. If the private reporting form is unavailable to you, open a public issue that says only "security contact requested", with no details, and a maintainer will arrange a private channel.

This is a volunteer-maintained proof of concept. We aim to acknowledge a report within a week and to say what we will do about it, but we do not offer a service-level agreement or a bounty.

## Supported versions

| Version | Supported |
|---|---|
| `main` (development) | yes, fixes land here first |
| 0.2.x | yes, while it is the latest release |
| earlier | no |

## Threat model and scope

EIJA v0.2 is designed for **one trusted OS user, one local server, synthetic data**. The threat model, the controls that exist and their residual limits are in [docs/SECURITY_AND_TRUST.md](docs/SECURITY_AND_TRUST.md). In particular:

* In scope: a remote page or network peer causing a local mutation; provider output escalating its authority or executing script in the Studio; credential or key disclosure through EIJA; replayed or forged evidence being accepted; a bypass of the authority-before-replay check; an agent-accessible path to approve or apply.
* Out of scope by design: an attacker who already runs as the same OS user (they can read `receipt.key`, edit the database or the source), deployment on a network or behind a reverse proxy, production student records, and the institutional identity of the "local owner". These are documented limitations, not vulnerabilities, but a report showing that the documentation understates them is welcome.

## Handling secrets

Never paste provider keys into an issue, a change case, a prompt or a browser field. Use `eija serve --ask-key` or your own secret manager. EIJA does not read Codex or other CLI token files and will not turn a subscription login into an API key.
