# Indirect Prompt Injection Lab (MITS 6100G – Hack Something)

A self-contained lab that demonstrates a local, tool-enabled RAG agent in two
states: **vulnerable** to indirect prompt injection, and **secure** against it.

- **Vulnerable state (OWASP LLM01/LLM06):** a hidden instruction is planted in an
  ordinary-looking document. When a *benign* user question retrieves that
  document, the model obeys the hidden instruction and calls `send_email` to
  exfiltrate sensitive records to an attacker-controlled inbox — zero-click, no
  malicious user prompt.
- **Secure state:** two independent layers gate `send_email`: (1) an
  **authorization gate** — was a send actually requested by the user? — and
  (2) an **egress allow-list** — is the recipient an approved internal
  address? Either layer failing blocks the call, so exfiltration is stopped
  even if a send genuinely was requested (e.g. a poisoned "send this to my
  boss"). Re-ask the same question after switching to secure and watch it
  get blocked.

Real-world anchor: **EchoLeak / CVE-2025-32711** (Microsoft 365 Copilot).

Everything runs locally on one machine with no external network. The attacker's
mail server is a local SMTP inbox (`listener.py`); the "sensitive data" is fake.

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

**Terminal A — start the attacker inbox (leave it running):**
```
python listener.py
```

**Terminal B — load documents, submit an intake form, then run the demo:**
```
python ingest.py
python submit_intake_form.py
python demo.py
```
`submit_intake_form.py` is interactive -- it prompts you for the intake fields,
including the "Reason for Visit / Symptom Description" free-text field. That field is
the delivery vector: type or paste an injected instruction there to simulate an
attacker submitting the intake form through the patient portal.
`demo.py` starts in **VULNERABLE** mode. Type a question, e.g. `What is our
refund policy?`, and watch Terminal A — if patient records arrive as an email,
the injection worked.

Switch modes live at the prompt:
```
/secure       switch to SECURE mode (authorization gate + egress allow-list ON)
/vulnerable   switch back to VULNERABLE mode (both defenses OFF)
/help         list commands
/quit         exit
```
Ask the same question again after `/secure` — the `send_email` call is now
blocked, and nothing reaches the attacker inbox.

> Note: Qdrant runs in local on-disk mode, which allows only one process to open the
> DB at a time. Run the scripts one after another (not simultaneously). That's why
> ingest and the demo are separate steps.

## 3. Architecture

```
documents/ --embed--> ingest.py -----------> Qdrant
                                                 |
submit_intake_form.py (interactive) --embed-----+
                                                 |
user question --retrieve.py--> context ---------+
                                                 |
                                    agent.py (tool-calling loop)
                                    |                |
                              defense.py        tools.py
                              (authorization    (lookup, send_email)
                               gate, egress           |
                               allow-list,             v
                               logging)         listener.py (outbound mail monitor)
```

| File | Purpose |
|------|---------|
| `config.py` | All settings: model names, paths, attacker inbox address |
| `listener.py` | Outbound mail monitor — shows legitimate sends (green) and attacker exfiltration (red) |
| `ingest.py` | Embeds the documents and loads them into Qdrant |
| `submit_intake_form.py` | Interactive patient-portal simulation — prompts for intake fields and upserts the submission into Qdrant. The free-text "Reason for Visit" field is the injection delivery vector |
| `retrieve.py` | Fetches the top matching documents for a query |
| `tools.py` | The two tools (`lookup`, `send_email`) + their schemas |
| `agent.py` | The tool-calling loop (the "agent") + defense checkpoint |
| `defense.py` | Authorization gate, egress allow-list, spotlighting, tool-call logging |
| `demo.py` | Interactive demo — ask questions, toggle vulnerable/secure live |
| `documents/` | Ten benign clinic KB docs |

## 4. Troubleshooting

Small local models sometimes ignore tool calls or don't follow the injected
instruction. If the injection doesn't fire in VULNERABLE mode:
- Confirm the agent calls tools *legitimately* first (ask "look up patient records
  and email them to me") — if that works, the plumbing is fine and it's a
  payload/prompt tuning issue rather than a code issue.
- Switch `CHAT_MODEL` in `config.py` to `llama3.1:8b`.
