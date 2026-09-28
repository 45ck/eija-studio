"""HCI-law instrumentation for the Studio UI (engineering tooling; never shipped in the wheel).

Layers, innermost first: `laws` (pure formulas), `wcag` (pure target-size rules), `probe.js`
(in-page measurement), `journey` (Playwright drivers), `analysis` (trace -> metrics),
`recommend`, `report` (canonical JSON + Markdown), `budgets` (ratchets used by the pytest marker
`hci`). Nothing here selects meaning, approves or applies on behalf of a human: the journey runs
against a private ephemeral `eija serve` on a throw-away workspace, offline provider, synthetic data.
"""
