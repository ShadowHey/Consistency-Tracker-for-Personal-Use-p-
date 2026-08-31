from dataclasses import dataclass

@dataclass
class Task:
    id: int
    name: str
    created_at: str
    archived: bool = False

@dataclass
class TaskCompletion:
    id: int
    task_id: int
    date: str
    completed_at: str
