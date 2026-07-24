"""Interactive CLI for the demo: type questions, the agent answers them, and
/secure and /vulnerable toggle the authorization gate live so you can re-ask
the same question and compare behavior side by side.

Run listener.py and ingest.py first (see README.md), then:
    python demo.py

Starts VULNERABLE (gate off) -- the realistic default a rushed team would
ship without thinking about it.
"""
import colorama
from colorama import Fore, Style
from agent import run_agent


def main():
    colorama.init(autoreset=True)
    secure = False
    print("RAG agent demo. It answers questions, and can look up records and")
    print("send emails on your behalf. Start VULNERABLE (no authorization gate).")
    print("Commands: /secure  /vulnerable  /help  /quit\n")
    while True:
        if secure:
            mode_tag = f"{Fore.GREEN}[SECURE]{Style.RESET_ALL}"
        else:
            mode_tag = f"{Fore.RED}[VULNERABLE]{Style.RESET_ALL}"
        try:
            line = input(f"{mode_tag} You: ").strip()
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
        print(f"\n{Fore.CYAN}[assistant]{Style.RESET_ALL} {answer}\n")


if __name__ == "__main__":
    main()
