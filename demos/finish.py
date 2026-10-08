"""Finish a recorded take for sharing: the browser video framed on a stage, as a 1080p H.264 MP4.

The take itself (`demos/output/<key>.webm`) is the evidence and is never altered. Finishing only frames it: the
video is scaled down, given rounded corners and a soft shadow, and set on a dark gradient, the way screen-recording
editors present a product video. Nothing is cut, sped up or reordered, so what the MP4 shows is what the take shows.
Zooms, chapters and captions are recorded live in the browser by the scenario (`demos.lib.recorder`), not added here.

ffmpeg must be on PATH; without it the CLI reports NOT_RUN.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

_TIMEOUT_S = 1800


class FfmpegMissingError(RuntimeError):
    """ffmpeg is not installed: NOT_RUN, never a pass."""


@dataclass(frozen=True)
class Stage:
    """Output canvas and where the framed video sits on it. The default keeps the 16:10 take at 94% height."""

    width: int = 1920
    height: int = 1080
    video_width: int = 1616
    video_height: int = 1010
    radius: int = 18
    shadow_blur: int = 28

    @property
    def x(self) -> int:
        return (self.width - self.video_width) // 2

    @property
    def y(self) -> int:
        return (self.height - self.video_height) // 2


def _ffmpeg() -> str:
    found = shutil.which("ffmpeg")
    if found is None:
        raise FfmpegMissingError("ffmpeg is not on PATH")
    return found


def _run(argv: list[str]) -> None:
    # argv[0] is the resolved ffmpeg path and every other element is built here: no shell, no user string.
    subprocess.run(argv, check=True, capture_output=True, timeout=_TIMEOUT_S)  # noqa: S603


def _rounded(width: int, height: int, radius: int) -> str:
    """geq expression: 255 inside a rounded rectangle filling the frame, 0 outside."""
    return (f"255*lte(hypot(max(0,abs(X-{width}/2)-{width / 2 - radius}),"
            f"max(0,abs(Y-{height}/2)-{height / 2 - radius})),{radius})")


def _still(ffmpeg: str, source: str, chain: str, out: Path) -> None:
    _run([ffmpeg, "-v", "error", "-y", "-f", "lavfi", "-i", source, "-vf", chain, "-frames:v", "1", str(out)])


DEFAULT_STAGE = Stage()


def finish(source: Path, out: Path, stage: Stage = DEFAULT_STAGE) -> Path:
    """Render `source` (any video ffmpeg reads) framed on the stage into `out` (MP4, H.264, faststart)."""
    ffmpeg = _ffmpeg()
    if not source.is_file():
        raise FileNotFoundError(source)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="demo-finish-") as tmp:
        mask, backdrop = Path(tmp) / "mask.png", Path(tmp) / "stage.png"
        w, h = stage.video_width, stage.video_height
        _still(ffmpeg, f"color=c=black:s={w}x{h}", f"format=gray,geq=lum='{_rounded(w, h, stage.radius)}'", mask)
        # Diagonal gradient in the title cards' greens, with the video's shadow baked in (offset 10px down).
        gradient = (f"format=rgb24,geq=r='11+22*(X+Y)/{stage.width + stage.height}':"
                    f"g='21+42*(X+Y)/{stage.width + stage.height}':b='17+30*(X+Y)/{stage.width + stage.height}'")
        shadow = (f"[1:v]format=gray,geq=lum='{_rounded(w, h, stage.radius)}',"
                  f"pad={stage.width}:{stage.height}:{stage.x}:{stage.y + 10}:black,"
                  f"boxblur={stage.shadow_blur}:2,lutyuv=y='val*0.6'[a];"
                  f"color=c=black:s={stage.width}x{stage.height},format=gray[k];[k][a]alphamerge[s];"
                  "[0:v][s]overlay=0:0")
        _run([ffmpeg, "-v", "error", "-y",
              "-f", "lavfi", "-i", f"color=c=black:s={stage.width}x{stage.height}",
              "-f", "lavfi", "-i", f"color=c=black:s={w}x{h}",
              "-filter_complex", f"[0:v]{gradient}[g];{shadow.replace('[0:v][s]', '[g][s]')}",
              "-frames:v", "1", str(backdrop)])
        graph = (f"[0:v]scale={w}:{h}:flags=lanczos,format=rgba[v];[2:v]format=gray[m];[v][m]alphamerge=shortest=1[vr];"
                 f"[1:v][vr]overlay={stage.x}:{stage.y}:shortest=1,format=yuv420p[out]")
        _run([ffmpeg, "-v", "error", "-y", "-i", str(source), "-loop", "1", "-i", str(backdrop),
              "-loop", "1", "-i", str(mask), "-filter_complex", graph, "-map", "[out]", "-r", "30",
              "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-movflags", "+faststart", str(out)])
    return out
