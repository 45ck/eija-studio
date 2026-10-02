# Immutable code change review

Documentation for [integration checkpoint `1f1b07f64889`](https://github.com/45ck/eija-studio/tree/1f1b07f648890d8e03f81d4269fa479d80a0f46a). This publication adds documentation and evidence to main; it does not merge the IDE implementation. Observations retain their own recorded source subjects and are not a blanket acceptance of every file in this checkpoint.

Run the commands below from a separate source checkout of that revision, for example:

```sh
git clone --branch integrate/all https://github.com/45ck/eija-studio.git eija-review-checkpoint
cd eija-review-checkpoint
git checkout --detach 1f1b07f648890d8e03f81d4269fa479d80a0f46a
```

EIJA can inspect two local Git commits without checking them out or executing the target project. The comparison is a separate subject from a model change case. A model receipt cannot establish that the compared application behaves as intended.

## Reproduce the navigation change

Install the optional JavaScript syntax adapter with `python -m pip install -e ".[dev,hci,source-analysis]"`. Start `eija serve --provider offline --pack packs/eija-review-slice --repo .` using a fresh workspace, then open **Changes → Code changes**.

Use these full local commit IDs:

- Before: `9c22d425ee33e52980a95b33330babec43c6aa59`
- After: `c666b6bb76905c0c9bd03e81cac0922136c4cf3e`

The commits must exist locally; this operation never fetches. The Git diff identifies the actual changed files. In `src/eija_studio/resources/web/app.js`, the independent expected syntax changes are `cases`, `load`, the create-button handler and the case-switcher handler; `task` is unchanged. These expectations are a regression oracle for this specific pair, not a general inference rule.

Select a changed file or extracted definition. **Before source** and **After source** show bounded excerpts of immutable blobs with their original line numbers. They never fall back to the current working file. Editing the current checkout or moving HEAD does not replace these historical bytes. Selecting another pair or definition cancels the previous presentation request; a late response cannot relabel the current selection.

Changed and unresolved definitions appear first. **All references** includes unchanged extracted definitions. The revision editor closes after the first successful comparison; **Change revisions** reopens the full IDs. Model changes remain a separate local tab with their own case, selection and evidence.

## What each result means

| Result | Establishes | Does not establish |
|---|---|---|
| Git commit/tree/blob and file digest | The identity of the inspected revision and bytes | Correctness, authorship by a particular agent or approval |
| Native Git unified diff | Exact text changes within the declared captured scope | Meaning of the change or runtime consequences |
| Python AST / JavaScript syntax facts | Bounded definitions, source ranges and deterministic syntax fingerprints | Semantic equivalence, complete call resolution or behavior |
| Declared Weave impact | Returned witness paths through the captured changed files and configured pack | Complete downstream impact; unmodified files and dynamic dependencies are omitted |
| Existing model verification | A result for its explicitly identified supported model subject | Verification of the compared Git commits |

JavaScript currently indexes supported top-level functions and literal function-valued assignments. Class syntax and dynamic targets remain explicit gaps. Both sides of the navigation example report PARTIAL because `ApiError` is unsupported. Missing parser packages, native failures, timeouts and malformed parser responses produce NOT_RUN; real file diffs remain usable when possible.

Source ranges use physical CR, LF and CRLF boundaries. The pinned JavaScript parser can incorrectly attach trailing comments to a function across bare CR. Its input view replaces only bare CR with LF without changing byte length; excerpts, offsets, source hashes and token fingerprints still use the original bytes. Worker-to-excerpt regressions retain trailing-comment, mixed-ending and literal-content cases. This is a bounded adapter workaround, not an upstream parser fix or behavioral proof.

## Boundaries and implementation

The application-owned read-only port supplies `repository_change(base, head)` and `repository_change_file(base, head, path, reference?)`. Authenticated HTTP and the existing narrow MCP surface expose the same results. Full lowercase 40- or 64-character object IDs are required. No branch/revision expression, caller-selected root, checkout, target test, hook, filter, textconv or external diff program is executed.

Git supplies object identity, inventory and the line diff. Existing Python AST/Weave infrastructure supplies Python facts. Pinned MIT Tree-sitter packages supply JavaScript parsing through the existing bounded process runner. The parent Studio process does not import the native parser. Byte offsets provide line ranges; the worker avoids native Point access after access violations were observed during early Windows experiments. The retained reduced reproductions were nondeterministic, so this is crash containment and a tested workaround, not a claim that an upstream defect is resolved.

Capture is limited to permitted changed files: at most 128 paths, 2 MiB per file and 32 MiB across both sides. Excluded counts reconcile with the changed inventory. Selected source is bounded to 200 lines / 32768 UTF-8 bytes and labels truncation. Historical `changed_source_hash` covers only the captured changed files; it is not interchangeable with the live connection's whole captured `source_hash`.

Known impact always declares `complete:false`. Current ignore policy is part of capture identity. Repositories with replacement objects or promisor configuration are refused. Unsupported, ambiguous, excluded and unavailable facts remain visible rather than becoming empty success.

Detail navigation can retain one comparison, bounded to 8 MiB of source and 2 MiB of serialized metadata. Explicit comparison always recaptures. Reuse checks the full changed-path ignore decisions, repository restrictions, pack and extractor prerequisites before serving a defensive copy and again before returning. This is point-in-time validation, not a filesystem lock. Transient extraction failures are not retained. One direct-adapter diagnostic measured a detail read at 0.603 seconds versus an earlier 2.632 seconds; these are single observations, not browser latency or a benchmark.

Git receives literal filenames: brackets cannot expand a selected path into neighboring files. Duplicate Python definitions remain ambiguous, and exceeding the 1024-symbol inventory limit offers no guessed symbol selection. Historical ranges count physical CR, LF or CRLF lines while preserving original bytes; Unicode separators inside a string do not become additional source lines.

## Validation record

The [review checkpoint](../design/2026-10-03-CODE-REVIEW-VALIDATION.md) records scoped browser checks, their source subjects and remaining gate failures. The [historical navigation proof](../demos/2026-10-03-NAVIGATION-RECOVERY-PROOF.md) reproduces two old-version display failures and their repair using exact exported commits; its [two-command replay guide](https://github.com/45ck/eija-studio/blob/1f1b07f648890d8e03f81d4269fa479d80a0f46a/tests/hci/repository_navigation_pair.md) records prerequisites and boundaries. Those observations remain separate from the code comparison's behavior status. The [whole-app acceptance](SELF-DOGFOOD-ACCEPTANCE.md) stays open, including human comprehension and parallel-agent coordination.
