#!/usr/bin/env python3
"""
One-shot Telegram poll — replaces the persistent long-polling daemon.

Rationale: any process detached from the tool call that launched it
(setsid/nohup/disown) gets reaped by this environment on some recurring
cycle (~10-20 min observed), regardless of tricks to survive its parent
shell exiting. A long-lived daemon is exactly the kind of process that
gets killed. Foreground, bounded tool calls do NOT get killed this way.

So: call this once per wake-up (routine firing or loop iteration) instead
of keeping a daemon alive. Uses timeout=0 (short poll — returns whatever
is already queued, does not block waiting for new messages), so it's
safe to call synchronously and cheaply on every wake-up.

Trade-off: replies to "actualise" arrive on the next wake-up cadence
instead of instantly. Given the daemon never survived long enough to be
reliably instant anyway, this is a net reliability win.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(ROOT / "scripts"))
from telegram_daemon import api, send, REFRESH_KEYWORDS, STATE_FILE
from telegram_report import build_full_report


def poll_once():
    last_id = 0
    if STATE_FILE.exists():
        try:
            last_id = int(STATE_FILE.read_text().strip())
        except ValueError:
            pass

    # NB: api()'s `timeout` kwarg is the local socket timeout, not a
    # Telegram-side long-poll duration (it's never forwarded as a query
    # param) — getUpdates already short-polls by default, so no override
    # needed here.
    result = api("getUpdates", offset=last_id + 1)
    if not result.get("ok"):
        print(f"getUpdates not ok: {result}")
        return

    handled = 0
    for u in result.get("result", []):
        last_id = max(last_id, u["update_id"])
        msg = u.get("message", {})
        text = (msg.get("text") or "").strip().lower()
        if any(kw in text for kw in REFRESH_KEYWORDS):
            print(f"Refresh requested: {text!r}")
            for chunk in build_full_report():
                send(chunk)
            handled += 1

    STATE_FILE.write_text(str(last_id))
    print(f"Polled. {handled} refresh request(s) handled. last_id={last_id}")


if __name__ == "__main__":
    poll_once()
