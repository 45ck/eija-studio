# New in the kernel: rules you draw, the kernel enforces (12 November 2026)

This is a scripted recording of the real PlayIDE page (`/play`). Every click is a real browser action against a real `eija serve`, and every step asserts text the page actually rendered. `python -m demos run playide_kernel_rules --dry-run` repeats the same clicks and assertions without video. The take is **PASS**, with no act skipped. It runs 3 minutes 2 seconds.

[Watch the README copy](assets/playide-kernel-20261112/playide-kernel-rules.mp4) (1280 wide).

## What it starts from

No shipped pack uses initiators, separation of duties, value guards or built references yet ([ADR-0243](../adr/0243-conformance-that-catches-divergence.md)). So before the take, the scenario writes a library-loan variant under `.tmp/demo-packs/` with those rules switched on, the same variant `tests/test_play_kernel_features.py` walks, and copies library-fines beside it. The first caption says the rules were switched on. No shipped pack changes. The last two chapters use shipped templates unchanged.

## What the run shows

| Chapter | What is real |
|---|---|
| Guards over record values | `CheckOut [renewals ≤ 3]` on the state machine, in UML's `event [guard]` notation, and the same guard in the permissions table ([ADR-0234](../adr/0234-guards-over-record-values.md)). |
| One action from several states | `Return` leaves `OnLoan` and `Overdue`. The outline names each source state; there is still one use case and one screen ([ADR-0232](../adr/0232-one-action-from-several-states.md)). |
| Who may start a record | Only a Member starts a loan. The use case diagram links Member to Create ([ADR-0231](../adr/0231-who-may-start-a-record.md)). |
| Separation of duties | The `four-eyes` law (whoever checks a loan out does not take its return) holds on every run the kernel allows ([ADR-0233](../adr/0233-separation-of-duties.md)). |
| Checked references | The borrower association is built: the app stores a member id and refuses one that names nobody ([ADR-0235](../adr/0235-built-associations.md)). |
| Signals between workflows | The System lens draws `«signal» LateReturn` from the loan workflow to the fines workflow ([ADR-0242](../adr/0242-messages-between-workflows.md)). |
| Prove the app matches | Build & run: all 432 conformance cases match the kernel, and all 7 scenario tests pass ([ADR-0243](../adr/0243-conformance-that-catches-divergence.md)). |
| Composite states and time events | From the refund-desk template: the `Deciding` composite state, `EscalateStale after(2 days)`, and the timer refused with `TIMER_NOT_DUE` until it is due ([ADR-0240](../adr/0240-composite-states.md), [ADR-0237](../adr/0237-time-events.md)). |
| Actions on linked objects | From the AI ops template: `OpenWindow / target.lock` locks the target service ([ADR-0241](../adr/0241-actions-on-linked-objects.md)). |

## Not shown

The chat is not used: nothing here comes from a model, live or offline. Nothing is approved or applied; that waits on the owner's source review and restamp (issue #80). The take does not show the kernel refusing a fourth renewal, a second deploy window or a same-actor return as a live action; those refusals are covered by the kernel and conformance tests, not by this video.

## Reproduce the recording

```bash
pip install -e ".[demos]"
python -m demos run playide_kernel_rules --dry-run   # same clicks and assertions, no video
python -m demos run playide_kernel_rules             # demos/output/playide_kernel_rules.webm and its manifest
python -m demos finish playide_kernel_rules          # demos/output/playide_kernel_rules.mp4 (1080p stage)
ffmpeg -i demos/output/playide_kernel_rules.mp4 -vf scale=1280:-2 -crf 30 -an -movflags +faststart \
  docs/demos/assets/playide-kernel-20261112/playide-kernel-rules.mp4
```

The poster is the frame at 1:36 (signals between workflows). A scenario may build its pack before the take with `PREPARE_PACK`, which writes only under `.tmp/`.
