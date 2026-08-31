from database.db import get_connection

def initialize_db():
    """Create tables if they don't exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                archived BOOLEAN DEFAULT 0
            )
        """)
        
        # Task Completions table
        # Date is stored as YYYY-MM-DD
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                UNIQUE(task_id, date)
            )
        """)
        
        # Study Sessions table
        # status: RUNNING, PAUSED, COMPLETED
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_timestamp INTEGER NOT NULL,
                end_timestamp INTEGER,
                duration_seconds INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User Achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                achievement_id TEXT PRIMARY KEY,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()

if __name__ == "__main__":
    initialize_db()
    print("Database initialized.")
