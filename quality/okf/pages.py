"""Page model and deterministic page rendering.

A concept page has machine-owned frontmatter and machine-owned *generated blocks* delimited by
``<!-- okf:generated:begin NAME -->`` / ``<!-- okf:generated:end NAME -->``. Everything outside those
blocks, and any frontmatter key the generator does not own, is human prose and is preserved verbatim.
Identical inputs produce byte-identical output: there is no wall-clock time anywhere in this module.
"""
from __future__ import annotations

import copy
import functools
import hashlib
import posixpath
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

OKF_VERSION = "0.2"
GENERATOR = "process:eija-okf-sync"   # OKF actor convention (SPEC section 7)
PLACEHOLDER = "_No curated notes yet._"
MACHINE_KEYS = ("type", "title", "description", "resource", "tags", "status", "generated", "sources")
RESERVED = ("index.md", "log.md")

_BLOCK = re.compile(r"<!-- okf:generated:begin (?P<name>[a-z-]+) -->\n(?P<body>.*?)\n<!-- okf:generated:end (?P=name) -->",
                    re.DOTALL)
_SPLIT = re.compile(r"\A---\n(?P<yaml>.*?)\n---\n(?P<body>.*)\Z", re.DOTALL)


@dataclass(frozen=True)
class Repo:
    root: Path
    bundle_name: str = "okf"

    @property
    def bundle(self) -> Path:
        return self.root / self.bundle_name


@dataclass(frozen=True)
class Source:
    """One provenance entry: what the page derives from and how that thing is hashed."""
    resource: str
    method: str
    title: str | None = None


@dataclass
class PageSpec:
    path: str                      # bundle-relative, e.g. "symbols/domain/policy/check_policy.md"
    type: str
    title: str
    description: str
    facts: str                     # generated markdown block
    tags: list[str] = field(default_factory=list)
    status: str = "stable"
    resource: str | None = None
    sources: list[Source] = field(default_factory=list)
    out: dict[str, list[str]] = field(default_factory=dict)   # label -> bundle paths this page links to
    back: list[str] = field(default_factory=list)   # pages listing this one under 'Referenced by', no outbound section
    seed: str = PLACEHOLDER


def one_line(text: str, limit: int = 220) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1].rstrip() + "…"


def plain(text: str) -> str:
    """Markdown links reduced to their link text (for one-line descriptions)."""
    return re.sub(r"\[([^\]]+)\]\([^)\s]*\)", r"\1", text)


def describe(text: str, limit: int = 220) -> str:
    return one_line(plain(text), limit)


def first_sentence(text: str, limit: int = 220) -> str:
    flat = " ".join(plain(text).split())
    match = re.search(r"(?<=[.!?])\s", flat)
    return one_line(flat[: match.start()] if match else flat, limit)


def md_cell(text: str) -> str:
    """Escape a value for a markdown table cell."""
    return " ".join(str(text).split()).replace("|", "\\|")


def fence(text: str) -> str:
    """Fence verbatim text so its markdown characters cannot restructure the page."""
    marker = "~~~"
    while marker in text:
        marker += "~"
    return f"{marker}text\n{text.rstrip()}\n{marker}"


_MD_LINK = re.compile(r"\]\((?P<target>[^)\s]+)\)")


def localize_links(text: str, source_dir: str) -> str:
    """Rewrite relative markdown links copied from a repo document into ``repo://`` URIs.

    A relative link such as ``../oss/REGISTER.md`` means something else inside the bundle. The rewritten
    URI is checked by the gate (a target that does not exist is reported, not hidden).
    """
    def swap(match: re.Match[str]) -> str:
        target = match["target"]
        if target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            return match.group(0)
        path, _, fragment = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(source_dir, path))
        return f"](repo://{resolved}{'#' + fragment if fragment else ''})"

    return _MD_LINK.sub(swap, text)


def quote(text: str) -> str:
    return "\n".join("> " + line if line.strip() else ">" for line in text.split("\n"))


# ---- reading ------------------------------------------------------------------------------------

@functools.lru_cache(maxsize=1024)
def _load_yaml(text: str) -> Any:
    return yaml.safe_load(text)


def sources_sha256(sources: Any) -> str | None:
    """One digest over a page's recorded source hashes (resource, method, sha256), order-independent.

    Returns None when ``sources`` is not a well-formed list, so a malformed page can never look aligned.
    """
    if not isinstance(sources, list):
        return None
    lines = []
    for entry in sources:
        if not isinstance(entry, dict) or not isinstance(entry.get("resource"), str):
            return None
        lines.append(f"{entry['resource']} {entry.get('hash_method')} {entry.get('sha256')}")
    return hashlib.sha256(chr(10).join(sorted(lines)).encode("utf-8")).hexdigest()


def human_sha256(body: str) -> str:
    """Digest of everything a human owns in a page body: the text outside the ``okf:generated`` blocks."""
    prose = _BLOCK.sub(lambda m: f"<generated {m['name']}>", body)
    return hashlib.sha256(" ".join(prose.split()).encode("utf-8")).hexdigest()


def is_curated(body: str) -> bool:
    """True when the page carries hand-written text under ``## Notes`` (anything but the placeholder)."""
    match = re.search(r"^## Notes\n\n(.*?)(?=\n<!-- okf|\Z)", body, re.DOTALL | re.MULTILINE)
    return bool(match and match[1].strip() and match[1].strip() != PLACEHOLDER)


def split_page(text: str) -> tuple[dict[str, Any], str]:
    """Split a page into ``(frontmatter mapping, body)``. Raises ValueError if it has no frontmatter."""
    match = _SPLIT.match(text)
    if not match:
        raise ValueError("no frontmatter block delimited by '---' lines")
    try:
        meta = copy.deepcopy(_load_yaml(match["yaml"]))    # callers mutate; the cache must not see it
    except yaml.YAMLError as exc:
        raise ValueError(f"frontmatter is not valid YAML: {exc}") from exc
    if not isinstance(meta, dict):
        raise ValueError("frontmatter is not a mapping")
    body = match["body"]
    return meta, (body[1:] if body.startswith("\n") else body)   # the blank separator line belongs to the layout


# ---- writing ------------------------------------------------------------------------------------

def dump_frontmatter(meta: dict[str, Any]) -> str:
    blob = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, default_flow_style=False, width=100000)
    return f"---\n{blob}---\n"


def frontmatter_for(spec: PageSpec, digests: dict[str, str], existing: dict[str, Any] | None, curated: bool = False) -> dict[str, Any]:
    """Machine-owned keys in a fixed order, then preserved human keys.

    Human-owned keys are kept verbatim: ``verified`` (an append-only attestation history; whether an entry
    still counts is decided at check time from the hashes it is bound to) and ``notes_baseline`` (the source
    state the curated Notes were last aligned to). For a page with hand-written Notes (``curated``) ``sync``
    NEVER advances an existing ``notes_baseline``: only ``review`` does, so regenerating cannot mark prose as
    re-read. A page with no hand-written text follows its sources (there is nothing to align), and a curated
    page with no baseline yet is seeded once; deleting the key to silence a finding is a visible diff in review.
    """
    description = spec.description
    if existing and isinstance(existing.get("description_override"), str) and existing["description_override"].strip():
        description = " ".join(existing["description_override"].split())   # human-owned one-line summary
    meta: dict[str, Any] = {"type": spec.type, "title": spec.title, "description": description}
    if spec.resource:
        meta["resource"] = spec.resource
    if spec.tags:
        meta["tags"] = list(spec.tags)
    meta["status"] = spec.status
    meta["generated"] = {"by": GENERATOR}
    if spec.sources:
        entries = []
        for source in spec.sources:
            entry: dict[str, Any] = {"resource": source.resource}
            if source.title:
                entry["title"] = source.title
            entry["hash_method"] = source.method
            entry["sha256"] = digests[source.resource]
            entries.append(entry)
        meta["sources"] = entries
    if existing:
        for key, value in existing.items():
            if key not in MACHINE_KEYS:
                meta[key] = value
        if meta.get("description_override") == spec.description:
            del meta["description_override"]           # redundant: it only repeats the generated description
    if "sources" in meta and (not curated or "notes_baseline" not in meta):
        meta["notes_baseline"] = sources_sha256(meta["sources"])
    return meta


def block(name: str, content: str) -> str:
    return f"<!-- okf:generated:begin {name} -->\n{content.strip()}\n<!-- okf:generated:end {name} -->"


def render_body(spec: PageSpec, blocks: dict[str, str], existing_body: str | None) -> str:
    """New page body, or the existing body with only the generated blocks replaced."""
    if existing_body is None:
        return (f"# {spec.title}\n\n{block('facts', blocks['facts'])}\n\n## Notes\n\n{spec.seed}\n\n"
                f"{block('links', blocks['links'])}\n")
    seen: set[str] = set()

    def swap(match: re.Match[str]) -> str:
        name = match["name"]
        seen.add(name)
        return block(name, blocks[name]) if name in blocks else ""

    body = _BLOCK.sub(swap, existing_body)
    for name in blocks:
        if name not in seen:
            body = body.rstrip("\n") + "\n\n" + block(name, blocks[name]) + "\n"
    return re.sub(r"\n{3,}", "\n\n", body)


def render_page(spec: PageSpec, blocks: dict[str, str], digests: dict[str, str], existing_text: str | None) -> str:
    existing_meta: dict[str, Any] | None = None
    existing_body: str | None = None
    if existing_text is not None:
        try:
            existing_meta, existing_body = split_page(existing_text)
        except ValueError:
            existing_meta, existing_body = None, None   # unparseable: regenerate; conformance reports it separately
    meta = frontmatter_for(spec, digests, existing_meta, curated=existing_body is not None and is_curated(existing_body))
    return dump_frontmatter(meta) + "\n" + render_body(spec, blocks, existing_body)


def link_entry(target: PageSpec | dict[str, str], path: str, relative_to: str | None = None) -> str:
    title = target.title if isinstance(target, PageSpec) else target["title"]
    description = target.description if isinstance(target, PageSpec) else target["description"]
    href = "/" + path if relative_to is None else path
    return f"* [{title}]({href}) - {one_line(description, 160)}"


def render_links(spec: PageSpec, catalog: dict[str, PageSpec], referenced_by: list[str]) -> str:
    sections = []
    for label, paths in spec.out.items():
        unique = sorted(set(paths))
        if unique:
            sections.append(f"## {label}\n\n" + "\n".join(link_entry(catalog[p], p) for p in unique))
    if referenced_by:
        sections.append("## Referenced by\n\n" + "\n".join(link_entry(catalog[p], p) for p in referenced_by))
    return "\n\n".join(sections) if sections else "_No generated cross-references._"
