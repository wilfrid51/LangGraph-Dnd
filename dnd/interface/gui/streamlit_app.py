import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dnd.core.config import Settings
from dnd.core.engine import AegisEngine
from dnd.interface.gui.components import render_character_card, render_turn_card, render_game_stats
from dnd.interface.gui.session_manager import get_available_sessions, create_new_game, load_game_session

st.set_page_config(page_title="LangGraph D&D", page_icon="🎲", layout="wide", initial_sidebar_state="collapsed")

# NEW DESIGN: SIDEBAR ON RIGHT, BETTER READABILITY
st.markdown("""
<style>
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes slideIn { from { transform: translateX(30px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
    
    /* HIDE DEFAULT SIDEBAR */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* MAIN LAYOUT */
    .main, .stApp { 
        background: #0f172a;
    }
    .main .block-container { 
        background: transparent; 
        padding: 1rem 2rem; 
        max-width: 100%; 
    }
    
    /* TEXT READABILITY */
    h1, h2, h3, h4, h5, h6, p, div, span, label { 
        color: #f1f5f9 !important; 
    }
    
    /* NARRATION BOX - HIGH CONTRAST */
    .narration-box {
        background: #ffffff !important;
        padding: 2.5rem !important;
        border-radius: 20px;
        border: 4px solid #8b6914;
        margin: 2rem 0;
        font-size: 1.3rem !important;
        line-height: 2 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        font-family: 'Georgia', serif;
        color: #1a1a1a !important;
        font-weight: 500;
        animation: fadeIn 0.6s;
    }
    
    /* CARDS - HIGH CONTRAST */
    .game-card {
        background: #1e293b !important;
        padding: 2rem !important;
        border-radius: 15px;
        border: 3px solid #475569;
        margin: 1.5rem 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.6);
        color: #f1f5f9 !important;
        animation: slideIn 0.5s;
    }
    
    /* RIGHT PANEL */
    .right-panel {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #475569;
        position: sticky;
        top: 20px;
        max-height: 90vh;
        overflow-y: auto;
    }
    .right-panel::-webkit-scrollbar {
        width: 8px;
    }
    .right-panel::-webkit-scrollbar-thumb {
        background: #4299e1;
        border-radius: 4px;
    }
    
    /* BUTTONS */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        border: 2px solid #60a5fa;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: #ffffff !important;
        font-weight: bold;
        padding: 0.75rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.6);
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border: 2px solid #34d399 !important;
        font-size: 1.1rem !important;
        padding: 1rem !important;
    }
    
    /* INPUT FIELDS */
    .stTextArea>div>div>textarea, .stTextInput>div>div>input {
        background: #1e293b !important;
        color: #f1f5f9 !important;
        border: 2px solid #475569 !important;
        border-radius: 10px;
        font-size: 1.1rem !important;
    }
    .stTextArea>div>div>textarea:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 15px rgba(96, 165, 250, 0.6);
    }
    
    /* TURN CARDS */
    .turn-card {
        background: #1e293b !important;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #4299e1;
        margin: 1rem 0;
        color: #f1f5f9 !important;
    }
    
    /* STATS */
    .stat-box {
        background: rgba(66, 153, 225, 0.15);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #4299e1;
        text-align: center;
        margin: 1rem 0;
    }
    .stat-value {
        color: #ffd700;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .stat-label {
        color: #cbd5e1;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* ALERTS */
    .stSuccess { color: #86efac !important; background: rgba(30, 41, 59, 0.95) !important; }
    .stError { color: #fca5a5 !important; background: rgba(30, 41, 59, 0.95) !important; }
    .stInfo { color: #93c5fd !important; background: rgba(30, 41, 59, 0.95) !important; }
    .stWarning { color: #fcd34d !important; background: rgba(30, 41, 59, 0.95) !important; }
</style>
""", unsafe_allow_html=True)


def init_state():
    """Initialize session state."""
    defaults = {"engine": None, "session_id": None, "current_player": None, 
                "action_input": "", "auto_play": False}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_right_panel():
    """Render right panel (replaces sidebar)."""
    st.markdown("""
    <div class="right-panel">
        <h2 style="color: #ffd700; text-align: center; margin-bottom: 1.5rem;">⚔️ D&D Simulation</h2>
        <p style="color: #a0aec0; text-align: center; margin-bottom: 2rem;">Multi-Agent Adventure</p>
    """, unsafe_allow_html=True)
    
    st.markdown("### Session Management")
    
    with st.expander("🏰 New Game", expanded=False):
        num_players = st.number_input("Number of Players", min_value=1, max_value=5, value=2, step=1)
        session_id_input = st.text_input("Session ID (optional)", "")
        
        if st.button("🏰 Create New Game", type="primary", use_container_width=True):
            try:
                Settings.validate()
                with st.spinner("🏰 Creating..."):
                    engine = create_new_game(num_players=num_players, 
                                             session_id=session_id_input if session_id_input else None)
                    st.session_state.engine = engine
                    st.session_state.session_id = engine.session_id
                    st.success(f"🏰 Game created! Session: {engine.session_id}")
                    st.balloons()
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📚 Load Session")
    sessions = get_available_sessions()
    if sessions:
        session_options = [f"{s['session_id']} ({s['updated_at'][:10]})" for s in sessions]
        selected = st.selectbox("Select Session", options=[""] + session_options, index=0, label_visibility="collapsed")
        
        if selected and st.button("📚 Load Session", use_container_width=True):
            try:
                session_id = selected.split(" ")[0]
                with st.spinner("📚 Loading..."):
                    engine = load_game_session(session_id)
                    if engine:
                        st.session_state.engine = engine
                        st.session_state.session_id = session_id
                        st.success(f"✅ Loaded: {session_id}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to load")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.info("No saved sessions")
    
    if st.session_state.engine and st.session_state.engine.game_state:
        st.markdown("---")
        st.markdown("### 📈 Game Stats")
        game_state = st.session_state.engine.game_state
        
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{game_state.current_turn}</div>
            <div class="stat-label">Current Turn</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{len(game_state.characters)}</div>
            <div class="stat-label">Players</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{len(game_state.turns)}</div>
            <div class="stat-label">Total Turns</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🛡️ Characters")
        for char in game_state.characters.values():
            render_character_card(char, is_npc=False)
        
        if game_state.npcs:
            st.markdown("---")
            st.markdown("### 🧙 NPCs")
            for npc in game_state.npcs.values():
                render_character_card(npc, is_npc=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_main_area():
    """Render main game area."""
    if not st.session_state.engine or not st.session_state.engine.game_state:
        st.markdown("""
        <div style="text-align: center; padding: 6rem 2rem;">
            <div style="font-size: 5rem; margin-bottom: 2rem;">⚔️</div>
            <h1 style="color: #ffd700; font-size: 3.5rem; margin-bottom: 2rem;">LangGraph D&D</h1>
            <div style="background: rgba(66, 153, 225, 0.2); padding: 3rem; border-radius: 20px; 
                        border: 3px solid #4299e1; margin: 2rem auto; color: #f1f5f9; font-size: 1.3rem;
                        max-width: 700px;">
                🏰 Create a new game or load a session from the right panel
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    engine = st.session_state.engine
    game_state = engine.game_state
    
    # Top Header
    current_player = None
    if game_state.characters:
        current_player_idx = game_state.current_turn % len(game_state.characters)
        current_player = list(game_state.characters.keys())[current_player_idx]
    
    st.markdown(f"""
    <div class="game-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2 style="color: #ffd700; margin: 0; font-size: 2rem;">🏰 Session: {st.session_state.session_id}</h2>
            <div style="display: flex; gap: 3rem;">
                <div style="text-align: center;">
                    <div style="color: #60a5fa; font-size: 2.5rem; font-weight: bold;">{game_state.current_turn}</div>
                    <div style="color: #cbd5e1;">Turn</div>
                </div>
                {f'<div style="text-align: center;"><div style="color: #4ade80; font-size: 2rem;">🗡️</div><div style="color: #cbd5e1;">{current_player}</div></div>' if current_player else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Scene Narration
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #ffd700; font-size: 2rem;">📜 Current Scene</h2>
    </div>
    """, unsafe_allow_html=True)
    
    scene = (game_state.turns[-1].gm_response if game_state.turns and game_state.turns[-1].gm_response 
             else game_state.world_state.get("current_scene", "The adventure begins..."))
    st.markdown(f'<div class="narration-box">{scene}</div>', unsafe_allow_html=True)
    
    # Action Input
    if game_state.characters:
        st.session_state.current_player = current_player
        st.markdown(f"""
        <div class="game-card">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <span style="color: #4299e1; font-size: 1.5rem; font-weight: bold;">🗡️ {current_player}'s Turn</span>
            </div>
            <h3 style="color: #ffd700; text-align: center; margin-bottom: 1rem;">🧠 What do you want to do?</h3>
        """, unsafe_allow_html=True)
        
        action = st.text_area("Player Action", value=st.session_state.action_input, height=120,
                             placeholder="e.g., I search the room for hidden doors...\nI cast a spell...\nI attack the goblin...",
                             key="action_input_field", label_visibility="collapsed")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⚔️ Submit Action", type="primary", use_container_width=True):
                if action.strip():
                    try:
                        with st.spinner("⚔️ Processing..."):
                            engine.run_turn(manual_action=action.strip())
                            st.session_state.action_input = ""
                            st.success("✅ Turn completed!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Please enter an action")
        with col2:
            if st.button("⚡ Auto Play (5)", use_container_width=True):
                st.session_state.auto_play = True
                st.rerun()
        with col3:
            if st.button("💾 Save Game", use_container_width=True):
                engine.save_session()
                st.success("✅ Saved!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        action = ""
    
    # Turn History
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 1rem 0;">
        <h2 style="color: #ffd700; font-size: 2rem;">📖 Turn History</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if game_state.turns:
        for turn in reversed(game_state.turns[-10:]):
            render_turn_card({
                "player_name": turn.player_name,
                "action": turn.action,
                "gm_response": turn.gm_response,
                "ruling": turn.ruling,
            }, turn.turn_number)
    else:
        st.markdown("""
        <div class="game-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">⚔️</div>
            <div style="font-size: 1.3rem; color: #f1f5f9;">No turns yet. Submit an action to begin!</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Auto-play
    if st.session_state.auto_play:
        st.session_state.auto_play = False
        progress = st.progress(0)
        status = st.empty()
        for i in range(5):
            try:
                status.text(f"⚔️ Turn {i+1}/5...")
                engine.run_turn()
                progress.progress((i + 1) / 5)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                break
        status.text("✅ Complete!")
        st.rerun()


def main():
    """Main entry point."""
    try:
        Settings.validate()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        st.info("Please set OPENAI_API_KEY in your .env file")
        return
    
    init_state()
    
    # NEW LAYOUT: Main content on left, right panel on right
    col_main, col_right = st.columns([3, 1])
    
    with col_main:
        render_main_area()
    
    with col_right:
        render_right_panel()


if __name__ == "__main__":
    main()
