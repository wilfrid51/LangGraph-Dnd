from datetime import datetime
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from enum import Enum
from pydantic import BaseModel, Field

from .rulings import Ruling
from .knowledge import KnowledgeGraph
from .characters import Character, PlayerCharacter, NPC

class EventType(str, Enum):
    """Types of game events."""
    PLAYER_ACTION = "player_action"
    GM_NARRATION = "gm_narration"
    RULING = "ruling"
    STATE_CHANGE = "state_change"
    NPC_ACTION = "npc_action"
    SECRET_REVEALED = "secret_revealed"


class Event(BaseModel):
    """A single event in the game."""
    
    turn_number: int
    event_type: EventType
    actor: str  # Character name or "GM"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    visible_to: List[str] = Field(default_factory=list)  # Empty = visible to all
    
    class Config:
        use_enum_values = True


class Turn(BaseModel):
    """A single turn in the game."""
    
    turn_number: int
    player_name: Optional[str] = None
    action: Optional[str] = None
    gm_response: Optional[str] = None
    ruling: Optional["Ruling"] = None
    events: List[Event] = Field(default_factory=list)
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class GameState(BaseModel):
    """Complete game state."""
    
    session_id: str
    current_turn: int = 0
    turns: List[Turn] = Field(default_factory=list)
    characters: Dict[str, Character] = Field(default_factory=dict)
    npcs: Dict[str, NPC] = Field(default_factory=dict)
    world_state: Dict[str, Any] = Field(default_factory=dict)
    knowledge_graph: KnowledgeGraph = Field(default_factory=lambda: KnowledgeGraph())
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def get_current_turn(self) -> Optional[Turn]:
        """Get the current turn object."""
        if self.current_turn > 0 and self.current_turn <= len(self.turns):
            return self.turns[self.current_turn - 1]
        return None
    
    def add_turn(self, turn: Turn) -> None:
        """Add a new turn to the game."""
        self.turns.append(turn)
        self.current_turn = len(self.turns)
        self.updated_at = datetime.now()
    
    def get_character(self, name: str) -> Optional[Character]:
        """Get a character by name."""
        return self.characters.get(name)
    
    def get_npc(self, name: str) -> Optional[NPC]:
        """Get an NPC by name."""
        return self.npcs.get(name)

