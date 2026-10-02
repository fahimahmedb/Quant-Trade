# SESSION PROMPT TEMPLATE (coordinator) — 2026-10-02

Draft skeleton only. The task organisation is being prepared by the owner (with another assistant); fill the WP card from that organisation. No build is started from this file.

## A. Mandatory preamble for every session prompt
```
You are session <WP-ID> of the Weather V3 programme. Role: <Architect on Sonnet | Astra independent | Analyst | Builder (only if BUILDER_AUTHORIZED)>.
Authority: REAL_CAPITAL_AUTHORIZED=FALSE, LIVE_TRADING_AUTHORIZED=FALSE, t0=NOT_DECLARED, BUILDER_AUTHORIZED=<as set by owner>. No real Weather outcomes/prices/P&L.
Read first (paths, not pasted): <digest path>, <WP card path>, <progress file path>. Slice the spec with grep/sed; do not read it whole.
Branch: <given by Blue/owner; never create or switch branches on your own>.
RESUME RULE: if <progress file> exists, continue from it; never restart finished cells (JSONL resumable, seeds = f(plan, cell, stream)).
CHECKPOINT RULE: update the progress file and push a WIP commit after every major step.
DONE RULE: when finished write <WP-ID>.DONE (verdict + SHA) next to the progress file, push, disable this session's heartbeat, hand back in <=12 lines.
```

## B. Auto-relaunch alerts (no owner message needed)
Problem: a session that hits the API usage limit cannot wake itself. Solution = alerts created by the COORDINATOR (not by the child) when it creates the session:
1. Per-session heartbeat: `create_trigger` with `persistent_session_id=<child session>`, cron hourly (`0 * * * *` is anchored to creation minute), `initiation=own_followup`, prompt = "HEARTBEAT: read <progress file>; if <WP-ID>.DONE exists, reply DONE; else continue the work from the progress file exactly where it stopped; do not restart finished work; push WIP." The message is queued while the limit holds and resumes the session as soon as it resets.
2. Coordinator watchdog (this session): hourly routine that lists child sessions (`list_sessions`), checks each progress file / branch head / .DONE marker, and (a) disables the heartbeat of a DONE session (`update_trigger enabled=false`), (b) re-fires (`fire_trigger`) a heartbeat whose session is idle with unfinished work, (c) reports to the owner only on a DONE verdict or a blocker needing a decision.
3. One-shot back-stop: when a hand-back says "limit resets at HH:MM", schedule `send_later` at that time into the same session.
4. Idempotence: heartbeats never spawn a second session for the same WP; duplicates are detected by the .DONE marker and progress file.
5. Cleanup: when the whole programme is DONE, disable all heartbeats and the watchdog.

## C. WP card fields (to be filled from the organisation)
ID | goal | inputs (paths+sections) | outputs (paths) | role+model | depends | CPU class / slice i/n | token class | acceptance | owner decision needed | stop conditions
