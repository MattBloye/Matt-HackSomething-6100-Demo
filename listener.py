"""Attacker listener -- a stand-in for the attacker's server.

Run this in ITS OWN terminal before running the attack:

    python listener.py

Anything the agent's `send` tool transmits shows up here. When you see data
appear, that is the "exfiltration" -- sensitive records reaching the attacker.
"""
import socket
from config import LISTENER_HOST, LISTENER_PORT


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((LISTENER_HOST, LISTENER_PORT))
        s.listen()
        print(f"[listener] waiting for data on {LISTENER_HOST}:{LISTENER_PORT} ...")
        print("[listener] (leave this running; press Ctrl+C to stop)\n")
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(65536)
                print(f"[listener] !!! received {len(data)} bytes from {addr[0]}:")
                print("-" * 50)
                print(data.decode(errors="replace"))
                print("-" * 50)
                print("[listener] ^ this represents STOLEN data reaching the attacker\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[listener] stopped.")
