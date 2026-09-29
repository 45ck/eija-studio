"""Video to GIF with ffmpeg (palettegen/paletteuse), fitted to the limits by `demos.prgif.fit`.

ffmpeg and ffprobe must be on PATH. When they are not, callers report NOT_RUN (`ToolMissingError`).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from demos.prgif.fit import (
    Candidate,
    DoesNotFitError,
    FitResult,
    Limits,
    Timing,
    candidates,
    fit,
    plan_timing,
)

_TIME = re.compile(r"time=(\d+):(\d+):(\d+(?:\.\d+)?)")
_TIMEOUT_S = 600


class ToolMissingError(RuntimeError):
    """A prerequisite program is not installed: NOT_RUN, never a pass."""


@dataclass(frozen=True)
class VideoInfo:
    width: int
    height: int
    duration_s: float


@dataclass(frozen=True)
class GifReport:
    path: Path
    source: VideoInfo
    timing: Timing
    fit: FitResult

    def summary(self) -> dict[str, object]:
        return {
            "gif": str(self.path), "bytes": self.fit.size,
            "width": self.fit.chosen.width, "fps": self.fit.chosen.fps,
            "seconds": round(self.timing.output_seconds, 2), "speed": round(self.timing.speed, 3),
            "tail_cut": self.timing.cut,
            "attempts": [f"{c.fps}fps/{c.width}px={size}B" for c, size in self.fit.attempts],
        }


def tool(name: str) -> str:
    found = shutil.which(name)
    if found is None:
        raise ToolMissingError(f"{name} is not on PATH")
    return found


def missing_tools() -> list[str]:
    return [name for name in ("ffmpeg", "ffprobe") if shutil.which(name) is None]


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    # argv[0] is a resolved ffmpeg/ffprobe path and the rest are built here: no shell, no user string.
    return subprocess.run(  # noqa: S603
        argv, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=_TIMEOUT_S
    )


def probe(video: Path) -> VideoInfo:
    """Width, height and duration. Browser-recorded WebM often has no duration header: decode to measure it."""
    result = _run([tool("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                   "stream=width,height:format=duration", "-of", "json", str(video)])
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe could not read {video}: {result.stderr.strip()}")
    data = json.loads(result.stdout)
    stream = data["streams"][0]
    duration = data.get("format", {}).get("duration")
    seconds = float(duration) if duration not in (None, "N/A") else _decoded_seconds(video)
    return VideoInfo(int(stream["width"]), int(stream["height"]), seconds)


def _decoded_seconds(video: Path) -> float:
    result = _run([tool("ffmpeg"), "-v", "info", "-nostats", "-stats", "-i", str(video), "-f", "null", "-"])
    matches = _TIME.findall(result.stderr)
    if not matches:
        raise RuntimeError(f"could not measure the duration of {video}")
    hours, minutes, seconds = matches[-1]
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def gif_filter(candidate: Candidate, timing: Timing, trim_start_s: float = 0.0) -> str:
    """One filter graph: trim the lead-in, retime, resample, scale, then a per-file palette."""
    return (
        f"trim=start={trim_start_s:.3f},setpts=(PTS-STARTPTS)/{timing.speed:.4f},"
        f"fps={candidate.fps},scale={candidate.width}:-2:flags=lanczos,split[a][b];"
        "[a]palettegen=max_colors=192:stats_mode=diff[p];"
        "[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
    )


def encode_once(source: Path, target: Path, candidate: Candidate, timing: Timing, trim_start_s: float) -> int:
    argv = [tool("ffmpeg"), "-v", "error", "-y", "-i", str(source),
            "-filter_complex", gif_filter(candidate, timing, trim_start_s),
            "-t", f"{timing.output_seconds:.3f}", "-loop", "0", str(target)]
    result = _run(argv)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({result.returncode}): {result.stderr.strip()[-800:]}")
    return target.stat().st_size


def video_to_gif(source: Path, target: Path, *, limits: Limits = Limits(), trim_start_s: float = 0.0) -> GifReport:
    info = probe(source)
    trim = min(max(trim_start_s, 0.0), max(info.duration_s - 0.5, 0.0))
    timing = plan_timing(info.duration_s - trim, limits)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = fit(lambda c: encode_once(source, target, c, timing, trim),
                     candidates(info.width, limits), limits.max_bytes)
    except DoesNotFitError:
        target.unlink(missing_ok=True)  # never leave an over-limit GIF behind to be published by mistake
        raise
    # The file on disk is the LAST attempt, which is the accepted one because `fit` stops at the first fit.
    return GifReport(path=target, source=info, timing=timing, fit=result)
