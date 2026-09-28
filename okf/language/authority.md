---
type: Ubiquitous Language Term
title: Authority
description: Permission to perform a domain or governance operation at the moment it commits.
resource: repo://docs/architecture/ARCHITECTURE.md#authority
tags:
- language
- ddd
status: stable
generated:
  by: process:eija-okf-sync
sources:
- resource: repo://docs/architecture/ARCHITECTURE.md#authority
  title: ARCHITECTURE.md
  hash_method: md-bold-term-v1
  sha256: 54ef80276337645be16c1170bf70b6901e47347a0489e50d1e900f694daf4279
---

# Authority

<!-- okf:generated:begin facts -->
## Definition

> permission to perform a domain or governance operation at the moment it commits. A previous successful call, model output or current UI selection cannot establish continuing authority.

Source: `repo://docs/architecture/ARCHITECTURE.md#authority`.
<!-- okf:generated:end facts -->

## Notes

Enforced at commit time by [check_actor](/symbols/application/runtime/check_actor.md) for actors and by [Principal.require](/symbols/domain/models/Principal.require.md) for governance. Protected authority rules live in [check_policy](/symbols/domain/policy/check_policy.md).

<!-- okf:generated:begin links -->
_No generated cross-references._
<!-- okf:generated:end links -->
