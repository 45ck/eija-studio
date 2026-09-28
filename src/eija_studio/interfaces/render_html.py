"""Self-contained HTML for `eija render --format html`: generated Mermaid text plus the vendored renderer.

The page embeds the pinned mermaid.min.js (resources/web/vendor) inline, so it needs no network and no
CDN. It carries no timestamp: equal diagrams give equal bytes. The Mermaid source stays visible under
each figure, because the text, not the picture, is what the drift check compares.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[1] / "resources" / "web" / "vendor"
CSP = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"
STYLE = """
body{margin:0;padding:24px;font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;background:#fff;color:#1f2328}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:32px 0 6px}p{margin:4px 0;color:#57606a;font-size:13px}
figure{margin:12px 0;padding:12px;border:1px solid #d0d7de;border-radius:8px;overflow-x:auto}
pre.mermaid{margin:0;background:transparent}details{margin-top:8px}summary{cursor:pointer;font-size:12px;color:#0969da}
pre.src{font:12px/1.5 ui-monospace,Consolas,monospace;background:#f6f8fa;padding:12px;border-radius:6px;overflow:auto}
"""
BOOT = """
mermaid.initialize({startOnLoad:false,securityLevel:"strict",htmlLabels:true,theme:"default"});
mermaid.run({querySelector:"pre.mermaid"}).catch(function(e){document.body.setAttribute("data-render-error",String(e&&e.message||e));});
"""


def mermaid_js() -> str:
    text = (VENDOR / "mermaid.min.js").read_text(encoding="utf-8")
    if "</script" in text.lower():  # would end the inline script early; refuse rather than corrupt the page
        raise ValueError("vendored mermaid contains a script terminator; re-vendor or change the embedding")
    return text


def html_page(title: str, panels: list[tuple[str, str, str]], *, renderer: str | None = None) -> str:
    """`panels` is (heading, note, mermaid text). Returns a complete HTML document."""
    body = "".join(
        f"<section><h2>{escape(heading)}</h2><p>{escape(note)}</p><figure><pre class=\"mermaid\">{escape(text)}</pre>"
        f"<details><summary>Generated Mermaid source</summary><pre class=\"src\">{escape(text)}</pre></details></figure></section>"
        for heading, note, text in panels)
    script = renderer if renderer is not None else mermaid_js()
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta http-equiv="Content-Security-Policy" content="{CSP}"><title>{escape(title)}</title><style>{STYLE}</style></head>\n'
            f"<body><h1>{escape(title)}</h1><p>Generated from the executable model by <code>eija render</code>. Do not edit; regenerate.</p>\n"
            f"{body}\n<script>{script}</script>\n<script>{BOOT}</script></body></html>\n")
