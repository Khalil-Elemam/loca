import chromadb
from sentence_transformers import SentenceTransformer
import torch

from .utils import get_project_cache_path
from .snippet import Snippet


project_cache_path = get_project_cache_path() / "chroma"
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device="cuda" if torch.cuda.is_available() else "cpu",
)
chroma_client = chromadb.PersistentClient(path=project_cache_path)

collection = chroma_client.get_or_create_collection(name="snippets")

delete = collection.delete


def add(snippets: list[Snippet]) -> None:
    """
    Add a list of Snippet objects to the ChromaDB collection.
    """
    if not snippets:
        return
    collection.add(
        ids=[s.id for s in snippets],
        documents=[s.code for s in snippets],
        embeddings=[model.encode(s.get_embedding_text()) for s in snippets],
        metadatas=[s.to_dict() for s in snippets],
    )


def query(q: str, n_results: int = 5) -> chromadb.QueryResult:
    query_embedding = model.encode(q)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas"],
    )


def clear() -> None:
    chroma_client.delete_collection(name="snippets")
