#!/usr/bin/env python3
"""
Persistent Telegram listener — reacts to keyword messages INSTANTLY
(long-polling), instead of waiting for the next scheduled check.

Runs forever. For "Actualise"/"status"/etc: computes current batch status
itself (pgrep, results files, timing) and replies directly via sendMessage —
no LLM round-trip needed for a simple factual status report. This is the
"push a button, get an answer now" path the periodic 30min loop can't give.

Launch (detached, survives the launching shell exiting):
  setsid nohup python3 scripts/telegram_daemon.py < /dev/null \
      > /tmp/telegram_daemon.log 2>&1 & disown
"""
import json
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(ROOT / "scripts"))
from telegram_report import build_full_report

SECRETS_DIR = Path("/tmp/claude-0/-home-user-Quant-Trade/d40e7f44-8dba-572d-ba27-6c7a61ed28ed/secrets")
TOKEN_FILE = SECRETS_DIR / "telegram_token.txt"
CHAT_ID_FILE = SECRETS_DIR / "telegram_chat_id.txt"
STATE_FILE = SECRETS_DIR / "telegram_daemon_last_update_id.txt"

REFRESH_KEYWORDS = {"actualise", "actualiser", "refresh", "status", "statut", "état", "etat"}


def api(method, timeout=35, **params):
    token = TOKEN_FILE.read_text().strip()
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=timeout) as resp:
        return json.loads(resp.read())


def send(text):
    # Les noms de strategies/modeles contiennent des underscores non apparies
    # (ex. "QuantNormal_Log_H_C1") qui cassent le parse_mode Markdown de
    # Telegram (italique non ferme -> HTTP 400 "can't parse entities").
    # On retente en texte brut plutot que de perdre la notification.
    chat_id = CHAT_ID_FILE.read_text().strip()
    try:
        api("sendMessage", chat_id=chat_id, text=text, parse_mode="Markdown")
    except urllib.error.HTTPError:
        api("sendMessage", chat_id=chat_id, text=text)


def main():
    last_id = 0
    if STATE_FILE.exists():
        try:
            last_id = int(STATE_FILE.read_text().strip())
        except ValueError:
            pass

    print(f"[{datetime.now(timezone.utc)}] Telegram daemon started, long-polling...", flush=True)

    while True:
        try:
            result = api("getUpdates", offset=last_id + 1, timeout=30)
        except Exception as e:
            print(f"[{datetime.now(timezone.utc)}] Poll error: {e}", flush=True)
            time.sleep(5)
            continue

        if not result.get("ok"):
            time.sleep(5)
            continue

        for u in result.get("result", []):
            last_id = max(last_id, u["update_id"])
            msg = u.get("message", {})
            text = (msg.get("text") or "").strip().lower()
            if any(kw in text for kw in REFRESH_KEYWORDS):
                print(f"[{datetime.now(timezone.utc)}] Refresh requested: {text!r}", flush=True)
                try:
                    for chunk in build_full_report():
                        send(chunk)
                except Exception as e:
                    print(f"[{datetime.now(timezone.utc)}] Send error: {e}", flush=True)

        STATE_FILE.write_text(str(last_id))


if __name__ == "__main__":
    main()
