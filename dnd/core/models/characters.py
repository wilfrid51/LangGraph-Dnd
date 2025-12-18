from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field

class Character(BaseModel):
    """Base character model."""
    
    name: str
    health: int = 100
    max_health: int = 100
    inventory: List[str] = Field(default_factory=list)
    location: str = "unknown"
    abilities: Dict[str, int] = Field(default_factory=dict)
    known_facts: Set[str] = Field(default_factory=set)
    secrets: Dict[str, str] = Field(default_factory=dict)
    
    def add_item(self, item: str) -> None:
        """Add an item to inventory."""
        if not self.has_item(item):
            self.inventory.append(item)
    
    def remove_item(self, item: str) -> None:
        """Remove an item from inventory."""
        self.inventory = [i for i in self.inventory if i.lower() != item.lower()]
    
    def has_item(self, item: str) -> bool:
        """Check if character has an item."""
        return item.lower() in [i.lower() for i in self.inventory]

    def learn_fact(self, fact: str) -> None:
        """Add a fact to character's knowledge."""
        self.known_facts.add(fact)
    
    def knows_fact(self, fact: str) -> bool:
        """Check if character knows a fact."""
        return fact in self.known_facts

class PlayerCharacter(Character):
    """A player-controlled character."""
    
    player_id: str
    secret_objectives: List[str] = Field(default_factory=list)

class NPC(Character):
    """A non-player character with motivations and agency."""
    
    motivations: List[str] = Field(default_factory=list)
    personality: str = ""
    disposition: Dict[str, int] = Field(default_factory=dict)
    knowledge: List[str] = Field(default_factory=list)  # What the NPC knows
    
    def get_disposition_toward(self, character_name: str) -> int:
        """Get NPC's disposition toward a character."""
        return self.disposition.get(character_name, 0)
    
    def adjust_disposition(self, character_name: str, delta: int) -> None:
        """Adjust disposition toward a character."""
        current = self.get_disposition_toward(character_name)
        self.disposition[character_name] = max(-100, min(100, current + delta))
    
    def would_do(self, action: str, context: Dict) -> tuple[bool, str]:
        """
        Determine if NPC would perform an action based on motivations.
        Returns (would_do, reasoning).
        """
        # This will be enhanced by the NPC agency system
        return True, "Default behavior"