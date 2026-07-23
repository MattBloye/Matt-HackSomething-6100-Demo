"""The two tools the agent can call, their schemas, and a name -> function registry.

Key idea to keep in mind: the MODEL only *decides* to call these tools. This file
is where the actions actually happen. It is the "hands" of the agent. That is also
why the defense lives at the point where these get executed (see agent.py / defense.py).
"""
import smtplib
from email.message import EmailMessage
from config import SMTP_HOST, SMTP_PORT

# --- Fake "sensitive" data, standing in for a real internal store --------------
# In a real system this would be customer PII, credentials, internal files, etc.
FAKE_RECORDS = {
    "customers": [
        {"name": "MITS Student1", "email": "Student1@MITS.com", "ssn": "123-45-6789"},
        {"name": "MITS Student2", "email": "Student2@MITS.com", "ssn": "987-65-4321"},
    ]
}


def lookup(query: str) -> str:
    """Return records from the internal 'database'. Read-only.

    Simplified: it ignores the query and returns everything. That's fine for the
    demo -- the point is that this tool exposes sensitive data.
    """
    return str(FAKE_RECORDS)


def send_email(to: str, data: str) -> str:
    """Send data to an external recipient by email. THIS is the dangerous capability.

    It sends a real email over SMTP. For the demo it always connects to the local
    attacker inbox (listener.py) regardless of `to`, so you can watch the "stolen"
    data arrive. The `to` value is still used as the message's To: header so you
    can see where the model *thought* it was sending.
    """
    msg = EmailMessage()
    msg["From"] = "assistant@company.local"
    msg["To"] = to
    msg["Subject"] = "Customer Records"
    msg.set_content(data)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.send_message(msg)
        return f"email sent to {to}"
    except ConnectionRefusedError:
        return "send_email failed: is listener.py (attacker inbox) running?"


# --- Registry: maps the tool name the model uses -> the real function ----------
REGISTRY = {"lookup": lookup, "send_email": send_email}

# --- Schemas: this is what we hand to the model so it knows the tools exist -----
# The model reads these descriptions to decide which tool to call and with what args.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "lookup",
            "description": "Look up customer records from the internal database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "what to search for"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send data to an external recipient address via email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "recipient address"},
                    "data": {"type": "string", "description": "the data to send"},
                },
                "required": ["to", "data"],
            },
        },
    },
]
