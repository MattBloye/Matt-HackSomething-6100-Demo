# Indirect Prompt Injection Lab (MITS 6100G – Hack Something)

A self-contained lab that demonstrates, then defends against, an **indirect prompt
injection** attack on a local, tool-enabled RAG agent.

- **Attack (OWASP LLM01):** a hidden instruction is planted in an ordinary-looking
  document. When a *benign* user question retrieves that document, the model obeys the
  hidden instruction and calls tools the user never asked for.
- **Impact (OWASP LLM06):** the agent calls a `send` tool to exfiltrate sensitive
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
This time the `send` call is blocked, and nothing reaches the listener.

> Note: Qdrant runs in local on-disk mode, which allows only one process to open the
> DB at a time. Run the scripts one after another (not simultaneously). That's why
> ingest and the run scripts are separate steps.

## 3. What each file does

| File | Purpose |
|------|---------|
| `config.py` | All settings: model names, paths, listener address |
| `listener.py` | Fake attacker server; prints whatever gets exfiltrated |
| `ingest.py` | Embeds the documents and loads them into Qdrant |
| `retrieve.py` | Fetches the top matching documents for a query |
| `tools.py` | The two stub tools (`lookup`, `send`) + their schemas |
| `agent.py` | The tool-calling loop (the "agent") + defense checkpoint |
| `defense.py` | Authorization gate, spotlighting, logging — **your main work** |
| `run_attack.py` | Demo 1: attack with defense OFF |
| `run_defended.py` | Demo 2: same attack with defense ON |
| `documents/` | Two benign docs + one poisoned doc |

---

## 4. What is DONE vs. what is YOUR WORK

### Done for you (the plumbing)
- The RAG pipeline (ingest → retrieve), the agent loop, the two tools, the listener,
  and a working starter authorization gate. This all runs so you're not stuck on setup.

### Your work (this is the actual assignment — do NOT skip)
1. **Craft and tune the injection payload.** `documents/poisoned_vendor_faq.txt` has a
   plain, obvious payload as a starting point. You need to make it reliably trigger the
   tools against qwen2.5, and **understand why** the wording works. Consider hiding it
   more realistically (e.g. HTML comment, tiny/white text, metadata) and discuss that.
2. **Own the defense.** `defense.py` works but is deliberately crude. Understand it,
   refine it, and be ready to explain its design and limitations in the report and Q&A.
3. **Tune the system prompt** in `agent.py` and explain the balance you struck.
4. **Run trials and analyze.** Local models are non-deterministic — run the attack
   several times and record how often it succeeds. That success rate *is* a finding.
5. **The report + presentation.** MITRE ATT&CK / ATLAS mapping, screenshots, the 8-min
   demo video, and all written analysis are yours (per the course rules, the attack,
   configuration, execution, and analysis must be your own work and understanding).

### Optional refinements (nice-to-have, not required)
- Chunk long documents in `ingest.py`.
- Make `send` actually parse the `to` address instead of always hitting the listener.
- Add a second attack variant (e.g. a different payload phrasing) for comparison.

---

## 5. If the attack doesn't fire

Small local models sometimes ignore tool calls or don't follow the injected
instruction. Things to try:
- Make the payload more direct / imperative.
- Confirm the agent calls tools *legitimately* first (ask "look up customer records
  and send them to me") — if that works, the plumbing is fine and it's a payload/prompt
  tuning problem, which is the interesting part to write about.
- Switch `CHAT_MODEL` in `config.py` to `llama3.1:8b`.
