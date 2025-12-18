import streamlit as st
from typing import Dict, Any
from dnd.core.models.characters import Character, PlayerCharacter, NPC
from dnd.core.models.rulings import Ruling, RulingOutcome


def render_health_bar(character: Character, max_width: int = 300) -> None:
    """Render a visual health bar for a character."""
    
    health_percent = (character.health / character.max_health) * 100
    
    # Color based on health percentage
    if health_percent > 60:
        color = "#48bb78"  # green
        emoji = "🟢"
    elif health_percent > 30:
        color = "#ed8936"  # orange
        emoji = "🟠"
    else:
        color = "#f56565"  # red
        emoji = "🔴"
    
    # Create a more visual health bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="background: #0f172a; border-radius: 10px; padding: 0.5rem; border: 2px solid #475569;">
            <div style="background: {color}; height: 25px; border-radius: 8px; width: {health_percent}%; 
                        display: flex; align-items: center; justify-content: center; 
                        transition: width 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">
                <span style="color: white; font-weight: bold; font-size: 0.9rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
                    {character.health}/{character.max_health}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align: center; font-size: 1.5rem;'>{emoji}</div>", unsafe_allow_html=True)


def render_character_card(character: Character, is_npc: bool = False) -> None:
    """Render a character information card with visual styling."""
    
    char_type = "👤 NPC" if is_npc else "⚔️ Player"
    icon = "👤" if is_npc else "⚔️"
    
    # Character header with icon
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                padding: 1rem; border-radius: 10px; border: 2px solid #475569; 
                margin: 0.5rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.5);">
        <h3 style="color: #ffd700; margin: 0; display: flex; align-items: center; gap: 0.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
            <span style="font-size: 1.5rem;">{icon}</span>
            <span style="font-weight: bold;">{character.name}</span>
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ❤️ Health")
        render_health_bar(character)
        
        st.markdown("### 📍 Location")
        st.markdown(f"<div style='background: #1a202c; padding: 0.75rem; border-radius: 8px; border: 1px solid #4a5568; color: #e2e8f0;'>{character.location}</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ⚡ Abilities")
        if character.abilities:
            for ability, value in character.abilities.items():
                # Visual ability bar
                ability_percent = min(100, (value / 20) * 100)
                st.markdown(f"""
                <div style="margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="color: #f1f5f9; font-weight: 500;">{ability.capitalize()}</span>
                        <span style="color: #ffd700; font-weight: bold;">{value}</span>
                    </div>
                    <div style="background: #0f172a; height: 8px; border-radius: 4px; overflow: hidden; border: 1px solid #475569;">
                        <div style="background: linear-gradient(90deg, #4299e1, #3182ce); height: 100%; width: {ability_percent}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("*None*")
    
    st.markdown("### 🎒 Inventory")
    if character.inventory:
        # Visual inventory grid
        cols = st.columns(min(4, len(character.inventory)))
        for idx, item in enumerate(character.inventory):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div style="background: #1e293b; padding: 0.75rem; border-radius: 8px; 
                            border: 1px solid #475569; text-align: center; color: #f1f5f9; font-weight: 500;">
                    🎁 {item}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: #a0aec0; font-style: italic;'>*Empty*</div>", unsafe_allow_html=True)
    
    # Show NPC-specific info
    if is_npc and isinstance(character, NPC):
        st.markdown("### 🎭 Motivations")
        for motivation in character.motivations:
            st.markdown(f"<div style='background: #1e293b; padding: 0.5rem; border-radius: 5px; margin: 0.25rem 0; color: #f1f5f9; font-weight: 500;'>💭 {motivation}</div>", unsafe_allow_html=True)
        
        if character.personality:
            st.markdown("### 🧠 Personality")
            st.markdown(f"<div style='background: #1e293b; padding: 0.75rem; border-radius: 8px; border: 1px solid #475569; color: #f1f5f9; font-weight: 500;'>{character.personality}</div>", unsafe_allow_html=True)


def render_ruling_card(ruling: Ruling) -> None:
    """Render a ruling with expandable details and visual styling."""
    
    outcome_colors = {
        RulingOutcome.SUCCESS: ("🟢", "#48bb78", "Success"),
        RulingOutcome.FAILURE: ("🔴", "#f56565", "Failure"),
        RulingOutcome.PARTIAL: ("🟡", "#ed8936", "Partial"),
        RulingOutcome.UNCERTAIN: ("⚪", "#a0aec0", "Uncertain"),
    }
    
    outcome_emoji, outcome_color, outcome_text = outcome_colors.get(ruling.outcome, ("⚪", "#a0aec0", "Unknown"))
    
    # Visual outcome badge
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%); 
                padding: 1rem; border-radius: 10px; border-left: 5px solid {outcome_color};
                margin: 0.5rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5rem;">{outcome_emoji}</span>
            <span style="color: {outcome_color}; font-weight: bold; font-size: 1.1rem;">{outcome_text}</span>
        </div>
        <div style="color: #e2e8f0;">{ruling.action[:80]}{'...' if len(ruling.action) > 80 else ''}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📋 View Details", expanded=False):
        st.markdown("#### ⚔️ Action")
        st.markdown(f"<div style='background: #1e293b; padding: 0.75rem; border-radius: 8px; color: #f1f5f9; font-weight: 500;'>{ruling.action}</div>", unsafe_allow_html=True)
        
        st.markdown("#### 📖 Narrative")
        st.info(ruling.narrative)
        
        # Reasoning trace
        if ruling.reasoning:
            st.markdown("#### 🧠 Reasoning Trace")
            with st.expander("🔍 View Reasoning Steps", expanded=False):
                for step in ruling.reasoning.steps:
                    st.markdown(f"""
                    <div style="background: #1e293b; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #4299e1;">
                        <strong style="color: #60a5fa; font-weight: bold;">Step {step.step_number}:</strong>
                        <div style="color: #f1f5f9; margin-top: 0.5rem; font-weight: 500;">{step.description}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if step.relevant_facts:
                        st.caption(f"📌 Facts: {', '.join(step.relevant_facts[:3])}")
                    if step.conclusion:
                        st.caption(f"💡 {step.conclusion}")
                
                st.markdown("#### ✅ Final Conclusion")
                st.markdown(f"<div style='background: #1e293b; padding: 1rem; border-radius: 8px; color: #f1f5f9; border: 2px solid #48bb78; font-weight: 500;'>{ruling.reasoning.final_conclusion}</div>", unsafe_allow_html=True)
        
        # State changes
        if ruling.state_changes:
            st.markdown("#### 🔄 State Changes")
            for key, value in ruling.state_changes.items():
                st.markdown(f"<div style='background: #1e293b; padding: 0.5rem; border-radius: 5px; margin: 0.25rem 0; color: #f1f5f9; font-weight: 500;'>✨ <strong>{key}:</strong> {value}</div>", unsafe_allow_html=True)


def render_turn_card(turn_data: Dict[str, Any], turn_number: int) -> None:
    """Render a turn history card with visual styling."""
    
    player_name = turn_data.get("player_name", "Unknown")
    action = turn_data.get("action", "")
    gm_response = turn_data.get("gm_response", "")
    ruling = turn_data.get("ruling")
    
    # Turn header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%); 
                padding: 1rem; border-radius: 10px; border: 2px solid #4a5568;
                margin: 0.75rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.5rem;">🎲</span>
            <span style="color: #ffd700; font-weight: bold; font-size: 1.2rem;">Turn {turn_number}</span>
            <span style="color: #4299e1; margin-left: auto;">⚔️ {player_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📜 View Turn Details", expanded=False):
        if action:
            st.markdown("#### ⚔️ Player Action")
            st.markdown(f"""
            <div style="background: #1e293b; padding: 1rem; border-radius: 8px; 
                        border-left: 4px solid #4299e1; color: #f1f5f9; font-weight: 500;">
                <strong style="color: #60a5fa; font-weight: bold;">{player_name}:</strong> {action}
            </div>
            """, unsafe_allow_html=True)
        
        if gm_response:
            st.markdown("#### 📖 GM Response")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                        padding: 1.5rem; border-radius: 10px; border: 3px solid #d97706;
                        color: #1c1917 !important; font-family: Georgia, serif; line-height: 1.8;
                        font-weight: 500; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                {gm_response}
            </div>
            """, unsafe_allow_html=True)
        
        if ruling:
            render_ruling_card(ruling)


def render_game_stats(game_state: Any) -> None:
    """Render game statistics with visual styling."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%); 
                    padding: 1rem; border-radius: 10px; border: 2px solid #4a5568;
                    text-align: center; margin: 0.5rem 0;">
            <div style="font-size: 2rem; color: #4299e1; font-weight: bold;">{game_state.current_turn}</div>
            <div style="color: #a0aec0; font-size: 0.9rem;">🎲 Current Turn</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%); 
                    padding: 1rem; border-radius: 10px; border: 2px solid #4a5568;
                    text-align: center; margin: 0.5rem 0;">
            <div style="font-size: 2rem; color: #48bb78; font-weight: bold;">{len(game_state.characters)}</div>
            <div style="color: #a0aec0; font-size: 0.9rem;">⚔️ Players</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                    padding: 1rem; border-radius: 10px; border: 2px solid #475569;
                    text-align: center; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">
            <div style="font-size: 2rem; color: #fb923c; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{len(game_state.turns)}</div>
            <div style="color: #cbd5e1; font-size: 0.9rem; font-weight: 500;">📜 Total Turns</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                    padding: 1rem; border-radius: 10px; border: 2px solid #475569;
                    text-align: center; margin: 0.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.5);">
            <div style="font-size: 2rem; color: #a78bfa; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{len(game_state.npcs)}</div>
            <div style="color: #cbd5e1; font-size: 0.9rem; font-weight: 500;">👤 NPCs</div>
        </div>
        """, unsafe_allow_html=True)

