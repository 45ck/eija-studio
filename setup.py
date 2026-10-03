"""Setuptools adapter: bundle the single authored packs tree into wheel build output."""
import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py


class BuildWithPacks(build_py):
    """Copy declared JSON pack data without creating a second source-tree copy."""

    def run(self):
        if self.editable_mode:
            super().run()
            return
        project = Path(__file__).resolve().parent
        source = project / "packs"
        files = sorted(source.rglob("*.json"))
        if not (source / "default.json").is_file() or not any(path.name == "pack.json" for path in files):
            raise ValueError("The authored default pointer and runtime packs are required for a distribution")
        for path in files:
            if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()):
                raise ValueError("Pack distribution inputs must stay inside the authored packs tree")
        build_root = Path(self.build_lib).resolve()
        target = build_root / "eija_studio" / "resources" / "packs"
        resolved = target.resolve()
        if (not resolved.is_relative_to(build_root) or resolved.is_relative_to(project / "src")
                or resolved.is_relative_to(source.resolve())):
            raise ValueError("Pack build output must be separate from authored source")
        super().run()
        if target.exists():
            shutil.rmtree(target)
        for path in files:
            destination = target / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)


if __name__ == "__main__":
    setup(cmdclass={"build_py": BuildWithPacks})
