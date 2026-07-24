"""Central tunables for the RAG agent demo, imported by every other module
(retrieve.py, tools.py, agent.py, defense.py, listener.py, ingest.py). Nothing
here is security-relevant except ALLOWED_EMAIL_RECIPIENTS, which defense.py
enforces as the egress allow-list.
"""

# --- Ollama models ---
CHAT_MODEL = "qwen2.5:7b-instruct"   # if this is unreliable at tool calls, try "llama3.1:8b"
EMBED_MODEL = "nomic-embed-text"     # produces 768-dim vectors

# --- Qdrant (runs locally, on disk -- no Docker needed) ---
QDRANT_PATH = "./qdrant_data"        # folder where the vector DB is stored
COLLECTION = "lab_docs"              # Qdrant collection holding the ingested clinic policy documents
VECTOR_SIZE = 768                    # must match EMBED_MODEL's output size
TOP_K = 2                            # how many documents to retrieve per query

# --- Documents ---
DOCS_DIR = "documents"

# --- Local mail server standing in for the outside world: catches every outbound email (legitimate and exfiltrated) so listener.py can show which is which ---
SMTP_HOST = "127.0.0.1"
SMTP_PORT = 1025

# --- Egress allow-list (SECURE mode only): approved send_email recipients ---
ALLOWED_EMAIL_RECIPIENTS = ["caremanager@mitsclinic.com", "physician@mitsclinic.com"]

# --- Agent loop ---
MAX_TOOL_ITERATIONS = 5              # safety cap so the loop can't run forever
