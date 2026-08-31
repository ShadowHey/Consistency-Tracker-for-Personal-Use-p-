import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from database.db import db_session
from config import GREEN_DAY_TASK_REQUIREMENT, RED_DAY_STUDY_REQUIREMENT

def get_day_boundaries(date_str: str) -> tuple[int, int]:
    """Returns the start and end Unix timestamps for a given YYYY-MM-DD string."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    start_ts = int(dt.timestamp())
    end_dt = dt + timedelta(days=1)
    end_ts = int(end_dt.timestamp())
    return start_ts, end_ts

def calculate_day_status(date_str: str) -> Dict[str, Any]:
    """Calculates the tasks, study seconds, and classification for a single day."""
    start_ts, end_ts = get_day_boundaries(date_str)
    now = int(time.time())
    
    with db_session() as conn:
        cursor = conn.cursor()
        
        # 1. Get completed tasks
        cursor.execute("SELECT COUNT(*) as count FROM task_completions WHERE date = ?", (date_str,))
        completed_tasks = cursor.fetchone()['count']
        
        # 2. Get study seconds
        cursor.execute("""
            SELECT start_timestamp, end_timestamp 
            FROM study_sessions 
            WHERE start_timestamp < ? AND (end_timestamp >= ? OR end_timestamp IS NULL)
        """, (end_ts, start_ts))
        
        study_seconds = 0
        for row in cursor.fetchall():
            s_start = max(row['start_timestamp'], start_ts)
            s_end = min(row['end_timestamp'] or now, end_ts)
            if s_end > s_start:
                study_seconds += (s_end - s_start)
                
    # 3. Classify
    is_active = completed_tasks > 0 or study_seconds > 0
    is_green_day = completed_tasks >= GREEN_DAY_TASK_REQUIREMENT
    is_red_day = study_seconds >= RED_DAY_STUDY_REQUIREMENT
    
    # Green level
    green_level = 0
    if completed_tasks > 0:
        green_level = min(8, completed_tasks)
        
    # Red level
    red_level = 0
    if study_seconds > 0:
        red_level = min(8, int(study_seconds // 3600))
        if red_level == 0 and study_seconds > 0:
            red_level = 1 # faint red for < 1 hour
            
    return {
        "date": date_str,
        "completed_tasks": completed_tasks,
        "study_seconds": study_seconds,
        "is_active": is_active,
        "is_green_day": is_green_day,
        "is_red_day": is_red_day,
        "green_level": green_level,
        "red_level": red_level
    }

def get_contribution_data(days: int = 365) -> List[Dict[str, Any]]:
    """Returns the daily status for the last `days` days, up to today."""
    today = datetime.now()
    data = []
    # Optimization: We could batch query this, but SQLite is fast enough for 365 days
    # Wait, 365 separate queries per day is 365 * 2 = 730 queries. Let's do it efficiently.
    
    # Efficient approach:
    # 1. Get all task completions for the date range
    # 2. Get all study sessions for the date range
    # 3. Bucket them in Python
    
    start_dt = today - timedelta(days=days - 1)
    start_date_str = start_dt.strftime("%Y-%m-%d")
    end_date_str = today.strftime("%Y-%m-%d")
    
    start_ts, _ = get_day_boundaries(start_date_str)
    _, end_ts = get_day_boundaries(end_date_str)
    
    task_counts = {}
    session_data = []
    
    with db_session() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT date, COUNT(*) as count FROM task_completions WHERE date >= ? AND date <= ? GROUP BY date", (start_date_str, end_date_str))
        for row in cursor.fetchall():
            task_counts[row['date']] = row['count']
            
        cursor.execute("SELECT start_timestamp, end_timestamp FROM study_sessions WHERE start_timestamp < ? AND (end_timestamp >= ? OR end_timestamp IS NULL)", (end_ts, start_ts))
        session_data = cursor.fetchall()

    now = int(time.time())
    
    for i in range(days):
        dt = start_dt + timedelta(days=i)
        date_str = dt.strftime("%Y-%m-%d")
        
        d_start_ts, d_end_ts = get_day_boundaries(date_str)
        
        completed_tasks = task_counts.get(date_str, 0)
        
        study_seconds = 0
        for s in session_data:
            # Overlap check
            if s['start_timestamp'] < d_end_ts and (s['end_timestamp'] is None or s['end_timestamp'] >= d_start_ts):
                s_start = max(s['start_timestamp'], d_start_ts)
                s_end = min(s['end_timestamp'] or now, d_end_ts)
                if s_end > s_start:
                    study_seconds += (s_end - s_start)
                    
        is_active = completed_tasks > 0 or study_seconds > 0
        
        green_level = min(8, completed_tasks) if completed_tasks > 0 else 0
        red_level = 0
        if study_seconds > 0:
            red_level = min(8, int(study_seconds // 3600))
            if red_level == 0:
                red_level = 1
                
        data.append({
            "date": date_str,
            "completed_tasks": completed_tasks,
            "study_seconds": study_seconds,
            "is_active": is_active,
            "is_green_day": completed_tasks >= GREEN_DAY_TASK_REQUIREMENT,
            "is_red_day": study_seconds >= RED_DAY_STUDY_REQUIREMENT,
            "green_level": green_level,
            "red_level": red_level
        })
        
    return data

def calculate_streaks(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates streaks from a list of chronological day data."""
    current_active = 0
    max_active = 0
    current_green = 0
    max_green = 0
    current_red = 0
    max_red = 0
    
    total_study = 0
    max_study_day = 0
    total_tasks = 0
    active_days_count = 0
    green_days_count = 0
    red_days_count = 0
    
    for day in data:
        # Accumulators
        total_study += day['study_seconds']
        total_tasks += day['completed_tasks']
        
        if day['study_seconds'] > max_study_day:
            max_study_day = day['study_seconds']
            
        if day['is_active']:
            active_days_count += 1
            current_active += 1
            max_active = max(max_active, current_active)
        else:
            current_active = 0
            
        if day['is_green_day']:
            green_days_count += 1
            current_green += 1
            max_green = max(max_green, current_green)
        else:
            current_green = 0
            
        if day['is_red_day']:
            red_days_count += 1
            current_red += 1
            max_red = max(max_red, current_red)
        else:
            current_red = 0
            
    avg_study = (total_study // active_days_count) if active_days_count > 0 else 0
    
    return {
        "current_active": current_active,
        "max_active": max_active,
        "current_green": current_green,
        "max_green": max_green,
        "current_red": current_red,
        "max_red": max_red,
        "total_study": total_study,
        "max_study_day": max_study_day,
        "avg_study": avg_study,
        "total_tasks": total_tasks,
        "active_days_count": active_days_count,
        "green_days_count": green_days_count,
        "red_days_count": red_days_count
    }
