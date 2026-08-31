from typing import List, Set
from database.db import db_session
from config import ACHIEVEMENT_DEFINITIONS
from models.achievement import UserAchievement

def get_unlocked_achievement_ids() -> Set[str]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT achievement_id FROM user_achievements")
        return {row['achievement_id'] for row in cursor.fetchall()}

def get_all_unlocked_achievements() -> List[UserAchievement]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_achievements ORDER BY unlocked_at DESC")
        return [UserAchievement(**dict(row)) for row in cursor.fetchall()]

def evaluate_and_unlock_achievements(stats: dict) -> List[str]:
    """
    Evaluates current stats against achievement definitions.
    Returns a list of newly unlocked achievement IDs.
    """
    unlocked_ids = get_unlocked_achievement_ids()
    newly_unlocked = []
    
    for definition in ACHIEVEMENT_DEFINITIONS:
        ach_id = definition['id']
        if ach_id in unlocked_ids:
            continue
            
        req = definition['requirement']
        category = definition['category']
        
        is_unlocked = False
        if category == 'green_streak' and stats['max_green'] >= req:
            is_unlocked = True
        elif category == 'red_streak' and stats['max_red'] >= req:
            is_unlocked = True
        elif category == 'study_time' and stats['total_study'] >= req:
            is_unlocked = True
        elif category == 'tasks' and stats['total_tasks'] >= req:
            is_unlocked = True
        elif category == 'record_time' and stats['max_study_day'] >= req:
            is_unlocked = True
            
        if is_unlocked:
            newly_unlocked.append(ach_id)
            
    if newly_unlocked:
        with db_session() as conn:
            cursor = conn.cursor()
            for ach_id in newly_unlocked:
                cursor.execute("INSERT OR IGNORE INTO user_achievements (achievement_id) VALUES (?)", (ach_id,))
                
    return newly_unlocked

def get_achievement_progress(stats: dict) -> dict:
    """Returns progress mapping for each achievement."""
    progress = {}
    for definition in ACHIEVEMENT_DEFINITIONS:
        ach_id = definition['id']
        req = definition['requirement']
        category = definition['category']
        
        current = 0
        if category == 'green_streak': current = stats['max_green']
        elif category == 'red_streak': current = stats['max_red']
        elif category == 'study_time': current = stats['total_study']
        elif category == 'tasks': current = stats['total_tasks']
        elif category == 'record_time': current = stats['max_study_day']
        
        progress[ach_id] = min(current, req)
        
    return progress
