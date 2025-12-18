"""Base submodule shim for langchain_core.runnables.base"""
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RunnableBase:
    name: str
    config: Dict[str, Any] = None


__all__ = ["RunnableBase"]


class Runnable(RunnableBase):
    def __call__(self, *args, **kwargs):
        return None

__all__.append("Runnable")


@dataclass
class RunnableConfig:
    options: Dict[str, Any] = None

__all__.append("RunnableConfig")


class RunnableLambda(Runnable):
    def __init__(self, func):
        super().__init__(name=getattr(func, "__name__", "lambda"))
        self._func = func

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)

__all__.append("RunnableLambda")


class RunnableParallel(Runnable):
    """Compatibility shim representing a parallel runnable."""
    def __init__(self, *runnables):
        super().__init__(name="parallel")
        self.runnables = list(runnables)

    def __call__(self, *args, **kwargs):
        results = []
        for r in self.runnables:
            try:
                results.append(r(*args, **kwargs))
            except Exception:
                results.append(None)
        return results


__all__.append("RunnableParallel")


class RunnableSequence(Runnable):
    """Compatibility shim representing a sequence of runnables run in order."""
    def __init__(self, *runnables):
        super().__init__(name="sequence")
        self.runnables = list(runnables)

    def __call__(self, *args, **kwargs):
        result = None
        for r in self.runnables:
            result = r(*args, **kwargs)
        return result


__all__.append("RunnableSequence")


class RunnableLike(Runnable):
    """Compatibility alias used in some langchain variants."""
    pass


__all__.append("RunnableLike")
