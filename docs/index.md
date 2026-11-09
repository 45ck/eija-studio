---
description: "PlayIDE (EIJA Studio) documentation: an open-source UML workbench that shows AI-proposed changes as a visual UML diff, checks them and runs the system locally."
---

# PlayIDE · EIJA Studio

**Review the UML diff. Understand the change. Run the system.**

PlayIDE is an open-source (Apache-2.0) workbench for software engineers who read UML. When an AI or a person proposes a change to a supported workflow, PlayIDE shows it as a visual UML diff, follows its effects to related diagrams, screens, laws and checks, and builds a local app you can run beside the diagram. It runs on the EIJA (Executable Intent and Journey Assurance) Python kernel. AI proposes. The kernel checks. The local owner decides.

This site is the documentation of the repository at <https://github.com/45ck/eija-studio>. The repository [README](https://github.com/45ck/eija-studio#readme) is the front door: the problem, the loop, a diagram generated from the real model, the quickstart and the comparison with alternatives.

| I want to | Go to |
|---|---|
| Install and run it | [Getting started](getting-started.md) |
| Understand the design and ubiquitous language | [Architecture](architecture/ARCHITECTURE.md) |
| Judge readiness honestly | [Technical lead review](TECHNICAL_LEAD_REVIEW.md), [Security and trust](SECURITY_AND_TRUST.md) |
| Read why decisions were made | [ADR index](adr/README.md) |
| See what evidence exists and what does not | [Verification](verification/VERIFICATION.md), [Formal V&V](lanes/formal.md) |
| See what is done, in progress and planned | [Roadmap](ROADMAP.md) |
| Use it from an agent | [Agents](lanes/agents.md) |
| Know which open-source tools it builds on | [OSS register](oss/REGISTER.md) |

Every status on this site carries a date and one of: on main, open PR, branch pushed, planned. Where a prerequisite is missing, results are reported `NOT_RUN`, never `PASS`.
