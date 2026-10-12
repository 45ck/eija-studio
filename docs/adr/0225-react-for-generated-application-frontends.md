# ADR-0225: React for generated application frontends

* Status: accepted for the generated local app target
* Date: 2026-10-11

## Context

Generated apps need consistent, maintained form and interaction components while remaining connected to EIJA's executable model. The owner requires React. Installing several overlapping design systems would increase maintenance without adding supported semantics.

## Decision

Use React with Mantine core/hooks for the generated frontend. Pin versions and retain an exact lockfile, authored source, dependency licences and a build manifest. Bundle the production JavaScript and external CSS at maintainer build time with esbuild. Ordinary Python package users run those local assets without Node, a CDN or a frontend build step.

React renders the records, forms, action choices, outcomes and history. Existing screen contracts supply labels, ordering and button text; the data model supplies types and validation; actual API responses supply available actions and refusal reasons. EIJA's runtime remains the authority. Screen fields that display record values are not new action-input semantics.

Preserve record/version/actor/operation binding, uncertain-write recovery and the committed-action observation bridge. Pause and replay remain read-only inspection. Keep the current strict content security policy, disable provider-generated inline styles, and use externally bundled styles. Library adoption cannot replace rendered accessibility and failure checks.

The exact generated build subject includes the React source, dependency lock, build manifest and emitted assets. A frontend change invalidates previous exact-app evidence. Architecture projections should identify React from those actual files, rather than infer it from a product label.

## Alternatives

MUI and Ant Design offer broader visual systems but overlap the chosen component responsibility. Copying a complete shadcn stack introduces another maintained template surface. Radix or React Aria remain useful candidates when a concrete Mantine component gap exists. State, query and form libraries are added for observed needs, rather than bundled speculatively.

The existing workbench remains on its current maxGraph/DOM adapter. This decision changes generated apps; a workbench rewrite requires its own concrete benefit and migration proof.

## Verification

Require reproducible bundle hashes, licence preservation, same-origin offline serving and zero CSP violations. Exercise keyboard focus, validation, retained values, refusals, read failure, duplicate/concurrent actions and post-commit trace delivery in the actual React app. Break label/required/control bindings deliberately and require checks to detect them. Prove the Python wheel includes the assets and runs outside the repository.
