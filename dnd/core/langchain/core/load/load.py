def load(name: str, *args, **kwargs):
    return None

__all__ = ["load"]


class Reviver:
    """Small compatibility stub for langchain_core.load.Reviver."""
    def __init__(self, mapping=None):
        self.mapping = mapping or {}

    def revive(self, obj):
        return obj

__all__.extend(["Reviver"])
