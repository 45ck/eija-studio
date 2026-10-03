"""The OKF gate: five independent checks, each returning findings.

conformance  OKF v0.2 section 11 plus the optional families of sections 5-9 (stricter where noted)
links        every internal markdown link resolves (the spec tolerates broken links; we do not, see ADR-0045)
codelinks    every ``repo://`` resource resolves and every recorded hash still matches, else STALE; curated Notes
             not re-read since their source changed are NOTES_STALE (``sync`` cannot clear that, ``review`` can)
coverage     every public domain/application symbol, ADR, acceptance row, term, gate and lane has a page
drift        regenerating the bundle is a no-op

What a pass establishes: the wiki is well-formed, navigable, and was baselined against the code as it
is now. It does NOT establish that any page's prose is correct, or that the code is.
"""
from __future__ import annotations

import contextlib
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
from .pages import OKF_VERSION, Repo, human_sha256, is_curated, sources_sha256, split_page

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


def valid_actor(value: Any) -> bool:
    return isinstance(value, str) and bool(_ACTOR.match(value))


def valid_iso(value: Any) -> bool:
    return _iso(value)


def _concepts(pages: dict[str, str]) -> dict[str, tuple[dict[str, Any], str]]:
    out = {}
    for path, text in pages.items():
        if not _is_reserved(path):
            with contextlib.suppress(ValueError):
                out[path] = split_page(text)
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


def _index_frontmatter(path: str, text: str, add) -> str | None:
    """Check the frontmatter rules of an index page; return the body, or None when the page cannot be read further."""
    if not text.startswith("---"):
        if path == "index.md":
            add("OKF_VERSION", path, f'root index.md should declare okf_version: "{OKF_VERSION}"')
        return text
    try:
        meta, body = split_page(text)
    except ValueError as exc:
        add("INDEX_FRONTMATTER", path, str(exc))
        return None
    if path != "index.md":
        add("INDEX_FRONTMATTER", path, "only the bundle-root index.md may carry frontmatter (okf_version)")
    elif set(meta) - {"okf_version"}:
        add("INDEX_FRONTMATTER", path, f"root index frontmatter may only carry okf_version, found {sorted(set(meta) - {'okf_version'})}")
    elif meta.get("okf_version") != OKF_VERSION:
        add("OKF_VERSION", path, f'okf_version must be "{OKF_VERSION}", found {meta.get("okf_version")!r}')
    return body


def _index(path: str, text: str, add) -> None:
    body = _index_frontmatter(path, text, add)
    if body is None:
        return
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
    _concept_fields(meta, path, add)
    _concept_lifecycle(meta, path, add)
    _concept_generated(meta, path, add)
    _concept_verified(meta, path, add)
    ids = _concept_sources(meta, path, add)
    if len(ids) != len(set(ids)):
        add("SOURCES", path, "`sources[].id` values must be unique")
    for label in sorted(set(_FOOTNOTE_REF.findall(body))):
        if label not in ids:
            add("FOOTNOTE", path, f"footnote [^{label}] has no matching `sources[].id`")


def _concept_fields(meta: dict[str, Any], path: str, add) -> None:
    kind = meta.get("type")
    if not isinstance(kind, str) or not kind.strip():
        add("TYPE", path, "frontmatter needs a non-empty string `type`")
    for key in ("title", "description", "resource"):
        if key in meta and not isinstance(meta[key], str):
            add("FIELD_TYPE", path, f"`{key}` must be a string")
    tags = meta.get("tags")
    if tags is not None and not (isinstance(tags, list) and all(isinstance(t, str) for t in tags)):
        add("FIELD_TYPE", path, "`tags` must be a list of strings")


def _concept_lifecycle(meta: dict[str, Any], path: str, add) -> None:
    if "status" in meta and meta["status"] not in STATUSES:
        add("STATUS", path, f"`status` must be one of {STATUSES}, found {meta['status']!r}")
    if "stale_after" in meta and not _iso(meta["stale_after"]):
        add("TIMESTAMP", path, "`stale_after` must be ISO 8601 with an explicit UTC offset")


def _concept_generated(meta: dict[str, Any], path: str, add) -> None:
    generated = meta.get("generated")
    if generated is None:
        return
    if not isinstance(generated, dict) or not isinstance(generated.get("by"), str) or not _ACTOR.match(generated["by"]):
        add("ACTOR", path, "`generated` needs `by` in actor form (producer/version, human:id or process:id)")
    elif "at" in generated and not _iso(generated["at"]):
        add("TIMESTAMP", path, "`generated.at` must be ISO 8601 with an explicit UTC offset")


def _verified_problem(entry: Any) -> str | None:
    """Why one `verified` entry is malformed, or None."""
    if not isinstance(entry, dict) or not valid_actor(entry.get("by")) or not _iso(entry.get("at")):
        return "each `verified` entry needs `by` (actor form) and `at` (ISO 8601 with offset)"
    if not all(isinstance(entry.get(k), str) and _SHA.match(entry[k]) for k in ("notes_sha256", "sources_sha256")):
        return ("each `verified` entry must be bound to the reviewed content: `notes_sha256` and `sources_sha256` "
                "(64 hex); use `python -m quality.okf review`")
    return None


def _concept_verified(meta: dict[str, Any], path: str, add) -> None:
    if "verified" not in meta:
        return
    entries = meta["verified"] if isinstance(meta["verified"], list) else [meta["verified"]]
    for entry in entries:
        problem = _verified_problem(entry)
        if problem:
            add("VERIFIED", path, problem)


def _concept_sources(meta: dict[str, Any], path: str, add) -> list[str]:
    """Check `sources`; return the declared footnote ids."""
    sources = meta.get("sources")
    if sources is None:
        return []
    if not isinstance(sources, list):
        add("SOURCES", path, "`sources` must be a list")
        return []
    ids: list[str] = []
    for entry in sources:
        if not isinstance(entry, dict) or not isinstance(entry.get("resource"), str) or not entry["resource"]:
            add("SOURCES", path, "every `sources` entry needs a non-empty `resource`")
        elif "id" in entry:
            ids.append(str(entry["id"]))
    return ids


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


def _broken_link(repo: Repo, pages: dict[str, str], path: str, href: str) -> Finding | None:
    """The finding for one markdown link of page `path`, or None when it resolves."""
    base = posixpath.dirname(path)
    target = href.split("#", 1)[0].split("?", 1)[0]
    if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
        return None   # anchors, http(s), mailto, repo:// (checked by codelinks)
    resolved = posixpath.normpath(target.lstrip("/") if target.startswith("/") else posixpath.join(base, target))
    if resolved.startswith(".."):
        if (repo.bundle / base / target).resolve().exists():
            return None
        return Finding("links", "BROKEN_LINK", path, f"link {href!r} leaves the bundle and the target does not exist")
    if resolved in pages or resolved + "/index.md" in pages:
        return None
    return Finding("links", "BROKEN_LINK", path, f"link {href!r} does not resolve to a page in the bundle")


def _broken_mention(repo: Repo, path: str, raw_mention: str) -> Finding | None:
    """The finding for one `repo://` mention in a page body, or None when it resolves."""
    mention = raw_mention.rstrip(".,")
    try:
        ref = cl.parse_uri(mention)
    except ValueError:
        return Finding("links", "BROKEN_REPO_URI", path, f"{mention!r} is not a valid repo:// URI")
    if not cl.resolves(repo.root, ref):
        return Finding("links", "BROKEN_REPO_URI", path, f"{mention!r} does not resolve in the repository")
    return None


def check_links(repo: Repo, pages: dict[str, str]) -> list[Finding]:
    found: list[Finding] = []
    for path, text in sorted(pages.items()):
        try:
            meta, body = split_page(text)
        except ValueError:
            meta, body = {}, text
        results = [_broken_link(repo, pages, path, href) for href in _hrefs(body)]
        if meta.get("status") != "deprecated":   # history may cite what is gone
            results += [_broken_mention(repo, path, m) for m in sorted(set(_REPO_MENTION.findall(body)))]
        found += [r for r in results if r is not None]
    return found


# ---- code links ---------------------------------------------------------------------------------

def current_sources_sha(repo: Repo, meta: dict[str, Any]) -> str | None:
    """Digest of the page's sources as they are NOW (recomputed from the code), or None if any cannot be resolved."""
    sources = meta.get("sources")
    if not isinstance(sources, list):
        return None
    now = []
    for entry in sources:
        if not isinstance(entry, dict) or not isinstance(entry.get("resource"), str):
            return None
        if entry["resource"].startswith(cl.SCHEME):
            try:
                sha = cl.digest(repo.root, cl.parse_uri(entry["resource"]), str(entry.get("hash_method")))
            except (cl.Unresolved, ValueError):
                return None
            now.append({**entry, "sha256": sha})
        else:
            now.append(entry)
    return sources_sha256(now)


def _check_resource(repo: Repo, path: str, meta: dict[str, Any], found: list[Finding]) -> bool:
    """Check the page's own `resource`. False when the URI is malformed: the rest of that page is then not checked."""
    resource = meta.get("resource")
    if not isinstance(resource, str) or not resource.startswith(cl.SCHEME) or meta.get("status") == "deprecated":
        return True
    try:
        ok = cl.resolves(repo.root, cl.parse_uri(resource))
    except ValueError as exc:
        found.append(Finding("codelinks", "BROKEN_RESOURCE", path, str(exc)))
        return False
    if not ok:
        found.append(Finding("codelinks", "BROKEN_RESOURCE", path, f"`resource` {resource} does not resolve to an existing file or symbol"))
    return True


def _check_source(repo: Repo, path: str, entry: Any, found: list[Finding]) -> bool:
    """Check one `repo://` source hash. True when the source changed since the page was baselined."""
    uri = entry.get("resource") if isinstance(entry, dict) else None
    if not isinstance(uri, str) or not uri.startswith(cl.SCHEME):
        return False
    recorded, method = entry.get("sha256"), entry.get("hash_method")
    if method not in cl.METHODS or not isinstance(recorded, str) or not _SHA.match(recorded):
        found.append(Finding("codelinks", "MISSING_HASH", path, f"source {uri} needs `hash_method` (one of {cl.METHODS}) and a 64-hex `sha256`"))
        return False
    try:
        current = cl.digest(repo.root, cl.parse_uri(uri), method)
    except (cl.Unresolved, ValueError) as exc:
        found.append(Finding("codelinks", "BROKEN_RESOURCE", path, f"source {uri}: {exc}"))
        return False
    if current == recorded:
        return False
    found.append(Finding("codelinks", "STALE", path, f"source {uri} changed since this page was baselined "
                         f"({method}: {recorded[:10]} -> {current[:10]}); run `python -m quality.okf sync`, re-read the page's "
                         "Notes, then `python -m quality.okf review`"))
    return True


def _notes_stale(repo: Repo, path: str, meta: dict[str, Any]) -> Finding | None:
    current_all = current_sources_sha(repo, meta)
    if current_all is None or meta.get("notes_baseline") == current_all:
        return None
    return Finding("codelinks", "NOTES_STALE", path, "hand-written Notes were last aligned to an older source state (or "
                   "have no recorded baseline); re-read them against the current source, edit if needed, then run "
                   "`python -m quality.okf review <page> --by <actor> --at <time>`. `sync` does not clear this")


def _check_page_codelinks(repo: Repo, path: str, meta: dict[str, Any], body: str) -> tuple[list[Finding], bool]:
    """Code-link findings of one page, and whether any of its sources is stale."""
    found: list[Finding] = []
    if not _check_resource(repo, path, meta, found):
        return found, False
    if meta.get("status") == "deprecated":   # history may cite what is gone: neither its sources nor its Notes are gated
        return found, False
    page_stale = False
    for entry in meta.get("sources") or []:
        page_stale = _check_source(repo, path, entry, found) or page_stale
    if not page_stale and is_curated(body) and isinstance(meta.get("sources"), list):
        notes = _notes_stale(repo, path, meta)
        if notes is not None:
            found.append(notes)
    return found, page_stale


def check_codelinks(repo: Repo, pages: dict[str, str]) -> tuple[list[Finding], list[str]]:
    found: list[Finding] = []
    stale: list[str] = []
    for path, (meta, body) in sorted(_concepts(pages).items()):
        page_found, page_stale = _check_page_codelinks(repo, path, meta, body)
        found += page_found
        if page_stale:
            stale.append(path)
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

def _bound_entries(entries: list[Any], notes_sha: str, current_sources: str | None) -> list[dict[str, Any]]:
    """The `verified` entries whose recorded prose and source hashes equal the current ones."""
    if current_sources is None:
        return []
    return [e for e in entries if isinstance(e, dict) and e.get("notes_sha256") == notes_sha
            and e.get("sources_sha256") == current_sources]


def trust_tier(meta: dict[str, Any], body: str = "", current_sources: str | None = None) -> str:
    """SPEC section 5.3, derived only from `verified` entries that are still bound to the page as it is now.

    An entry counts when its recorded prose hash and source hash equal the current ones; an older entry stays in
    the file as history but no longer raises the tier. The actor is a self-declared label (`human:` is not authenticated).
    """
    entries = meta.get("verified")
    entries = entries if isinstance(entries, list) else ([entries] if entries else [])
    current = _bound_entries(entries, human_sha256(body), current_sources)
    if not current:
        return "unverified"
    return "human-reviewed" if any(str(e.get("by", "")).startswith("human:") for e in current) else "machine-confirmed"


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
    try:
        if "coverage" in only:
            report.findings += check_coverage(repo, pages)
        if "drift" in only:
            report.findings += check_drift(repo, set(report.stale))
    except (SyntaxError, ValueError, cl.Unresolved) as exc:
        report.findings.append(Finding("coverage", "BROKEN_SOURCE", "src", "the bundle cannot be derived from the sources (unparseable file or "
                                       f"colliding page paths), so coverage and drift cannot be established: {type(exc).__name__}: {exc}"))
    concepts = _concepts(pages)
    tiers: dict[str, int] = {}
    curated = 0
    for (meta, body) in concepts.values():
        tier = trust_tier(meta, body, current_sources_sha(repo, meta))
        tiers[tier] = tiers.get(tier, 0) + 1
        curated += is_curated(body)
    report.stats = {"pages": len(concepts), "trust_tiers": dict(sorted(tiers.items())), "pages_with_curated_notes": curated,
                    "stale_pages": len(report.stale),
                    "notes_stale_pages": sum(f.code == "NOTES_STALE" for f in report.findings)}
    return report


def format_report(report: Report) -> str:
    lines = [f.line() for f in report.findings]
    if report.stale:
        lines += ["", f"Pages requiring review ({len(report.stale)}): the source they describe changed."] + [f"  - okf/{p}" for p in report.stale]
    lines += ["", "okf: " + ("PASS" if report.ok else f"FAIL ({len(report.findings)} findings)") + f"  {report.stats}"]
    return "\n".join(lines)

