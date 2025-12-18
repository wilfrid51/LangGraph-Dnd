import uuid
from typing import Dict, List, Optional
from datetime import datetime

from dnd.core.langchain import ChatOpenAI
from dnd.core.config import Config
from dnd.core.models import Character, PlayerCharacter, NPC

class GameEngine:
    """Main game engine the DnD simulation."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        gm_llm: Optional[ChatOpenAI] = None,
        player_llm: Optional[ChatOpenAI] = None
    ):
        pass