"""The ADR index generator: parsing, determinism, drift detection."""
from pathlib import Path

from quality.tools.adr_index import END, START, collect, main, parse_adr

README = f"""# Architecture decision records

intro

{START}
old table
{END}

## Reserved numbers
kept
"""


def adr(dir_: Path, name: str, heading: str, status: str = "accepted") -> Path:
    path = dir_ / name
    path.write_bytes(f"# {heading}\n\n* Status: {status}\n* Date: 2026-09-29\n".encode())
    return path


def tree(tmp_path: Path) -> Path:
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    (adr_dir / "README.md").write_bytes(README.encode())
    adr(adr_dir, "0015-licence.md", "ADR-0015: Apache-2.0")
    adr(adr_dir, "0059-hci-colour.md", "HCI-ADR-0059: Colour system", "proposed (until measured)")
    return tmp_path


def test_status_is_reduced_to_its_first_phrase_and_hci_prefix_is_accepted(tmp_path):
    adr_dir = tree(tmp_path) / "docs" / "adr"
    parsed, problem = parse_adr(adr_dir / "0059-hci-colour.md")
    assert problem is None and parsed.status == "proposed" and parsed.title == "Colour system"


def test_write_then_check_is_clean_and_idempotent(tmp_path):
    root = tree(tmp_path)
    assert main(["--write", "--root", str(root)]) == 0
    first = (root / "docs" / "adr" / "README.md").read_bytes()
    assert main(["--write", "--root", str(root)]) == 0
    assert (root / "docs" / "adr" / "README.md").read_bytes() == first
    assert main(["--check", "--root", str(root)]) == 0
    assert b"[0015](0015-licence.md)" in first and b"## Reserved numbers\nkept" in first


def test_check_fails_when_an_adr_is_added_without_regenerating(tmp_path):
    root = tree(tmp_path)
    assert main(["--write", "--root", str(root)]) == 0
    adr(root / "docs" / "adr", "0016-oss-first.md", "ADR-0016: OSS first")
    assert main(["--check", "--root", str(root)]) == 1


def test_duplicate_numbers_and_mismatched_headings_are_reported(tmp_path):
    root = tree(tmp_path)
    adr(root / "docs" / "adr", "0015-other.md", "ADR-0015: Duplicate")
    adr(root / "docs" / "adr", "0020-wrong.md", "ADR-0021: Heading disagrees with the file name")
    _, problems = collect(root / "docs" / "adr")
    assert any("duplicate ADR number 0015" in p for p in problems)
    assert any("heading says ADR-0021" in p for p in problems)


def test_a_record_without_status_is_refused(tmp_path):
    root = tree(tmp_path)
    (root / "docs" / "adr" / "0030-nostatus.md").write_bytes(b"# ADR-0030: No status\n\ntext\n")
    _, problems = collect(root / "docs" / "adr")
    assert any("no '* Status:" in p for p in problems)
