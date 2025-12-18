from typing import Any, Iterable, Tuple


class ChatPromptTemplate:
    """
    This is a stub for the ChatPromptTemplate class from langchain_core.
    It is used to mock the ChatPromptTemplate class for testing purposes.
    It is not a real prompt template and is meant only to allow quick local verification and smoke tests.
    """
    def __init__(self, messages: Iterable[Tuple[str, str]] | None = None):
        self.messages = list(messages or [])

    @classmethod
    def from_messages(cls, messages: Iterable[Tuple[str, str]]):
        return cls(messages)

    def __or__(self, llm: Any):
        # Return a simple callable object that accepts invocation
        class _Chain:
            def __init__(self, prompt, llm):
                self.prompt = prompt
                self.llm = llm

            def invoke(self, *args, **kwargs):
                class _Resp:
                    content = "(stubbed response)"

                return _Resp()

        return _Chain(self, llm)
