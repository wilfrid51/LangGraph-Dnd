from dataclasses import dataclass
from typing import Any, Callable, Dict
import os

# Allow this module to behave like a package by exposing a __path__ that
# points to the companion 'runnables' directory so submodules like
# 'langchain_core.runnables.base' can be imported even when a module file
# exists in the same location.
__path__ = [os.path.join(os.path.dirname(__file__), "runnables")]


@dataclass
class RunnableConfig:
    options: Dict[str, Any] = None


class Runnable:
    def __init__(self, func: Callable[..., Any], config: RunnableConfig = None):
        self.func = func
        self.config = config or RunnableConfig()

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def run(runnable: Runnable, *args, **kwargs):
    return runnable(*args, **kwargs)


__all__ = ["Runnable", "run", "RunnableConfig"]
