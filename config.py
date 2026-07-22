"""Central configuration for the prompt injection lab.

Change model names, paths, and the attacker listener address here so you don't
have to hunt through the other files.
"""

# --- Ollama models ---
CHAT_MODEL = "qwen2.5:7b-instruct"   # if this is unreliable at tool calls, try "llama3.1:8b"
EMBED_MODEL = "nomic-embed-text"     # produces 768-dim vectors

# --- Qdrant (runs locally, on disk -- no Docker needed) ---
QDRANT_PATH = "./qdrant_data"        # folder where the vector DB is stored
COLLECTION = "lab_docs"
VECTOR_SIZE = 768                    # must match EMBED_MODEL's output size
TOP_K = 3                            # how many documents to retrieve per query

# --- Documents ---
DOCS_DIR = "documents"

# --- Attacker listener (stands in for the attacker's server) ---
LISTENER_HOST = "127.0.0.1"
LISTENER_PORT = 9999

# --- Agent loop ---
MAX_TOOL_ITERATIONS = 5              # safety cap so the loop can't run forever
