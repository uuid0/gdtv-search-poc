import datetime
import re
from pathlib import Path
from subprocess import run, PIPE
from time import time, sleep
from uuid import uuid4
from pandas import Timedelta

from transcribe.preprocessing import WhisperPreprocessor
from transcribe.types import Transcript, TranscriptWord


class WhisperTranscriber:
    _preprocessor: WhisperPreprocessor
    _work_dir: Path
    _whisper_bin: Path
    _model_path: Path
    _model_name: str
    _num_whisper_threads: int

    def __init__(
            self,
            work_dir: Path,
            whisper_bin: Path,
            model_path: Path,
            model_name: str = "ggml-medium-q5_0.bin",
            num_whisper_threads: int = 1,
    ):
        self._preprocessor = WhisperPreprocessor()
        self._work_dir = work_dir
        self._whisper_bin = whisper_bin
        self._model_path = model_path
        self._model_name = model_name
        self._num_whisper_threads = num_whisper_threads

    def transcribe(
            self,
            video_path: Path,
    ) -> Transcript:
        started_at = time()
        tmp_id = uuid4()
        tmp_dir = self._work_dir / str(tmp_id)
        tmp_dir.mkdir(parents=False, exist_ok=False)
        audio_path = tmp_dir / "audio.wav"
        try:
            self._preprocessor.prepare_audio(
                video_path=video_path,
                output_path=audio_path,
            )
            words, duration_ms = self._transcribe_audio(
                audio_path=audio_path,
            )
            elapsed_seconds = time() - started_at
            return Transcript(
                audio_path=str(audio_path),
                words=words,
                elapsed_seconds=elapsed_seconds,
                duration_ms=duration_ms,
            )
        finally:
            audio_path.unlink(missing_ok=True)
            tmp_dir.rmdir()

    def _transcribe_audio(
            self,
            audio_path: Path,
    ) -> tuple[list[TranscriptWord], int]:
        ok, stdout, stderr = self._call_whisper(
            audio_path=audio_path,
        )
        if not ok:
            raise RuntimeError(stderr)
        return self._parse_to_transcript(
            raw=stdout,
        )

    def _call_whisper(
            self,
            audio_path: Path,
            language: str = "en",
    ) -> tuple[bool, str, str]:
        cmd = [
            str(self._whisper_bin),
            "-ml", "1",
            "-m", str(self._model_path / self._model_name),
            "-l", language,
            "-t", str(self._num_whisper_threads),
            "-f", str(audio_path.absolute()),
        ]
        result = run(
            cmd,
            stderr=PIPE,
            stdout=PIPE,
        )
        return result.returncode == 0, result.stdout.decode("utf-8"), result.stderr.decode("utf-8")

    def _parse_to_transcript(self, raw: str) -> tuple[list[TranscriptWord], int]:
        lines = raw.splitlines()
        words: list[TranscriptWord] = []
        cur_word: TranscriptWord | None = None
        duration_ms = 0
        line_pattern = re.compile(r'^\[([0-9:.]*) --> ([0-9:.]*)\]  (.*)$')
        for line in lines:
            m = line_pattern.match(line)
            if m:
                start_s, end_s, word = m.groups()
                start_ms = int(Timedelta(start_s).total_seconds() * 1000)
                end_ms = int(Timedelta(end_s).total_seconds() * 1000)
                if end_ms > duration_ms:
                    duration_ms = end_ms
                if word.startswith(" "):
                    if cur_word is not None:
                        words.append(cur_word)
                        cur_word = None
                    word = word.strip()
                if cur_word is None:
                    cur_word = TranscriptWord(
                        start_ms=start_ms,
                        end_ms=end_ms,
                        word=word,
                    )
                else:
                    cur_word["end_ms"] = end_ms
                    cur_word["word"] += word
        if cur_word is not None:
            words.append(cur_word)
        return words, duration_ms
