"""Check the OSS community files exist and agree with the project metadata.

What this establishes: the files GitHub and contributors expect are present; `CITATION.cff` names the
same version and licence as `pyproject.toml`; the Code of Conduct is the Contributor Covenant 2.1 text
with a contact filled in; the roadmap names every one of the 13 lane ADR blocks; issue templates parse.

What this does NOT establish: that the policies are good, that the contact address is monitored, or
that CITATION.cff passes the full CFF JSON schema (no validator is installed; see ADR-0043).
Exit 0 = PASS. A check that cannot run because a library is missing prints NOT_RUN and does not pass.
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
# The 13 capability lanes' reserved ADR blocks (docs/adr/README.md). Other blocks may exist.
LANE_BLOCKS = ["0021-0022", "0023-0024", "0025-0026", "0027-0028", "0029-0030", "0031-0032", "0033-0034",
               "0035-0036", "0037-0038", "0039-0040", "0041-0042", "0043-0044", "0045-0046"]


def text(rel: str) -> str:
    return (ROOT / rel).read_bytes().decode("utf-8")


def check_presence() -> list[str]:
    return [f"missing file: {rel}" for rel in REQUIRED if not (ROOT / rel).is_file()]


def check_citation() -> list[str]:
    errors: list[str] = []
    cff = text("CITATION.cff")
    project = tomllib.loads(text("pyproject.toml"))["project"]
    for key in ("cff-version", "message", "title", "authors", "version", "license", "repository-code"):
        if not re.search(rf"^{re.escape(key)}:", cff, re.M):
            errors.append(f"CITATION.cff lacks key '{key}'")
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


def check_roadmap() -> list[str]:
    roadmap = text("docs/ROADMAP.md")
    errors = [f"docs/ROADMAP.md does not mention ADR block {b}" for b in LANE_BLOCKS if b not in roadmap]
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
    errors = []
    for path in sorted((ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml")):
        doc = yaml.safe_load(path.read_bytes().decode("utf-8"))
        rel = path.relative_to(ROOT).as_posix()
        if path.name == "config.yml":
            continue
        if not isinstance(doc, dict) or not {"name", "description", "body"} <= doc.keys():
            errors.append(f"{rel}: needs name, description and body")
            continue
        ids = [b.get("id") for b in doc["body"] if b.get("type") != "markdown"]
        if len(ids) != len(set(ids)):
            errors.append(f"{rel}: duplicate field ids")
    return errors, []


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
    print(f"{'FAIL' if errors else 'PASS'} community files ({len(REQUIRED)} required present)"
          + (f", {len(not_run)} check NOT_RUN" if not_run else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
