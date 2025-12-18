from typing import List, Dict, Any, Optional

from dnd.core.langchain import ChatOpenAI
from dnd.core.langchain.core.prompts import ChatPromptTemplate

from dnd.core.config import Settings
from dnd.core.models.state import GameState, Turn
from dnd.core.models.knowledge import KnowledgeGraph, Fact, ConfidenceLevel


class MemoryManager:
    """
    Manages game memory using multiple techniques:
    - Windowing: Keep recent turns
    - Summarization: Compress old turns
    - Key-Value Memory: Store facts separately
    - Context Pruning: Remove low-relevance content
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model=Settings.DEFAULT_MODEL, temperature=0.3)
        self.max_context_turns = Settings.MAX_CONTEXT_TURNS
        self.consolidation_threshold = Settings.MEMORY_CONSOLIDATION_THRESHOLD
    
    def get_relevant_context(
        self,
        game_state: GameState,
        current_turn: int,
        character_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get relevant context for a character, applying windowing and summarization.
        
        Returns a dict with:
        - summary: Compressed summary of old turns
        - recent_turns: Recent turn details
        - key_facts: Important facts from knowledge graph
        """
        all_turns = game_state.turns
        
        # Determine what to include
        if len(all_turns) <= self.max_context_turns:
            # No need for summarization yet
            recent_turns = all_turns
            summary = None
        else:
            # Split into old and recent
            old_turns = all_turns[:-self.max_context_turns]
            recent_turns = all_turns[-self.max_context_turns:]
            
            # Summarize old turns
            summary = self._summarize_turns(old_turns, character_name)
        
        # Extract key facts from knowledge graph
        key_facts = self._extract_key_facts(game_state.knowledge_graph, character_name)
        
        # Filter events by character perspective if needed
        if character_name:
            recent_turns = self._filter_turns_by_perspective(recent_turns, character_name)
        
        return {
            "summary": summary,
            "recent_turns": recent_turns,
            "key_facts": key_facts,
            "total_turns": len(all_turns),
        }
    
    def _summarize_turns(self, turns: List[Turn], character_name: Optional[str] = None) -> str:
        """Summarize a list of turns."""
        if not turns:
            return ""
        
        # Build summary prompt
        turn_texts = []
        for turn in turns:
            text = f"Turn {turn.turn_number}: "
            if turn.player_name:
                text += f"{turn.player_name} {turn.action or ''}. "
            if turn.gm_response:
                text += f"GM: {turn.gm_response[:200]}"
            turn_texts.append(text)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a memory consolidation system. Create a concise summary of these game events, focusing on important facts, character state changes, and narrative developments. Keep it under 300 words."),
            ("human", "\n".join(turn_texts))
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({})
        return result.content
    
    def _extract_key_facts(
        self,
        knowledge_graph: KnowledgeGraph,
        character_name: Optional[str] = None
    ) -> List[str]:
        """Extract key facts from knowledge graph."""
        # Get high-confidence facts
        facts = knowledge_graph.get_facts_by_confidence(ConfidenceLevel.MEDIUM)
        
        # Filter by character if specified
        if character_name:
            # This would be enhanced with character-specific filtering
            pass
        
        # Return fact contents
        return [f.content for f in facts[:20]]  # Limit to top 20
    
    def _filter_turns_by_perspective(
        self,
        turns: List[Turn],
        character_name: str
    ) -> List[Turn]:
        """Filter turns to only include events visible to the character."""
        filtered = []
        for turn in turns:
            # Create a filtered version of the turn
            visible_events = [
                event for event in turn.events
                if not event.visible_to or character_name in event.visible_to or "GM" in event.visible_to
            ]
            if visible_events or turn.player_name == character_name:
                # Create a copy with filtered events
                turn_dict = turn.model_dump()
                turn_dict["events"] = [e.model_dump() for e in visible_events]
                filtered.append(Turn(**turn_dict))
        return filtered
    
    def consolidate_if_needed(self, game_state: GameState) -> bool:
        """
        Check if consolidation is needed and perform it.
        Returns True if consolidation was performed.
        """
        if len(game_state.turns) < self.consolidation_threshold:
            return False
        
        # Extract and store key facts
        self._extract_and_store_facts(game_state)
        
        # Mark old turns as summarized (in a real implementation, we'd store this)
        return True
    
    def _extract_and_store_facts(self, game_state: GameState) -> None:
        """Extract facts from recent turns and store in knowledge graph."""
        # Look for important facts in recent turns
        recent_turns = game_state.turns[-10:]
        
        for turn in recent_turns:
            # Extract facts from GM responses and events
            if turn.gm_response:
                facts = self._extract_facts_from_text(turn.gm_response, turn.turn_number)
                for fact in facts:
                    game_state.knowledge_graph.add_fact(fact)
    
    def _extract_facts_from_text(self, text: str, turn_number: int) -> List[Fact]:
        """
        Extract structured facts from narrative text.
        
        This is a simplified version - in production, you'd use more sophisticated
        extraction techniques like NER, structured LLM output, or dedicated fact
        extraction models. For now, we use pattern matching for common game elements.
        """
        facts = []
        text_lower = text.lower()
        
        # Extract item mentions
        from dnd.core.utils.helpers import extract_items_from_text
        items = extract_items_from_text(text)
        for item in items:
            facts.append(Fact(
                content=f"Item mentioned: {item}",
                confidence=ConfidenceLevel.MEDIUM,
                source="narrative",
                turn_observed=turn_number
            ))
        
        # Extract location mentions (simple pattern)
        location_keywords = ["room", "chamber", "hall", "corridor", "dungeon", "cave", "temple"]
        for keyword in location_keywords:
            if keyword in text_lower:
                facts.append(Fact(
                    content=f"Location mentioned: {keyword}",
                    confidence=ConfidenceLevel.MEDIUM,
                    source="narrative",
                    turn_observed=turn_number
                ))
                break  # Only one location per turn typically
        
        return facts


# Public alias to present an alternate API surface
class VaultManager(MemoryManager):
    """Alias for `MemoryManager` exposed under the name `VaultManager`."""

    pass