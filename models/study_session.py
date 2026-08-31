from dataclasses import dataclass
from typing import Optional

@dataclass
class StudySession:
    id: int
    start_timestamp: int
    end_timestamp: Optional[int]
    duration_seconds: int
    status: str
    created_at: str
