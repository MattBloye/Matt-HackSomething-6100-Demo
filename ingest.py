"""Load every document in documents/, embed it, and store it in Qdrant.

Run this once (and again whenever you change the documents):

    python ingest.py
"""
import os
import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import QDRANT_PATH, COLLECTION, VECTOR_SIZE, EMBED_MODEL, DOCS_DIR


def embed(text: str) -> list:
    """Turn text into a vector using the local embedding model."""
    return ollama.embeddings(model=EMBED_MODEL, prompt=text).embedding


def ingest():
    client = QdrantClient(path=QDRANT_PATH)

    # Fresh start each run so re-ingesting is predictable.
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    points = []
    for i, fname in enumerate(sorted(os.listdir(DOCS_DIR))):
        path = os.path.join(DOCS_DIR, fname)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        # NOTE: each file is stored as one chunk. Fine for a small demo.
        # TODO (optional, your call): split long docs into smaller chunks for more
        # realistic retrieval. Not required for the attack to work.
        points.append(
            PointStruct(id=i, vector=embed(text), payload={"source": fname, "text": text})
        )
        print(f"[ingest] embedded {fname}")

    client.upsert(collection_name=COLLECTION, points=points)
    client.close()
    print(f"[ingest] stored {len(points)} documents in Qdrant at {QDRANT_PATH}")


if __name__ == "__main__":
    ingest()
