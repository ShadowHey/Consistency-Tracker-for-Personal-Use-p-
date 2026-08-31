from typing import List, Set
from database.db import db_session
from models.task import Task

def add_task(name: str) -> int:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (name) VALUES (?)", (name,))
        return cursor.lastrowid

def get_active_tasks() -> List[Task]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE archived = 0 ORDER BY created_at ASC")
        return [Task(**dict(row)) for row in cursor.fetchall()]

def get_completed_task_ids(date: str) -> Set[int]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT task_id FROM task_completions WHERE date = ?", (date,))
        return {row['task_id'] for row in cursor.fetchall()}

def toggle_task_completion(task_id: int, date: str) -> bool:
    """Toggles task completion for a specific date. Returns True if now completed."""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM task_completions WHERE task_id = ? AND date = ?", (task_id, date))
        row = cursor.fetchone()
        
        if row:
            # It was completed, so un-complete it
            cursor.execute("DELETE FROM task_completions WHERE id = ?", (row['id'],))
            return False
        else:
            # It was not completed, so complete it
            cursor.execute("INSERT INTO task_completions (task_id, date) VALUES (?, ?)", (task_id, date))
            return True

def archive_task(task_id: int):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET archived = 1 WHERE id = ?", (task_id,))
