---
type: Class
title: domain.transactions.TransactionDocument
description: One semantic transaction as a JSON document (contracts/semantic-transaction.schema.json).
resource: repo://src/eija_studio/domain/transactions.py#TransactionDocument
tags:
- symbol
- domain
- class
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://src/eija_studio/domain/transactions.py#TransactionDocument
  title: domain/transactions.py
  hash_method: ast-sig-v1
  sha256: ab563f27181dc263c3b6083bac981832277517d73d40e635d1b91fa6983dc76d
notes_baseline: 8c0b55aa409421dd5a939ae885d6639b87fa95b40b54161f07ddabd4bb6ba359
---

# domain.transactions.TransactionDocument

<!-- okf:generated:begin facts -->
| | |
|---|---|
| Kind | class |
| Module | [`domain/transactions`](/modules/domain/transactions.md) |
| Signature | `class TransactionDocument(RootModel[Transaction])` |
| Code | `repo://src/eija_studio/domain/transactions.py#TransactionDocument` |
| Hash | `ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed |

## Docstring

~~~text
One semantic transaction as a JSON document (contracts/semantic-transaction.schema.json).
~~~
<!-- okf:generated:end facts -->

## Notes

_No curated notes yet._

<!-- okf:generated:begin links -->
## Depends on

* [domain.transactions.Transaction](/symbols/domain/transactions/Transaction.md) - Type alias `Transaction` in `domain/transactions`.

## Referenced by

* [domain.transactions.parse_transaction](/symbols/domain/transactions/parse_transaction.md) - Validate one transaction document; a malformed one is ``EDIT_INVALID``, never a crash.
<!-- okf:generated:end links -->
