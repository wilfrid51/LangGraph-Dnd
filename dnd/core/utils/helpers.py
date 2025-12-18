import re
from typing import List, Optional
from dnd.core.models.characters import Character


def format_turn_summary(turn_number: int, player: str, action: str, outcome: str) -> str:
    """Format a turn into a readable summary."""
    return f"Turn {turn_number}: {player} -> {action} -> {outcome}"


def extract_items_from_text(text: str) -> List[str]:
    """
    Extract item mentions from text.
    This is a simple heuristic - in production you'd use more sophisticated NLP.
    """
    items = []
    text_lower = text.lower()
    
    # Common item patterns
    item_patterns = [
        r"(?:found|picked up|acquired|obtained|took)\s+(?:a|an|the)?\s*([a-z\s]+?)(?:\.|,|$)",
        r"(?:has|holding|carrying)\s+(?:a|an|the)?\s*([a-z\s]+?)(?:\.|,|$)",
    ]
    
    for pattern in item_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            item = match.strip()
            # Filter out common false positives
            if item and len(item) > 2 and item not in ["the", "a", "an"]:
                items.append(item)
    
    # Also check for explicit item mentions
    known_items = ["key", "potion", "sword", "shield", "torch", "rope", "dagger"]
    for item in known_items:
        if item in text_lower:
            items.append(item)
    
    return list(set(items))  # Remove duplicates


def validate_character_state(character: Character) -> tuple[bool, Optional[str]]:
    """
    Validate character state for consistency.
    Returns (is_valid, error_message).
    """
    if character.health < 0:
        return False, f"Character {character.name} has negative health"
    
    if character.health > character.max_health:
        return False, f"Character {character.name} has health exceeding max_health"
    
    if not character.location:
        return False, f"Character {character.name} has no location"
    
    return True, None

