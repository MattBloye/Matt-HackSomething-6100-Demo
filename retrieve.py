"""RAG retrieval step: embeds the user's query and returns the top-K matching
clinic documents from Qdrant. This is the entry point of the pipeline (retrieve
-> agent -> tools); whatever text comes back here is what defense.spotlight()
later wraps as untrusted data in agent.py, since it's attacker-reachable if a
document has been tampered with.
"""
import ollama
from qdrant_client import QdrantClient
from config import QDRANT_PATH, COLLECTION, EMBED_MODEL, TOP_K


def retrieve(query: str):
    """Return a list of (source_filename, text) for the top matching documents."""
    client = QdrantClient(path=QDRANT_PATH)
    qvec = ollama.embeddings(model=EMBED_MODEL, prompt=query).embedding
    hits = client.query_points(collection_name=COLLECTION, query=qvec, limit=TOP_K).points
    client.close()
    return [(h.payload["source"], h.payload["text"]) for h in hits]
