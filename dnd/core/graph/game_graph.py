from typing import TypedDict, Annotated, List, Dict, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages


from dnd.core.models.state import GameState, Turn, Event, EventType
from dnd.core.models.rulings import Ruling
from dnd.core.agents.gm import Keeper
from dnd.core.agents.player import PlayerAgent
from dnd.core.logging.logger import RealmRecorder


class GameGraphState(TypedDict):
    """State for the LangGraph."""
    game_state: GameState
    current_player: Optional[str]
    action: Optional[str]
    ruling: Optional[Ruling]
    narration: Optional[str]
    logger: RealmRecorder
    manual_action: Optional[str]  # For manual action input from GUI


def create_game_graph(
    game_state: GameState,
    gm: Keeper,
    players: Dict[str, PlayerAgent],
    logger: RealmRecorder
) -> tuple[StateGraph, GameGraphState]:
    """
    Create the LangGraph state graph for the D&D simulation.
    """
    # Store agents in a way accessible to nodes
    # We'll use closures to capture them
    def make_player_action_node():
        def node(state: GameGraphState) -> GameGraphState:
            return player_action_node(state, players)
        return node
    
    def make_gm_resolve_node():
        def node(state: GameGraphState) -> GameGraphState:
            return gm_resolve_node(state, gm)
        return node
    
    graph = StateGraph(GameGraphState)
    
    # Add nodes
    graph.add_node("select_player", select_player_node)
    graph.add_node("player_action", make_player_action_node())
    graph.add_node("gm_resolve", make_gm_resolve_node())
    graph.add_node("update_state", update_state_node)
    graph.add_node("gm_narrate", gm_narrate_node)
    
    # Set entry point
    graph.set_entry_point("select_player")
    
    # Add edges
    graph.add_edge("select_player", "player_action")
    graph.add_edge("player_action", "gm_resolve")
    graph.add_edge("gm_resolve", "update_state")
    graph.add_edge("update_state", "gm_narrate")
    graph.add_edge("gm_narrate", END)
    
    # Compile the graph
    compiled_graph = graph.compile()
    
    # Initialize state
    initial_state: GameGraphState = {
        "game_state": game_state,
        "current_player": None,
        "action": None,
        "ruling": None,
        "narration": None,
        "logger": logger,
        "manual_action": None,
    }
    
    return compiled_graph, initial_state


def select_player_node(state: GameGraphState) -> GameGraphState:
    """Select the next player to act."""
    game_state = state["game_state"]
    players = list(game_state.characters.keys())
    
    if not players:
        raise ValueError("No players in game")
    
    # Simple round-robin
    current_turn = game_state.current_turn
    player_index = current_turn % len(players)
    current_player = players[player_index]
    
    state["current_player"] = current_player
    return state


def player_action_node(state: GameGraphState, players: Dict[str, PlayerAgent]) -> GameGraphState:
    """Get action from player agent or use manual action if provided."""
    game_state = state["game_state"]
    current_player = state["current_player"]
    logger = state["logger"]
    
    if not current_player:
        raise ValueError("No current player selected")
    
    # Check if manual action is provided (from GUI)
    if state.get("manual_action"):
        action = state["manual_action"]
        logger.log_event(
            EventType.PLAYER_ACTION,
            current_player,
            f"{current_player} performs manual action: {action}"
        )
    else:
        # Get player agent
        player_agent = players.get(current_player)
        if not player_agent:
            raise ValueError(f"Player agent not found for {current_player}")
        
        # Log player action event
        logger.log_event(
            EventType.PLAYER_ACTION,
            current_player,
            f"{current_player} is deciding their action"
        )
        
        # Get action from player agent
        action = player_agent.decide_action(game_state)
    
    state["action"] = action
    return state


def gm_resolve_node(state: GameGraphState, gm: Keeper) -> GameGraphState:
    """GM resolves the player action."""
    game_state = state["game_state"]
    current_player = state["current_player"]
    action = state["action"]
    logger = state["logger"]
    
    if not current_player or not action:
        raise ValueError("Missing player or action")
    
    # Resolve action
    ruling = gm.resolve_action(game_state, current_player, action)
    
    # Log ruling
    logger.log_ruling(ruling, game_state.current_turn)
    
    state["ruling"] = ruling
    return state


def update_state_node(state: GameGraphState) -> GameGraphState:
    """Update game state based on ruling."""
    game_state = state["game_state"]
    current_player = state["current_player"]
    ruling = state["ruling"]
    logger = state["logger"]
    
    if not ruling:
        return state
    
    character = game_state.get_character(current_player)
    if not character:
        return state
    
    # Apply state changes
    changes = ruling.state_changes
    
    # Update inventory
    if "item_acquired" in changes:
        character.add_item(changes["item_acquired"])
        logger.log_event(
            EventType.STATE_CHANGE,
            "system",
            f"{current_player} acquired {changes['item_acquired']}"
        )
    
    if "item_used" in changes:
        character.remove_item(changes["item_used"])
        logger.log_event(
            EventType.STATE_CHANGE,
            "system",
            f"{current_player} used {changes['item_used']}"
        )
    
    # Update health
    if "health_restored" in changes:
        character.health = min(character.max_health, character.health + changes["health_restored"])
    
    if "damage_taken" in changes:
        character.health = max(0, character.health - changes["damage_taken"])
    
    # Update world state
    game_state.world_state.update(changes.get("world_changes", {}))
    
    return state


def gm_narrate_node(state: GameGraphState) -> GameGraphState:
    """GM narrates the result."""
    game_state = state["game_state"]
    ruling = state["ruling"]
    logger = state["logger"]
    
    if not ruling:
        return state
    
    # Use ruling narrative
    narration = ruling.narrative
    
    # Create turn
    turn = Turn(
        turn_number=game_state.current_turn + 1,
        player_name=state["current_player"],
        action=state["action"],
        gm_response=narration,
        ruling=ruling,
        state_snapshot={
            "characters": {name: char.model_dump() for name, char in game_state.characters.items()},
            "world_state": game_state.world_state,
        }
    )
    
    # Add events
    turn.events.append(Event(
        turn_number=turn.turn_number,
        event_type=EventType.PLAYER_ACTION,
        actor=state["current_player"] or "Unknown",
        content=state["action"] or "",
    ))
    
    turn.events.append(Event(
        turn_number=turn.turn_number,
        event_type=EventType.GM_NARRATION,
        actor="GM",
        content=narration,
    ))
    
    # Add turn to game state
    game_state.add_turn(turn)
    
    # Log turn
    logger.log_turn(turn)
    
    state["narration"] = narration
    return state