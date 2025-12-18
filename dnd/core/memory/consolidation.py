from typing import List
from dnd.core.models.state import Turn


def consolidate_memory(turns: List[Turn], max_turns: int = 10) -> tuple[str, List[Turn]]:
    """
    Consolidate old turns into a summary, keeping recent turns.
    
    Returns (summary, recent_turns).
    """
    if len(turns) <= max_turns:
        return "", turns
    
    old_turns = turns[:-max_turns]
    recent_turns = turns[-max_turns:]
    
    # Create summary from old turns
    summary = summarize_turns(old_turns)
    
    return summary, recent_turns


def summarize_turns(turns: List[Turn]) -> str:
    """Create a text summary of turns."""
    if not turns:
        return ""
    
    parts = []
    for turn in turns:
        part = f"Turn {turn.turn_number}: "
        if turn.player_name and turn.action:
            part += f"{turn.player_name} attempted to {turn.action}. "
        if turn.gm_response:
            # Truncate long responses
            response = turn.gm_response[:150] + "..." if len(turn.gm_response) > 150 else turn.gm_response
            part += f"Result: {response}"
        parts.append(part)
    
    return "\n".join(parts)

