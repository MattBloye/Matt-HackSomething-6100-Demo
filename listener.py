"""Attacker inbox -- a stand-in for the attacker's mail server.

Run this in ITS OWN terminal before running the demo:

    python listener.py

Anything the agent's `send_email` tool transmits shows up here as a received
email. When you see one appear, that is the "exfiltration" -- sensitive records
reaching the attacker.
"""
import time
from email import message_from_bytes
from email.policy import default
from aiosmtpd.controller import Controller
from config import SMTP_HOST, SMTP_PORT


class InboxHandler:
    async def handle_DATA(self, server, session, envelope):
        msg = message_from_bytes(envelope.content, policy=default)
        print("\n[attacker inbox] !!! NEW EMAIL RECEIVED")
        print(f"  from:    {msg['From']}")
        print(f"  to:      {msg['To']}")
        print(f"  subject: {msg['Subject']}")
        print("  body:")
        print("  " + msg.get_content().strip().replace("\n", "\n  "))
        print("  ^ this represents STOLEN data reaching the attacker\n")
        return "250 Message accepted for delivery"


def main():
    controller = Controller(InboxHandler(), hostname=SMTP_HOST, port=SMTP_PORT)
    controller.start()
    print(f"[attacker inbox] listening for mail on {SMTP_HOST}:{SMTP_PORT} ...")
    print("[attacker inbox] (leave running; Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        print("\n[attacker inbox] stopped.")


if __name__ == "__main__":
    main()
