import time
from typing import Optional, List
from database.db import db_session
from models.study_session import StudySession

def get_running_session() -> Optional[StudySession]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_sessions WHERE status = 'RUNNING' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            return StudySession(**dict(row))
    return None

def start_session() -> int:
    """Starts a new study session."""
    # Ensure no other session is running
    running = get_running_session()
    if running:
        return running.id
        
    now = int(time.time())
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO study_sessions (start_timestamp, duration_seconds, status) VALUES (?, 0, 'RUNNING')",
            (now,)
        )
        return cursor.lastrowid

def pause_session(session_id: int):
    """Pauses a running session."""
    now = int(time.time())
    with db_session() as conn:
        cursor = conn.cursor()
        # Get start time
        cursor.execute("SELECT start_timestamp FROM study_sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return
            
        start_ts = row['start_timestamp']
        duration = now - start_ts
        
        cursor.execute(
            "UPDATE study_sessions SET end_timestamp = ?, duration_seconds = ?, status = 'PAUSED' WHERE id = ?",
            (now, duration, session_id)
        )

def resume_session() -> int:
    """Resumes by starting a new session (the UI will aggregate them)."""
    return start_session()

def stop_session(session_id: Optional[int] = None):
    """Stops the current session and marks all paused sessions as completed."""
    now = int(time.time())
    with db_session() as conn:
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute("SELECT start_timestamp, status FROM study_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row and row['status'] == 'RUNNING':
                start_ts = row['start_timestamp']
                duration = now - start_ts
                cursor.execute(
                    "UPDATE study_sessions SET end_timestamp = ?, duration_seconds = ?, status = 'COMPLETED' WHERE id = ?",
                    (now, duration, session_id)
                )
        
        # Mark all paused sessions as completed
        cursor.execute("UPDATE study_sessions SET status = 'COMPLETED' WHERE status = 'PAUSED'")

def get_todays_sessions(start_of_day_ts: int, end_of_day_ts: int) -> List[StudySession]:
    """Get all sessions that overlap with today."""
    with db_session() as conn:
        cursor = conn.cursor()
        # A session overlaps if it started before end_of_day and (ended after start_of_day or is still running)
        cursor.execute("""
            SELECT * FROM study_sessions 
            WHERE start_timestamp < ? 
            AND (end_timestamp >= ? OR end_timestamp IS NULL)
            ORDER BY start_timestamp ASC
        """, (end_of_day_ts, start_of_day_ts))
        return [StudySession(**dict(row)) for row in cursor.fetchall()]
