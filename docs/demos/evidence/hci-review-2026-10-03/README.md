# Integration HCI evidence, 3 October 2026

This is an unchanged archive of the generated [REPORT.md](REPORT.md), [report snapshot](report.snapshot.json) and [trace](trace.snapshot.json) from [integration checkpoint `1f1b07f64889`](https://github.com/45ck/eija-studio/tree/1f1b07f648890d8e03f81d4269fa479d80a0f46a). The files retain their recorded subject and original outcome; this publication is not a browser rerun.

Observed budget flags: **15 PASS, 1 GAP, 2 FAIL**.

| Metric | Recorded value | Target | Limit | Outcome |
| --- | --- | --- | --- | --- |
| memory.max_chunks_viewport | 56 | 9 | 27 | FAIL |
| klm.pointer_expert_time | 65.31 | 65 | 65 | FAIL |
| doherty.settled_p95 | 747.6 | 400 | 4000 | GAP |

Reproduction must use the [pinned instrumentation guide](https://github.com/45ck/eija-studio/blob/1f1b07f648890d8e03f81d4269fa479d80a0f46a/docs/hci/README.md) and its source checkout. Main has a different analyzer and canonical threshold snapshot; do not rederive these historical observations with main's runner or alter its gates to accommodate this archive. Strict source freshness of the integration capture does not mean that its HCI budgets passed. Prediction and instrumented measurements on synthetic data do not establish human comprehension or usability.

Original file SHA-256 identities:

- `REPORT.md`: `a8e8e99efc783fffbe6ce84b4bc64eb818c4e8afdef15901c7829ca293f8bde6`
- `report.snapshot.json`: `d1a4acf476da37e77b167d7d21085069c55d327f4d239dc6c776a860f0c4238b`
- `trace.snapshot.json`: `08978f6ab3a6019c212643bcc396deb280d1ec103a1812d8b5ce1b995bda3283`
