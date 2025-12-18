from typing import List, Dict, Any, Optional
from dnd.core.logging.storage import SessionStorage
from dnd.core.engine import AegisEngine
from dnd.core.models.characters import PlayerCharacter


def get_available_sessions() -> List[Dict[str, Any]]:
    """Get list of available game sessions."""
    storage = SessionStorage()
    return storage.list_sessions()


def create_new_game(num_players: int, session_id: Optional[str] = None) -> AegisEngine:
    """Create a new game with specified number of players."""
    # Create player characters
    player_chars = []
    for i in range(num_players):
        char = PlayerCharacter(
            name=f"Player{i+1}",
            player_id=f"player_{i+1}",
            health=100,
            max_health=100,
            abilities={"strength": 14, "dexterity": 12, "charisma": 10},
            location="dungeon_entrance"
        )
        player_chars.append(char)
    
    # Create game engine
    engine = AegisEngine(session_id=session_id)
    engine.initialize_game(
        player_characters=player_chars,
        initial_scene="You find yourselves at the entrance of an ancient dungeon. Torches flicker in the darkness ahead."
    )
    
    return engine


def load_game_session(session_id: str) -> Optional[AegisEngine]:
    """Load an existing game session."""
    engine = AegisEngine()
    if engine.load_session(session_id):
        return engine
    return None

