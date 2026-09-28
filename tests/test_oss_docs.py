"""Tests for the oss lane's documentation gates. Each gate has a negative control: a planted defect it must catch."""
import importlib.util
import sys
from pathlib import Path

import pytest

from eija_studio.domain.impact import model_impact
from eija_studio.domain.models import SemanticTransaction
from eija_studio.domain.policy import apply_transaction, baseline

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gen():
    return load("gen_readme_diagram")


@pytest.fixture
def links():
    return load("check_doc_links")


@pytest.fixture
def community():
    return load("check_community_files")


@pytest.fixture
def pr_status():
    return load("check_pr_status")


# --- README diagram: a projection of the real model --------------------------------------------

def test_committed_readme_matches_the_model(gen):
    current = gen.README.read_bytes().decode("utf-8")
    assert gen.splice(current, gen.render_block()) == current


def test_render_is_deterministic(gen):
    assert gen.render_block() == gen.render_block()


def test_diff_reports_the_real_semantic_change(gen):
    before = baseline()
    after = apply_transaction(before, SemanticTransaction(kind="enable_recommendation"))
    d = gen.diff(before, after)
    assert d["states"] == ["Recommended"]
    assert d["removed"] == []
    assert [a.split()[0] for a in d["added"]] == ["`TR-RECOMMEND`"]
    assert sorted(c.split()[0] for c in d["changed"]) == ["`TR-APPROVE`", "`TR-REJECT`"]
    assert gen.diff(before, before) == {"states": [], "added": [], "changed": [], "removed": []}


def test_block_shows_the_kernel_rejecting_a_teacher_approval(gen):
    block = gen.render_block()
    assert "PROTECTED_AUTHORITY:Approve" in block
    assert "Recommended --> Approved: Approve / Registrar (changed)" in block


def test_stale_readme_is_detected(gen, monkeypatch, tmp_path, capsys):
    stale = tmp_path / "README.md"
    stale.write_bytes(gen.splice(gen.README.read_bytes().decode("utf-8"), gen.render_block())
                      .replace("Recommend / Teacher (new)", "Recommend / Teacher").encode("utf-8"))
    monkeypatch.setattr(gen, "README", stale)
    assert gen.main(["--check"]) == 1
    assert "stale" in capsys.readouterr().out


def test_block_shows_the_kernels_impact_closure(gen):
    before = baseline()
    after = apply_transaction(before, SemanticTransaction(kind="enable_recommendation"))
    impact = model_impact(before, after)
    block = gen.render_block()
    assert f"reaches {len(impact['affected'])} artefacts" in block
    assert "- `review-packet`" in block and "- `rule:` Approve, Recommend, Reject" in block


def test_group_affected_groups_by_kind_and_keeps_bare_ids(gen):
    assert gen._group_affected(["rule:B", "rule:A", "review-packet"]) == ["- `review-packet`", "- `rule:` A, B"]


def test_splice_refuses_a_readme_without_markers(gen):
    with pytest.raises(SystemExit):
        gen.splice("# no markers here", gen.render_block())


# --- link checker -------------------------------------------------------------------------------

def _repo(tmp_path, links_module, monkeypatch, readme: str, **files: str):
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text(readme, encoding="utf-8")
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    monkeypatch.setattr(links_module, "ROOT", tmp_path)
    return tmp_path


def test_broken_relative_link_is_flagged(links, tmp_path, monkeypatch):
    root = _repo(tmp_path, links, monkeypatch, "[gone](docs/missing.md) [ok](docs/here.md)", **{"docs/here.md": "# Here\n"})
    broken, pending, ok = links.check(root / "README.md")
    assert broken == ["README.md: docs/missing.md does not exist"] and ok == 1 and pending == []


def test_missing_anchor_is_flagged_and_present_anchor_passes(links, tmp_path, monkeypatch):
    root = _repo(tmp_path, links, monkeypatch, "[a](docs/here.md#real-heading) [b](docs/here.md#nope)",
                 **{"docs/here.md": "# Here\n\n## Real `heading`\n"})
    broken, _, ok = links.check(root / "README.md")
    assert ok == 1 and len(broken) == 1 and "#nope" in broken[0]


def test_links_in_code_and_comments_are_ignored(links, tmp_path, monkeypatch):
    readme = "`[x](nope.md)`\n\n```md\n[y](nope2.md)\n```\n\n<!-- ![z](nope3.png) -->\n"
    root = _repo(tmp_path, links, monkeypatch, readme)
    assert links.check(root / "README.md") == ([], [], 0)


def test_pending_target_is_reported_never_ok_and_then_checked_once_it_exists(links, tmp_path, monkeypatch):
    monkeypatch.setitem(links.PENDING, "docs/later.md", "some lane")
    root = _repo(tmp_path, links, monkeypatch, "[soon](docs/later.md)")
    broken, pending, ok = links.check(root / "README.md")
    assert broken == [] and ok == 0 and len(pending) == 1 and "some lane" in pending[0]
    (root / "docs" / "later.md").write_text("# Later\n", encoding="utf-8")
    assert links.check(root / "README.md") == ([], [], 1)


def test_link_escaping_the_repo_and_html_src_are_flagged(links, tmp_path, monkeypatch):
    root = _repo(tmp_path, links, monkeypatch, '<img src="docs/nope.svg"> [up](../outside.md)')
    broken, _, _ = links.check(root / "README.md")
    assert any("nope.svg" in b for b in broken) and any("escapes" in b for b in broken)


def test_external_links_are_not_fetched(links, tmp_path, monkeypatch):
    root = _repo(tmp_path, links, monkeypatch, "[x](https://example.invalid/x) [m](mailto:a@b.c)")
    assert links.check(root / "README.md") == ([], [], 0)


def test_repository_links_all_resolve(links):
    broken = [b for f in links.checked_files() for b in links.check(f)[0]]
    assert broken == []


# --- community files ---------------------------------------------------------------------------

def test_citation_version_drift_is_flagged(community, tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "0.3.0"\nlicense = "Apache-2.0"\n', encoding="utf-8")
    (tmp_path / "CITATION.cff").write_text("cff-version: 1.2.0\nmessage: m\ntitle: t\nauthors: []\nversion: 0.2.0\n"
                                           "license: Apache-2.0\nrepository-code: x\n", encoding="utf-8")
    monkeypatch.setattr(community, "ROOT", tmp_path)
    assert community.check_citation() == ["CITATION.cff version 0.2.0 != pyproject 0.3.0"]


def test_conduct_placeholder_is_flagged(community, tmp_path, monkeypatch):
    (tmp_path / "CODE_OF_CONDUCT.md").write_text("Contributor Covenant version 2.1 [INSERT CONTACT METHOD]", encoding="utf-8")
    monkeypatch.setattr(community, "ROOT", tmp_path)
    assert community.check_conduct() == ["CODE_OF_CONDUCT.md still has an unfilled [INSERT ...] contact placeholder"]


def test_repository_community_files_pass(community):
    assert community.check_presence() == []
    assert community.check_citation() == []
    assert community.check_conduct() == []
    assert community.check_roadmap() == []
    assert community.check_line_endings() == []


def _root_with(tmp_path, community, monkeypatch, **files: str):
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8", newline="")
    monkeypatch.setattr(community, "ROOT", tmp_path)
    return tmp_path


def test_missing_required_file_is_flagged(community, tmp_path, monkeypatch):
    _root_with(tmp_path, community, monkeypatch, LICENSE="x")
    missing = community.check_presence()
    assert "missing file: CONTRIBUTING.md" in missing and "missing file: LICENSE" not in missing


def test_crlf_line_endings_are_flagged(community, tmp_path, monkeypatch):
    _root_with(tmp_path, community, monkeypatch, **{"SECURITY.md": "a\r\nb\r\n", "LICENSE": "a\nb\n"})
    assert community.check_line_endings() == ["SECURITY.md has CRLF line endings"]


EN_DASH = chr(0x2013)
ADR_TABLE = f"| Numbers | Lane |\n|---|---|\n| 0021{EN_DASH}0022 | providers |\n| 0057{EN_DASH}0088 | ux |\n| 0089-0112 | weave |\n"


def test_reserved_blocks_are_read_from_the_adr_table(community, tmp_path, monkeypatch):
    _root_with(tmp_path, community, monkeypatch, **{"docs/adr/README.md": ADR_TABLE})
    assert community.reserved_blocks() == [(21, 22), (57, 88), (89, 112)]


def test_roadmap_must_cover_every_reserved_block(community, tmp_path, monkeypatch):
    dated = "Status as of **2026-09-29**\n"
    _root_with(tmp_path, community, monkeypatch, **{"docs/adr/README.md": ADR_TABLE, "CHANGELOG.md": "## Unreleased\n",
                                                     "docs/ROADMAP.md": dated + "| 0021-0022 | a |\n| 0057-0136 | b |\n"})
    assert community.check_roadmap() == []  # a wider roadmap range covers narrower reserved blocks
    (tmp_path / "docs/ROADMAP.md").write_text(dated + "| 0021-0022 | a |\n| 0057-0088 | b |\n", encoding="utf-8")
    assert community.check_roadmap() == ["docs/ROADMAP.md does not cover reserved ADR block 0089-0112"]
    (tmp_path / "docs/ROADMAP.md").write_text("| 0021-0022 | a |\n| 0057-0136 | b |\n", encoding="utf-8")
    assert community.check_roadmap() == ["docs/ROADMAP.md lacks a dated 'Status as of' line"]


def test_roadmap_check_fails_without_a_reserved_table(community, tmp_path, monkeypatch):
    _root_with(tmp_path, community, monkeypatch, **{"docs/adr/README.md": "no table", "CHANGELOG.md": "## Unreleased\n",
                                                     "docs/ROADMAP.md": "Status as of **2026-09-29**\n"})
    assert community.check_roadmap() == ["docs/adr/README.md has no reserved ADR block table"]


def test_issue_form_defects_are_flagged(community):
    ok = {"name": "n", "description": "d", "body": [{"type": "input", "id": "a"}, {"type": "markdown"}]}
    assert community._template_errors("t.yml", ok) == []
    assert community._template_errors("t.yml", {"name": "n"}) == ["t.yml: needs name, description and body"]
    dup = {**ok, "body": [{"type": "input", "id": "a"}, {"type": "textarea", "id": "a"}]}
    assert community._template_errors("t.yml", dup) == ["t.yml: duplicate field ids"]


def test_unparseable_issue_forms_are_flagged_when_yaml_exists(community, tmp_path, monkeypatch):
    pytest.importorskip("yaml")
    _root_with(tmp_path, community, monkeypatch, **{".github/ISSUE_TEMPLATE/bug.yml": "name: only a name\n"})
    errors, not_run = community.check_templates()
    assert errors == [".github/ISSUE_TEMPLATE/bug.yml: needs name, description and body"] and not_run == []


def _run_main(community, monkeypatch, capsys, *, errors=(), not_run=()):
    monkeypatch.setattr(community, "check_presence", list)
    for name in ("check_citation", "check_conduct", "check_roadmap", "check_line_endings"):
        monkeypatch.setattr(community, name, list)
    monkeypatch.setattr(community, "check_templates", lambda: (list(errors), list(not_run)))
    code = community.main()
    return code, capsys.readouterr().out


def test_a_skipped_check_is_not_run_and_never_a_pass(community, monkeypatch, capsys):
    """Missing PyYAML must not print PASS or exit 0: exit 2 and a NOT_RUN summary."""
    code, out = _run_main(community, monkeypatch, capsys, not_run=["issue-template YAML parse (PyYAML not installed)"])
    assert code == community.NOT_RUN_EXIT == 2
    assert "NOT_RUN issue-template YAML parse" in out and "PASS" not in out


def test_failure_outranks_not_run_and_a_clean_run_passes(community, monkeypatch, capsys):
    code, out = _run_main(community, monkeypatch, capsys, errors=["x"], not_run=["y"])
    assert code == 1 and out.startswith("FAIL x")
    code, out = _run_main(community, monkeypatch, capsys)
    assert code == 0 and out.startswith("PASS")


def test_missing_yaml_reports_not_run(community, monkeypatch):
    monkeypatch.setitem(sys.modules, "yaml", None)  # makes `import yaml` raise ImportError
    errors, not_run = community.check_templates()
    assert errors == [] and len(not_run) == 1 and "PyYAML" in not_run[0]


# --- pull-request status claims ---------------------------------------------------------------

def test_claims_are_extracted_from_prose(pr_status):
    text = "row | open PR #4 | merged pr #9 (was Closed PR #7) | not a claim: PR #12 alone"
    assert pr_status.claims(text) == [("OPEN", 4), ("MERGED", 9), ("CLOSED", 7)]


def test_stale_claims_are_reported_and_current_ones_are_not(pr_status):
    live = {4: "OPEN", 9: "MERGED", 3: "MERGED"}
    assert pr_status.stale([("OPEN", 4), ("MERGED", 9)], live) == []
    assert pr_status.stale([("OPEN", 3), ("OPEN", 99)], live) == [
        "PR #3 claimed OPEN but is MERGED", "PR #99 claimed OPEN but GitHub lists no such pull request"]


def test_pr_status_is_not_run_without_gh(pr_status, monkeypatch, capsys):
    monkeypatch.setattr(pr_status, "live_states", lambda: None)
    assert pr_status.main() == pr_status.NOT_RUN_EXIT
    out = capsys.readouterr().out
    assert "NOT_RUN" in out and "PASS" not in out


def test_repository_pr_claims_exist_in_the_docs(pr_status):
    """Guards the gate itself: the pages still make claims for it to check."""
    found = [c for f in pr_status.claim_files() for c in pr_status.claims(f.read_bytes().decode("utf-8"))]
    assert ("OPEN", 14) in found and ("MERGED", 3) in found
