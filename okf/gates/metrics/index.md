# Gates defined in quality/sessions/metrics.py

# Quality Gates

* [nox -s metrics_report](metrics-report.md) - Release evidence: coverage export, full-profile measurement (median and IQR), all budgets, dashboard in reports/metrics/.
* [nox -s metrics_snapshot_fresh](metrics-snapshot-fresh.md) - Release tier: the committed snapshot's deterministic sections describe the CURRENT source (strict drift check).
* [nox -s metrics](metrics.md) - Structural metrics (Martin, complexity, test inventory), structural budgets, dashboard renders from its snapshot.
