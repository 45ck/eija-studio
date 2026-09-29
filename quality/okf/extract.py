"""Extractors: turn code and docs into page specifications.

Each extractor reads a *source of truth* that already exists in the repository (python modules, the
ubiquitous-language section, ADR files, the acceptance matrix, nox sessions) and emits pages whose
machine-owned content is a pure function of those inputs. Nothing here reads a clock, the network or
git history, and every collection is sorted, so the output is reproducible.

What the pages establish: *this is what the source says, and here is the hash of it*. They do not
establish that the source is correct.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from . import codelink as cl
from .pages import (
    PageSpec,
    Repo,
    Source,
    describe,
    fence,
    first_sentence,
    localize_links,
    md_cell,
    one_line,
    quote,
)

PKG = "src/eija_studio"
LAYERS = ("domain", "application", "adapters", "interfaces")
COVERED_LAYERS = ("domain", "application")    # every public symbol here must have a page (coverage gate)
ARCH = "docs/architecture/ARCHITECTURE.md"
ADR_README = "docs/adr/README.md"
ACCEPTANCE = "docs/verification/ACCEPTANCE_MATRIX.csv"
VV_ADR = "docs/adr/0018-formal-vv-portfolio.md"
POC_LOG = "docs/adr/0000-poc-decision-log.md"

DIR_DESCRIPTIONS = {
    "": "EIJA Studio knowledge base",
    "language": "Ubiquitous language: the domain terms the kernel is built around",
    "contexts": "Bounded contexts from the architecture context map",
    "modules": "Source modules grouped by layer",
    "modules/domain": "Domain layer: contracts, protected policy, impact closure and evidence assessment",
    "modules/application": "Application layer: runtime, verifier, compiler, ports and the Studio use cases",
    "modules/adapters": "Adapters: SQLite, providers, receipts and identity behind application ports",
    "modules/interfaces": "Interfaces: the eija CLI and the FastAPI HTTP app",
    "symbols": "Public domain and application symbols with code-linked hashes",
    "symbols/domain": "Domain-layer symbols",
    "symbols/application": "Application-layer symbols",
    "adrs": "Architecture decision records",
    "adrs/poc": "The fourteen POC decisions ADR-001 to ADR-014 from the decision log",
    "requirements": "Acceptance matrix criteria and their evidence",
    "verification": "Verification techniques and evidence kinds",
    "gates": "nox quality gates",
    "lanes": "Capability lanes and their reserved ADR blocks",
}


def describe_dir(directory: str) -> str:
    if directory in DIR_DESCRIPTIONS:
        return DIR_DESCRIPTIONS[directory]
    parts = directory.split("/")
    if parts[0] == "symbols" and len(parts) == 3:
        return f"Symbols of {parts[1]}.{parts[2]}"
    if parts[0] == "gates" and len(parts) == 2:
        return f"Gates defined in quality/sessions/{parts[1].replace('-', '_')}.py"
    return directory


@dataclass(frozen=True)
class SymbolInfo:
    layer: str
    module: str          # "domain/policy"
    name: str            # "check_policy" or "Studio.create"
    kind: str            # function | class | constant | type-alias | method
    node: ast.AST
    doc: str | None
    owner: str | None = None   # owning class for methods

    @property
    def page(self) -> str:
        return f"symbols/{self.module}/{self.name}.md"

    @property
    def uri(self) -> str:
        return f"repo://{PKG}/{self.module}.py#{self.name}"


def read(repo: Repo, path: str) -> str:
    return cl.read_text(repo.root, path)


def module_id(path: str) -> str:
    return path[len(PKG) + 1:-3]


def python_modules(repo: Repo) -> list[str]:
    """Repo-relative python module paths in scope, sorted."""
    found = []
    for layer in LAYERS:
        folder = repo.root / PKG / layer
        if folder.is_dir():
            found += [f"{PKG}/{layer}/{p.name}" for p in folder.glob("*.py") if p.name != "__init__.py"]
    if (repo.root / PKG / "bootstrap.py").is_file():
        found.append(f"{PKG}/bootstrap.py")
    return sorted(found)


def _is_protocol(node: ast.ClassDef) -> bool:
    return any((isinstance(b, ast.Name) and b.id == "Protocol") or (isinstance(b, ast.Attribute) and b.attr == "Protocol")
               for b in node.bases)


def symbols_of(repo: Repo) -> list[SymbolInfo]:
    """Public symbols of domain/application modules, plus public methods of their non-Protocol classes."""
    out: list[SymbolInfo] = []
    for path in python_modules(repo):
        mid = module_id(path)
        layer = mid.split("/")[0]
        if layer not in COVERED_LAYERS:
            continue
        tree = cl.parse_module(read(repo, path), path)
        for name, kind, node in cl.public_symbols(tree):
            doc = ast.get_docstring(node, clean=True) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else None
            out.append(SymbolInfo(layer, mid, name, kind, node, doc))
            if isinstance(node, ast.ClassDef) and not _is_protocol(node):
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and not member.name.startswith("_"):
                        out.append(SymbolInfo(layer, mid, f"{name}.{member.name}", "method", member,
                                              ast.get_docstring(member, clean=True), owner=name))
    return sorted(out, key=lambda s: (s.module, s.name))


# ---- signatures ---------------------------------------------------------------------------------

def signature(info: SymbolInfo) -> str:
    node = info.node
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        return f"{prefix} {node.name}({ast.unparse(node.args)}){ret}"
    if isinstance(node, ast.ClassDef):
        bases = [ast.unparse(b) for b in node.bases] + [ast.unparse(k) for k in node.keywords]
        return f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}"
    text = ast.unparse(node)
    return text if len(text) <= 160 and "\n" not in text else one_line(text, 160)


def _names(nodes: list[ast.AST]) -> set[str]:
    found: set[str] = set()
    for root in nodes:
        for child in ast.walk(root):
            if isinstance(child, ast.Name):
                found.add(child.id)
    return found


def _signature_nodes(node: ast.AST) -> list[ast.AST]:
    """AST parts that make up a symbol's *interface* (used for class-level dependency edges)."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return [node.args, *([node.returns] if node.returns else []), *node.decorator_list]
    if isinstance(node, ast.ClassDef):
        parts: list[ast.AST] = [*node.bases, *node.keywords, *node.decorator_list]
        for member in node.body:
            if isinstance(member, ast.AnnAssign):
                parts.append(member)
            elif isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and cl.is_public(member.name):
                parts += _signature_nodes(member)
        return parts
    return [node]


def _import_map(repo: Repo, path: str, symbol_index: dict[tuple[str, str], SymbolInfo]) -> dict[str, tuple[str, str]]:
    """local name -> (module id, symbol name) for names imported from other in-scope modules."""
    tree = cl.parse_module(read(repo, path), path)
    package = module_id(path).split("/")[:-1]
    mapping: dict[str, tuple[str, str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        target = _absolute(package, node)
        if target is None:
            continue
        for alias in node.names:
            if (target, alias.name) in symbol_index:
                mapping[alias.asname or alias.name] = (target, alias.name)
    return mapping


def _absolute(package: list[str], node: ast.ImportFrom) -> str | None:
    """Module id (``domain/models``) of an internal ``from`` import, or None for external ones."""
    if node.level:
        base = package[: len(package) - (node.level - 1)] if node.level > 1 else package
        parts = base + (node.module.split(".") if node.module else [])
    else:
        parts = (node.module or "").split(".")
        if parts[:1] != ["eija_studio"]:
            return None
        parts = parts[1:]
    return "/".join(parts) if parts else None


def module_imports(repo: Repo, path: str, known: set[str]) -> list[str]:
    tree = cl.parse_module(read(repo, path), path)
    package = module_id(path).split("/")[:-1]
    found = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            target = _absolute(package, node)
            if target in known:
                found.add(target)
    return sorted(found)


# ---- symbol and module pages --------------------------------------------------------------------

def symbol_pages(repo: Repo) -> list[PageSpec]:
    symbols = symbols_of(repo)
    index = {(s.module, s.name): s for s in symbols if s.kind != "method"}
    imports = {mid: _import_map(repo, f"{PKG}/{mid}.py", index) for mid in sorted({s.module for s in symbols})}
    return [_symbol_page(s, symbols, index, imports[s.module]) for s in symbols]


_HASH_NOTE = {
    cl.AST_SIG: "`ast-sig-v1` over the class signature view: fields and public method signatures; method bodies and private helpers are NOT hashed",
    cl.AST_CLOSURE: "`ast-v2` over the normalised AST plus the same-module private helpers it reaches (comments and formatting ignored)",
}


_TYPE_LABEL = {"function": "Function", "class": "Class", "constant": "Constant", "type-alias": "Type Alias", "method": "Method"}


def _symbol_dependencies(s: SymbolInfo, index: dict[tuple[str, str], SymbolInfo], imports: dict[str, tuple[str, str]]) -> set[str]:
    """Pages of the symbols this one names: imported ones and same-module ones, never itself or its own class."""
    walk_nodes = _signature_nodes(s.node) if s.kind == "class" else [s.node]
    deps: set[str] = set()
    for name in _names(walk_nodes):
        target = imports.get(name) or ((s.module, name) if (s.module, name) in index else None)
        if target and target != (s.module, s.owner or s.name) and target != (s.module, s.name):
            deps.add(index[target].page)
    return deps


def _symbol_facts_table(s: SymbolInfo, method: str) -> tuple[str, list[str]]:
    """(the facts table, the pages that link back to this symbol: its module and, for a method, its class)."""
    module_page = f"modules/{s.module}.md"
    lines = ["| | |", "|---|---|", f"| Kind | {s.kind} |", f"| Module | [`{s.module}`](/{module_page}) |"]
    back = [module_page]
    if s.owner:
        owner_page = f"symbols/{s.module}/{s.owner}.md"
        lines.append(f"| Class | [`{s.owner}`](/{owner_page}) |")
        back.append(owner_page)
    lines += [f"| Signature | `{md_cell(signature(s))}` |", f"| Code | `{s.uri}` |", f"| Hash | {_HASH_NOTE[method]} |"]
    return "\n".join(lines), back


def _fields_section(node: ast.ClassDef) -> list[str]:
    fields = [(m.target.id, ast.unparse(m.annotation), ast.unparse(m.value) if m.value else "")
              for m in node.body if isinstance(m, ast.AnnAssign) and isinstance(m.target, ast.Name)]
    if not fields:
        return []
    rows = "\n".join(f"| `{n}` | `{md_cell(a)}` | {'`' + md_cell(one_line(v, 80)) + '`' if v else ''} |" for n, a, v in fields)
    return ["## Fields\n\n| Field | Annotation | Default |\n|---|---|---|\n" + rows]


def _members_section(s: SymbolInfo, node: ast.ClassDef, symbols: list[SymbolInfo]) -> list[str]:
    """The public methods of a class, or the members of a Protocol that has no method pages of its own."""
    methods = [m for m in symbols if m.owner == s.name and m.module == s.module]
    if methods:
        return ["## Methods\n\n" + "\n".join(
            f"* [`{m.name.split('.', 1)[1]}`](/{m.page}) - `{md_cell(signature(m))}`" for m in methods)]
    return _protocol_section(s, node)


def _protocol_section(s: SymbolInfo, node: ast.ClassDef) -> list[str]:
    if not _is_protocol(node):
        return []
    protocol = [m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if not protocol:
        return []
    return ["## Protocol members\n\nStructural interface implemented by adapters; not a class to instantiate.\n\n"
            + "\n".join(f"* `{md_cell(signature(SymbolInfo(s.layer, s.module, m.name, 'method', m, None)))}`" for m in protocol)]


def _class_sections(s: SymbolInfo, symbols: list[SymbolInfo]) -> list[str]:
    """Fields, methods or protocol members of a class symbol."""
    if not isinstance(s.node, ast.ClassDef):
        raise TypeError(f"{s.name}: a class symbol must wrap ast.ClassDef")
    return [*_fields_section(s.node), *_members_section(s, s.node, symbols)]


def _symbol_page(s: SymbolInfo, symbols: list[SymbolInfo], index: dict[tuple[str, str], SymbolInfo],
                 imports: dict[str, tuple[str, str]]) -> PageSpec:
    is_class = s.kind == "class"
    method = cl.AST_SIG if is_class else cl.AST_CLOSURE
    deps = _symbol_dependencies(s, index, imports)
    table, back = _symbol_facts_table(s, method)
    parts = [table, "## Docstring\n\n" + (fence(s.doc) if s.doc else "_The source carries no docstring._")]
    if is_class:
        parts += _class_sections(s, symbols)
    out: dict[str, list[str]] = {"Depends on": sorted(deps)} if deps else {}
    description = first_sentence(s.doc) if s.doc else _bare_description(s)
    return PageSpec(path=s.page, type=_TYPE_LABEL[s.kind], title=f"{s.module.replace('/', '.')}.{s.name}",
                    description=description, facts="\n\n".join(parts), tags=["symbol", s.layer, s.kind], resource=s.uri,
                    sources=[Source(s.uri, method, f"{s.module}.py")], out=out, back=back)


def _bare_description(s: SymbolInfo) -> str:
    """One-line description for a symbol with no docstring; short enough that no index line is cut mid-phrase."""
    if s.kind in ("constant", "type-alias"):
        return f"{_cap(s.kind.replace('-', ' '))} `{s.name}` in `{s.module}`."
    return f"`{one_line(signature(s), 110)}` in `{s.module}`."


def _public_symbols_section(own: list[SymbolInfo], layer: str) -> list[str]:
    if own:
        return ["## Public symbols\n\n" + "\n".join(
            f"* [`{s.name}`](/{s.page}) ({s.kind}) - {one_line(first_sentence(s.doc) if s.doc else 'no docstring', 120)}" for s in own)]
    if layer not in COVERED_LAYERS:
        return ["## Public symbols\n\n_Symbol pages are generated for the domain and application layers only._"]
    return []


def _module_page(repo: Repo, path: str, known: set[str], symbols: list[SymbolInfo]) -> PageSpec:
    mid = module_id(path)
    layer = mid.split("/")[0] if "/" in mid else "root"
    doc = ast.get_docstring(cl.parse_module(read(repo, path), path), clean=True)
    uri = f"repo://{path}"
    imports = module_imports(repo, path, known)
    parts = ["| | |\n|---|---|\n" + "\n".join([f"| Layer | {layer} |", f"| Code | `{uri}` |",
             "| Hash | `ast-api-v1` over public signatures, fields and docstrings (bodies excluded) |"])]
    parts.append("## Module docstring\n\n" + (fence(doc) if doc else "_The source carries no module docstring._"))
    parts += _public_symbols_section([s for s in symbols if s.module == mid and s.kind != "method"], layer)
    out: dict[str, list[str]] = {}
    if imports:
        out["Imports"] = [f"modules/{m}.md" for m in imports]
        parts.append("## Internal imports\n\n" + "\n".join(f"* [`{m}`](/modules/{m}.md)" for m in imports))
    return PageSpec(path=f"modules/{mid}.md", type="Module", title=mid.replace("/", "."),
                    description=first_sentence(doc) if doc else f"Module `{mid}` (no module docstring).",
                    facts="\n\n".join(parts), tags=["module", layer], resource=uri,
                    sources=[Source(uri, cl.AST_API, f"{mid}.py")], out=out)


def module_pages(repo: Repo, symbols: list[SymbolInfo]) -> list[PageSpec]:
    paths = python_modules(repo)
    known = {module_id(p) for p in paths}
    return [_module_page(repo, path, known, symbols) for path in paths]


# ---- ubiquitous language and context map --------------------------------------------------------

def _unique_symbol(symbols: list[SymbolInfo], name: str) -> SymbolInfo | None:
    hits = [s for s in symbols if s.name == name and s.kind != "method"]
    return hits[0] if len(hits) == 1 else None


def _cap(text: str) -> str:
    return text[:1].upper() + text[1:]


def _realised_pages(symbols: list[SymbolInfo], term: str) -> list[str]:
    """Pages of the unique public symbols a term is realised as: its CamelCase form and the form without its last word."""
    camel = "".join(w.capitalize() if not w[:1].isupper() else w for w in term.split())
    realised: list[str] = []
    for name in [camel, "".join(term.split()[:-1])]:
        hit = _unique_symbol(symbols, name) if name else None
        if hit and hit.page not in realised:
            realised.append(hit.page)
    return realised


def _language_page(term: str, definition: str, terms: list[tuple[str, str]], symbols: list[SymbolInfo]) -> PageSpec:
    realised = _realised_pages(symbols, term)
    related = [f"language/{cl.slug(other)}.md" for other, _ in terms if other != term and other in definition]
    out = {}
    parts = ["## Definition\n\n" + quote(localize_links(definition, "docs/architecture")),
             f"Source: `repo://{ARCH}#{cl.slug(term)}`."]
    if realised:
        out["Realised in code"] = realised
    if related:
        out["Related terms"] = related
    uri = f"repo://{ARCH}#{cl.slug(term)}"
    return PageSpec(path=f"language/{cl.slug(term)}.md", type="Ubiquitous Language Term", title=term,
                    description=_cap(first_sentence(definition)), facts="\n\n".join(parts),
                    tags=["language", "ddd"], resource=uri, sources=[Source(uri, cl.MD_TERM, "ARCHITECTURE.md")], out=out)


def language_pages(repo: Repo, symbols: list[SymbolInfo]) -> list[PageSpec]:
    text = read(repo, ARCH)
    section = re.search(r"^## Ubiquitous language\n(.*?)(?=^## )", text, re.DOTALL | re.MULTILINE)
    terms = cl.md_terms(section[1]) if section else []
    return [_language_page(term, definition, terms, symbols) for term, definition in terms]


def _module_page_for(path_text: str, modules: set[str]) -> str | None:
    """``domain/policy.py`` (or a full ``src/eija_studio/...`` path) -> module page path, if it exists."""
    tail = path_text.strip().strip("`")
    tail = tail[len(PKG) + 1:] if tail.startswith(PKG + "/") else tail
    tail = tail[:-3] if tail.endswith(".py") else tail
    return f"modules/{tail}.md" if tail in modules else None


def _contract_lines(contracts: str, symbols: list[SymbolInfo], out: dict[str, list[str]]) -> list[str]:
    lines = []
    for name in [c.strip() for c in contracts.split(",") if c.strip()]:
        hit = _unique_symbol(symbols, name.replace(" ", ""))
        if hit:
            out.setdefault("Published contracts", []).append(hit.page)
            lines.append(f"* [`{name}`](/{hit.page})")
        else:
            lines.append(f"* {name} (no public symbol of this name)")
    return lines


def _implementation_lines(implementation: str, modules: set[str], out: dict[str, list[str]]) -> list[str]:
    lines = []
    for token in re.findall(r"`([^`]+)`", implementation):
        page = _module_page_for(token, modules)
        if page:
            out.setdefault("Implementing modules", []).append(page)
            lines.append(f"* [`{token}`](/{page})")
        else:
            lines.append(f"* `{token}`")
    return lines


def _context_page(cells: list[str], symbols: list[SymbolInfo], modules: set[str]) -> PageSpec:
    area, owns, contracts, implementation = cells
    slug = cl.slug(area)
    out: dict[str, list[str]] = {}
    contract_lines = _contract_lines(contracts, symbols, out)
    impl_lines = _implementation_lines(implementation, modules, out)
    uri = f"repo://{ARCH}#{slug}"
    facts = "\n\n".join([f"## Owns\n\n{owns}", "## Published contracts\n\n" + "\n".join(contract_lines),
                         "## Implementation\n\n" + "\n".join(impl_lines),
                         f"Source: context map row `{uri}`. These are responsibility boundaries inside a modular monolith, "
                         "not separately deployed services."])
    return PageSpec(path=f"contexts/{slug}.md", type="Bounded Context", title=area,
                    description=f"Owns {describe(owns, 180)}", facts=facts, tags=["ddd", "context-map"],
                    resource=uri, sources=[Source(uri, cl.MD_ROW, "ARCHITECTURE.md")], out=out)


def context_pages(repo: Repo, symbols: list[SymbolInfo]) -> list[PageSpec]:
    text = read(repo, ARCH)
    section = re.search(r"^## Context map\n(.*?)(?=^## )", text, re.DOTALL | re.MULTILINE)
    modules = {module_id(p) for p in python_modules(repo)}
    return [_context_page(cells, symbols, modules) for cells in cl.md_table_rows(section[1] if section else "")
            if len(cells) == 4]


# ---- ADRs ---------------------------------------------------------------------------------------

_STATUS = {"accepted": "stable", "proposed": "draft", "superseded": "deprecated"}


def adr_files(repo: Repo) -> list[str]:
    folder = repo.root / "docs" / "adr"
    return sorted(f"docs/adr/{p.name}" for p in folder.glob("[0-9][0-9][0-9][0-9]-*.md"))


def _adr_meta(text: str) -> dict[str, str]:
    meta = {}
    for key in ("Status", "Date", "Lane"):
        match = re.search(rf"^\* {key}: (.+)$", text, re.MULTILINE)
        if match:
            meta[key.lower()] = match[1].strip()
    return meta


def _adr_summary(text: str, title: re.Match[str] | None, stem: str) -> str:
    """The context paragraph, else the first paragraph after the date line, else the title."""
    context = re.search(r"^## Context and problem statement\n+(.+?)(?:\n\n|\Z)", text, re.MULTILINE | re.DOTALL)
    body_start = re.search(r"^\* Date:[^\n]*\n\n(?:## [^\n]*\n\n)?(.+?)(?:\n\n|\Z)", text, re.MULTILINE | re.DOTALL)
    if context:
        return context[1]
    if body_start:
        return body_start[1]
    return title[1] if title else stem


def _adr_refs(text: str, number: str, catalog_paths: dict[str, str]) -> list[str]:
    """Pages of the other ADRs this one names, by file name or as ADR-NNNN."""
    named = re.findall(r"\b(\d{4})-[a-z0-9-]+\.md", text) + re.findall(r"ADR-(\d{4})", text)
    return sorted({catalog_paths[n] for n in named if n in catalog_paths and n != number})


def _adr_facts(repo: Repo, path: str, text: str, meta: dict[str, str]) -> str:
    headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
    outcome = re.search(r"^## Decision outcome\n+(.*?)(?=^#{2,3} |\Z)", text, re.MULTILINE | re.DOTALL)
    mentioned = sorted({m for m in re.findall(r"`([A-Za-z0-9_./-]+\.(?:py|md|json|csv|toml))`", text)
                        if (repo.root / m).is_file() and not m.startswith(("docs/adr/", repo.bundle_name + "/"))})   # never the bundle itself: keeps sync a fixpoint
    parts = ["| | |\n|---|---|\n" + "\n".join(
        [f"| Status | {md_cell(meta.get('status', 'unknown'))} |", f"| Date | {md_cell(meta.get('date', 'unknown'))} |"]
        + ([f"| Lane | {md_cell(localize_links(meta['lane'], 'docs/adr'))} |"] if "lane" in meta else []) + [f"| Source | `repo://{path}` |"])]
    if outcome:
        parts.append("## Decision outcome (verbatim)\n\n" + quote(localize_links("\n".join(outcome[1].strip().split("\n")[:20]), "docs/adr")))
    if headings:
        parts.append("## Sections\n\n" + "\n".join(f"* {h}" for h in headings))
    if mentioned:
        parts.append("## Code and docs mentioned\n\nExistence-checked by the gate; not hashed (an ADR is a decision record, "
                     "not a description of current code).\n\n" + "\n".join(f"* `repo://{m}`" for m in mentioned))
    return "\n\n".join(parts)


def _adr_page(repo: Repo, path: str, catalog_paths: dict[str, str]) -> PageSpec:
    text = read(repo, path)
    stem = Path(path).stem
    title = re.search(r"^# (.+)$", text, re.MULTILINE)
    meta = _adr_meta(text)
    status_word = meta.get("status", "proposed").split()[0].rstrip(",;.(").lower()
    refs = _adr_refs(text, stem[:4], catalog_paths)
    uri = f"repo://{path}"
    return PageSpec(path=f"adrs/{stem}.md", type="Architecture Decision Record",
                    title=title[1] if title else stem, description=first_sentence(_adr_summary(text, title, stem)),
                    facts=_adr_facts(repo, path, text, meta), tags=["adr", status_word], status=_STATUS.get(status_word, "draft"),
                    resource=uri, sources=[Source(uri, cl.FILE_LF, Path(path).name)], out={"Related decisions": refs} if refs else {})


def adr_pages(repo: Repo, catalog_paths: dict[str, str]) -> list[PageSpec]:
    """``catalog_paths`` maps a 4-digit ADR number to its page path, for cross-references."""
    return [_adr_page(repo, path, catalog_paths) for path in adr_files(repo)]


def poc_decision_pages(repo: Repo, catalog_paths: dict[str, str]) -> list[PageSpec]:
    if not (repo.root / POC_LOG).is_file():
        return []
    parent = catalog_paths.get("0000")
    pages = []
    for cells in cl.md_table_rows(read(repo, POC_LOG)):
        if len(cells) != 4 or not re.fullmatch(r"ADR-\d{3}", cells[0]):
            continue
        ident, decision, rejected, consequence = cells
        uri = f"repo://{POC_LOG}#{cl.slug(ident)}"
        facts = "\n\n".join([f"## Decision and rationale\n\n{decision}", f"## Rejected shortcut\n\n{rejected}",
                             f"## Consequence and revisit trigger\n\n{consequence}",
                             f"Source: `{uri}`. Accepted for the local POC only; not an endorsement for production."])
        pages.append(PageSpec(path=f"adrs/poc/{cl.slug(ident)}.md", type="Architecture Decision Record",
                              title=f"{ident}: {first_sentence(decision, 90).rstrip('.')}",
                              description=first_sentence(decision), facts=facts, tags=["adr", "poc-log", "accepted"], resource=uri,
                              sources=[Source(uri, cl.MD_ROW, "0000-poc-decision-log.md")],
                              out={"Decision log": [parent]} if parent else {}))
    return pages


# ---- acceptance requirements --------------------------------------------------------------------

def requirement_pages(repo: Repo, modules: set[str]) -> list[PageSpec]:
    pages = []
    for row in cl.csv_rows(read(repo, ACCEPTANCE)):
        ident = row["id"]
        out: dict[str, list[str]] = {}
        evidence = []
        for item in [e.strip() for e in row["v0_2_evidence"].split(";") if e.strip()]:
            page = _module_page_for(item, modules)
            if page:
                out.setdefault("Evidence modules", []).append(page)
                evidence.append(f"* [`{item}`](/{page})")
            elif (repo.root / item).is_file():
                evidence.append(f"* `repo://{item}`")
            else:
                evidence.append(f"* `{item}` (not a resolvable repository path)")
        table = ["| Field | Value |", "|---|---|"] + [f"| {k} | {md_cell(v)} |" for k, v in row.items()]
        uri = f"repo://{ACCEPTANCE}#{ident}"
        status = row["v0_2_status"]
        facts = "\n\n".join(["\n".join(table), "## Evidence files\n\n" + "\n".join(evidence),
                             f"Source: matrix row `{uri}`. `PASS_LOCAL` means only the declared synthetic/local portion was "
                             "exercised; `PARTIAL` and `NOT_RUN` stay visible and are never rounded up."])
        pages.append(PageSpec(path=f"requirements/{ident.lower()}.md", type="Acceptance Criterion",
                              title=f"{ident}: {row['area']}", description=f"{status}: {describe(row['observable_acceptance_criterion'], 190)}",
                              facts=facts, tags=["acceptance", cl.slug(row["area"]), status.lower()], resource=uri,
                              sources=[Source(uri, cl.CSV_ROW, "ACCEPTANCE_MATRIX.csv")], out=out))
    return pages


# ---- verification techniques --------------------------------------------------------------------

IMPLEMENTED_EVIDENCE = (
    {"slug": "integration-test", "title": "Bounded runtime matrix (integration_test)", "kind": "integration_test",
     "claim": "runtime_matrix",
     "establishes": "Every cell of a declared actor x state x action matrix, run against the real runtime in a sandbox, matched "
                    "a hand-written oracle that is partly derived from the model under test. The receipt is recomputed from raw observations.",
     "not": "Not a proof over arbitrary histories, not an independent oracle (same author), not crash durability of the "
            "owner workspace, and never evidence of human comprehension (that stays UNKNOWN).",
     "code": ("application/verifier.py#verify_runtime", "domain/evidence.py#assess_receipt", "domain/evidence.py#aggregate_status")},
)


def verification_pages(repo: Repo, catalog_paths: dict[str, str], symbols: list[SymbolInfo]) -> list[PageSpec]:
    pages: list[PageSpec] = []
    by_key = {(s.module, s.name): s for s in symbols}
    for item in IMPLEMENTED_EVIDENCE:
        sources, out, code_lines = [], {"Implemented by": []}, []
        for ref in item["code"]:
            module, name = ref.split(".py#")
            symbol = by_key.get((module, name))
            uri = f"repo://{PKG}/{module}.py#{name}"
            sources.append(Source(uri, cl.AST_CLOSURE, f"{module}.{name}"))
            if symbol:
                out["Implemented by"].append(symbol.page)
                code_lines.append(f"* [`{module}.{name}`](/{symbol.page})")
        facts = "\n\n".join(["| | |\n|---|---|\n" + "\n".join([f"| Evidence kind | `{item['kind']}` |", f"| Claim | `{item['claim']}` |",
                             "| Status | implemented in the kernel |"]),
                             f"## What it can establish\n\n{item['establishes']}", f"## What it does not establish\n\n{item['not']}",
                             "## Implemented by\n\n" + "\n".join(code_lines)])
        pages.append(PageSpec(path=f"verification/{item['slug']}.md", type="Verification Technique", title=item["title"],
                              description=f"Implemented: {first_sentence(item['establishes'])}", facts=facts, tags=["verification", "implemented"],
                              resource=sources[0].resource, sources=sources, out=out))
    adr_path = catalog_paths.get("0018")
    if (repo.root / VV_ADR).is_file():
        text = read(repo, VV_ADR)
        for cells in cl.md_table_rows(text):
            if len(cells) != 4 or not cells[3].startswith("`"):
                continue
            technique, tool, establishes, kind = cells
            kind_id = kind.strip("`")
            uri = f"repo://{VV_ADR}#{kind_id}"
            facts = "\n\n".join(["| | |\n|---|---|\n" + "\n".join([f"| Evidence kind | `{kind_id}` |", f"| Tool | {md_cell(tool)} |",
                                 f"| Source | `{uri}` |"]),
                                 f"## What it can establish\n\n{establishes}",
                                 "**Status: planned, not implemented in the kernel.** The ADR names this technique; no code in this repository "
                                 "produces this evidence yet. The page is `draft` (unreviewed plan) whatever the ADR's own status becomes, "
                                 "and it is a distinct evidence kind that may never be relabelled as another."])
            pages.append(PageSpec(path=f"verification/{cl.slug(kind_id)}.md", type="Verification Technique", title=technique,
                                  description=f"Planned (not implemented). Would establish: {describe(establishes, 160)}", facts=facts,
                                  tags=["verification", "planned"], status="draft", resource=uri,
                                  sources=[Source(uri, cl.MD_ROW, "0018-formal-vv-portfolio.md")],
                                  out={"Decision": [adr_path]} if adr_path else {}))
    return pages


# ---- gates and lanes ----------------------------------------------------------------------------

def _session_options(deco: ast.Call, default_name: str) -> tuple[str, list[str]]:
    """(session name, sorted tags) from the literal keywords of a ``@nox.session(...)`` decorator."""
    name, tags = default_name, []
    for kw in deco.keywords:
        try:
            value = ast.literal_eval(kw.value)
        except ValueError:
            continue
        if kw.arg == "name" and isinstance(value, str):
            name = value
        if kw.arg == "tags" and isinstance(value, (list, tuple)):
            tags = sorted(str(t) for t in value)
    return name, tags


def _session_defs(tree: ast.Module) -> list[tuple[ast.FunctionDef, str, list[str]]]:
    found = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for deco in node.decorator_list:
            if isinstance(deco, ast.Call) and ast.unparse(deco.func) == "nox.session":
                found.append((node, *_session_options(deco, node.name)))
    return found


def gate_pages(repo: Repo) -> list[PageSpec]:
    pages = []
    folder = repo.root / "quality" / "sessions"
    for path in sorted(folder.glob("*.py")) if folder.is_dir() else []:
        if path.name == "__init__.py":
            continue
        rel = f"quality/sessions/{path.name}"
        tree = cl.parse_module(read(repo, rel), rel)
        for node, name, tags in _session_defs(tree):
            doc = ast.get_docstring(node, clean=True)
            uri = f"repo://{rel}#{node.name}"
            facts = "\n\n".join(["| | |\n|---|---|\n" + "\n".join([f"| Command | `nox -s {name}` |",
                                 f"| Tiers | {', '.join(f'`{t}`' for t in tags) or '_none_'} |", f"| Session module | `repo://{rel}` |",
                                 f"| Code | `{uri}` |"]),
                                 "## Docstring\n\n" + (fence(doc) if doc else "_The session carries no docstring._"),
                                 "Tiers: `fast` (seconds, pre-commit), `full` (the PR gate) and `release` (maintainer evidence; may "
                                 "need Docker, Java or Chromium and reports `NOT_RUN`, never `PASS`, without them)."])
            pages.append(PageSpec(path=f"gates/{cl.slug(path.stem)}/{cl.slug(name)}.md", type="Quality Gate", title=f"nox -s {name}",
                                  description=first_sentence(doc) if doc else f"nox session `{name}` in `{path.name}`.",
                                  facts=facts, tags=["gate", *tags], resource=uri, sources=[Source(uri, cl.AST_CLOSURE, path.name)]))
    return pages


def _short(slug: str, limit: int = 40) -> str:
    if len(slug) <= limit:
        return slug
    words = slug[:limit].rsplit("-", 1)[0].split("-")
    while words and words[-1] in {"and", "of", "the", "for", "to", "with"}:
        words.pop()
    return "-".join(words)


def lane_pages(repo: Repo, catalog_paths: dict[str, str]) -> list[PageSpec]:
    text = read(repo, ADR_README)
    section = re.search(r"^## Reserved numbers for capability lanes\n(.*)\Z", text, re.DOTALL | re.MULTILINE)
    pages = []
    for cells in cl.md_table_rows(section[1] if section else ""):
        if len(cells) != 2:
            continue
        numbers, lane = cells
        match = re.fullmatch(r"(\d{4})\s*[–—-]\s*(\d{4})", numbers)
        if not match:
            continue
        low, high = int(match[1]), int(match[2])
        adrs = sorted(p for n, p in catalog_paths.items() if low <= int(n) <= high)
        slug = f"{match[1]}-{_short(cl.slug(lane.split('(')[0]))}"
        uri = f"repo://{ADR_README}#{cl.slug(numbers)}"
        facts = "\n\n".join(["| | |\n|---|---|\n" + "\n".join([f"| Reserved ADR numbers | {match[1]}–{match[2]} |",
                             "| Branch convention | `lane/<name>` (see AGENTS.md, Capability lanes) |", f"| Source | `{uri}` |"]),
                             "## Landed ADRs\n\n" + ("Listed under the generated links below." if adrs else "_None yet: the lane has not "
                                                     "recorded a decision in its reserved block._")])
        pages.append(PageSpec(path=f"lanes/{slug}.md", type="Capability Lane", title=lane, description=f"Capability lane with ADR numbers {match[1]}–{match[2]} reserved.",
                              facts=facts, tags=["lane"], resource=uri, sources=[Source(uri, cl.MD_ROW, "docs/adr/README.md")],
                              out={"Landed ADRs": adrs} if adrs else {}))
    return pages


def collect(repo: Repo) -> list[PageSpec]:
    """Every generated page, in a stable order."""
    symbols = symbols_of(repo)
    modules = {module_id(p) for p in python_modules(repo)}
    adr_paths = {Path(p).stem[:4]: f"adrs/{Path(p).stem}.md" for p in adr_files(repo)}
    pages = [*symbol_pages(repo), *module_pages(repo, symbols), *language_pages(repo, symbols), *context_pages(repo, symbols),
             *adr_pages(repo, adr_paths), *poc_decision_pages(repo, adr_paths), *requirement_pages(repo, modules),
             *verification_pages(repo, adr_paths, symbols), *gate_pages(repo), *lane_pages(repo, adr_paths)]
    folded: dict[str, int] = {}
    for page in pages:
        folded[page.path.casefold()] = folded.get(page.path.casefold(), 0) + 1
    duplicates = sorted({p.path for p in pages if folded[p.path.casefold()] > 1})
    if duplicates:
        raise ValueError(f"extractors produced page paths that collide (compared case-insensitively, as on Windows and macOS): {duplicates}")
    return sorted(pages, key=lambda p: p.path)
