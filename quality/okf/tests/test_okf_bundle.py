"""The OKF bundle gate end to end, on the real repository and on mutated copies of it.

Every negative test asserts the specific finding a maintainer would see, not just "something failed".
"""
import csv
import re
import shutil
import sys
from pathlib import Path

import pytest

pytest.importorskip("yaml", reason="NOT_RUN: install the okf extra (pip install -e .[okf])")
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
PARTS = ("src/eija_studio", "docs", "quality", "tests", "scripts", "okf")   # everything the generator reads


def _snapshot(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for part in PARTS for p in (root / part).rglob("*") if p.is_file()}


@pytest.fixture(scope="module")
def workspace(tmp_path_factory):
    """One private working copy of the inputs the wiki is derived from, shared by the module's tests.

    Copying ~250 files per test made the tooling suite slower than the whole kernel suite on the reference
    HDD machine; instead every test mutates this copy and ``repo`` restores it byte for byte afterwards.
    """
    root = tmp_path_factory.mktemp("okf-work")
    for part in PARTS:
        shutil.copytree(ROOT / part, root / part, ignore=IGNORE)
    for name in ("noxfile.py", "AGENTS.md", "pyproject.toml"):
        shutil.copy2(ROOT / name, root / name)
    return root, _snapshot(root)


@pytest.fixture
def repo(workspace):
    """The working copy, guaranteed identical to the committed inputs at the start and restored at the end of each test."""
    root, snapshot = workspace
    _restore(root, snapshot)
    yield Repo(root)
    _restore(root, snapshot)


def _restore(root: Path, snapshot: dict[str, bytes]) -> None:
    for part in PARTS:
        for path in (root / part).rglob("*"):
            if path.is_file() and path.relative_to(root).as_posix() not in snapshot:
                path.unlink()                                  # a file the test created
    for rel, data in snapshot.items():
        target = root / rel
        if not target.is_file() or target.read_bytes() != data:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)


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


def review(repo: Repo, page: str, by: str = "human:reviewer", check: bool = True) -> int:
    status = cli.main(["--root", str(repo.root), "review", page, "--by", by, "--at", "2026-09-28T09:00:00Z"])
    assert status == 0 or not check
    return status


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
        if text.startswith("---\ntype:"):
            generated = split_page(text)[0].get("generated")
            assert generated is None or generated == {"by": "process:eija-okf-sync"}   # review times live in `verified`, an explicit argument


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
    edit(page, "\n---\n", "\nx_owner_note: keep me\n---\n")
    review(repo, CHECK_POLICY)
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


def _assert_notes_stay_red_and_history_kept(after, page):
    assert not after.ok and codes(after) == ["NOTES_STALE"] and after.stale == []            # generated parts are baselined, prose is not
    assert "Teacher can never approve" in page.read_text(encoding="utf-8")                   # the contradicted prose is still there
    assert after.stats["trust_tiers"].get("human-reviewed", 0) == 0                          # old attestation no longer counts
    assert len(split_page(page.read_text(encoding="utf-8"))[0]["verified"]) == 1               # ...but the history is kept, not dropped


def test_sync_rebaselines_generated_content_but_cannot_clear_stale_notes_or_raise_the_tier(repo):
    """The reviewers' scenario: gut check_policy, sync, and the page whose Notes now lie must stay red."""
    page = repo.bundle / CHECK_POLICY
    confirmed_before = run_checks(repo).stats["trust_tiers"].get("machine-confirmed", 0)
    review(repo, CHECK_POLICY)
    assert run_checks(repo).stats["trust_tiers"]["human-reviewed"] == 1 and run_checks(repo).ok
    sync(repo)
    assert run_checks(repo).stats["trust_tiers"]["human-reviewed"] == 1        # nothing changed: attestation still current
    text = (repo.root / POLICY).read_text(encoding="utf-8")
    start = text.index("def check_policy(")
    end = text.index("\n\n\n", start)
    (repo.root / POLICY).write_bytes((text[:start] + "def check_policy(model: Workflow) -> list[str]:\n    return []" + text[end:]).encode("utf-8"))
    report = run_checks(repo)
    assert report.stale == [CHECK_POLICY] and "STALE" in codes(report, "codelinks")
    sync(repo)
    _assert_notes_stay_red_and_history_kept(run_checks(repo), page)
    review(repo, CHECK_POLICY, by="process:eija-okf-test")
    ok = run_checks(repo)
    assert ok.ok and ok.stats["trust_tiers"].get("machine-confirmed", 0) == confirmed_before + 1
    assert ok.stats["trust_tiers"].get("human-reviewed", 0) == 0
    assert len(split_page(page.read_text(encoding="utf-8"))[0]["verified"]) == 2


def test_uncurated_pages_follow_their_source_and_are_not_gated_for_notes(repo):
    uncurated = "symbols/domain/models/AGENT.md"
    assert "_No curated notes yet._" in (repo.bundle / uncurated).read_text(encoding="utf-8")
    edit(repo.root / "src/eija_studio/domain/models.py", 'Principal(id="agent"', 'Principal(id="agent-2"')
    assert uncurated in run_checks(repo).stale
    sync(repo)
    report = run_checks(repo)
    assert uncurated not in [f.path for f in report.findings]         # nothing hand-written on it to re-read
    assert report.ok


def test_verified_entry_is_bound_to_the_prose_and_the_sources(repo):
    page = repo.bundle / CHECK_POLICY
    review(repo, CHECK_POLICY)
    assert run_checks(repo).stats["trust_tiers"]["human-reviewed"] == 1
    set_notes(page, "A Teacher can approve if assigned.")                                       # the prose is inverted after the review
    report = run_checks(repo)
    assert report.ok                                                                            # a hash cannot judge prose...
    assert report.stats["trust_tiers"].get("human-reviewed", 0) == 0                            # ...but the attestation no longer counts
    assert "verified" in split_page(page.read_text(encoding="utf-8"))[0]


def test_unbound_verified_entry_is_a_conformance_error(repo):
    edit(repo.bundle / CHECK_POLICY, "\n---\n", "\nverified:\n- by: human:someone\n  at: '2026-09-28T09:00:00Z'\n---\n")
    assert "VERIFIED" in codes(run_checks(repo, ("conformance",)), "conformance")
    assert run_checks(repo).stats["trust_tiers"].get("human-reviewed", 0) == 0                 # a forged, unbound entry never raises the tier


def test_review_refuses_a_page_whose_sources_changed(repo, capsys):
    edit(repo.root / POLICY, '"PROTECTED_STATE:"', '"PROTECTED_STATE_V2:"')
    status = review(repo, CHECK_POLICY, check=False)
    assert status == 1 and "refusing to review" in capsys.readouterr().err
    assert "verified" not in split_page((repo.bundle / CHECK_POLICY).read_text(encoding="utf-8"))[0]


@pytest.mark.parametrize("args, message", [
    (["--by", "whoever", "--at", "2026-09-28T09:00:00Z"], "--by must be"),
    (["--by", "human:x", "--at", "garbage"], "--at must be"),
    (["--by", "human:x", "--at", "yesterday"], "--at must be"),
    (["--by", "human:x", "--at", "2026-09-28T09:00:00"], "--at must be"),        # no UTC offset
])
def test_review_rejects_malformed_actor_and_time_before_writing(repo, capsys, args, message):
    before = (repo.bundle / CHECK_POLICY).read_bytes()
    assert cli.main(["--root", str(repo.root), "review", CHECK_POLICY, *args]) == 2
    assert message in capsys.readouterr().err
    assert (repo.bundle / CHECK_POLICY).read_bytes() == before


@pytest.mark.parametrize("name, message", [
    ("../../../AGENTS.md", "not a concept page"),
    ("../okf/index.md", "not a concept page"),
    ("index.md", "not a concept page"),
    ("nope/missing.md", "no such page"),
])
def test_review_confines_itself_to_concept_pages_inside_the_bundle(repo, capsys, name, message):
    assert review(repo, name, check=False) == 1
    assert message in capsys.readouterr().err


def test_review_of_a_vanished_symbol_is_a_refusal_not_a_traceback(repo, capsys):
    edit(repo.root / POLICY, "def check_policy(", "def check_policy_v2(")
    assert review(repo, CHECK_POLICY, check=False) == 1
    assert "refusing to review" in capsys.readouterr().err


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
    after = run_checks(repo)
    assert [(f.code, f.path) for f in after.findings] == [("NOTES_STALE", "modules/domain/policy.md")]   # its public API changed and its Notes are hand-written
    review(repo, "modules/domain/policy.md")
    assert run_checks(repo).ok


def test_unresolvable_resource_on_a_live_page_is_reported(repo):
    edit(repo.bundle / CHECK_POLICY, "policy.py#check_policy\n", "policy.py#nope\n")
    assert "BROKEN_RESOURCE" in codes(run_checks(repo), "codelinks")


def test_missing_hash_or_unknown_method_is_reported(repo):
    page = repo.bundle / CHECK_POLICY
    edit(page, "  hash_method: ast-v2\n", "  hash_method: made-up-v9\n")
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


# ---- what a hash covers: private helpers, collisions, unparseable sources -----------------------

def test_removing_a_check_inside_a_private_helper_stales_the_public_methods_that_use_it(repo):
    service = repo.root / "src/eija_studio/application/service.py"
    edit(service, "            c.at_version(expected)\n", "            pass\n")           # drops the CAS check inside Studio._case
    report = run_checks(repo)
    stale = set(report.stale)
    assert {"symbols/application/service/Studio.select.md", "symbols/application/service/Studio.edit.md"} <= stale
    assert "symbols/application/service/Studio.md" not in stale                  # documented limit: the class page hashes signatures only
    assert not report.ok


def test_page_paths_that_differ_only_by_case_are_rejected_not_silently_overwritten(repo, capsys):
    with (repo.root / "src/eija_studio/domain/impact.py").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("\n\ndef Foo() -> None:\n    return None\n\n\ndef foo() -> None:\n    return None\n")
    report = run_checks(repo)
    assert "BROKEN_SOURCE" in codes(report) and "collide" in " ".join(f.message for f in report.findings)
    assert cli.main(["--root", str(repo.root), "sync"]) == 1
    assert "collide" in capsys.readouterr().err
    assert not (repo.bundle / "symbols/domain/impact/Foo.md").exists()          # nothing was written half-way


def test_a_syntax_error_in_a_covered_source_is_a_finding_not_a_traceback(repo, capsys):
    edit(repo.root / "src/eija_studio/application/service.py", "class Studio:", "class Studio(:")
    report = run_checks(repo)
    assert "BROKEN_SOURCE" in codes(report) and not report.ok
    assert cli.main(["--root", str(repo.root), "sync"]) == 1
    assert "cannot build the bundle" in capsys.readouterr().err


# ---- honest labels on the retrieval surface -----------------------------------------------------

def test_planned_techniques_are_labelled_in_the_verification_index(repo):
    index = (repo.bundle / "verification/index.md").read_text(encoding="utf-8")
    planned = [line for line in index.split("\n") if "(bounded-model-check.md)" in line or "(smt-proof.md)" in line]
    assert planned and all("Planned (not implemented)" in line for line in planned)
    implemented = [line for line in index.split("\n") if "integration-test.md" in line]
    assert implemented and "Implemented:" in implemented[0]


def test_unrun_criteria_and_planned_pages_are_labelled_where_a_retriever_reads_them(repo):
    assert "Planned (not implemented)" in split_page((repo.bundle / "verification/tlc-model-check.md").read_text(encoding="utf-8"))[0]["description"]
    rows = csv.DictReader((repo.root / "docs/verification/ACCEPTANCE_MATRIX.csv").read_text(encoding="utf-8").splitlines())
    not_run = next(row["id"] for row in rows if row["v0_2_status"] == "NOT_RUN")
    assert split_page((repo.bundle / f"requirements/{not_run.lower()}.md").read_text(encoding="utf-8"))[0]["description"].startswith("NOT_RUN: ")
    assert "# Acceptance Criteria\n" in (repo.bundle / "requirements/index.md").read_text(encoding="utf-8")


def test_planned_pages_stay_draft_even_when_the_governing_adr_is_accepted(repo):
    adr = repo.root / "docs/adr/0018-formal-vv-portfolio.md"
    text = adr.read_text(encoding="utf-8")
    edit(adr, next(line for line in text.split("\n") if line.startswith("* Status:")), "* Status: accepted")
    sync(repo)
    for page in ("bend-proof", "smt-proof", "tlc-model-check"):
        assert split_page((repo.bundle / f"verification/{page}.md").read_text(encoding="utf-8"))[0]["status"] == "draft"


def test_okf_gate_tiers_keep_the_code_linked_checks_out_of_fast():
    from quality.okf.extract import gate_pages

    tags = {p.title: p.tags for p in gate_pages(Repo(ROOT)) if p.path.startswith("gates/okf/")}
    assert "fast" in tags["nox -s okf_structure"] and "fast" not in tags["nox -s okf"]
    assert {"full", "release"} <= set(tags["nox -s okf"])
