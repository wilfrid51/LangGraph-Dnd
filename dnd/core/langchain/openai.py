from dataclasses import dataclass
from typing import Any

@dataclass
class ChatOpenAI:
    """
    This is a stub for the ChatOpenAI class from langchain_openai.
    It is used to mock the ChatOpenAI class for testing purposes.
    It is not a real LLM client and is meant only to allow quick local verification and smoke tests.
    """
    model: str | None = None
    temperature: float = 0.7

    def __call__(self, *args: Any, **kwargs: Any):
        return self

    def invoke(self, *args: Any, **kwargs: Any):
        class _Resp:
            content = "(stubbed response)"
        return _Resp()