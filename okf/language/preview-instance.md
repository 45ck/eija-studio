---
type: Ubiquitous Language Term
title: Preview Instance
description: One isolated persisted execution of the candidate model.
resource: repo://docs/architecture/ARCHITECTURE.md#preview-instance
tags:
- language
- ddd
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#preview-instance
  title: ARCHITECTURE.md
  hash_method: md-bold-term-v1
  sha256: 1ed1b22feef6a146d018c225499473130555090f6f4f74158fcde32f5775a8df
notes_baseline: 973051fa93026284069af84407fa3d534edb370d593d3c6a3ff300ca8c2aab75
---

# Preview Instance

<!-- okf:generated:begin facts -->
## Definition

> one isolated persisted execution of the candidate model. It carries model hash and version. A changed candidate makes old instances stale; reset creates a new instance instead of silently migrating it.

Source: `repo://docs/architecture/ARCHITECTURE.md#preview-instance`.
<!-- okf:generated:end facts -->

## Notes

Created by [initialise](/symbols/application/runtime/initialise.md), advanced by [execute](/symbols/application/runtime/execute.md), reset by [Studio.reset_preview](/symbols/application/service/Studio.reset_preview.md). Bound to a model hash and version.

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
