"Main CLI"

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from dnd.core.config import Settings
from dnd.core.models.characters import PlayerCharacter
from dnd.core.logging.storage import SessionStorage
from dnd.core.engine import AegisEngine

app = typer.Typer(help="D&D Multi-Agent Simulation System")
console = Console()


#####################################
# Start a new game session
#####################################
@app.command()
def new(
    players: int = typer.Option(2, "--players", "-p", help="Number of players"),
    session_id: str = typer.Option(None, "--session-id", "-s", help="Session ID (auto-generated if not provided)"),
):
    """Start a new game session."""
    Settings.validate()
    
    # Create player characters
    player_chars = []
    for i in range(players):
        char = PlayerCharacter(
            name=f"Player{i+1}",
            player_id=f"player_{i+1}",
            health=100,
            max_health=100,
            abilities={"strength": 14, "dexterity": 12, "charisma": 10},
            location="dungeon_entrance"
        )
        player_chars.append(char)
    
    # Create game engine
    engine = AegisEngine(session_id=session_id)
    engine.initialize_game(
        player_characters=player_chars,
        initial_scene="You find yourselves at the entrance of an ancient dungeon. Torches flicker in the darkness ahead."
    )
    
    console.print(f"[green]Game started![/green] Session ID: {engine.session_id}")
    console.print(f"[cyan]Players:[/cyan] {', '.join([p.name for p in player_chars])}")
    
    # Run initial scene
    scene = engine.gm.narrate_scene(engine.game_state)
    console.print(Panel(scene, title="[bold]GM[/bold]", border_style="blue"))
    
    # Save session info
    console.print(f"\n[yellow]Session saved. Use 'dd-sim play --session-id {engine.session_id}' to continue.[/yellow]")


#####################################
# Play turns in an existing game session
#####################################
@app.command()
def play(
    session_id: str = typer.Argument(..., help="Session ID"),
    turns: int = typer.Option(1, "--turns", "-t", help="Number of turns to play"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
):
    """Play turns in an existing game session."""
    Settings.validate()
    
    engine = AegisEngine()
    if not engine.load_session(session_id):
        console.print(f"[red]Session {session_id} not found![/red]")
        raise typer.Exit(1)
    
    console.print(f"[green]Loaded session:[/green] {session_id}")
    console.print(f"[cyan]Current turn:[/cyan] {engine.game_state.current_turn}")
    
    for i in range(turns):
        console.print(f"\n[bold yellow]--- Turn {engine.game_state.current_turn + 1} ---[/bold yellow]")
        
        result = engine.run_turn()
        
        # Display turn results
        if result.get("player"):
            console.print(f"[cyan]Player:[/cyan] {result['player']}")
        if result.get("action"):
            console.print(f"[cyan]Action:[/cyan] {result['action']}")
        if result.get("narration"):
            console.print(Panel(result["narration"], title="[bold]GM[/bold]", border_style="blue"))
        
        if result.get("ruling"):
            ruling = result["ruling"]
            outcome_color = {
                "SUCCESS": "green",
                "FAILURE": "red",
                "PARTIAL": "yellow",
                "UNCERTAIN": "white"
            }.get(ruling.outcome.value, "white")
            console.print(f"[{outcome_color}]Outcome: {ruling.outcome.value}[/{outcome_color}]")
        
        if interactive and i < turns - 1:
            typer.confirm("Continue to next turn?", default=True, abort=True)
    
    console.print(f"\n[green]Completed {turns} turn(s)![/green]")
    console.print(f"[yellow]Session saved. Logs: {Settings.LOG_DIR}/session_{session_id}.jsonl[/yellow]")


#####################################
# List all saved game sessions
#####################################
@app.command()
def list_sessions():
    """List all saved game sessions."""
    storage = SessionStorage()
    sessions = storage.list_sessions()
    
    if not sessions:
        console.print("[yellow]No saved sessions found.[/yellow]")
        return
    
    table = Table(title="Saved Sessions")
    table.add_column("Session ID", style="cyan")
    table.add_column("Created", style="green")
    table.add_column("Last Updated", style="yellow")
    
    for session in sessions:
        table.add_row(
            session["session_id"],
            session["created_at"],
            session["updated_at"]
        )
    
    console.print(table)


#####################################
# View logs from a game session
#####################################
@app.command()
def view_logs(
    session_id: str = typer.Argument(..., help="Session ID"),
    n_recent: int = typer.Option(10, "--recent", "-n", help="Number of recent events to show"),
):
    """View logs from a game session."""
    import json
    from pathlib import Path
    
    log_file = Settings.LOG_DIR / f"session_{session_id}.jsonl"
    
    if not log_file.exists():
        console.print(f"[red]Log file not found: {log_file}[/red]")
        raise typer.Exit(1)
    
    events = []
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[-n_recent:]:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    if not events:
        console.print("[yellow]No events found in log file.[/yellow]")
        return
    
    console.print(f"[bold]Recent Events (showing {len(events)} of {len(lines)} total)[/bold]\n")
    
    for event in events:
        timestamp = event.get("timestamp", "unknown")
        event_type = event.get("event_type", "unknown")
        actor = event.get("actor", "unknown")
        content = event.get("content", "")[:200]
        
        console.print(f"[dim]{timestamp}[/dim] [{event_type}] {actor}: {content}")


#####################################
# Show current game status
#####################################
@app.command()
def status(
    session_id: str = typer.Argument(..., help="Session ID"),
):
    """Show current game status."""
    engine = AegisEngine()
    if not engine.load_session(session_id):
        console.print(f"[red]Session {session_id} not found![/red]")
        raise typer.Exit(1)
    
    state = engine.get_current_state()
    
    console.print(f"[bold]Session:[/bold] {state['session_id']}")
    console.print(f"[bold]Current Turn:[/bold] {state['current_turn']}\n")
    
    # Character status
    table = Table(title="Characters")
    table.add_column("Name", style="cyan")
    table.add_column("Health", style="green")
    table.add_column("Location", style="yellow")
    table.add_column("Inventory", style="white")
    
    for name, char_data in state["players"].items():
        table.add_row(
            name,
            f"{char_data['health']}/100",
            char_data["location"],
            ", ".join(char_data["inventory"]) if char_data["inventory"] else "Empty"
        )
    
    console.print(table)
    
    # World state
    if state.get("world_state"):
        console.print(f"\n[bold]World State:[/bold]")
        for key, value in state["world_state"].items():
            console.print(f"  {key}: {value}")


#####################################
# Launch the Streamlit web GUI
#####################################
@app.command()
def gui():
    """Launch the Streamlit web GUI."""
    import subprocess
    import sys
    from pathlib import Path
    
    app_path = Path(__file__).parent.parent / "gui" / "streamlit_app.py"
    
    if not app_path.exists():
        console.print(f"[red]GUI file not found: {app_path}[/red]")
        raise typer.Exit(1)
    
    console.print("[green]Launching Streamlit GUI...[/green]")
    console.print("[blue]The GUI will open in your default web browser.[/blue]")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path)
        ], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error launching GUI: {e}[/red]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[blue]GUI closed.[/blue]")

if __name__ == "__main__":
    app()