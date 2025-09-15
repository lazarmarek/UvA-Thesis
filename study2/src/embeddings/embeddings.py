from __future__ import annotations
from typing import Sequence, Protocol, Optional, runtime_checkable
import torch

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

@runtime_checkable
class TextEmbedding(Protocol):
    def embed_query(self, text: str) -> list[float]: ...
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

class BGETextEmbeddings(TextEmbedding):
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        device = device or ("cuda" if (torch and torch.cuda.is_available()) else "cpu")
        self._emb = HuggingFaceBgeEmbeddings(
            model_name=model_name or "BAAI/bge-base-en-v1.5",
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True},
            query_instruction="Represent this sentence for searching relevant passages:",
        )
    def embed_query(self, text: str) -> list[float]:
        return self._emb.embed_query(text)
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return self._emb.embed_documents(list(texts))
    @property
    def inner(self):  # for LangChain integrations that expect its type
        return self._emb

class HFTextEmbeddings(TextEmbedding):
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        device = device or ("cuda" if (torch and torch.cuda.is_available()) else "cpu")
        self._emb = HuggingFaceEmbeddings(
            model_name=model_name or "sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True},
        )
    def embed_query(self, text: str) -> list[float]:
        return self._emb.embed_query(text)
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return self._emb.embed_documents(list(texts))
    @property
    def inner(self):
        return self._emb

class EmbeddingsFactory:
    _registry = {
        "bge": BGETextEmbeddings,
        "hf": HFTextEmbeddings,
    }
    @classmethod
    def create(cls, kind: str = "bge", **kwargs) -> TextEmbedding:
        kind = (kind or "bge").lower()
        if kind not in cls._registry:
            raise ValueError(f"Unknown embeddings kind: {kind}")
        return cls._registry[kind](**kwargs)