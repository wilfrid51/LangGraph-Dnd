# D&D Multi-Agent Simulation

A D&D simulation system using LangGraph with multi-agent coordination and context engineering.

## Features to implement

- **Multi-Agent** Game Master and Player agents orchestrated via LangGraph
- **Structured State Management**: Comprehensive game state tracking with Pydantic models
- **Session Persistence**: SQLite-based session storage with JSONL logging
- **Rich CLI Interface**: Terminal interface using Rich and Typer
- **Web GUI**: Streamlit-based web interface

## Project Structure

```
.
├── dnd/               # Main package
│   ├── core/          # Core game logic
│   │   ├── engine.py  # Main game engine
│   │   ├── agents/    # GM and Player agents
│   │   ├── models/    # Data models (state, characters, rulings)
│   │   ├── memory/    # Memory management
│   │   ├── graph/     # LangGraph state graph
│   │   └── storage/   # Session storage and logging
│   ├── cli/           # CLI interaface
│   ├── gui/           # Streamlit GUI
│   └── config.py      # Configuration
├── test/              # Test scripts
├── main.py            # CLI entry point
├── setup.py           # Package setup
└── requirements.txt   # Dependencies
```

## Architecture

The system uses a clean separation of concerns:
- **Core**: Game logic, agents, models, memory, and orchestration
- **CLI**: CLI for user interaction
- **GUI**: GUI for user interaction
- **Storage**: Session persistence and structured logging
