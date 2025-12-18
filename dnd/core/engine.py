import uuid
from typing import Dict, List, Optional

from dnd.core.langchain import ChatOpenAI

from dnd.core.config import Settings
from dnd.core.models.characters import PlayerCharacter, NPC
from dnd.core.agents.player import PlayerAgent
from dnd.core.logging import SessionStorage
from dnd.core.graph import create_game_graph
from dnd.core.agents import Keeper
from dnd.core.logging.logger import RealmRecorder, SessionRecorder
from dnd.core.models.state import GameState

class GameEngine:
    """Main game engine the DnD simulation."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        gm_llm: Optional[ChatOpenAI] = None,
        player_llm: Optional[ChatOpenAI] = None
    ):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.gm_llm = gm_llm or ChatOpenAI(model=Settings.GM_MODEL, temperature=0.7)
        self.player_llm = player_llm or ChatOpenAI(model=Settings.PLAYER_MODEL, temperature=0.8)
        
        self.gm = Keeper(llm=self.gm_llm)
        self.logger = RealmRecorder(self.session_id)
        self.session_logger = SessionRecorder(self.session_id)
        self.storage = SessionStorage()
        
        self.game_state: Optional[GameState] = None
        self.players: Dict[str, PlayerAgent] = {}
        self.graph = None
        self.graph_state = None
    
    def initialize_game(
        self,
        player_characters: List[PlayerCharacter],
        npcs: Optional[List[NPC]] = None,
        initial_scene: str = "You find yourselves at the entrance of an ancient dungeon."
    ) -> None:
        """Initialize a new game session."""
        # Create game state
        self.game_state = GameState(
            session_id=self.session_id,
            current_turn=0
        )
        
        # Add players
        for char in player_characters:
            self.game_state.characters[char.name] = char
            self.players[char.name] = PlayerAgent(
                character=char,
                llm=self.player_llm,
            )
        
        # Add NPCs
        if npcs:
            for npc in npcs:
                self.game_state.npcs[npc.name] = npc
        
        # Set initial scene
        self.game_state.world_state["current_scene"] = initial_scene
        
        # Create graph
        self.graph, self.graph_state = create_game_graph(
            self.game_state,
            self.gm,
            self.players,
            self.logger
        )
        
        # Log initialization
        from dnd.core.models.state import EventType
        self.logger.log_event(
            EventType.STATE_CHANGE,
            "system",
            f"Game initialized with {len(player_characters)} players",
            {"players": [p.name for p in player_characters]}
        )
        
        # Save initial state
        self.save_session()
    
    def run_turn(self, manual_action: Optional[str] = None) -> Dict:
        """
        Run a single turn of the game.
        
        Args:
            manual_action: Optional manual action string. If provided, uses this
                          instead of asking the player agent to decide.
        """
        if not self.game_state or not self.graph:
            raise ValueError("Game not initialized. Call initialize_game() first.")
        
        # Store manual action in graph state if provided
        if manual_action:
            self.graph_state["manual_action"] = manual_action
        
        # Run the graph
        result = self.graph.invoke(self.graph_state)
        
        # Clear manual action after use
        if "manual_action" in self.graph_state:
            del self.graph_state["manual_action"]
        
        # Update graph state
        self.graph_state = result
        
        # Save session
        self.save_session()
        
        return {
            "turn_number": self.game_state.current_turn,
            "player": result.get("current_player"),
            "action": result.get("action"),
            "narration": result.get("narration"),
            "ruling": result.get("ruling"),
        }
    def run_turns(self, n_turns: int) -> List[Dict]:
        """Run multiple turns."""
        results = []
        for _ in range(n_turns):
            result = self.run_turn()
            results.append(result)
        return results

    def save_session(self) -> None:
        """Save the current session."""
        if self.game_state:
            self.storage.save_session(self.game_state)
            self.session_logger.log_game_state(self.game_state)

    def load_session(self, session_id: str) -> bool:
        """Load a saved session."""
        game_state = self.storage.load_session(session_id)
        if not game_state:
            return False

        self.session_id = session_id
        self.game_state = game_state
        # Use alias logging class when restoring
        self.logger = RealmRecorder(session_id)

        # Recreate players
        self.players = {}
        for char_name, char_data in game_state.characters.items():
            if isinstance(char_data, PlayerCharacter):
                self.players[char_name] = PlayerAgent(
                    character=char_data,
                    llm=self.player_llm,
                )

        # Recreate graph
        self.graph, self.graph_state = create_game_graph(
            self.game_state,
            self.gm,
            self.players,
            self.logger
        )

        return True

    def get_current_state(self) -> Dict:
        """Get current game state summary."""
        if not self.game_state:
            return {}

        return {
            "session_id": self.game_state.session_id,
            "current_turn": self.game_state.current_turn,
            "players": {
                name: {
                    "health": char.health,
                    "location": char.location,
                    "inventory": char.inventory,
                }
                for name, char in self.game_state.characters.items()
            },
            "world_state": self.game_state.world_state,
        }


# Public alias for a different import name
class AegisEngine(GameEngine):
    """Alias for `GameEngine` offering a renamed public symbol."""

    pass

