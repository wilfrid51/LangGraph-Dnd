from typing import Dict, Any, Optional, List

from dnd.core.langchain import ChatOpenAI
from dnd.core.langchain.core.prompts import ChatPromptTemplate

from dnd.core.config import Config, Settings
from dnd.core.models.state import GameState
from dnd.core.models.rulings import Ruling, RulingOutcome, ReasoningTrace, ReasoningStep
from dnd.core.models.characters import NPC, Character

class GameMaster:
    """
    Game Master agent responsible for:
    - Narrating scenes
    - Resolving player actions
    - Maintaining world consistency
    - Managing NPCs
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model=Settings.GM_MODEL, temperature=0.7)
    
    def narrate_scene(self, game_state: GameState, scene_description: str = None) -> str:
        """Narrate the current scene."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_gm_system_prompt()),
            ("human", f"Describe the current scene: {scene_description}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({}) 
        return response.content
    
    def resolve_action(
        self,
        game_state: GameState,
        player_name: str,
        action: str
    ) -> Ruling:
        """
        Resolve a player action with explicit reasoning trace.
        Implements Challenge 3: The Ruling
        """
        character = game_state.get_character(player_name)
        if not character:
            raise ValueError(f"Character {player_name} not found")
        
        # Build reasoning trace
        reasoning = self._build_reasoning_trace(game_state, character, action)
        
        # Determine outcome
        outcome = self._determine_outcome(reasoning, character, action)
        
        # Generate narrative
        narrative = self._generate_narrative(action, outcome, reasoning)
        
        # Determine state changes
        state_changes = self._determine_state_changes(action, outcome, character)
        
        ruling = Ruling(
            action=action,
            outcome=outcome,
            reasoning=reasoning,
            narrative=narrative,
            state_changes=state_changes
        )
        
        return ruling
    
    def _build_reasoning_trace(
        self,
        game_state: GameState,
        character: "Character",
        action: str
    ) -> ReasoningTrace:
        """Build explicit reasoning trace for the action."""
        reasoning = ReasoningTrace(
            situation=f"{character.name} attempts to: {action}",
            final_conclusion=""
        )
        
        # Step 1: Understand the action
        reasoning.add_step(
            "Understanding the action",
            [],
            f"Player wants to: {action}"
        )
        
        # Step 2: Gather relevant facts
        relevant_facts = self._gather_relevant_facts(game_state, character, action)
        reasoning.relevant_facts = relevant_facts
        
        reasoning.add_step(
            "Gathering relevant facts",
            relevant_facts,
            f"Found {len(relevant_facts)} relevant facts"
        )
        
        # Step 3: Check character abilities
        ability_check = self._check_abilities(character, action)
        reasoning.add_step(
            "Checking character abilities",
            [ability_check],
            ability_check
        )
        
        # Step 4: Consider obstacles
        obstacles = self._identify_obstacles(game_state, action)
        reasoning.add_step(
            "Identifying obstacles",
            obstacles,
            f"Found {len(obstacles)} potential obstacles"
        )
        
        # Step 5: Determine outcome
        outcome_reasoning = self._reason_about_outcome(character, action, relevant_facts, obstacles)
        reasoning.final_conclusion = outcome_reasoning
        
        return reasoning


# Backwards-compatible alias: alternate public name
class Keeper(GameMaster):
    """Alias for `GameMaster` exposed under a different name."""

    pass
    
    def _gather_relevant_facts(
        self,
        game_state: GameState,
        character: Character,
        action: str
    ) -> List[str]:
        """Gather facts relevant to the action."""
        facts = []
        
        # Character state
        facts.append(f"{character.name} has {character.health}/{character.max_health} health")
        if character.inventory:
            facts.append(f"{character.name} has items: {', '.join(character.inventory)}")
        facts.append(f"{character.name} is at {character.location}")
        
        # World state (convert to string safely)
        if game_state.world_state:
            world_state_str = ", ".join([f"{k}: {v}" for k, v in game_state.world_state.items()])
            facts.append(f"World state: {world_state_str}")
        
        # Recent events
        recent_turns = game_state.turns[-3:]
        for turn in recent_turns:
            if turn.gm_response:
                facts.append(f"Recent: {turn.gm_response[:100]}")
        
        return facts
    
    def _check_abilities(self, character: Character, action: str) -> str:
        """Check if character has relevant abilities."""
        action_lower = action.lower()
        
        checks = []
        if "climb" in action_lower or "athletics" in action_lower:
            strength = character.abilities.get("strength", 10)
            checks.append(f"Strength: {strength}")
        
        if "persuade" in action_lower or "charisma" in action_lower or "convince" in action_lower:
            charisma = character.abilities.get("charisma", 10)
            checks.append(f"Charisma: {charisma}")
        
        if "stealth" in action_lower or "sneak" in action_lower:
            dex = character.abilities.get("dexterity", 10)
            checks.append(f"Dexterity: {dex}")
        
        return "; ".join(checks) if checks else "No specific ability checks needed"
    
    def _identify_obstacles(self, game_state: GameState, action: str) -> List[str]:
        """Identify potential obstacles."""
        obstacles = []
        action_lower = action.lower()
        
        # Check world state for obstacles
        if "door" in action_lower and "locked" in str(game_state.world_state).lower():
            obstacles.append("Locked door")
        
        if "climb" in action_lower and "slippery" in str(game_state.world_state).lower():
            obstacles.append("Slippery surface")
        
        return obstacles
    
    def _reason_about_outcome(
        self,
        character: Character,
        action: str,
        facts: List[str],
        obstacles: List[str]
    ) -> str:
        """
        Reason about the likely outcome of an action.
        
        This uses the LLM to make a judgment call based on character capabilities,
        current situation, and narrative consistency. The reasoning is captured
        in the trace for auditability.
        """
        # Build context about character capabilities
        ability_summary = ", ".join([
            f"{k}: {v}" for k, v in character.abilities.items()
        ]) if character.abilities else "Standard abilities"
        
        inventory_summary = ", ".join(character.inventory) if character.inventory else "No items"
        
        # Build the prompt text manually, escaping any curly braces to avoid template variable issues
        facts_str = ', '.join(facts[:10])
        obstacles_str = ', '.join(obstacles) if obstacles else 'None'
        
        # Use .format() with escaped braces to avoid LangChain template variable interpretation
        prompt_text = f"""
Action: {action}
Character: {character.name}
Abilities: {ability_summary}
Inventory: {inventory_summary}
Health: {character.health}/{character.max_health}
Relevant Facts: {facts_str}
Obstacles: {obstacles_str}

Determine if this action should succeed, fail, or partially succeed. Consider:
1. Character abilities and items (do they have what's needed?)
2. Obstacles present (are they surmountable?)
3. Narrative consistency (does this make sense?)
4. Character health/state (are they in good condition?)

Respond with: SUCCESS, FAILURE, or PARTIAL, followed by brief reasoning (2-3 sentences).
""".format(
            action=action,
            character_name=character.name,
            ability_summary=ability_summary,
            inventory_summary=inventory_summary,
            health=character.health,
            max_health=character.max_health,
            facts=facts_str,
            obstacles=obstacles_str
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a reasoning system for a D&D game. Analyze the situation 
            and determine the likely outcome. Be fair but realistic - not every action 
            should succeed. Consider the character's capabilities and the obstacles present."""),
            ("human", prompt_text)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content
    
    def _determine_outcome(self, reasoning: ReasoningTrace, character: "Character", action: str) -> RulingOutcome:
        """Determine the outcome from reasoning."""
        conclusion = reasoning.final_conclusion.upper()
        
        if "SUCCESS" in conclusion:
            return RulingOutcome.SUCCESS
        elif "PARTIAL" in conclusion:
            return RulingOutcome.PARTIAL
        elif "FAILURE" in conclusion:
            return RulingOutcome.FAILURE
        else:
            return RulingOutcome.UNCERTAIN
    
    def _generate_narrative(self, action: str, outcome: RulingOutcome, reasoning: ReasoningTrace) -> str:
        """Generate narrative description of the outcome."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Dungeon Master narrating the outcome of a player action. Be vivid and engaging."),
            ("human", f"""
Action: {action}
Outcome: {outcome.value}
Reasoning: {reasoning.final_conclusion}

Narrate what happens in 2-3 sentences. Make it engaging and consistent with the outcome.
""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content
    
    def _determine_state_changes(
        self,
        action: str,
        outcome: RulingOutcome,
        character: "Character"
    ) -> Dict[str, Any]:
        """Determine what state changes should occur."""
        changes = {}
        action_lower = action.lower()
        
        # Item acquisition
        if "find" in action_lower or "pick up" in action_lower or "take" in action_lower:
            if outcome == RulingOutcome.SUCCESS:
                # Extract item name (simplified)
                if "key" in action_lower:
                    changes["item_acquired"] = "brass_key"
                elif "potion" in action_lower:
                    changes["item_acquired"] = "healing_potion"
        
        # Item usage
        if "use" in action_lower or "drink" in action_lower:
            if "potion" in action_lower and outcome == RulingOutcome.SUCCESS:
                changes["health_restored"] = 20
                changes["item_used"] = "healing_potion"
        
        # Health changes
        if "damage" in action_lower or "attack" in action_lower:
            if outcome == RulingOutcome.FAILURE:
                changes["damage_taken"] = 5
        
        return changes
    
    def validate_npc_action(
        self,
        npc: NPC,
        assumed_action: str,
        context: Dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Validate if an NPC would perform an action (Challenge 5: Living World).
        Returns (would_do, actual_response).
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an NPC behavior validator. Determine if an NPC would perform an action based on their motivations and personality."),
            ("human", f"""
NPC: {npc.name}
Motivations: {', '.join(npc.motivations)}
Personality: {npc.personality}
Assumed Action: {assumed_action}
Context: {context}

Would this NPC perform this action? If not, what would they actually do instead?
Respond with: YES or NO, followed by reasoning and alternative action if NO.
""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        content = response.content
        
        would_do = "YES" in content.upper()
        return would_do, content
    
    def _get_gm_system_prompt(self) -> str:
        """Get the system prompt for the GM."""
        return """You are the Dungeon Master for a Dungeons & Dragons campaign. You are:
- Fair but challenging
- Focused on narrative consistency
- Creative and engaging in your descriptions
- Careful to maintain world consistency
- Never reveal information characters wouldn't know

You narrate scenes, resolve actions, and maintain the game world."""
    
    def _build_scene_prompt(self, context: Dict[str, Any], scene_description: Optional[str] = None) -> str:
        """Build the prompt for scene narration."""
        parts = []
        
        if context.get("summary"):
            parts.append(f"Previous events summary:\n{context['summary']}\n")
        
        if context.get("recent_turns"):
            parts.append("Recent turns:")
            for turn in context["recent_turns"][-3:]:
                parts.append(f"  Turn {turn.turn_number}: {turn.gm_response[:100] if turn.gm_response else ''}")
        
        if context.get("key_facts"):
            parts.append(f"\nKey facts: {', '.join(context['key_facts'][:5])}")
        
        # Get current scene from world state if available
        current_scene = scene_description or "The adventure continues..."
        if context.get("game_state") and context["game_state"].world_state.get("current_scene"):
            current_scene = context["game_state"].world_state.get("current_scene")
        
        if scene_description:
            parts.append(f"\nDescribe this scene: {scene_description}")
        else:
            parts.append(f"\nNarrate the current scene for the players. Current scene: {current_scene}")
        
        return "\n".join(parts)

