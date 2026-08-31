import os
import time
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# --- MOCKING DB PATH FOR TESTS ---
temp_db_fd, temp_db_path = tempfile.mkstemp()
os.close(temp_db_fd)

import config
config.DB_PATH = Path(temp_db_path)
config.APP_DATA_DIR = Path(temp_db_path).parent

import database.db
database.db.DB_PATH = Path(temp_db_path)
database.db.APP_DATA_DIR = Path(temp_db_path).parent

# --- IMPORTS AFTER MOCKING ---
from database.migrations import initialize_db
from services.task_service import add_task, toggle_task_completion, get_completed_task_ids, get_active_tasks
from services.timer_service import start_session, pause_session, stop_session, get_running_session
from services.stats_service import calculate_day_status, get_contribution_data, calculate_streaks

def setup_module(module):
    """Setup test database before tests."""
    initialize_db()

def teardown_module(module):
    """Cleanup test database after tests."""
    os.remove(temp_db_path)

def test_task_service():
    task_id1 = add_task("Test Task 1")
    task_id2 = add_task("Test Task 2")
    
    tasks = get_active_tasks()
    assert len(tasks) == 2
    
    date_str = "2026-08-31"
    
    # Complete task 1
    completed = toggle_task_completion(task_id1, date_str)
    assert completed == True
    
    completed_ids = get_completed_task_ids(date_str)
    assert task_id1 in completed_ids
    assert task_id2 not in completed_ids
    
    # Uncomplete task 1
    completed = toggle_task_completion(task_id1, date_str)
    assert completed == False
    
    completed_ids = get_completed_task_ids(date_str)
    assert len(completed_ids) == 0

def test_timer_service():
    session_id = start_session()
    running = get_running_session()
    assert running is not None
    assert running.id == session_id
    
    # Simulate time passing by modifying the db row directly for the test
    with database.db.db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE study_sessions SET start_timestamp = start_timestamp - 3600 WHERE id = ?", (session_id,))
        
    pause_session(session_id)
    running = get_running_session()
    assert running is None  # No longer running
    
    with database.db.db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT duration_seconds, status FROM study_sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        assert row['status'] == 'PAUSED'
        assert row['duration_seconds'] >= 3600
        
    stop_session(session_id)
    with database.db.db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM study_sessions WHERE id = ?", (session_id,))
        assert cursor.fetchone()['status'] == 'COMPLETED'

def test_stats_service_and_streaks():
    # Insert some mock data for past days
    today = datetime.now()
    day1 = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    day2 = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    
    task_id = add_task("Streak Task")
    
    # Day 1: 3 tasks (Green)
    toggle_task_completion(task_id, day1)
    toggle_task_completion(add_task("A"), day1)
    toggle_task_completion(add_task("B"), day1)
    
    # Day 2: 8 hours study (Red)
    day2_ts = int((today - timedelta(days=1)).timestamp()) + 3600
    with database.db.db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO study_sessions (start_timestamp, end_timestamp, duration_seconds, status) VALUES (?, ?, ?, 'COMPLETED')",
            (day2_ts, day2_ts + 8*3600, 8*3600)
        )
        
    # Check day 1 status
    status1 = calculate_day_status(day1)
    assert status1['completed_tasks'] == 3
    assert status1['is_green_day'] == True
    assert status1['is_red_day'] == False
    
    # Check day 2 status
    status2 = calculate_day_status(day2)
    assert status2['study_seconds'] == 8 * 3600
    assert status2['is_green_day'] == False
    assert status2['is_red_day'] == True
    
    # Check contribution data and streaks
    data = get_contribution_data(days=5)
    streaks = calculate_streaks(data)
    
    assert streaks['total_study'] >= 8 * 3600
    assert streaks['max_green'] >= 1
    assert streaks['max_red'] >= 1
