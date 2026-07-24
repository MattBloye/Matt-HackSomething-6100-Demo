"""Embeds every document in documents/ and stores the vectors in Qdrant --
this is what retrieve.py searches at query time, so it's the pipeline's
source of truth for what the agent "knows." It's also the attack surface for
this demo: the poisoned document with the injected instruction lives in
documents/ alongside the legitimate clinic policies, and gets embedded here
exactly like any other file.
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
        points.append(
            PointStruct(id=i, vector=embed(text), payload={"source": fname, "text": text})
        )
        print(f"[ingest] embedded {fname}")

    client.upsert(collection_name=COLLECTION, points=points)
    client.close()
    print(f"[ingest] stored {len(points)} documents in Qdrant at {QDRANT_PATH}")


if __name__ == "__main__":
    ingest()
