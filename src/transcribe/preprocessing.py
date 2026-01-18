from pathlib import Path
from subprocess import PIPE, Popen
from typing import TypedDict


class WhisperPreprocessor:
    # Settings for use with whisper
    _sample_rate_hz: int = 16000
    _channels: int = 1

    def __init__(self):
        pass

    def prepare_audio(
            self,
            video_path: Path,
            output_path: Path,
    ):
        cmd = [
            "ffmpeg",
            "-loglevel", "quiet",
            "-i", str(video_path.absolute()),
            "-ar", str(self._sample_rate_hz),
            "-ac", str(self._channels),
            str(output_path.absolute()),
        ]
        print(" ".join(cmd))
        with Popen(cmd, stdout=PIPE, stderr=PIPE) as p:
            out, err = p.communicate()
            if p.returncode != 0:
                raise RuntimeError(f"Failed to extract audio from video ('{video_path}'): {err}")
