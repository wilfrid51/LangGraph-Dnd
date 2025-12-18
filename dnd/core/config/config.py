import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # LangSmith (optional)
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_API_KEY: Optional[str] = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "dd-simulation")
    
    # Memory Management
    MAX_CONTEXT_TURNS: int = int(os.getenv("MAX_CONTEXT_TURNS", "10"))
    MEMORY_CONSOLIDATION_THRESHOLD: int = int(os.getenv("MEMORY_CONSOLIDATION_THRESHOLD", "20"))
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    LOG_DIR: Path = BASE_DIR / os.getenv("LOG_DIR", "logs")
    SESSION_DB: Path = BASE_DIR / os.getenv("SESSION_DB", "sessions.db")
    
    # Model Configuration
    DEFAULT_MODEL: str = "gpt-4o-mini"
    GM_MODEL: str = os.getenv("GM_MODEL", "gpt-4o-mini")
    PLAYER_MODEL: str = os.getenv("PLAYER_MODEL", "gpt-4o-mini")
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment or .env file")


# Initialize directories on import
Config.ensure_directories()


# Public alias for a different import name
class Settings(Config):
    """
    Alias for `Config` to present an alternative public symbol name.

    This subclass does not change behavior; it exists purely for API surface
    differentiation during delivery.
    """

    pass