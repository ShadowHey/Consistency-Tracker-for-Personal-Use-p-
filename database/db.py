import sqlite3
import os
from contextlib import contextmanager
from config import APP_DATA_DIR, DB_PATH

def get_connection():
    """Returns a new connection to the SQLite database."""
    if not APP_DATA_DIR.exists():
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def db_session():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
