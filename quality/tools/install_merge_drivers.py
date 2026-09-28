"""Register the repository's merge drivers (eija-toml, eija-generated) in THIS clone's git config.

Git stores merge-driver definitions in .git/config, which is per clone and not versioned, so each
maintainer runs this once (worktrees of one clone share it). Without it git silently falls back to its
ordinary line-based merge, so nothing breaks; you just get the old conflicts back.

    python -m quality.tools.install_merge_drivers
"""
# ruff: noqa: T201
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRIVER = "eija-toml"


ATTRIBUTES_MARKER = "info/attributes"
ATTRIBUTES = """# EIJA merge drivers (written by quality/tools/install_merge_drivers.py)
# Clone-level so they also apply to lane branches created before the committed .gitattributes existed:
# git reads merge attributes from the branch being merged INTO.
docs/adr/README.md merge=eija-generated
pyproject.toml merge=eija-toml
docs/oss/REGISTER.md merge=union
AGENTS.md merge=union
.gitignore merge=union
"""


def write_clone_attributes() -> None:
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=ROOT, check=True,  # noqa: S607
                            capture_output=True, text=True).stdout.strip()
    path = (ROOT / common / "info" / "attributes").resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(ATTRIBUTES.encode("utf-8"))


def main() -> int:
    script = (ROOT / "quality" / "tools" / "tomlmerge.py").as_posix()
    python = Path(sys.executable).as_posix()
    commands = [
        ["git", "config", f"merge.{DRIVER}.name", "Key-granular three-way merge for TOML"],
        ["git", "config", f"merge.{DRIVER}.driver", f'"{python}" "{script}" %O %A %B'],
        # generated files: keep the side that still carries the generator marker; regenerate afterwards
        ["git", "config", "merge.eija-generated.name", "Keep the generated-marker side; regenerate"],
        ["git", "config", "merge.eija-generated.driver",
         f'"{python}" "{(ROOT / "quality" / "tools" / "keep_generated.py").as_posix()}" %O %A %B'],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)  # noqa: S603 - argv is built from constants above
    write_clone_attributes()
    print(f"registered merge drivers -> {python} (attributes: {ATTRIBUTES_MARKER})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
