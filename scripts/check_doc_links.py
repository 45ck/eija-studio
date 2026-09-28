"""Check that relative links and heading anchors in the README, community files and docs/ resolve.

What this establishes: every relative Markdown/HTML link in the checked files points at a file or
directory that exists in this checkout, and every `#anchor` matches a heading in the target file
(GitHub-style slugs). External http(s)/mailto links are NOT fetched: this is an offline check.

What this does NOT establish: that external URLs are alive, that link text is accurate, or that the
target says what the sentence claims. Targets another lane will create are in PENDING: they are
reported as pending (never as ok) and do not fail the gate; once the file exists they are checked
like any other link.

    python scripts/check_doc_links.py            # exit 1 on a broken link
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# target (repo-relative, posix) -> the lane that creates it. Remove an entry once it lands.
PENDING: dict[str, str] = {
    "docs/agents/quickstart.md": "agents lane (open PR #8)",
    "docs/engineering/LANE-MAP.md": "merge-hygiene (open PR #9)",
    "docs/engineering/PRODUCT-THESIS.md": "merge-hygiene (open PR #9)",
}

FILES = ["README.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "CHANGELOG.md", "AGENTS.md",
         ".github/PULL_REQUEST_TEMPLATE.md"]
FENCE = re.compile(r"^(```|~~~).*?^\1[ \t]*$", re.S | re.M)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)  # a TODO comment may mention a future target
INLINE_CODE = re.compile(r"`[^`\n]*`")
MD_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_ATTR = re.compile(r"""\b(?:src|href)\s*=\s*["']([^"']+)["']""")
REF_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?\s*$", re.M)
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", re.M)


def read(path: Path) -> str:
    """UTF-8 text with LF endings, so a CRLF checkout (autocrlf) parses the same as an LF one."""
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def slug(text: str) -> str:
    """GitHub-style heading slug (close enough for ASCII headings; documented limit)."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("`", "").strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def strip_code(text: str) -> str:
    return INLINE_CODE.sub("", HTML_COMMENT.sub("", FENCE.sub("", text)))


def anchors(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    out: set[str] = set()
    for m in HEADING.finditer(FENCE.sub("", read(path))):
        base = slug(m.group(1))
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.add(base if n == 0 else f"{base}-{n}")
    return out


def targets(text: str) -> list[str]:
    body = strip_code(text)
    found = MD_LINK.findall(body) + HTML_ATTR.findall(body) + REF_DEF.findall(body)
    return [t for t in found if not re.match(r"^[a-z][a-z0-9+.-]*:", t, re.I)]  # http:, mailto:, data:


def checked_files() -> list[Path]:
    files = [ROOT / f for f in FILES if (ROOT / f).is_file()]
    files += sorted((ROOT / "docs").rglob("*.md"))
    files += sorted((ROOT / ".github").rglob("*.md"))
    files += sorted((ROOT / ".github").rglob("*.yml"))
    return sorted(set(files))


def check(path: Path) -> tuple[list[str], list[str], int]:
    """Return (broken, pending, ok_count) for one file."""
    broken: list[str] = []
    pending: list[str] = []
    ok = 0
    rel = path.relative_to(ROOT).as_posix()
    for raw in targets(read(path)):
        target, _, fragment = raw.partition("#")
        dest = (path.parent / target).resolve() if target else path
        try:
            key = dest.relative_to(ROOT).as_posix()
        except ValueError:
            broken.append(f"{rel}: {raw} escapes the repository")
            continue
        if not dest.exists():
            if key in PENDING:
                pending.append(f"{rel}: {raw} (pending: {PENDING[key]})")
            else:
                broken.append(f"{rel}: {raw} does not exist")
            continue
        if fragment and dest.suffix == ".md" and fragment.lower() not in anchors(dest):
            broken.append(f"{rel}: {raw} has no heading '#{fragment}' in {key}")
            continue
        ok += 1
    return broken, pending, ok


def unlisted_adrs() -> list[str]:
    """ADR files the ADR index does not link. Reported, and a failure: the index is the source of truth."""
    index = read(ROOT / "docs/adr/README.md")
    return [p.name for p in sorted((ROOT / "docs/adr").glob("[0-9][0-9][0-9][0-9]-*.md")) if p.name not in index]


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args(argv)
    broken: list[str] = []
    pending: list[str] = []
    ok = 0
    files = checked_files()
    for f in files:
        b, p, n = check(f)
        broken += b
        pending += p
        ok += n
    for adr in unlisted_adrs():
        broken.append(f"docs/adr/README.md: ADR file {adr} is not linked from the index")
    for line in pending:
        print("PENDING", line)
    for line in broken:
        print("BROKEN ", line)
    print(f"{'FAIL' if broken else 'PASS'} {len(files)} files, {ok} links ok, {len(pending)} pending, {len(broken)} broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
