from typing import TypedDict

class TranscriptWord(TypedDict):
    start_ms: int
    end_ms: int
    word: str

class Transcript(TypedDict):
    audio_path: str
    words: list[TranscriptWord]
    duration_ms: int
    elapsed_seconds: float
