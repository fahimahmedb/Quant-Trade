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
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0].parent
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
    chat_id = CHAT_ID_FILE.read_text().strip()
    api("sendMessage", chat_id=chat_id, text=text)


def fmt_duration(seconds):
    if seconds is None:
        return "—"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s:02d}s"


def build_status_message():
    running = bool(subprocess.run(["pgrep", "-f", "ml_tests_50_robust.py"],
                                   capture_output=True).stdout.strip())
    n_done = len(list((ROOT / "results").glob("strategy_*.json")))

    passed = failed = 0
    for f in (ROOT / "results").glob("strategy_*.json"):
        try:
            d = json.loads(f.read_text())
            if d.get("result") == "PASS":
                passed += 1
            elif d.get("result") == "FAIL":
                failed += 1
        except Exception:
            pass

    start_file = Path("/tmp/iter3_start_ts.txt")
    elapsed = None
    remaining = None
    if start_file.exists():
        try:
            start_ts = int(start_file.read_text().strip())
            elapsed = time.time() - start_ts
            if n_done > 0:
                remaining = (elapsed / n_done) * (50 - n_done)
        except ValueError:
            pass

    status_emoji = "🟢" if running else "🔴"
    lines = [
        f"{status_emoji} Iteration 3 — {'EN COURS' if running else 'ARRÊTÉE'}",
        f"Tests: {n_done}/50 ({passed} PASS, {failed} FAIL)",
        f"Écoulé: {fmt_duration(elapsed)} | Restant estimé: {fmt_duration(remaining)}",
        f"Généré: {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}",
    ]
    return "\n".join(lines)


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
                    send(build_status_message())
                except Exception as e:
                    print(f"[{datetime.now(timezone.utc)}] Send error: {e}", flush=True)

        STATE_FILE.write_text(str(last_id))


if __name__ == "__main__":
    main()
