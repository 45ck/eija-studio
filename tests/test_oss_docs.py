"""Tests for the oss lane's documentation gates. Each gate has a negative control: a planted defect it must catch."""
import importlib.util
from pathlib import Path

import pytest

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


# --- README diagram: a projection of the real model --------------------------------------------

def test_committed_readme_matches_the_model(gen):
    current = gen.README.read_bytes().decode("utf-8")
    assert gen.splice(current, gen.render_block()) == current


def test_render_is_deterministic(gen):
    assert gen.render_block() == gen.render_block()


def test_diff_reports_the_real_semantic_change(gen):
    from eija_studio.domain.models import SemanticTransaction
    from eija_studio.domain.policy import apply_transaction, baseline

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
    assert broken == [] and links.unlisted_adrs() == []


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
