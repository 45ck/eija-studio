---
type: Function
title: domain.sequences.messages
description: Every message, fragments' operands included, in reading order.
resource: repo://src/eija_studio/domain/sequences.py#messages
tags:
- symbol
- domain
- function
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/sequences.py#messages
  title: domain/sequences.py
  hash_method: ast-v2
  sha256: 3b9f66d62f87d3c9c37d57d8f5b58beb4133b2776d75678dcd7c8c4a2c96043a
notes_baseline: 4a950d4f769d2fcd4a5a6295e9c3b1f8c7ad21aa1c58a7bead296b6c794115b6
---

# domain.sequences.messages

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | function |
| Module | [`domain/sequences`](/modules/domain/sequences.md) |
| Signature | `def messages(steps: tuple[Step, ...]) -> list[Message]` |
| Code | `repo://src/eija_studio/domain/sequences.py#messages` |
| Hash | `ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored) |

## Docstring

~~~text
Every message, fragments' operands included, in reading order.
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.sequences.Message](/symbols/domain/sequences/Message.md) - `class Message(Contract)` in `domain/sequences`.
* [domain.sequences.Step](/symbols/domain/sequences/Step.md) - Type alias `Step` in `domain/sequences`.

## Referenced by

* [domain.sequences.Interaction.known_records](/symbols/domain/sequences/Interaction.known_records.md) - `def known_records(self) -> Interaction` in `domain/sequences`.
<!-- okf:generated:end links -->
