from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class RulingOutcome(str, Enum):
    """Possible ruling outcomes."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"
    UNCERTAIN = "UNCERTAIN"


class ReasoningStep(BaseModel):
    """A single step in reasoning."""
    
    step_number: int
    description: str
    relevant_facts: List[str] = Field(default_factory=list)
    conclusion: Optional[str] = None


class ReasoningTrace(BaseModel):
    """Complete reasoning trace for a ruling."""
    
    situation: str
    relevant_facts: List[str] = Field(default_factory=list)
    steps: List[ReasoningStep] = Field(default_factory=list)
    final_conclusion: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def add_step(self, description: str, facts: List[str] = None, conclusion: str = None) -> None:
        """Add a reasoning step."""
        step = ReasoningStep(
            step_number=len(self.steps) + 1,
            description=description,
            relevant_facts=facts or [],
            conclusion=conclusion
        )
        self.steps.append(step)


class Ruling(BaseModel):
    """A GM ruling on a player action."""
    
    action: str
    outcome: RulingOutcome
    reasoning: ReasoningTrace
    narrative: str
    state_changes: Dict[str, Any] = Field(default_factory=dict)
    can_challenge: bool = True
    challenged: bool = False
    challenge_resolution: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def challenge(self, player_reasoning: str) -> None:
        """Mark this ruling as challenged."""
        self.challenged = True
        self.challenge_resolution = player_reasoning

