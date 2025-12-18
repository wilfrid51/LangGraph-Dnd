from typing import List, Dict, Any, Optional

from dnd.core.langchain import ChatOpenAI
from dnd.core.langchain.core.prompts import ChatPromptTemplate

from dnd.core.config import Config, Settings
from dnd.core.models.state import GameState
from dnd.core.models.characters import PlayerCharacter
from dnd.core.memory import VaultManager

class PlayerAgent:
    """Player agent that takes actions in the game with perspective filtering."""
    
    def __init__(
        self,
        character: PlayerCharacter,
        llm: Optional[ChatOpenAI] = None,
        memory_manager: Optional[VaultManager] = None
    ):
        self.character = character
        self.llm = llm or ChatOpenAI(model=Settings.PLAYER_MODEL, temperature=0.8)
        self.memory_manager = memory_manager or VaultManager()
    
    def decide_action(self, game_state: GameState) -> str:
        """
        Decide on an action based on the character's perspective.
        Only sees what the character would know.
        """
        # Get filtered context (only what this character knows)
        context = self.memory_manager.get_relevant_context(
            game_state,
            game_state.current_turn,
            character_name=self.character.name
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_player_system_prompt()),
            ("human", self._build_action_prompt(context))
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content.strip()
    
    def _get_player_system_prompt(self) -> str:
        """Get system prompt for the player."""
        secret_info = ""
        if self.character.secret_objectives:
            secret_info = f"\n\nYour secret objectives (known only to you): {', '.join(self.character.secret_objectives)}"
        
        return f"""You are {self.character.name}, a player character in a D&D campaign.

Your character:
- Health: {self.character.health}/{self.character.max_health}
- Inventory: {', '.join(self.character.inventory) if self.character.inventory else 'Empty'}
- Location: {self.character.location}
- Abilities: {self.character.abilities}{secret_info}

Decide what action you want to take. Be creative and in-character. Respond with just the action you want to perform, in first person (e.g., "I search the room for hidden doors")."""
    
    def _build_action_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for action decision."""
        parts = []
        
        parts.append(f"You are {self.character.name}. What do you do?")
        
        if context.get("summary"):
            parts.append(f"\nPrevious events:\n{context['summary']}")
        
        if context.get("recent_turns"):
            parts.append("\nRecent events:")
            for turn in context["recent_turns"][-3:]:
                if turn.gm_response:
                    parts.append(f"  {turn.gm_response[:200]}")
        
        if context.get("key_facts"):
            known_facts = [f for f in context["key_facts"] if self.character.knows_fact(f)]
            if known_facts:
                parts.append(f"\nThings you know: {', '.join(known_facts[:5])}")
        
        parts.append("\nWhat action do you take?")
        
        return "\n".join(parts)