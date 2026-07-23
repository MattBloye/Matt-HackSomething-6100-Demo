"""DEMO 2 -- the same attack with the defense ON.

Run listener.py and ingest.py first (same as the attack), then:
  python run_defended.py

Same poisoned document, same harmless question -- but the authorization gate blocks
the unauthorized 'send_email', so nothing reaches the listener. Compare the console output
to run_attack.py: you should see the tool call marked BLOCKED.
"""
from agent import run_agent

USER_QUESTION = "What is our refund policy?"

if __name__ == "__main__":
    print("=== DEFENDED RUN (defense ON) ===")
    answer = run_agent(USER_QUESTION, defense_on=True)
    print(f"\n[agent -> user] {answer}")
    print("\nCheck the listener: it should have received NOTHING this time.")
