"""Create bounded, exact exports and source intake for the fixed navigation proof.

Run from a source checkout with the hci and source-analysis extras installed and
the checkout root on PYTHONPATH. This command starts no server or browser, does
not execute exported code, and never checks out or modifies Git objects/index.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

import repository_navigation_pair as probe

from eija_studio.adapters.repository_changes import RepositoryChanges
from eija_studio.adapters.repository_analysis import syntax_reader
from eija_studio.domain.pack import load_pack

CHECKOUT = Path(__file__).resolve().parents[2]


def sha_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def git_state(repository):
    return {"head": probe._git_read(repository, "rev-parse", "HEAD").decode().strip(),
            "status_sha256": hashlib.sha256(probe._git_read(repository, "status", "--porcelain=v1", "--untracked-files=all")).hexdigest()}


def inventory(repository, commit):
    """Bound archive creation before it starts; the shared validator rechecks the result."""
    rows = probe._git_read(repository, "ls-tree", "-r", "-l", "-z", "--full-tree", commit, "--", *probe.SCOPES)
    result, total, case_names = {}, 0, set()
    for raw in rows.split(b"\0"):
        if not raw:
            continue
        metadata, name = raw.decode("utf-8").split("\t", 1)
        mode, kind, oid, size = metadata.split()
        probe.require(probe.in_scope(name) and probe.excluded_path(name) is None, "EXPORT_PATH_UNSUPPORTED")
        probe.require(kind == "blob" and mode in {"100644", "100755"}, "EXPORT_MODE_UNSUPPORTED")
        probe.require(name not in result and name.casefold() not in case_names, "EXPORT_PATH_COLLISION")
        size = int(size)
        total += size
        probe.require(0 <= size <= probe.MAX_FILE_BYTES and total <= probe.MAX_TOTAL_BYTES, "EXPORT_BYTE_LIMIT")
        result[name] = {"mode": mode, "git_blob": oid, "bytes": size}
        case_names.add(name.casefold())
        probe.require(len(result) <= probe.MAX_FILES, "EXPORT_FILE_LIMIT")
    probe.require(bool(result), "EXPORT_INVENTORY_EMPTY")
    return result, total


def member_bytes(archive, member, expected):
    probe.require(member.isfile() and not member.issym() and not member.islnk(), "ARCHIVE_FILE_NONREGULAR")
    probe.require(not member.mode & ~0o777, "ARCHIVE_SPECIAL_PERMISSION")
    probe.require(bool(member.mode & 0o111) == (expected["mode"] == "100755"), "ARCHIVE_EXECUTABLE_MODE_MISMATCH")
    probe.require(member.size == expected["bytes"] and member.size <= probe.MAX_FILE_BYTES, "ARCHIVE_SIZE_MISMATCH")
    stream = archive.extractfile(member)
    probe.require(stream is not None, "ARCHIVE_CONTENT_UNAVAILABLE")
    with stream:
        data = stream.read(probe.MAX_FILE_BYTES + 1)
    probe.require(len(data) == member.size, "ARCHIVE_CONTENT_LENGTH_MISMATCH")
    algorithm = "sha1" if len(expected["git_blob"]) == 40 else "sha256"
    blob = hashlib.new(algorithm, b"blob " + str(len(data)).encode() + b"\0" + data, usedforsecurity=False).hexdigest()
    probe.require(blob == expected["git_blob"], "ARCHIVE_BLOB_MISMATCH")
    return data, {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "git_blob": blob}


def unpack_owned(archive_path, root, expected):
    """Write only exact, bounded regular members into a new root; never tar.extractall."""
    root.mkdir(exist_ok=False)
    allowed_dirs = {str(parent) for name in expected for parent in PurePosixPath(name).parents if str(parent) != "."}
    directories, files, total = set(), {}, 0
    with tarfile.open(archive_path, "r:") as archive:
        for entries, member in enumerate(archive, start=1):
            probe.require(entries <= probe.MAX_FILES * 4, "ARCHIVE_ENTRY_LIMIT")
            name = member.name.rstrip("/")
            probe.require(probe.excluded_path(name) is None and not PurePosixPath(name).is_absolute(), "ARCHIVE_PATH_UNSAFE")
            if member.isdir():
                probe.require(name in allowed_dirs and name not in directories, "ARCHIVE_DIRECTORY_UNEXPECTED")
                directories.add(name)
                continue
            probe.require(name in expected and name not in files, "ARCHIVE_FILE_UNEXPECTED")
            data, identity = member_bytes(archive, member, expected[name])
            total += len(data)
            probe.require(total <= probe.MAX_TOTAL_BYTES, "ARCHIVE_BYTE_LIMIT")
            destination = root.joinpath(*PurePosixPath(name).parts)
            probe.require(destination.resolve().is_relative_to(root.resolve()), "ARCHIVE_PATH_ESCAPED")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as output:
                output.write(data)
            files[name] = identity
    probe.require(set(files) == set(expected), "ARCHIVE_INVENTORY_MISMATCH")
    return files, total


def export_side(repository, out, side, commit, expected, expected_total):
    tree = probe._tree(repository, commit)
    archive = out / "archives" / (side + ".tar")
    probe.require(not archive.exists(), "ARCHIVE_ALREADY_EXISTS")
    probe._git_read(repository, "archive", "--format=tar", "--output=" + str(archive), commit, "--", *probe.SCOPES)
    probe.require(archive.stat().st_size <= probe.MAX_TOTAL_BYTES + probe.MAX_FILES * 1024 + 10240, "ARCHIVE_BYTE_LIMIT")
    root = out / side
    files, total = unpack_owned(archive, root, expected)
    probe.require(total == expected_total, "EXPORT_TOTAL_MISMATCH")
    spec = {"commit": commit, "tree": tree.tree, "root": str(root), "files": files}
    checked = probe.validate_export(repository, spec, commit)
    return spec, {"commit": commit, "tree": tree.tree, "files": len(files), "bytes": total,
                  "content_sha256": checked["content_sha256"], "app_js": files[probe.APP],
                  "archive": {"path": archive.relative_to(out).as_posix(), "bytes": archive.stat().st_size,
                              "sha256": sha_file(archive)}, "probe_export_validation": "PASS"}


def create_exports(repository, out, inventories, before):
    manifest = {"schema": "eija.navigation-pair-exports.v1", "repository_root": str(repository),
                "scope": list(probe.SCOPES), "pack": probe.PACK,
                "declared_agent_assistance": {"status": "declared", "label": "Codex-assisted",
                    "basis": "Project development record; not authenticated by Git author fields or this export."}}
    checks = {}
    (out / "archives").mkdir()
    for side, commit in probe.PAIR.items():
        manifest[side], checks[side] = export_side(repository, out, side, commit, *inventories[side])
    manifest_path = out / "exports-manifest.json"
    probe.write_json(manifest_path, manifest)
    reread, checked_repository = probe.read_manifest(manifest_path)
    probe.require(checked_repository == repository and reread == manifest, "EXPORT_MANIFEST_RECHECK_MISMATCH")
    subjects = {side: probe.validate_export(repository, manifest[side], commit) for side, commit in probe.PAIR.items()}
    comparison = RepositoryChanges(repository, load_pack(out / "head" / probe.PACK), syntax_reader=syntax_reader)
    intake_path = out / "comparison.json"
    probe.write_json(intake_path, comparison.compare_commits(probe.PAIR["base"], probe.PAIR["head"]))
    intake = probe.validate_intake(intake_path, subjects)
    after = git_state(repository)
    probe.require(before == after, "REPOSITORY_GIT_OBSERVATION_CHANGED")
    return {"schema": "eija.navigation-export-validation.v1", "status": "PASS", "utc": datetime.now(UTC).isoformat(),
            "manifest": "exports-manifest.json", "manifest_sha256": sha_file(manifest_path),
            "comparison": "comparison.json", "intake": intake, "exports": checks,
            "git_before": before, "git_after": after, "git_observation_unchanged": True,
            "script_sha256": sha_file(Path(__file__)), "probe_sha256": sha_file(Path(probe.__file__)),
            "browser": "NOT_RUN", "server": "NOT_RUN", "target_code_execution": "NONE",
            "boundary": "Exact exported source integrity and linked read-only intake only; no behavior or human-value claim."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=CHECKOUT, help="Local EIJA Git checkout containing both fixed commits; defaults to this tooling checkout")
    parser.add_argument("--out", type=Path, required=True, help="New export bundle directory outside the repository; existing directories are refused")
    args = parser.parse_args(argv)
    repository, out = args.repository.expanduser().resolve(), args.out.expanduser().resolve()
    probe.require(not out.exists() and not out.is_symlink(), "OUTPUT_ALREADY_EXISTS")
    probe.require(not out.is_relative_to(repository), "OUTPUT_INSIDE_REPOSITORY")
    probe._validate_root(repository)
    # All immutable inventories must exist and pass the source cap before writing an export.
    inventories = {side: inventory(repository, commit) for side, commit in probe.PAIR.items()}
    before = git_state(repository)
    out.mkdir(parents=True, exist_ok=False)
    try:
        result = create_exports(repository, out, inventories, before)
    except Exception as error:
        result = {"schema": "eija.navigation-export-validation.v1", "status": "NOT_PROVEN",
                  "utc": datetime.now(UTC).isoformat(), "error": {"type": type(error).__name__, "message": str(error)[:1000]},
                  "browser": "NOT_RUN", "server": "NOT_RUN", "target_code_execution": "NONE",
                  "retention": "Partial exports are retained; use a new output directory for a later attempt."}
    probe.write_json(out / "validation.json", result)
    sys.stdout.write(json.dumps({"status": result["status"], "out": str(out), "validation": "validation.json"}) + "\n")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
