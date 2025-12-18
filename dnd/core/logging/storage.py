import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..config import Settings
from ..models.state import GameState


class SessionStorage:
    """SQLite-based session storage."""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Settings.SESSION_DB
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                state_json TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_session(self, game_state: GameState) -> None:
        """Save a game session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        state_json = json.dumps(game_state.model_dump(), default=str)
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions (session_id, created_at, updated_at, state_json)
            VALUES (?, ?, ?, ?)
        """, (
            game_state.session_id,
            game_state.created_at.isoformat(),
            game_state.updated_at.isoformat(),
            state_json
        ))
        
        conn.commit()
        conn.close()
    
    def load_session(self, session_id: str) -> Optional[GameState]:
        """Load a game session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT state_json FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        state_dict = json.loads(row[0])
        return GameState(**state_dict)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all saved sessions."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, created_at, updated_at 
            FROM sessions 
            ORDER BY updated_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "session_id": row[0],
                "created_at": row[1],
                "updated_at": row[2],
            }
            for row in rows
        ]


def get_session_storage() -> SessionStorage:
    """Get a session storage instance."""
    return SessionStorage()