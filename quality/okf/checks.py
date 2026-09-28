"""The OKF gate: five independent checks, each returning findings.

conformance  OKF v0.2 section 11 plus the optional families of sections 5-9 (stricter where noted)
links        every internal markdown link resolves (the spec tolerates broken links; we do not, see ADR-0045)
codelinks    every ``repo://`` resource resolves and every recorded hash still matches, else STALE
coverage     every public domain/application symbol, ADR, acceptance row, term, gate and lane has a page
drift        regenerating the bundle is a no-op

What a pass establishes: the wiki is well-formed, navigable, and was baselined against the code as it
is now. It does NOT establish that any page's prose is correct, or that the code is.
"""
from __future__ import annotations

import difflib
import posixpath
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from markdown_it import MarkdownIt

from . import codelink as cl
from .build import build, existing_pages
from .extract import collect
from .pages import OKF_VERSION, PLACEHOLDER, Repo, split_page

CHECKS = ("conformance", "links", "codelinks", "coverage", "drift")
STATUSES = ("draft", "stable", "deprecated")
_ACTOR = re.compile(r"^(?:(?:human|process):\S+|[^\s/:]+/\S+)$")
_REPO_MENTION = re.compile(r"repo://[A-Za-z0-9_./\-]+(?:#[A-Za-z0-9_.\-]+)?")
_FOOTNOTE_REF = re.compile(r"\[\^([\w-]+)\](?!:)")
_SHA = re.compile(r"^[0-9a-f]{64}$")
_ENTRY = re.compile(r"^[*-] \[[^\]]+\]\([^)\s]+\)")


@dataclass(frozen=True)
class Finding:
    check: str
    code: str
    path: str
    message: str

    def line(self) -> str:
        return f"[{self.code}] {self.path}: {self.message}"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.findings


# ---- helpers ------------------------------------------------------------------------------------

def _is_reserved(path: str) -> bool:
    return posixpath.basename(path) in ("index.md", "log.md")


def _iso(value: Any) -> bool:
    """ISO 8601 datetime with an explicit UTC offset (SPEC section 5)."""
    if isinstance(value, datetime):
        return value.tzinfo is not None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None and "T" in value
        except ValueError:
            return False
    return False


def _concepts(pages: dict[str, str]) -> dict[str, tuple[dict[str, Any], str]]:
    out = {}
    for path, text in pages.items():
        if not _is_reserved(path):
            try:
                out[path] = split_page(text)
            except ValueError:
                pass
    return out


# ---- conformance --------------------------------------------------------------------------------

def check_conformance(pages: dict[str, str]) -> list[Finding]:
    found: list[Finding] = []

    def add(code: str, path: str, message: str) -> None:
        found.append(Finding("conformance", code, path, message))

    for required in ("index.md", "log.md"):
        if required not in pages:
            add("MISSING_RESERVED", required, f"bundle root has no {required} (the spec makes it optional; we require it)")
    for path, text in sorted(pages.items()):
        name = posixpath.basename(path)
        if name == "index.md":
            _index(path, text, add)
        elif name == "log.md":
            _log(path, text, add)
        else:
            _concept(path, text, add)
    return found


def _index(path: str, text: str, add) -> None:
    body = text
    if text.startswith("---"):
        try:
            meta, body = split_page(text)
        except ValueError as exc:
            add("INDEX_FRONTMATTER", path, str(exc))
            return
        if path != "index.md":
            add("INDEX_FRONTMATTER", path, "only the bundle-root index.md may carry frontmatter (okf_version)")
        elif set(meta) - {"okf_version"}:
            add("INDEX_FRONTMATTER", path, f"root index frontmatter may only carry okf_version, found {sorted(set(meta) - {'okf_version'})}")
        elif meta.get("okf_version") != OKF_VERSION:
            add("OKF_VERSION", path, f'okf_version must be "{OKF_VERSION}", found {meta.get("okf_version")!r}')
    elif path == "index.md":
        add("OKF_VERSION", path, f'root index.md should declare okf_version: "{OKF_VERSION}"')
    if not re.search(r"^# \S", body, re.MULTILINE):
        add("INDEX_STRUCTURE", path, "index has no '# Heading' section")
    if not any(_ENTRY.match(line) for line in body.split("\n")):
        add("INDEX_STRUCTURE", path, "index has no '* [Title](url) - description' entries")
    for line in body.split("\n"):
        if line.startswith(("* ", "- ")) and not _ENTRY.match(line):
            add("INDEX_STRUCTURE", path, f"list item is not a '* [Title](url)' entry: {line[:80]!r}")


def _log(path: str, text: str, add) -> None:
    if not re.search(r"^# \S", text, re.MULTILINE):
        add("LOG_STRUCTURE", path, "log has no '# Title' heading")
    dates = re.findall(r"^## (.+)$", text, re.MULTILINE)
    if not dates:
        add("LOG_STRUCTURE", path, "log has no '## YYYY-MM-DD' entries")
    parsed: list[date] = []
    for heading in dates:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", heading):
                raise ValueError
            parsed.append(date.fromisoformat(heading))
        except ValueError:
            add("LOG_DATE", path, f"date heading {heading!r} is not ISO 8601 YYYY-MM-DD")
    if parsed != sorted(parsed, reverse=True):
        add("LOG_ORDER", path, "log entries must be newest first")
    for block in re.split(r"^## .+$", text, flags=re.MULTILINE)[1:]:
        if not re.search(r"^[*-] ", block, re.MULTILINE):
            add("LOG_STRUCTURE", path, "a dated log entry has no bullet items")


def _concept(path: str, text: str, add) -> None:
    try:
        meta, body = split_page(text)
    except ValueError as exc:
        add("FRONTMATTER", path, str(exc))
        return
    kind = meta.get("type")
    if not isinstance(kind, str) or not kind.strip():
        add("TYPE", path, "frontmatter needs a non-empty string `type`")
    for key in ("title", "description", "resource"):
        if key in meta and not isinstance(meta[key], str):
            add("FIELD_TYPE", path, f"`{key}` must be a string")
    tags = meta.get("tags")
    if tags is not None and not (isinstance(tags, list) and all(isinstance(t, str) for t in tags)):
        add("FIELD_TYPE", path, "`tags` must be a list of strings")
    if "status" in meta and meta["status"] not in STATUSES:
        add("STATUS", path, f"`status` must be one of {STATUSES}, found {meta['status']!r}")
    if "stale_after" in meta and not _iso(meta["stale_after"]):
        add("TIMESTAMP", path, "`stale_after` must be ISO 8601 with an explicit UTC offset")
    generated = meta.get("generated")
    if generated is not None:
        if not isinstance(generated, dict) or not isinstance(generated.get("by"), str) or not _ACTOR.match(generated["by"]):
            add("ACTOR", path, "`generated` needs `by` in actor form (producer/version, human:id or process:id)")
        elif "at" in generated and not _iso(generated["at"]):
            add("TIMESTAMP", path, "`generated.at` must be ISO 8601 with an explicit UTC offset")
    if "verified" in meta:
        entries = meta["verified"] if isinstance(meta["verified"], list) else [meta["verified"]]
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("by"), str) or not _ACTOR.match(entry["by"]) or not _iso(entry.get("at")):
                add("VERIFIED", path, "each `verified` entry needs `by` (actor form) and `at` (ISO 8601 with offset)")
    ids: list[str] = []
    sources = meta.get("sources")
    if sources is not None:
        if not isinstance(sources, list):
            add("SOURCES", path, "`sources` must be a list")
        else:
            for entry in sources:
                if not isinstance(entry, dict) or not isinstance(entry.get("resource"), str) or not entry["resource"]:
                    add("SOURCES", path, "every `sources` entry needs a non-empty `resource`")
                    continue
                if "id" in entry:
                    ids.append(str(entry["id"]))
    if len(ids) != len(set(ids)):
        add("SOURCES", path, "`sources[].id` values must be unique")
    for label in sorted(set(_FOOTNOTE_REF.findall(body))):
        if label not in ids:
            add("FOOTNOTE", path, f"footnote [^{label}] has no matching `sources[].id`")


# ---- links --------------------------------------------------------------------------------------

_MD = MarkdownIt("zero").enable(["fence", "code", "backticks", "link", "escape", "list"])   # just what link extraction needs


def _hrefs(body: str) -> list[str]:
    tokens = _MD.parse(body)
    out: list[str] = []

    def walk(items) -> None:
        for token in items:
            if token.type == "link_open":
                out.append(token.attrGet("href") or "")
            if token.children:
                walk(token.children)

    walk(tokens)
    return out


def check_links(repo: Repo, pages: dict[str, str]) -> list[Finding]:
    found: list[Finding] = []
    for path, text in sorted(pages.items()):
        try:
            meta, body = split_page(text)
        except ValueError:
            meta, body = {}, text
        base = posixpath.dirname(path)
        for href in _hrefs(body):
            target = href.split("#", 1)[0].split("?", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                continue   # anchors, http(s), mailto, repo:// (checked by codelinks)
            resolved = posixpath.normpath(target.lstrip("/") if target.startswith("/") else posixpath.join(base, target))
            if resolved.startswith(".."):
                outside = (repo.bundle / base / target).resolve()
                if not outside.exists():
                    found.append(Finding("links", "BROKEN_LINK", path, f"link {href!r} leaves the bundle and the target does not exist"))
                continue
            if resolved in pages or resolved + "/index.md" in pages:
                continue
            found.append(Finding("links", "BROKEN_LINK", path, f"link {href!r} does not resolve to a page in the bundle"))
        for mention in sorted(set(_REPO_MENTION.findall(body))) if meta.get("status") != "deprecated" else []:   # history may cite what is gone
            mention = mention.rstrip(".,")
            try:
                ref = cl.parse_uri(mention)
            except ValueError:
                found.append(Finding("links", "BROKEN_REPO_URI", path, f"{mention!r} is not a valid repo:// URI"))
                continue
            if not cl.resolves(repo.root, ref):
                found.append(Finding("links", "BROKEN_REPO_URI", path, f"{mention!r} does not resolve in the repository"))
    return found


# ---- code links ---------------------------------------------------------------------------------

def check_codelinks(repo: Repo, pages: dict[str, str]) -> tuple[list[Finding], list[str]]:
    found: list[Finding] = []
    stale: list[str] = []
    for path, (meta, _body) in sorted(_concepts(pages).items()):
        deprecated = meta.get("status") == "deprecated"
        resource = meta.get("resource")
        if isinstance(resource, str) and resource.startswith(cl.SCHEME) and not deprecated:
            try:
                ok = cl.resolves(repo.root, cl.parse_uri(resource))
            except ValueError as exc:
                found.append(Finding("codelinks", "BROKEN_RESOURCE", path, str(exc)))
                continue
            if not ok:
                found.append(Finding("codelinks", "BROKEN_RESOURCE", path, f"`resource` {resource} does not resolve to an existing file or symbol"))
        for entry in meta.get("sources") or []:
            uri = entry.get("resource") if isinstance(entry, dict) else None
            if not isinstance(uri, str) or not uri.startswith(cl.SCHEME) or deprecated:
                continue
            recorded, method = entry.get("sha256"), entry.get("hash_method")
            if method not in cl.METHODS or not isinstance(recorded, str) or not _SHA.match(recorded):
                found.append(Finding("codelinks", "MISSING_HASH", path, f"source {uri} needs `hash_method` (one of {cl.METHODS}) and a 64-hex `sha256`"))
                continue
            try:
                current = cl.digest(repo.root, cl.parse_uri(uri), method)
            except (cl.Unresolved, ValueError) as exc:
                found.append(Finding("codelinks", "BROKEN_RESOURCE", path, f"source {uri}: {exc}"))
                continue
            if current != recorded:
                stale.append(path)
                found.append(Finding("codelinks", "STALE", path, f"source {uri} changed since this page was baselined "
                                     f"({method}: {recorded[:10]} -> {current[:10]}); review the page, then run `python -m quality.okf sync`"))
    return found, sorted(set(stale))


# ---- coverage -----------------------------------------------------------------------------------

def check_coverage(repo: Repo, pages: dict[str, str]) -> list[Finding]:
    found: list[Finding] = []
    concepts = _concepts(pages)
    for spec in collect(repo):
        if spec.path not in pages:
            found.append(Finding("coverage", "MISSING_PAGE", spec.path, f"no concept page for {spec.resource} ({spec.type})"))
        elif spec.path in concepts and concepts[spec.path][0].get("resource") != spec.resource:
            found.append(Finding("coverage", "WRONG_RESOURCE", spec.path,
                                 f"page `resource` is {concepts[spec.path][0].get('resource')!r}, expected {spec.resource!r}"))
    return found


# ---- drift --------------------------------------------------------------------------------------

def check_drift(repo: Repo, skip: set[str]) -> list[Finding]:
    found: list[Finding] = []
    disk = existing_pages(repo)
    expected = build(repo).files
    for path in sorted(set(expected) | set(disk)):
        if path in skip:
            continue
        if path not in disk:
            found.append(Finding("drift", "DRIFT", path, "missing on disk; run `python -m quality.okf sync`"))
        elif path not in expected:
            found.append(Finding("drift", "DRIFT", path, "on disk but not produced by the generator"))
        elif disk[path] != expected[path]:
            diff = [d for d in difflib.unified_diff(disk[path].split("\n"), expected[path].split("\n"), "disk", "regenerated", n=0, lineterm="")
                    if not d.startswith(("---", "+++", "@@"))][:4]
            found.append(Finding("drift", "DRIFT", path, "regeneration would change this page: " + " | ".join(d[:100] for d in diff)))
    return found


# ---- orchestration ------------------------------------------------------------------------------

def trust_tier(meta: dict[str, Any]) -> str:
    """SPEC section 5.3, derived only from `verified`."""
    if "verified" not in meta:
        return "unverified"
    entries = meta["verified"] if isinstance(meta["verified"], list) else [meta["verified"]]
    return "human-reviewed" if any(isinstance(e, dict) and str(e.get("by", "")).startswith("human:") for e in entries) else "machine-confirmed"


def run_checks(repo: Repo, only: tuple[str, ...] = CHECKS) -> Report:
    pages = existing_pages(repo)
    report = Report()
    if not repo.bundle.is_dir():
        report.findings.append(Finding("conformance", "MISSING_BUNDLE", repo.bundle_name, "bundle directory does not exist; run `python -m quality.okf sync`"))
        return report
    if "conformance" in only:
        report.findings += check_conformance(pages)
    if "links" in only:
        report.findings += check_links(repo, pages)
    if "codelinks" in only:
        found, report.stale = check_codelinks(repo, pages)
        report.findings += found
    if "coverage" in only:
        report.findings += check_coverage(repo, pages)
    if "drift" in only:
        report.findings += check_drift(repo, set(report.stale))
    concepts = _concepts(pages)
    tiers: dict[str, int] = {}
    curated = 0
    for _path, (meta, body) in concepts.items():
        tiers[trust_tier(meta)] = tiers.get(trust_tier(meta), 0) + 1
        notes = re.search(r"^## Notes\n\n(.*?)(?=\n<!-- okf|\Z)", body, re.DOTALL | re.MULTILINE)
        curated += bool(notes and notes[1].strip() and notes[1].strip() != PLACEHOLDER)
    report.stats = {"pages": len(concepts), "trust_tiers": dict(sorted(tiers.items())), "pages_with_curated_notes": curated,
                    "stale_pages": len(report.stale)}
    return report


def format_report(report: Report) -> str:
    lines = [f.line() for f in report.findings]
    if report.stale:
        lines += ["", f"Pages requiring review ({len(report.stale)}): the code they describe changed."] + [f"  - okf/{p}" for p in report.stale]
    lines += ["", "okf: " + ("PASS" if report.ok else f"FAIL ({len(report.findings)} findings)") + f"  {report.stats}"]
    return "\n".join(lines)

