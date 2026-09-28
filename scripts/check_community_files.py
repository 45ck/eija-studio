"""Check the OSS community files exist and agree with the project metadata.

What this establishes: the files GitHub and contributors expect are present; `CITATION.cff` names the
same version and licence as `pyproject.toml`; the Code of Conduct is the Contributor Covenant 2.1 text
with a contact filled in; the roadmap covers every ADR block reserved in docs/adr/README.md; issue
templates parse.

What this does NOT establish: that the policies are good, that the contact address is monitored, or
that CITATION.cff passes the full CFF JSON schema (no validator is installed; see ADR-0043).
Exit codes: 0 = every check ran and passed; 1 = a check failed; 2 = nothing failed but a check could not
run (PyYAML missing), reported as NOT_RUN and never as PASS. The nox session turns exit 2 into a skip.
"""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "CITATION.cff", "CHANGELOG.md",
    "docs/ROADMAP.md", "docs/getting-started.md", "docs/assets/banner.svg", "mkdocs.yml",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml", ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/new_domain_proposal.yml",
]
NOT_RUN_EXIT = 2
RANGE = re.compile(r"(\d{4})\s*[-\N{EN DASH}]\s*(\d{4})")


def text(rel: str) -> str:
    return (ROOT / rel).read_bytes().decode("utf-8")


def check_presence() -> list[str]:
    return [f"missing file: {rel}" for rel in REQUIRED if not (ROOT / rel).is_file()]


def check_citation() -> list[str]:
    cff = text("CITATION.cff")
    project = tomllib.loads(text("pyproject.toml"))["project"]
    keys = ("cff-version", "message", "title", "authors", "version", "license", "repository-code")
    errors = [f"CITATION.cff lacks key '{key}'" for key in keys if not re.search(rf"^{re.escape(key)}:", cff, re.M)]
    if (m := re.search(r"^version:\s*(\S+)", cff, re.M)) and m.group(1) != project["version"]:
        errors.append(f"CITATION.cff version {m.group(1)} != pyproject {project['version']}")
    if (m := re.search(r"^license:\s*(\S+)", cff, re.M)) and m.group(1) != project["license"]:
        errors.append(f"CITATION.cff license {m.group(1)} != pyproject {project['license']}")
    return errors


def check_conduct() -> list[str]:
    coc = text("CODE_OF_CONDUCT.md")
    errors = []
    if "Contributor Covenant" not in coc or "version 2.1" not in coc:
        errors.append("CODE_OF_CONDUCT.md is not Contributor Covenant 2.1")
    if "[INSERT" in coc:
        errors.append("CODE_OF_CONDUCT.md still has an unfilled [INSERT ...] contact placeholder")
    return errors


def reserved_blocks() -> list[tuple[int, int]]:
    """ADR number blocks reserved in the first column of the table in docs/adr/README.md."""
    rows = re.finditer(r"^\|\s*(\d{4}\s*[-\N{EN DASH}]\s*\d{4})\s*\|", text("docs/adr/README.md"), re.M)
    return [(int(m.group(1)), int(m.group(2))) for r in rows if (m := RANGE.match(r.group(1)))]


def check_roadmap() -> list[str]:
    """Every reserved ADR block lies inside some range the roadmap names; the status line is dated."""
    roadmap = text("docs/ROADMAP.md")
    named = [(int(a), int(b)) for a, b in RANGE.findall(roadmap)]
    blocks = reserved_blocks()
    errors = [] if blocks else ["docs/adr/README.md has no reserved ADR block table"]
    errors += [f"docs/ROADMAP.md does not cover reserved ADR block {lo:04d}-{hi:04d}"
               for lo, hi in blocks if not any(a <= lo and hi <= b for a, b in named)]
    if not re.search(r"^Status as of \*\*\d{4}-\d{2}-\d{2}\*\*", roadmap, re.M):
        errors.append("docs/ROADMAP.md lacks a dated 'Status as of' line")
    if "## Unreleased" not in text("CHANGELOG.md"):
        errors.append("CHANGELOG.md lacks an '## Unreleased' section")
    return errors


def check_templates() -> tuple[list[str], list[str]]:
    """Return (errors, not_run)."""
    try:
        import yaml
    except ImportError:
        return [], ["issue-template YAML parse (PyYAML not installed; pip install -e '.[docs]')"]
    errors: list[str] = []
    for path in sorted((ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml")):
        rel = path.relative_to(ROOT).as_posix()
        if path.name != "config.yml":
            errors += _template_errors(rel, yaml.safe_load(path.read_bytes().decode("utf-8")))
    return errors, []


def _template_errors(rel: str, doc: object) -> list[str]:
    """Structural problems of one parsed GitHub issue form (not a full schema validation)."""
    if not isinstance(doc, dict) or not {"name", "description", "body"} <= doc.keys():
        return [f"{rel}: needs name, description and body"]
    ids = [b.get("id") for b in doc["body"] if b.get("type") != "markdown"]
    return [f"{rel}: duplicate field ids"] if len(ids) != len(set(ids)) else []


def check_line_endings() -> list[str]:
    files = [*REQUIRED, "scripts/check_doc_links.py", "scripts/check_community_files.py", "scripts/gen_readme_diagram.py",
             "README.md", "quality/sessions/oss.py"]
    return [f"{rel} has CRLF line endings" for rel in files if (ROOT / rel).is_file() and b"\r\n" in (ROOT / rel).read_bytes()]


def main() -> int:
    errors = check_presence()
    if errors:  # later checks read these files
        print("\n".join(f"FAIL {e}" for e in errors))
        return 1
    errors += check_citation() + check_conduct() + check_roadmap() + check_line_endings()
    tmpl_errors, not_run = check_templates()
    errors += tmpl_errors
    for e in errors:
        print("FAIL", e)
    for n in not_run:
        print("NOT_RUN", n)
    if errors:
        print(f"FAIL community files ({len(errors)} problems)")
        return 1
    if not_run:
        print(f"NOT_RUN-PARTIAL community files: {len(not_run)} check(s) could not run; the rest passed")
        return NOT_RUN_EXIT
    print(f"PASS community files ({len(REQUIRED)} required present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
