"""The OKF bundle gate end to end, on the real repository and on mutated copies of it.

Every negative test asserts the specific finding a maintainer would see, not just "something failed".
"""
import re
import shutil
import sys
from pathlib import Path

import pytest

pytest.importorskip("frontmatter", reason="NOT_RUN: install the okf extra (pip install -e .[okf])")
pytest.importorskip("yaml")
pytest.importorskip("markdown_it")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from quality.okf import __main__ as cli  # noqa: E402
from quality.okf.build import build, existing_pages  # noqa: E402
from quality.okf.checks import run_checks  # noqa: E402
from quality.okf.pages import MACHINE_KEYS, Repo, dump_frontmatter, split_page  # noqa: E402

POLICY = "src/eija_studio/domain/policy.py"
CHECK_POLICY = "symbols/domain/policy/check_policy.md"


IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "resources", "web")


@pytest.fixture(scope="module")
def pristine(tmp_path_factory):
    """One copy of the parts of the checkout the wiki is derived from, plus the committed bundle."""
    root = tmp_path_factory.mktemp("okf-pristine")
    for part in ("src/eija_studio", "docs", "quality", "tests", "scripts", "okf"):
        shutil.copytree(ROOT / part, root / part, ignore=IGNORE)
    for name in ("noxfile.py", "AGENTS.md", "pyproject.toml"):
        shutil.copy2(ROOT / name, root / name)
    return root


@pytest.fixture
def repo(pristine, tmp_path):
    """A private, mutable copy per test."""
    shutil.copytree(pristine, tmp_path / "repo")
    return Repo(tmp_path / "repo")


def codes(report, check=None):
    return sorted({f.code for f in report.findings if check in (None, f.check)})


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_bytes().decode("utf-8")
    assert old in text, old
    path.write_bytes(text.replace(old, new, 1).encode("utf-8"))


def set_notes(page: Path, text: str) -> None:
    """Replace the human-owned Notes region of a page."""
    old = page.read_bytes().decode("utf-8")
    new, count = re.subn(r"(## Notes\n\n).*?(\n\n<!-- okf:generated:begin links)", lambda m: m[1] + text + m[2], old, flags=re.DOTALL)
    assert count == 1
    page.write_bytes(new.encode("utf-8"))


def machine_view(text: str, ignore_description: bool = False):
    """What the generator owns on a page: machine frontmatter keys and generated blocks."""
    meta, body = split_page(text)
    if ignore_description:
        meta.pop("description")
    kept = {k: v for k, v in meta.items() if k in MACHINE_KEYS}
    return kept, re.findall(r"<!-- okf:generated:begin (\w+) -->\n(.*?)\n<!-- okf:generated:end", body, re.DOTALL)


def sync(repo: Repo) -> None:
    assert cli.main(["--root", str(repo.root), "sync"]) == 0


# ---- the committed bundle -----------------------------------------------------------------------

def test_committed_bundle_passes_every_check():
    report = run_checks(Repo(ROOT))
    assert report.ok, "\n".join(f.line() for f in report.findings)
    assert report.stats["pages"] > 150


def test_bundle_declares_okf_v02_and_reserved_files_exist():
    meta, _ = split_page((ROOT / "okf" / "index.md").read_text(encoding="utf-8"))
    assert meta == {"okf_version": "0.2"}
    assert (ROOT / "okf" / "log.md").is_file()


def test_generated_pages_never_carry_wall_clock_timestamps():
    for text in existing_pages(Repo(ROOT)).values():
        if text.startswith("---"):
            assert "generated:\n  by: process:eija-okf-sync\n" in text or "generated" not in text.split("---")[1]
            assert "\n  at:" not in text.split("---")[1]


# ---- determinism and drift ----------------------------------------------------------------------

def test_regeneration_is_a_byte_identical_noop_and_a_fresh_build_reproduces_machine_content(repo):
    committed = existing_pages(repo)
    assert build(repo).files == committed                       # regeneration over the committed bundle changes nothing
    shutil.rmtree(repo.bundle)
    sync(repo)
    fresh = existing_pages(repo)
    assert set(fresh) == set(committed)
    for path, text in committed.items():
        if text.startswith("---\ntype:"):                        # concept pages: machine-owned parts reproduce exactly
            overridden = "description_override" in split_page(text)[0]      # a human-owned summary replaces the generated one
            assert machine_view(fresh[path], overridden) == machine_view(text, overridden), path


def test_second_sync_writes_nothing(repo):
    sync(repo)
    before = {p: (repo.bundle / p).read_bytes() for p in existing_pages(repo)}
    sync(repo)
    assert {p: (repo.bundle / p).read_bytes() for p in existing_pages(repo)} == before


def test_hand_edited_generated_block_is_reported_as_drift(repo):
    edit(repo.bundle / CHECK_POLICY, "| Kind | function |", "| Kind | a hand-edited lie |")
    report = run_checks(repo)
    assert codes(report, "drift") == ["DRIFT"] and not report.ok
    sync(repo)
    assert run_checks(repo).ok            # sync restores the machine-owned block


# ---- human prose survives ----------------------------------------------------------------------

def test_human_prose_verified_and_unknown_keys_survive_regeneration(repo):
    page = repo.bundle / CHECK_POLICY
    set_notes(page, "PROSE-MARKER: policy is protected; see [Authority](/language/authority.md).")
    edit(page, "\n---\n", "\nx_owner_note: keep me\nverified:\n- by: human:reviewer\n  at: '2026-09-28T09:00:00Z'\n---\n")
    sync(repo)
    text = page.read_text(encoding="utf-8")
    meta, _ = split_page(text)
    assert "PROSE-MARKER" in text
    assert meta["x_owner_note"] == "keep me"
    assert meta["verified"][0]["by"] == "human:reviewer"
    assert run_checks(repo).ok


def test_description_override_is_human_owned(repo):
    page = repo.bundle / CHECK_POLICY
    meta, body = split_page(page.read_text(encoding="utf-8"))
    meta["description_override"] = "A curated one-line summary."
    page.write_bytes((dump_frontmatter(meta) + "\n" + body).encode("utf-8"))
    sync(repo)
    assert split_page(page.read_text(encoding="utf-8"))[0]["description"] == "A curated one-line summary."
    assert run_checks(repo).ok


# ---- STALE: the code moved on -------------------------------------------------------------------

def test_semantic_code_change_makes_exactly_the_linked_pages_stale(repo):
    edit(repo.root / POLICY, '"UNSUPPORTED_WORKFLOW_SHAPE"', '"UNSUPPORTED_WORKFLOW_SHAPE_V2"')
    report = run_checks(repo)
    assert report.stale == [CHECK_POLICY]
    assert "STALE" in codes(report, "codelinks")
    stale_line = next(f for f in report.findings if f.code == "STALE")
    assert "check_policy" in stale_line.message and "python -m quality.okf sync" in stale_line.message
    assert not any(f.code == "DRIFT" and f.path == CHECK_POLICY for f in report.findings)   # reported once, as STALE


def test_formatting_only_change_is_not_stale(repo):
    edit(repo.root / POLICY, "def ensure_policy(model: Workflow) -> None:", "# reviewed\ndef ensure_policy(model:  Workflow)  ->  None:")
    assert run_checks(repo).ok


def test_sync_rebaselines_and_resets_verification(repo):
    page = repo.bundle / CHECK_POLICY
    assert cli.main(["--root", str(repo.root), "review", CHECK_POLICY, "--by", "human:reviewer", "--at", "2026-09-28T09:00:00Z"]) == 0
    assert "human:reviewer" in page.read_text(encoding="utf-8") and run_checks(repo).ok
    sync(repo)
    assert "human:reviewer" in page.read_text(encoding="utf-8")        # nothing changed: attestation kept
    edit(repo.root / POLICY, '"PROTECTED_AUTHORITY:"', '"PROTECTED_AUTHORITY_V2:"')
    assert run_checks(repo).stale == [CHECK_POLICY]
    sync(repo)
    assert "verified" not in split_page(page.read_text(encoding="utf-8"))[0]   # trust tier falls back to unverified
    assert run_checks(repo).ok


def test_review_refuses_a_page_whose_sources_changed(repo, capsys):
    edit(repo.root / POLICY, '"PROTECTED_STATE:"', '"PROTECTED_STATE_V2:"')
    status = cli.main(["--root", str(repo.root), "review", CHECK_POLICY, "--by", "human:reviewer", "--at", "2026-09-28T09:00:00Z"])
    assert status == 1 and "refusing to verify" in capsys.readouterr().err
    assert "verified" not in split_page((repo.bundle / CHECK_POLICY).read_text(encoding="utf-8"))[0]


def test_changed_adr_and_acceptance_row_are_stale(repo):
    edit(repo.root / "docs/adr/0016-oss-first-adapters-not-engines.md", "Every capability first adopts", "Every capability sometimes adopts")
    edit(repo.root / "docs/verification/ACCEPTANCE_MATRIX.csv", "Contract,Unknown fields", "Contract,Some unknown fields")
    assert run_checks(repo).stale == ["adrs/0016-oss-first-adapters-not-engines.md", "requirements/ac01.md"]


# ---- code-link integrity and coverage -----------------------------------------------------------

def test_renamed_symbol_marks_old_page_deprecated_and_new_symbol_needs_a_page(repo):
    edit(repo.root / POLICY, "def check_policy(", "def check_policy_v2(")
    report = run_checks(repo)
    assert {"STALE", "BROKEN_RESOURCE"} & set(codes(report, "codelinks"))
    assert "MISSING_PAGE" in codes(report, "coverage")
    sync(repo)
    old = split_page((repo.bundle / CHECK_POLICY).read_text(encoding="utf-8"))[0]
    assert old["status"] == "deprecated"                       # kept for links and history (SPEC section 5.4)
    assert (repo.bundle / "symbols/domain/policy/check_policy_v2.md").is_file()
    assert run_checks(repo).ok


def test_unresolvable_resource_on_a_live_page_is_reported(repo):
    edit(repo.bundle / CHECK_POLICY, "policy.py#check_policy\n", "policy.py#nope\n")
    assert "BROKEN_RESOURCE" in codes(run_checks(repo), "codelinks")


def test_missing_hash_or_unknown_method_is_reported(repo):
    page = repo.bundle / CHECK_POLICY
    edit(page, "  hash_method: ast-v1\n", "  hash_method: made-up-v9\n")
    assert "MISSING_HASH" in codes(run_checks(repo), "codelinks")


def test_new_public_symbol_new_adr_and_deleted_page_break_coverage(repo):
    with (repo.root / "src/eija_studio/domain/impact.py").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("\n\ndef brand_new_public_function() -> None:\n    return None\n")
    (repo.root / "docs/adr/0045-copy.md").write_text("# ADR-0045: Copy\n\n* Status: accepted\n* Date: 2026-09-28\n\nBody.\n", encoding="utf-8")
    (repo.bundle / "requirements/ac05.md").unlink()
    report = run_checks(repo)
    missing = {f.path for f in report.findings if f.code == "MISSING_PAGE"}
    assert {"symbols/domain/impact/brand_new_public_function.md", "adrs/0045-copy.md", "requirements/ac05.md"} <= missing
    sync(repo)
    assert run_checks(repo).ok


# ---- links --------------------------------------------------------------------------------------

def test_broken_internal_link_and_broken_repo_uri_are_errors(repo):
    page = repo.bundle / CHECK_POLICY
    set_notes(page, "See [nowhere](/language/nowhere.md), [rel](../missing.md), `repo://src/eija_studio/domain/policy.py#gone`.")
    found = {(f.code, f.message.split("'")[1] if "'" in f.message else "") for f in run_checks(repo).findings if f.check == "links"}
    assert ("BROKEN_LINK", "/language/nowhere.md") in found
    assert ("BROKEN_LINK", "../missing.md") in found
    assert any(code == "BROKEN_REPO_URI" for code, _ in found)


def test_links_inside_code_spans_and_fences_are_not_links(repo):
    set_notes(repo.bundle / CHECK_POLICY, "Write `[x](/nope.md)` like this.\n\n```\n[y](/nope2.md)\n```")
    assert run_checks(repo, ("links",)).ok


# ---- conformance --------------------------------------------------------------------------------

@pytest.mark.parametrize("mutation, expected", [
    (lambda p: p.write_text("# no frontmatter here\n", encoding="utf-8"), "FRONTMATTER"),
    (lambda p: p.write_text("---\ntype: ''\n---\nbody\n", encoding="utf-8"), "TYPE"),
    (lambda p: p.write_text("---\ntitle: no type\n---\nbody\n", encoding="utf-8"), "TYPE"),
    (lambda p: p.write_text("---\ntype: [unclosed\n---\nbody\n", encoding="utf-8"), "FRONTMATTER"),
    (lambda p: p.write_text("---\ntype: X\nstatus: finished\n---\nb\n", encoding="utf-8"), "STATUS"),
    (lambda p: p.write_text("---\ntype: X\ngenerated: {by: somebody}\n---\nb\n", encoding="utf-8"), "ACTOR"),
    (lambda p: p.write_text("---\ntype: X\nverified: {by: human:a, at: 2026-09-28}\n---\nb\n", encoding="utf-8"), "VERIFIED"),
    (lambda p: p.write_text("---\ntype: X\nsources: [{title: no resource}]\n---\nb\n", encoding="utf-8"), "SOURCES"),
    (lambda p: p.write_text("---\ntype: X\n---\nClaim.[^ghost]\n", encoding="utf-8"), "FOOTNOTE"),
])
def test_conformance_rejects_malformed_concepts(repo, mutation, expected):
    mutation(repo.bundle / "language" / "authority.md")
    assert expected in codes(run_checks(repo, ("conformance",)), "conformance")


def test_a_concept_with_only_type_is_conformant(repo):
    (repo.bundle / "language" / "authority.md").write_text("---\ntype: Anything\n---\nbody\n", encoding="utf-8")
    assert run_checks(repo, ("conformance",)).ok


def test_reserved_file_structure_is_enforced(repo):
    log = repo.bundle / "log.md"
    log.write_text("# Log\n\n## 2026-09-01\n* older\n\n## 2026-09-28\n* newer\n", encoding="utf-8")
    assert "LOG_ORDER" in codes(run_checks(repo, ("conformance",)))
    log.write_text("# Log\n\n## 28/09/2026\n* x\n", encoding="utf-8")
    assert "LOG_DATE" in codes(run_checks(repo, ("conformance",)))
    log.write_text("# Log\n\n## 2026-13-45\n* x\n", encoding="utf-8")
    assert "LOG_DATE" in codes(run_checks(repo, ("conformance",)))
    (repo.bundle / "language" / "index.md").write_text("---\ntype: nope\n---\n# H\n* [a](a.md)\n", encoding="utf-8")
    assert "INDEX_FRONTMATTER" in codes(run_checks(repo, ("conformance",)))
    (repo.bundle / "index.md").write_text("---\nokf_version: '0.1'\n---\n# H\n* [a](a.md)\n", encoding="utf-8")
    assert "OKF_VERSION" in codes(run_checks(repo, ("conformance",)))


def test_missing_reserved_files_are_reported(repo):
    (repo.bundle / "log.md").unlink()
    assert "MISSING_RESERVED" in codes(run_checks(repo, ("conformance",)))


def test_missing_bundle_reports_instead_of_passing(tmp_path):
    report = run_checks(Repo(tmp_path))
    assert not report.ok and codes(report) == ["MISSING_BUNDLE"]


# ---- honesty of the generated pages -------------------------------------------------------------

def test_prewritten_trust_is_never_invented_by_the_generator(repo):
    shutil.rmtree(repo.bundle)
    sync(repo)
    for text in existing_pages(repo).values():
        if text.startswith("---\ntype:"):
            assert "\nverified:" not in text, "the generator must not mint verification"
