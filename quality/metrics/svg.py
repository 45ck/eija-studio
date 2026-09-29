"""Tiny dependency-free SVG chart primitives (static output, no scripts, no network).

Colours come from CSS custom properties defined by the page (`--series-1..3`, `--ink`, `--muted`,
`--grid`), so light and dark themes are one stylesheet. Every mark carries a `<title>` child, which
gives a native hover tooltip without JavaScript. Output is a pure function of the input numbers.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from html import escape

W = 640  # viewBox width; the page scales the SVG to its container


def esc(value: object) -> str:
    return escape(str(value), quote=True)


def num(x: float) -> str:
    """Stable short number formatting for coordinates."""
    return f"{x:.1f}".rstrip("0").rstrip(".") if x != int(x) else str(int(x))


def fmt(x: float | int | None, digits: int = 2) -> str:
    """Compact, locale-independent number formatting."""
    if x is None:
        return "n/a"
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, int):
        return f"{x:,}"
    if abs(x) >= 1000:
        return f"{x:,.0f}"
    s = f"{x:.{digits}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def sig(x: float | None) -> str:
    """Four significant digits, for durations spanning microseconds to seconds."""
    return "n/a" if x is None else f"{x:.4g}"


def nice_ticks(lo: float, hi: float, count: int = 5) -> list[float]:
    if hi <= lo:
        return [lo]
    raw = (hi - lo) / count
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    start = math.ceil(lo / step) * step
    ticks, t = [], start
    while t <= hi + step * 1e-9:
        ticks.append(round(t, 10))
        t += step
    return ticks


def linear(d0: float, d1: float, r0: float, r1: float) -> Callable[[float], float]:
    span = (d1 - d0) or 1.0
    return lambda v: r0 + (v - d0) / span * (r1 - r0)


def log10s(d0: float, d1: float, r0: float, r1: float) -> Callable[[float], float]:
    a, b = math.log10(d0), math.log10(d1)
    return lambda v: r0 + (math.log10(max(v, d0)) - a) / (b - a) * (r1 - r0)


def frame(height: int, body: str, label: str) -> str:
    return (f'<svg class="chart" viewBox="0 0 {W} {height}" role="img" aria-label="{esc(label)}" '
            f'preserveAspectRatio="xMidYMid meet">{body}</svg>')


def text(x: float, y: float, s: object, cls: str = "t", anchor: str = "start") -> str:
    return f'<text class="{cls}" x="{num(x)}" y="{num(y)}" text-anchor="{anchor}">{esc(s)}</text>'


def axes(x_scale, y_scale, xt: Sequence[float], yt: Sequence[float], box: tuple[float, float, float, float],
         xlabel: str, ylabel: str, xfmt=fmt, yfmt=fmt) -> str:
    left, top, right, bottom = box
    out = []
    for t in yt:
        y = y_scale(t)
        out.append(f'<line class="gl" x1="{num(left)}" x2="{num(right)}" y1="{num(y)}" y2="{num(y)}"/>')
        out.append(text(left - 6, y + 4, yfmt(t), "tick", "end"))
    for t in xt:
        x = x_scale(t)
        out.append(f'<line class="gl" x1="{num(x)}" x2="{num(x)}" y1="{num(top)}" y2="{num(bottom)}"/>')
        out.append(text(x, bottom + 16, xfmt(t), "tick", "middle"))
    out.append(f'<line class="axis" x1="{num(left)}" x2="{num(right)}" y1="{num(bottom)}" y2="{num(bottom)}"/>')
    out.append(f'<line class="axis" x1="{num(left)}" x2="{num(left)}" y1="{num(top)}" y2="{num(bottom)}"/>')
    out.append(text((left + right) / 2, bottom + 34, xlabel, "axl", "middle"))
    out.append(f'<text class="axl" transform="rotate(-90 12 {num((top + bottom) / 2)})" x="12" '
               f'y="{num((top + bottom) / 2)}" text-anchor="middle">{esc(ylabel)}</text>')
    return "".join(out)


def spread_labels(items: list[tuple[float, str, str]], gap: float = 13.0) -> list[tuple[float, str, str]]:
    """Nudge label y positions apart (top to bottom) so direct labels never overlap."""
    placed: list[tuple[float, str, str]] = []
    last = -1e9
    for wanted, label, tip in sorted(items, key=lambda i: (i[0], i[1])):
        y = max(wanted, last + gap)
        placed.append((y, label, tip))
        last = y
    return placed


def hbars(rows: Sequence[tuple[str, float, str, str]], vmax: float, label: str, unit: str = "",
          width: int = W, label_w: int = 190) -> str:
    """Horizontal bars. rows = (label, value, css class, tooltip). Value printed at the bar end."""
    bar_h, gap, top = 16, 8, 6
    x = linear(0, vmax or 1, label_w, width - 60)
    parts = []
    for i, (name, value, cls, tip) in enumerate(rows):
        y = top + i * (bar_h + gap)
        w = max(x(value) - label_w, 1.5 if value else 0)
        parts.append(text(label_w - 8, y + 12, name, "t", "end"))
        parts.append(f'<rect class="{cls}" x="{label_w}" y="{y}" width="{num(w)}" height="{bar_h}" rx="3"><title>{esc(tip)}</title></rect>')
        parts.append(text(label_w + w + 6, y + 12, f"{fmt(value)}{unit}", "val"))
    return frame(top * 2 + len(rows) * (bar_h + gap), "".join(parts), label)
