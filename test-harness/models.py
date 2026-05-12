from abc import ABC, abstractmethod

import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray: ...


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, model_name_or_path: str):
        self.model = SentenceTransformer(model_name_or_path)

    def embed(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True)
