# Gates defined in quality/sessions/hci.py

# Quality Gates

* [nox -s hci_docs](hci-docs.md) - Drift check (no browser): snapshot == derive(committed trace, current laws + budgets); REPORT.md == render(snapshot).
* [nox -s hci_snapshot_fresh](hci-snapshot-fresh.md) - Release tier: the committed HCI evidence must describe the CURRENT UI bytes (strict drift check, no browser).
* [nox -s hci](hci.md) - Drive real Chrome through the owner journey against a real `eija serve`; enforce the HCI budgets.
