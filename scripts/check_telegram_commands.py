#!/usr/bin/env python3
"""
Poll Telegram for new incoming messages and react to known commands.

State (last processed update_id) is kept in a local file so re-running
this doesn't re-process old messages. Designed to be called repeatedly
(every 30min loop / hourly Routine) — cheap no-op when there's nothing new.

Usage:
  python3 scripts/check_telegram_commands.py
  -> prints "REFRESH_REQUESTED" on stdout if the user asked for a status
     refresh (so the caller can decide to regenerate + reply), else prints
     "NO_COMMAND".
"""
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path

SECRETS_DIR = Path("/tmp/claude-0/-home-user-Quant-Trade/d40e7f44-8dba-572d-ba27-6c7a61ed28ed/secrets")
TOKEN_FILE = SECRETS_DIR / "telegram_token.txt"
CHAT_ID_FILE = SECRETS_DIR / "telegram_chat_id.txt"
STATE_FILE = SECRETS_DIR / "telegram_last_update_id.txt"

REFRESH_KEYWORDS = {"actualise", "actualiser", "refresh", "status", "statut", "état", "etat"}


def api(method, **params):
    token = TOKEN_FILE.read_text().strip()
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    if not TOKEN_FILE.exists() or not CHAT_ID_FILE.exists():
        print("NO_COMMAND")
        return

    last_id = 0
    if STATE_FILE.exists():
        try:
            last_id = int(STATE_FILE.read_text().strip())
        except ValueError:
            pass

    result = api("getUpdates", offset=last_id + 1, timeout=5)
    if not result.get("ok"):
        print("NO_COMMAND")
        return

    updates = result.get("result", [])
    refresh_requested = False
    max_id = last_id

    for u in updates:
        max_id = max(max_id, u["update_id"])
        msg = u.get("message", {})
        text = (msg.get("text") or "").strip().lower()
        if any(kw in text for kw in REFRESH_KEYWORDS):
            refresh_requested = True

    if max_id > last_id:
        STATE_FILE.write_text(str(max_id))

    print("REFRESH_REQUESTED" if refresh_requested else "NO_COMMAND")


if __name__ == "__main__":
    main()
