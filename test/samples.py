"""Example: Basic game session."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dnd.core.config import Config
from dnd.core.engine import GameEngine
from dnd.core.models.characters import PlayerCharacter, NPC

# Validate config
Config.validate()

# Create player characters
throg = PlayerCharacter(
    name="Throg",
    player_id="throg",
    health=100,
    max_health=100,
    abilities={"strength": 16, "dexterity": 12, "charisma": 8},
    location="dungeon_entrance",
    secret_objectives=["Find the ancient artifact"]
)

elara = PlayerCharacter(
    name="Elara",
    player_id="elara",
    health=80,
    max_health=80,
    abilities={"strength": 10, "dexterity": 16, "charisma": 14},
    location="dungeon_entrance"
)

# Create an NPC
captain_vex = NPC(
    name="Captain Vex",
    health=100,
    motivations=["Loyal to the king", "Values honor above gold"],
    personality="Suspicious, formal, honorable",
    disposition={"Throg": 0, "Elara": 0}
)

# Create game engine
engine = GameEngine(session_id="example_001")
engine.initialize_game(
    player_characters=[throg, elara],
    npcs=[captain_vex],
    initial_scene="You stand before the entrance to the ancient dungeon. Captain Vex guards the door, eyeing you warily."
)

print(f"Game started! Session ID: {engine.session_id}\n")

# Run initial narration
scene = engine.gm.narrate_scene(engine.game_state)
print(f"GM: {scene}\n")

# Play a few turns
for i in range(5):
    print(f"\n--- Turn {engine.game_state.current_turn + 1} ---")
    result = engine.run_turn()
    
    print(f"Player: {result['player']}")
    print(f"Action: {result['action']}")
    print(f"GM: {result['narration']}")
    print(f"Outcome: {result['ruling'].outcome.value if result.get('ruling') else 'N/A'}")

print(f"\n\nGame complete! Session saved.")
print(f"View logs: python -m dnd.interface.cli.main view-logs {engine.session_id}")

