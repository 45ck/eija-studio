# Gates defined in quality/sessions/visual.py

# Quality Gates

* [nox -s diagrams_drift](diagrams-drift.md) - docs/diagrams/*.md equal a fresh render of the executable model (no browser, no network).
* [nox -s diagrams_syntax](diagrams-syntax.md) - Every emitted diagram is accepted by the real renderers, and the real-browser negative controls pass.
* [nox -s visual_screenshots](visual-screenshots.md) - Drive the real Studio in Chrome to the Visual view, assert no CSP violation, refresh docs/assets/*.png.
