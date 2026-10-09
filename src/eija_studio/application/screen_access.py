"""Accessibility of the generated screens (ADR-0218): what can be checked without a browser, checked every time.

The built app's page comes from fixed templates (`resources/appgen/web/`) filled with the designed screens and the
record class (ADR-0150, ADR-0154). So its accessibility has two parts. One is fixed by the templates: text contrast in
the light and the dark theme, colours that bypass the theme, labelled controls, keyboard order and how a required field
is marked. The other changes with every design: labels a screen repeats, labels that read as code, and actions from
one state that look alike. Both are judged here, against WCAG 2.2 level AA success criteria, with the measured value
where there is one. A pass is not a full audit: it says nothing about what only a person or a browser can judge (an
axe-core run on the built app is the browser tests' job).

Pure: the theme CSS and the page templates are passed in, so the same inputs always give the same report.
"""
from __future__ import annotations

import re
from typing import Any

from eija_studio.domain.data import DataModel
from eija_studio.domain.models import Workflow
from eija_studio.domain.screens import Screens

AA_TEXT = 4.5  # WCAG 2.2 SC 1.4.3, normal-size text
# (what, foreground token, background token): the text the generated page draws on each surface.
PAIRS = (
    ("Text on panels", "ink", "panel"),
    ("Secondary text on panels", "muted", "panel"),
    ("Secondary text on the page", "muted", "bg"),
    ("Button text", "accent-ink", "accent"),
    ("Success notices", "ok", "ok-bg"),
    ("Refusal notices", "bad", "bad-bg"),
    ("Warning notices", "ink", "warn-bg"),
    ("The current record, state and screen", "ink", "current"),
)
_ROOT = re.compile(r":root\s*\{([^}]*)\}")
_DARK = re.compile(r"@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}\s*\}")
_TOKEN = re.compile(r"--([a-z-]+)\s*:\s*(#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b)")
_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
_HEX = re.compile(r"#[0-9a-fA-F]{3,6}\b")
_CODE_LIKE = re.compile(r"^[a-z]+(?:[A-Z][a-z0-9]*)+$|_")


def _long(colour: str) -> str:
    """#rgb as #rrggbb."""
    return "#" + "".join(c * 2 for c in colour[1:]) if len(colour) == 4 else colour


def _tokens(block: str) -> dict[str, str]:
    return {name: _long(value.lower()) for name, value in _TOKEN.findall(block)}


def themes(css: str) -> dict[str, dict[str, str]]:
    """The theme tokens of the light page and of the dark one (the dark block overrides the light)."""
    root, dark = _ROOT.search(css), _DARK.search(css)
    light = _tokens(root.group(1)) if root else {}
    return {"light": light, "dark": light | (_tokens(dark.group(1)) if dark else {})}


def luminance(colour: str) -> float:
    """WCAG relative luminance of a #rrggbb colour."""
    channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(foreground: str, background: str) -> float:
    high, low = sorted((luminance(foreground), luminance(background)), reverse=True)
    return round((high + 0.05) / (low + 0.05), 2)


def _check(check: str, wcag: str, status: str, text: str, **detail: Any) -> dict[str, Any]:
    return {"check": check, "wcag": wcag, "status": status, "text": text, **({"detail": detail} if detail else {})}


def _contrast_checks(css: str) -> list[dict[str, Any]]:
    found = []
    for mode, tokens in themes(css).items():
        rows: list[dict[str, Any]] = []
        low: list[str] = []
        for what, fg, bg in PAIRS:
            if fg not in tokens or bg not in tokens:
                low.append(f"{what}: the theme has no --{fg if fg not in tokens else bg}")
                continue
            ratio = contrast(tokens[fg], tokens[bg])
            rows.append({"what": what, "ratio": ratio, "foreground": tokens[fg], "background": tokens[bg]})
            if ratio < AA_TEXT:
                low.append(f"{what} {ratio}:1")
        worst = min((float(r["ratio"]) for r in rows), default=0.0)
        found.append(_check(f"contrast-{mode}", "1.4.3", "FAIL" if low else "PASS",
                            f"Text contrast in the {mode} theme is at least {AA_TEXT}:1 (lowest {worst}:1)" if not low
                            else f"Text contrast in the {mode} theme is below {AA_TEXT}:1: {'; '.join(low)}", pairs=rows))
    return found


def _fixed_colours(css: str) -> dict[str, Any]:
    """A colour written into a rule instead of a theme token stays the same in the dark theme, whatever is behind it."""
    stripped = _DARK.sub("", _ROOT.sub("", css, count=1), count=1)
    fixed = sorted({selector.strip() for selector, body in _RULE.findall(stripped) if _HEX.search(body)})
    return _check("theme-colours", "1.4.3", "FAIL" if fixed else "PASS",
                  "Every colour comes from the theme, so the dark theme keeps its contrast" if not fixed
                  else f"Colours written outside the theme, unchanged in the dark theme: {', '.join(fixed)}", selectors=fixed)


def _template_checks(page: str, html: str) -> list[dict[str, Any]]:
    positive = re.findall(r"tabindex\D{0,4}([1-9]\d*)", page + html)
    labelled = 'el("label"' in page and "{ for: id }" in page and '<label class="actor">' in html
    required = "input.required = true" in page
    return [
        _check("keyboard-order", "2.4.3", "FAIL" if positive else "PASS",
               "Keyboard order follows the screen: fields in the screen's order, no positive tabindex" if not positive
               else "A positive tabindex changes the keyboard order"),
        _check("labelled-controls", "1.3.1, 4.1.2", "PASS" if labelled else "FAIL",
               "Every input and the actor picker has a label tied to it" if labelled else "A control is not tied to a label"),
        _check("required-in-code", "3.3.2, 1.4.1", "PASS" if required else "FAIL",
               "A required field is marked required for assistive technology, not only with *" if required
               else "A required field is marked only visually"),
    ]


def _repeated_labels(screens: Screens) -> list[str]:
    repeated = []
    for screen in screens.screens:
        labels = [(f.label or f.attribute).strip().lower() for f in screen.fields]
        repeated += [f"{screen.title}: {label}" for label in sorted({x for x in labels if labels.count(x) > 1})]
    return repeated


def _code_like_labels(screens: Screens, data: DataModel | None) -> list[str]:
    attributes = {a.name for a in data.entity(data.record).attributes} if data else set()
    return [f"{screen.title}: {f.attribute}" for screen in screens.screens for f in screen.fields
            if not f.label and f.attribute in attributes and _CODE_LIKE.search(f.attribute)]


def _alike_actions(screens: Screens, model: Workflow) -> list[str]:
    titles = {s.use_case: s.title.strip().lower() for s in screens.screens if s.use_case is not None}
    alike = []
    for state in model.states:
        shown = [titles.get(t.action, t.action.lower()) for t in model.transitions if t.from_state == state]
        alike += [f"{state}: {title}" for title in sorted({x for x in shown if shown.count(x) > 1})]
    return alike


def _design_checks(screens: Screens, model: Workflow, data: DataModel | None) -> list[dict[str, Any]]:
    repeated, alike, code_like = _repeated_labels(screens), _alike_actions(screens, model), _code_like_labels(screens, data)
    return [
        _check("distinct-labels", "1.3.1, 2.4.6", "FAIL" if repeated else "PASS",
               "No screen repeats a label" if not repeated else f"A screen repeats a label: {'; '.join(repeated)}", where=repeated),
        _check("actions-told-apart", "2.4.6", "FAIL" if alike else "PASS",
               "The actions offered together have different titles" if not alike
               else f"Actions offered together look alike: {'; '.join(alike)}", where=alike),
        _check("labels-read-as-words", "2.4.6", "WARN" if code_like else "PASS",
               "Every label reads as words" if not code_like
               else f"These fields show the attribute's name as the label; give them a label: {'; '.join(code_like)}", where=code_like),
    ]


def check_accessibility(screens: Screens, model: Workflow, data: DataModel | None, *, theme_css: str, page_js: str,
                        page_html: str) -> dict[str, Any]:
    """Each check with its WCAG success criteria and PASS, WARN (advice) or FAIL, the design's first."""
    checks = [*_design_checks(screens, model, data), *_contrast_checks(theme_css), _fixed_colours(theme_css),
              *_template_checks(page_js, page_html)]
    return {"standard": "WCAG 2.2 AA", "checks": checks,
            "passed": sum(c["status"] == "PASS" for c in checks), "failed": sum(c["status"] == "FAIL" for c in checks),
            "limits": "Checked without a browser: the page templates, their theme and the screens. It is not a full audit."}
