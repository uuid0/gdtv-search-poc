from datetime import datetime
from typing import TypedDict


class ConceptDocument(TypedDict):
    id: str
    concept_name: str
    description: str
    keywords: list[str]
    share: float
    duration_ms: int
    course_id: str
    video_id: str
    updated_at: datetime
    newly_introduced: bool
    further_discussed: bool
    just_mentioned: bool
