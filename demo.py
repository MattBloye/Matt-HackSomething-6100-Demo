"""Interactive demo: ask the agent questions and toggle the security posture live.

Run listener.py and ingest.py first (see README.md), then:
    python demo.py

Starts VULNERABLE (no authorization gate) -- the realistic default a rushed
developer would ship. Use /secure and /vulnerable to switch modes and re-ask
the same question to compare behavior.
"""
from agent import run_agent


def main():
    secure = False  # start vulnerable -- the default a rushed dev would ship
    print("RAG agent demo. It answers questions, and can look up records and")
    print("send emails on your behalf. Start VULNERABLE (no authorization gate).")
    print("Commands: /secure  /vulnerable  /help  /quit\n")
    while True:
        mode = "SECURE" if secure else "VULNERABLE"
        try:
            line = input(f"[{mode}] You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line == "/quit":
            break
        if line == "/secure":
            secure = True
            print("-> SECURE mode: authorization gate is ON\n")
            continue
        if line == "/vulnerable":
            secure = False
            print("-> VULNERABLE mode: authorization gate is OFF\n")
            continue
        if line == "/help":
            print("Commands: /secure  /vulnerable  /help  /quit\n")
            continue
        answer = run_agent(line, defense_on=secure)
        print(f"\n[assistant] {answer}\n")


if __name__ == "__main__":
    main()
