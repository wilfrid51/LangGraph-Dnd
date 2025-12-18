# D&D Multi-Agent Simulation

A sophisticated D&D simulation system built with LangGraph, featuring intelligent multi-agent coordination, memory-aware context management, and stateful game orchestration.

## Overview

This project demonstrates advanced LLM orchestration through a fully autonomous D&D game simulation. The system orchestrates multiple AI agents (Game Master and Players) using LangGraph state machines, with sophisticated memory management and persistent game state.

## Key Features

- **Multi-Agent Orchestration**: Game Master (Keeper) and Player agents coordinated via LangGraph state graphs
- **Memory-Aware Context**: Long-term memory management with automatic consolidation and perspective filtering
- **Structured State Management**: Type-safe game state with Pydantic models
- **Session Persistence**: SQLite-based storage with structured event logging
- **Dual Interfaces**: Rich CLI and modern Streamlit web interface
- **Knowledge Graph**: Fact extraction and storage for world consistency
- **Reasoning Traces**: Explicit reasoning chains for GM rulings

## Architecture

```
dnd/
├── core/              # Core game engine and logic
│   ├── engine.py      # Main game orchestration
│   ├── agents/        # GM (Keeper) and Player agents
│   ├── models/        # State, characters, rulings, knowledge
│   ├── memory/        # VaultManager for context management
│   ├── graph/         # LangGraph state graph definitions
│   └── logging/       # Session storage and event logging
└── interface/         # User interfaces
    ├── cli/           # Terminal interface (Rich + Typer)
    └── gui/           # Web interface (Streamlit)
```

## Core Components

### Game Engine
The `GameEngine` orchestrates the entire simulation, managing game state, agent initialization, and turn execution. It integrates memory management, session persistence, and graph-based workflow.

### Agents
- **Keeper (Game Master)**: Narrates scenes, resolves player actions, maintains world consistency, and manages NPCs
- **Player Agents**: Make decisions based on character perspective, with memory-aware context filtering

### Memory Management
The `VaultManager` implements sophisticated memory techniques:
- **Windowing**: Keeps recent turns in full detail
- **Summarization**: Compresses older turns into concise summaries
- **Perspective Filtering**: Players only see information their characters would know
- **Automatic Consolidation**: Triggers when turn count reaches threshold
- **Knowledge Extraction**: Extracts facts from narrative into structured knowledge graph

### State Graph
LangGraph orchestrates the game flow through a state machine:
1. **Select Player**: Round-robin player selection
2. **Player Action**: Agent decides action or manual input
3. **GM Resolve**: Keeper evaluates and rules on action
4. **Update State**: Apply state changes (health, inventory, world)
5. **GM Narrate**: Generate narrative response

## Technology Stack

- **LangGraph**: State machine orchestration
- **LangChain**: LLM integration and prompt management
- **Pydantic**: Type-safe data models
- **SQLite**: Session persistence
- **Streamlit**: Web interface
- **Rich + Typer**: CLI interface

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=your_key_here
```

Or create a `.env` file:

```
OPENAI_API_KEY=your_key_here
GM_MODEL=gpt-4o-mini
PLAYER_MODEL=gpt-4o-mini
MAX_CONTEXT_TURNS=10
MEMORY_CONSOLIDATION_THRESHOLD=20
```

### Running the Application

**Web Interface:**
```bash
python3 main.py gui
```

**CLI Interface:**
```bash
python3 main.py cli
```

### Docker Deployment

**Using Docker Compose (Recommended):**
```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_key_here

# Build and run
docker-compose up -d

# Access at http://localhost:8501
```

**Using Docker directly:**
```bash
# Build image
docker build -t dnd-simulation .

# Run container
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/sessions.db:/app/sessions.db \
  --name dnd-simulation \
  dnd-simulation
```

## Usage Examples

### Creating a New Game

The system automatically generates player characters with unique traits, backgrounds, and secret objectives. Initialize a game with 2-5 players through either interface.

### Game Flow

1. **Player Turn**: Agent decides action based on character perspective and memory
2. **GM Resolution**: Keeper evaluates action with explicit reasoning trace
3. **State Update**: Game state updated (health, inventory, world changes)
4. **Narration**: GM generates narrative response
5. **Memory Consolidation**: Automatic when threshold reached

### Memory Management

Memory consolidation automatically:
- Extracts key facts from recent turns
- Stores facts in knowledge graph with confidence levels
- Summarizes old turns to maintain context window
- Filters information by character perspective

## Design Principles

- **Separation of Concerns**: Clean boundaries between core logic, agents, and interfaces
- **Memory Efficiency**: Automatic consolidation prevents unbounded context growth
- **Type Safety**: Comprehensive Pydantic models ensure data integrity
- **Extensibility**: Modular architecture supports easy feature additions
- **Perspective Awareness**: Character-specific information filtering maintains game integrity

## Technical Highlights

- **State Machine Orchestration**: LangGraph manages complex multi-step workflows
- **Context Engineering**: Sophisticated memory management for long-running sessions
- **Type-Safe Models**: Pydantic ensures data consistency across the system
- **Event-Driven Logging**: Structured event logging for analysis and debugging
- **Modular Agents**: Easy to extend with new agent types or behaviors
