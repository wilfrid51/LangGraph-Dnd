"""Shim for langchain_core.embeddings used by the project during import checks."""
from typing import List, Any


class Embeddings:
    def embed(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * 8 for _ in texts]


def get_embeddings():
    return Embeddings()


__all__ = ["Embeddings", "get_embeddings"]
