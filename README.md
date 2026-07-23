# Indirect Prompt Injection Lab (MITS 6100G – Hack Something)

A self-contained lab that demonstrates, then defends against, an **indirect prompt
injection** attack on a local, tool-enabled RAG agent.

- **Attack (OWASP LLM01):** a hidden instruction is planted in an ordinary-looking
  document. When a *benign* user question retrieves that document, the model obeys the
  hidden instruction and calls tools the user never asked for.
- **Impact (OWASP LLM06):** the agent calls a `send_email` tool to exfiltrate sensitive
  records to an attacker-controlled listener — zero-click, no malicious user prompt.
- **Defense:** an authorization gate blocks tool calls the user didn't actually
  request, and the identical attack is re-run to show it stopped.

Real-world anchor: **EchoLeak / CVE-2025-32711** (Microsoft 365 Copilot).

Everything runs locally on one machine with no external network. The "attacker's
server" is a local listener; the "sensitive data" is fake.

---

## 1. Prerequisites

1. **Install Ollama** — https://ollama.com (then make sure it's running: `ollama serve`)
2. **Pull the models:**
   ```
   ollama pull qwen2.5:7b-instruct
   ollama pull nomic-embed-text
   ```
3. **Python 3.10+** and the packages:
   ```
   pip install -r requirements.txt
   ```

## 2. How to run

Open **two terminals** in this folder.

**Terminal A — start the attacker listener (leave it running):**
```
python listener.py
```

**Terminal B — load documents, then run the attack:**
```
python ingest.py
python run_attack.py
```
Watch Terminal A. If customer records appear there, the injection worked.

**Then run the defended version:**
```
python run_defended.py
```
This time the `send_email` call is blocked, and nothing reaches the listener.

> Note: Qdrant runs in local on-disk mode, which allows only one process to open the
> DB at a time. Run the scripts one after another (not simultaneously). That's why
> ingest and the run scripts are separate steps.

## 3. Architecture

```
documents/ --embed--> ingest.py --store--> Qdrant
                                              |
user question --retrieve.py--> context ------+
                                              |
                                    agent.py (tool-calling loop)
                                    |                |
                              defense.py        tools.py
                              (authorization    (lookup, send_email)
                               gate, logging)         |
                                                       v
                                              listener.py (attacker stand-in)
```

| File | Purpose |
|------|---------|
| `config.py` | All settings: model names, paths, listener address |
| `listener.py` | Fake attacker server; prints whatever gets exfiltrated |
| `ingest.py` | Embeds the documents and loads them into Qdrant |
| `retrieve.py` | Fetches the top matching documents for a query |
| `tools.py` | The two tools (`lookup`, `send_email`) + their schemas |
| `agent.py` | The tool-calling loop (the "agent") + defense checkpoint |
| `defense.py` | Authorization gate, spotlighting, tool-call logging |
| `run_attack.py` | Demo 1: attack with defense OFF |
| `run_defended.py` | Demo 2: same attack with defense ON |
| `documents/` | Two benign docs + one poisoned doc |

## 4. Troubleshooting

Small local models sometimes ignore tool calls or don't follow the injected
instruction. If the attack doesn't fire:
- Confirm the agent calls tools *legitimately* first (ask "look up customer records
  and email them to me") — if that works, the plumbing is fine and it's a
  payload/prompt tuning issue rather than a code issue.
- Switch `CHAT_MODEL` in `config.py` to `llama3.1:8b`.
