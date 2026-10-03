# Native Workspace focus: corrected test assumption

This changes only the browser replay and its unit oracle. It does not add a product focus trap, alter native navigation, relax a HCI budget, or convert an old result to PASS.

## Retained actual observation

Both `outputs/pof/workspace-shell-browser-1` and `workspace-shell-browser-2` remain unchanged failures under the earlier always-inside assertion. Browser 2 used replay SHA `03e235134a1f263a53c18c2032884683c805dd43ea455e02bef5d612dfc79b66`. Its first four groups passed before the 1440-pixel native focus cycle failed.

The final three records in `workspace-shell-browser-2/workspace-1440-modal-focus-trail.json` show:

1. Layout `SUMMARY`: inside dialog, document focused, dialog open and modal.
2. One native Tab: `BODY`, empty id, outside dialog, `document.hasFocus()` false, dialog still open and modal.
3. Exactly one further native Tab: `BUTTON#close-workspace`, inside dialog, document focused, dialog still open and modal.

The trail SHA256 is `0cc57b3c35f8345ff27a78a43f98dbff3ddd986c3d8d0f4684e861e57265d784`. First-outside and next-Tab screenshots are retained alongside it. This is evidence of a user-agent focus boundary, not evidence that a page control behind the modal became operable. Browser chrome itself is not inspected or identified by this DOM observation.

## Why the assumption changes

The HTML sequential focus navigation algorithm's step 8 permits focus to move to browser controls in the navigation direction when the document has no next eligible target. The modal can remain active during that transition. [HTML Standard, sequential focus navigation](https://html.spec.whatwg.org/multipage/interaction.html#sequential-focus-navigation).

The expectation that Tab immediately cycles between the last and first dialog controls appears in ARIA authoring guidance. The standards discussion explicitly contrasts that expectation with native dialog navigation through browser controls. This replay follows the observed native boundary and checks page inertness separately; it does not claim that this resolves every accessibility interpretation. [WHATWG HTML issue 8339](https://github.com/whatwg/html/issues/8339).

## Exact revised oracle

- Every recorded state must retain `dialogOpen=true` and `dialogModal=true`.
- Ordinary success requires a dialog descendant and `documentHasFocus=true`.
- The only accepted outside observation is `BODY`, empty id, `inside=false` and `documentHasFocus=false` while the dialog remains modal.
- Forward traversal may encounter that boundary only after Layout, the last current control. Exactly one further native Tab must reenter the dialog. At narrow widths, an actually overflowing dialog may itself receive native scroll-region focus before Close; one further Tab must reach Close. Reverse traversal from Close may pass through that same scroll-region stop before the user-agent boundary; one further Shift+Tab from the boundary must return to Layout.
- No repeated boundary, wrong return, closed dialog, nonmodal dialog, focused page BODY, or background page control is accepted. All nine work destinations and all three panel destinations must still be observed. Case/state/no-POST, shortcut, Escape and restoration checks remain intact.
- A bounded negative control attempts `focus()` on the existing inert New intent button while Workspace is modal. The browser must keep focus on Close. It does not activate the button or change product DOM/state.

Focus records continue to persist after every key, with screenshots at recognized boundaries. No extra retries or direct focus restoration mask a failed return.

The third retained run passed both desktop widths, then exposed the narrow native scroll-region stop: at 320px, returning from the user-agent boundary focused `DIALOG#workspace-dialog`, still modal and document-focused. That earlier Close-only expectation remains a retained failure. The current check accepts this one additional stop only after measuring genuine vertical overflow and requires the next native key to reach the exact next control. Both directions retain every intermediate observation. HTML includes scrollable regions among native focusable areas; this is not an application focus trap. [HTML focusable areas](https://html.spec.whatwg.org/multipage/interaction.html#focusable-area).

## Verification and handoff

Sixteen focused tests of the actual replay oracle pass, covering both expected return controls and rejected boundary/return counterexamples. Intended-path Ruff and Python AST checks pass. No browser ran during this staging task; native backward traversal and the inert-background probe are **NOT_RUN** until root's fresh serialized replay.

Apply the two-file guarded manifest, then run the existing seven-group command with a fresh output directory after normal browser readiness. Retain the old failures and describe this as an oracle correction when reporting the new result. This is not evidence that the previous scripts passed.

## Reproduce

After endpoint browser preflight, use the installed development/HCI environment and isolated Playwright Chromium. Run browser workloads serially. From the checkout, set `PYTHONPATH` to the checkout root and run:

```powershell
python tests/hci/workspace_shell_review.py --out reports/workspace-shell-review-new
```

The output directory must be new. The seven groups inspect actual empty/loading/unavailable/retained case inventory and retry, then all nine Workspace views and three panel routes at 1440, 1280 and 320 pixels. Two real draft-case creations are the only setup writes; later navigation must preserve independent case/history/packet observations. This default-pack shell check does not validate a connected repository, live inference, owner decisions or human usability. Standalone oracle tests use a pytest import fixture and report NOT_RUN if the optional Playwright runtime is missing; importing the harness starts no browser or server.
