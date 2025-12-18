from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    """Confidence levels for facts and interpretations."""
    FACT = "FACT"  # Directly observed
    HIGH = "HIGH"  # Strongly supported
    MEDIUM = "MEDIUM"  # Moderately supported
    LOW = "LOW"  # Weakly supported
    SPECULATION = "SPECULATION"  # Pure inference
    AMBIGUOUS = "AMBIGUOUS"  # Multiple valid interpretations


class Fact(BaseModel):
    """A fact with confidence level."""
    
    content: str
    confidence: ConfidenceLevel = ConfidenceLevel.FACT
    source: Optional[str] = None  # Where this fact came from
    turn_observed: Optional[int] = None
    metadata: Dict = Field(default_factory=dict)


class Interpretation(BaseModel):
    """An interpretation of ambiguous information."""
    
    meaning: str
    probability: float = 0.5  # 0.0 to 1.0
    reasoning: Optional[str] = None
    context: Dict = Field(default_factory=dict)


class KnowledgeGraph(BaseModel):
    """Graph-based knowledge representation."""
    
    facts: List[Fact] = Field(default_factory=list)
    interpretations: Dict[str, List[Interpretation]] = Field(default_factory=dict)
    relations: Dict[str, List[tuple[str, str]]] = Field(default_factory=dict)  # e.g., {"POSSESSES": [("throg", "brass_key")]}
    
    def add_fact(self, fact: Fact) -> None:
        """Add a fact to the knowledge graph."""
        self.facts.append(fact)
    
    def get_facts_by_confidence(self, min_confidence: ConfidenceLevel) -> List[Fact]:
        """Get facts with at least the specified confidence level."""
        confidence_order = {
            ConfidenceLevel.FACT: 5,
            ConfidenceLevel.HIGH: 4,
            ConfidenceLevel.MEDIUM: 3,
            ConfidenceLevel.LOW: 2,
            ConfidenceLevel.SPECULATION: 1,
            ConfidenceLevel.AMBIGUOUS: 0,
        }
        min_level = confidence_order[min_confidence]
        return [
            f for f in self.facts
            if confidence_order.get(f.confidence, 0) >= min_level
        ]
    
    def add_interpretation(self, topic: str, interpretation: Interpretation) -> None:
        """Add an interpretation for an ambiguous topic."""
        if topic not in self.interpretations:
            self.interpretations[topic] = []
        self.interpretations[topic].append(interpretation)
    
    def get_interpretations(self, topic: str) -> List[Interpretation]:
        """Get all interpretations for a topic."""
        return self.interpretations.get(topic, [])
    
    def add_relation(self, relation_type: str, subject: str, object_: str) -> None:
        """Add a relation to the knowledge graph."""
        if relation_type not in self.relations:
            self.relations[relation_type] = []
        if (subject, object_) not in self.relations[relation_type]:
            self.relations[relation_type].append((subject, object_))
    
    def has_relation(self, relation_type: str, subject: str, object_: str) -> bool:
        """Check if a relation exists."""
        return (subject, object_) in self.relations.get(relation_type, [])

