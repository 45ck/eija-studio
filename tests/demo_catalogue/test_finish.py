"""Finishing frames a take without altering it; missing ffmpeg is NOT_RUN, never a pass."""
import shutil
import subprocess

import pytest

from demos import __main__ as cli
from demos import finish as fin


def test_stage_centres_the_video():
    stage = fin.Stage()
    assert (stage.x, stage.y) == ((1920 - 1616) // 2, (1080 - 1010) // 2)
    assert stage.video_width / stage.video_height == pytest.approx(1440 / 900)


def test_missing_ffmpeg_is_reported_not_passed(tmp_path, monkeypatch):
    monkeypatch.setattr(fin.shutil, "which", lambda _name: None)
    take = tmp_path / "take.webm"
    take.write_bytes(b"x")
    with pytest.raises(fin.FfmpegMissingError):
        fin.finish(take, tmp_path / "out.mp4")


def test_cli_finish_without_a_take_fails(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "OUTPUT", tmp_path)
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    assert cli.main(["finish", "nothing_here"]) == cli.EXIT_FAIL
    assert "no take" in capsys.readouterr().out


@pytest.mark.skipif(shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None, reason="NOT_RUN: ffmpeg")
def test_finish_renders_a_1080p_mp4_of_the_same_length(tmp_path):
    take = tmp_path / "take.webm"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1440x900:d=1:r=25", str(take)],
                   check=True)
    out = fin.finish(take, tmp_path / "take.mp4")
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height:format=duration",
                            "-of", "default=nw=1", str(out)], check=True, capture_output=True, text=True).stdout
    assert "codec_name=h264" in probe and "width=1920" in probe and "height=1080" in probe
    duration = float(next(line for line in probe.splitlines() if line.startswith("duration=")).split("=")[1])
    assert duration == pytest.approx(1.0, abs=0.1)
