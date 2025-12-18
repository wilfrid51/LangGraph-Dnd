import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from dnd.core.config import Settings
from dnd.core.models.state import GameState, Turn, EventType
from dnd.core.models.rulings import Ruling


class GameLogger:
    """Structured logger for game events."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.log_file = Settings.LOG_DIR / f"session_{session_id}.jsonl"
        self.events: List[Dict[str, Any]] = []
    
    def log_event(
        self,
        event_type: EventType,
        actor: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        visible_to: Optional[List[str]] = None
    ) -> None:
        """Log a game event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "actor": actor,
            "content": content,
            "metadata": metadata or {},
            "visible_to": visible_to or [],
        }
        
        self.events.append(event)
        self._write_event(event)
    
    def log_turn(self, turn: Turn) -> None:
        """Log a complete turn."""
        turn_data = {
            "timestamp": turn.timestamp.isoformat(),
            "turn_number": turn.turn_number,
            "player_name": turn.player_name,
            "action": turn.action,
            "gm_response": turn.gm_response,
            "events": [e.model_dump() for e in turn.events],
            "state_snapshot": turn.state_snapshot,
        }
        
        if turn.ruling:
            turn_data["ruling"] = turn.ruling.model_dump()
        
        self._write_event({
            "event_type": "turn_complete",
            "actor": "system",
            "content": f"Turn {turn.turn_number} completed",
            "metadata": turn_data,
        })
    
    def log_ruling(self, ruling: Ruling, turn_number: int) -> None:
        """Log a GM ruling."""
        self.log_event(
            EventType.RULING,
            "GM",
            f"Ruling on action: {ruling.action}",
            {
                "ruling": ruling.model_dump(),
                "turn_number": turn_number,
            }
        )
    
    def _write_event(self, event: Dict[str, Any]) -> None:
        """Write event to log file."""
        def json_serializer(obj):
            """Custom JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, set):
                return list(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, default=json_serializer) + "\n")
    
    def get_recent_events(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get the N most recent events."""
        return self.events[-n:] if len(self.events) >= n else self.events
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Get all logged events."""
        return self.events


class SessionLogger:
    """Manages logging for a game session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = GameLogger(session_id)
    
    def log_game_state(self, game_state: GameState) -> None:
        """Log complete game state snapshot."""
        snapshot = {
            "session_id": game_state.session_id,
            "current_turn": game_state.current_turn,
            "characters": {
                name: char.model_dump() for name, char in game_state.characters.items()
            },
            "npcs": {
                name: npc.model_dump() for name, npc in game_state.npcs.items()
            },
            "world_state": game_state.world_state,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.logger.log_event(
            EventType.STATE_CHANGE,
            "system",
            "Game state snapshot",
            {"snapshot": snapshot},
            visible_to=None
        )


# Alternate public names for logging utilities
class RealmRecorder(GameLogger):
    """Alias for `GameLogger` exposed as `RealmRecorder`."""

    pass


class SessionRecorder(SessionLogger):
    """Alias for `SessionLogger` exposed as `SessionRecorder`."""

    pass

