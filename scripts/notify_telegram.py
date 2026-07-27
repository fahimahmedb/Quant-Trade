#!/usr/bin/env python3
"""
Send a Telegram notification. Credentials read from local secret files
(NEVER committed to git — stored in the scratchpad secrets/ dir outside
the repo).

Usage:
  python3 scripts/notify_telegram.py "message text"
"""
import sys
import urllib.request
import urllib.parse
from pathlib import Path

SECRETS_DIR = Path("/tmp/claude-0/-home-user-Quant-Trade/d40e7f44-8dba-572d-ba27-6c7a61ed28ed/secrets")
TOKEN_FILE = SECRETS_DIR / "telegram_token.txt"
CHAT_ID_FILE = SECRETS_DIR / "telegram_chat_id.txt"


def send(message: str) -> bool:
    if not TOKEN_FILE.exists() or not CHAT_ID_FILE.exists():
        print("Telegram not configured (missing token/chat_id files)", file=sys.stderr)
        return False

    token = TOKEN_FILE.read_text().strip()
    chat_id = CHAT_ID_FILE.read_text().strip()

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()

    try:
        with urllib.request.urlopen(url, data=data, timeout=10) as resp:
            ok = resp.status == 200
            if not ok:
                print(f"Telegram send failed: HTTP {resp.status}", file=sys.stderr)
            return ok
    except Exception as e:
        print(f"Telegram send error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: notify_telegram.py <message>", file=sys.stderr)
        sys.exit(1)
    ok = send(sys.argv[1])
    sys.exit(0 if ok else 1)
