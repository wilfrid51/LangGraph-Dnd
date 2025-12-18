from dataclasses import dataclass
from typing import Any, List


@dataclass
class AIMessage:
    content: str


@dataclass
class HumanMessage:
    content: str


@dataclass
class SystemMessage:
    content: str


def to_message_dict(msg: Any) -> dict:
    return {"content": getattr(msg, "content", str(msg))}

# Backwards-compatible alias expected by some langchain versions
class AnyMessage:
    def __init__(self, content: str):
        self.content = content


class BaseMessage(AnyMessage):
    pass


@dataclass
class BaseMessageChunk:
    text: str
    chunk_index: int = 0
    metadata: dict = None


__all__ = [
    "AIMessage",
    "HumanMessage",
    "SystemMessage",
    "AnyMessage",
    "BaseMessage",
    "BaseMessageChunk",
    "MessageLikeRepresentation",
    "to_message_dict",
    "RemoveMessage",
    "convert_to_messages",
]


# Minimal alias used by some langchain versions
class MessageLikeRepresentation(dict):
    def __init__(self, content: str, **kwargs):
        super().__init__(content=content, **kwargs)


class RemoveMessage(BaseMessage):
    """Marker message used when a message is removed or redacted."""
    def __init__(self, content: str = ""):
        super().__init__(content)


def convert_to_messages(data: Any) -> List[BaseMessage]:
    """Convert various inputs into a list of BaseMessage instances."""
    if isinstance(data, BaseMessage):
        return [data]
    if isinstance(data, (AIMessage, HumanMessage, SystemMessage, AnyMessage)):
        return [BaseMessage(getattr(data, "content", str(data)))]
    if isinstance(data, str):
        return [BaseMessage(data)]
    if isinstance(data, list):
        out: List[BaseMessage] = []
        for item in data:
            out.extend(convert_to_messages(item))
        return out
    return [BaseMessage(str(data))]


def message_chunk_to_message(chunk: BaseMessageChunk) -> BaseMessage:
    """Convert a BaseMessageChunk into a BaseMessage instance."""
    text = getattr(chunk, "text", "")
    return BaseMessage(text)
