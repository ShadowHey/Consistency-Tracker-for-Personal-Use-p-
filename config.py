import os
from pathlib import Path

# Data directory
APP_DATA_DIR = Path.home() / "Library" / "Application Support" / "StudyTracker"
DB_PATH = APP_DATA_DIR / "data.db"

# Core definitions
GREEN_DAY_TASK_REQUIREMENT = 3
RED_DAY_STUDY_REQUIREMENT = 8 * 60 * 60  # 8 hours in seconds
GRAPH_DAYS = 365

# Thresholds
# Green levels (0 to 8) based on tasks completed
# 0 = empty/no green
# 1 = 1 task
# 2 = 2 tasks
# 3 = 3 tasks
# 4 = 4 tasks
# 5 = 5 tasks
# 6 = 6 tasks
# 7 = 7 tasks
# 8 = 8+ tasks

# Red levels (0 to 8) based on study time
# Target is 8 hours (28800 seconds)
# level = min(8, study_seconds // 3600)  (1 hour = 1 level)

# Colors
THEME_COLORS = {
    "background": "#0D1117",
    "panel": "#161B22",
    "text_primary": "#C9D1D9",
    "text_secondary": "#8B949E",
    "border": "#30363D",
    
    # Contribution Graph Colors (Base black + greens and reds)
    "graph_empty": "#161B22",
    "graph_outline": "rgba(255, 255, 255, 0.05)",
    
    "green_levels": [
        "#161B22",  # 0
        "#0E4429",  # 1 (faint)
        "#006D32",  # 2 (faint)
        "#26A641",  # 3 (green level 1)
        "#2DA346",  # 4
        "#33A14B",  # 5
        "#399E50",  # 6
        "#3F9C55",  # 7
        "#39D353",  # 8 (max)
    ],
    
    "red_levels": [
        "rgba(0, 0, 0, 0)",      # 0
        "rgba(110, 20, 20, 0.3)",  # 1 (1 hr)
        "rgba(130, 20, 20, 0.4)",  # 2
        "rgba(150, 25, 25, 0.5)",  # 3
        "rgba(170, 30, 30, 0.6)",  # 4
        "rgba(190, 35, 35, 0.7)",  # 5
        "rgba(210, 40, 40, 0.8)",  # 6
        "rgba(230, 45, 45, 0.9)",  # 7
        "rgba(255, 50, 50, 1.0)",  # 8 (8 hrs max)
    ],
    
    "gold": "#D4AF37"
}

# Achievements
ACHIEVEMENT_DEFINITIONS = [
    # Green Streaks
    {"id": "green_streak_3", "name": "Getting Started", "description": "3 consecutive green days.", "category": "green_streak", "requirement": 3, "tier": "bronze"},
    {"id": "green_streak_7", "name": "One Week Green", "description": "7 consecutive green days.", "category": "green_streak", "requirement": 7, "tier": "bronze"},
    {"id": "green_streak_30", "name": "Monthly Master", "description": "30 consecutive green days.", "category": "green_streak", "requirement": 30, "tier": "silver"},
    {"id": "green_streak_100", "name": "Century Club", "description": "100 consecutive green days.", "category": "green_streak", "requirement": 100, "tier": "gold"},
    
    # Red Streaks
    {"id": "red_streak_3", "name": "Deep Dive", "description": "3 consecutive red days.", "category": "red_streak", "requirement": 3, "tier": "bronze"},
    {"id": "red_streak_7", "name": "Hell Week", "description": "7 consecutive red days.", "category": "red_streak", "requirement": 7, "tier": "silver"},
    
    # Study Time
    {"id": "study_time_10", "name": "First 10 Hours", "description": "Study for 10 hours total.", "category": "study_time", "requirement": 10 * 3600, "tier": "bronze"},
    {"id": "study_time_100", "name": "Dedicated", "description": "Study for 100 hours total.", "category": "study_time", "requirement": 100 * 3600, "tier": "silver"},
    {"id": "study_time_500", "name": "Scholar", "description": "Study for 500 hours total.", "category": "study_time", "requirement": 500 * 3600, "tier": "gold"},
    
    # Task Completion
    {"id": "tasks_10", "name": "Task Starter", "description": "Complete 10 tasks.", "category": "tasks", "requirement": 10, "tier": "bronze"},
    {"id": "tasks_100", "name": "Task Machine", "description": "Complete 100 tasks.", "category": "tasks", "requirement": 100, "tier": "silver"},
    {"id": "tasks_500", "name": "Executioner", "description": "Complete 500 tasks.", "category": "tasks", "requirement": 500, "tier": "gold"},
    
    # Daily Records
    {"id": "record_8h", "name": "The 8-Hour Shift", "description": "Study for 8 hours in one day.", "category": "record_time", "requirement": 8 * 3600, "tier": "silver"},
    {"id": "record_12h", "name": "Insomniac", "description": "Study for 12 hours in one day.", "category": "record_time", "requirement": 12 * 3600, "tier": "gold"},
]
