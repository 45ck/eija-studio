"""Register the repository's merge drivers in THIS clone's git config.

Git stores merge-driver definitions in .git/config, which is per clone and not versioned, so each
maintainer runs this once (worktrees of one clone share it). Without it git silently falls back to its
ordinary line-based merge, so nothing breaks; you just get the old conflicts back.

    python -m quality.tools.install_merge_drivers
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRIVER = "eija-toml"


def main() -> int:
    script = (ROOT / "quality" / "tools" / "tomlmerge.py").as_posix()
    python = Path(sys.executable).as_posix()
    commands = [
        ["git", "config", f"merge.{DRIVER}.name", "Key-granular three-way merge for TOML"],
        ["git", "config", f"merge.{DRIVER}.driver", f'"{python}" "{script}" %O %A %B'],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    print(f"registered merge driver {DRIVER!r} -> {python} {script}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
