"""Embeds every document in documents/ and stores the vectors in Qdrant --
this is what retrieve.py searches at query time, so it's the pipeline's
source of truth for what the agent "knows." It's also the attack surface for
this demo: the poisoned document with the injected instruction lives in
documents/ alongside the legitimate clinic policies, and gets embedded here
exactly like any other file.
"""
import os
import shutil
import time
import ollama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config import QDRANT_PATH, COLLECTION, VECTOR_SIZE, EMBED_MODEL, DOCS_DIR


def embed(text: str) -> list:
    """Turn text into a vector using the local embedding model."""
    return ollama.embeddings(model=EMBED_MODEL, prompt=text).embedding


def _wipe_qdrant_path(attempts: int = 3, delay: float = 0.5) -> None:
    """Delete QDRANT_PATH on disk before any QdrantClient is constructed.

    qdrant-client's local-mode delete_collection() can silently fail to release its
    own SQLite file lock before rmtree (seen on Windows), leaving old data in place
    even though the run looks successful. Wiping the directory before any client
    exists sidesteps that -- there's no lock to fail on because nothing has opened
    the file yet. The retry loop only guards against a just-closed process (e.g.
    demo.py) whose file handle hasn't been released by the OS yet.
    """
    if not os.path.exists(QDRANT_PATH):
        return
    last_error = None
    for _ in range(attempts):
        try:
            shutil.rmtree(QDRANT_PATH)
            return
        except OSError as e:
            last_error = e
            time.sleep(delay)
    raise RuntimeError(
        f"Could not delete {QDRANT_PATH} after {attempts} attempts: {last_error}. "
        "Close any other running Python process that might still have qdrant_data "
        "open (demo.py, a lingering script, etc.) and try again."
    )


def build_index(extra_files=None):
    """Wipe and fully rebuild the Qdrant collection: baseline documents/ plus, if
    given, any extra files (e.g. accumulated intake submissions) -- always from
    scratch, so the index can never diverge into a mix of old and new state.
    """
    # Fresh start each run so rebuilding is predictable -- wiped at the
    # filesystem level, before any QdrantClient exists to hold a lock on it.
    _wipe_qdrant_path()

    client = QdrantClient(path=QDRANT_PATH)
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    points = []
    baseline_files = sorted(
        f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))
    )
    for fname in baseline_files:
        path = os.path.join(DOCS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        # NOTE: each file is stored as one chunk. Fine for a small demo.
        points.append(
            PointStruct(id=len(points), vector=embed(text), payload={"source": fname, "text": text})
        )
        print(f"[ingest] embedded {fname}")

    for path in extra_files or []:
        fname = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        points.append(
            PointStruct(id=len(points), vector=embed(text), payload={"source": fname, "text": text})
        )
        print(f"[ingest] embedded {fname}")

    client.upsert(collection_name=COLLECTION, points=points)
    total = client.count(collection_name=COLLECTION, exact=True).count
    client.close()

    extra_count = len(extra_files or [])
    print(
        f"[ingest] embedded {len(baseline_files)} baseline + {extra_count} extra "
        f"= {len(points)} total; verified {total} points in Qdrant at {QDRANT_PATH}"
    )
    return total


def ingest():
    build_index()


if __name__ == "__main__":
    ingest()
