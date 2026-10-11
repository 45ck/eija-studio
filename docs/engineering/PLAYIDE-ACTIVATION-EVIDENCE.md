# PlayIDE activation behavior evidence

The activation checker observes **actual Studio services and SQLite adapters** against
hand-declared expectations. It does not execute the `eija-review-slice` reference pack
and call that implementation conformance. Repository AST facts, reference-model
simulation, and these observed direct-call outcomes remain distinct.

Run from the checkout with the pinned Python environment:

```powershell
python -m pytest tests/test_activation_selfdogfood.py -q
python -m verification.selfdogfood --out reports/activation-selfdogfood.json
```

`run_activation_checks()` is the read-only engineering entry point. It reads this
checkout's implementation identity, source symbols and Git revision, then constructs
fresh, disposable synthetic SQLite workspaces under `.tmp`. It opens no existing
user workspace, makes no network calls, reads no launch capability or existing receipt
key, and never stamps source. The disposable signer creates its own temporary key.
The CLI optionally writes a report only at the caller's requested path.

## What is exercised

The five-command fixture is independently written: add the recommendation state,
move approval and rejection to it, add recommendation, then restore rejection from
Submitted. The last command differs from the existing named pack meaning. Checks
compare the exact resulting workflow, commands, mixed authorship and rounds,
history replay readiness, and unchanged active model before activation.

The named service checks cover candidate identity, stale transfer, denied agent
transfer/meaning selection/approval/application, source review, stale evidence,
changed review subject, edit invalidation with retained receipts, two competing
activations, actual adapter CAS, rollback after baseline update, duplicate application,
and reopening through fresh SQLite connections. A synthetic test owner acknowledges
fixture questions only inside its disposable test workspace. That is a mechanical
test of a service boundary, not an owner review of this implementation.

Seven visible faults clone actual local callables into private synthetic classes:
remove each of the four owner capability checks, the exact review-subject check,
the runtime-evidence eligibility blocker, or the case SQL version predicate. A
control is detected only when its behavioral expectation fails on the concrete
unsafe outcome. A changed digest, unrelated crash, or import failure does not count.
No global service class or production source is patched.

## Report and limits

The report identifies the source commit and dirty paths, complete implementation
content manifest, pack/model identities, checker content manifest, Python/platform,
each observation, each detected counterexample, assumptions, and skipped work.
Changes detected between the measured implementation and checker manifests make
its overall status `STALE`. `SOURCE_REVIEW_REQUIRED`
is derived from the normal measured implementation identity and remains visible even
when the bounded synthetic checks pass. Results never become production eligibility
receipts or confer approval authority.

The oracle is explicit and separately expressed, but shares this change's authorship.
The mutation set is visible, not independent or hidden. One excursion fixture and
selected interleavings do not establish complete implementation equivalence, all
software semantics, institutional identity, power-loss durability, browser usability,
or human comprehension. Normal owner source review and release activation remain
`NOT_RUN`; ordinary browser evidence belongs in its own run record.
