import chromadb

from .utils import get_project_cache_path
from .snippet import Snippet


project_cache_path = get_project_cache_path() / "chroma"
chroma_client = chromadb.PersistentClient(path=project_cache_path)

collection = chroma_client.get_or_create_collection(name="snippets")


def add(snippets: list[Snippet]) -> None:
    """
    Add a list of Snippet objects to the ChromaDB collection.
    """
    if not snippets:
        return
    collection.add(
        ids=[s.id for s in snippets],
        documents=[s.code for s in snippets],
        metadatas=[s.to_dict() for s in snippets],
    )


delete = collection.delete
query = collection.query


def clear() -> None:
    chroma_client.delete_collection(name="snippets")
