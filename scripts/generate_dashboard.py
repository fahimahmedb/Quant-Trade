#!/usr/bin/env python3
"""
Generate a static HTML monitoring dashboard from current ML testing state.

Reads:
- /tmp/iter3.pid, /tmp/iter3_start_ts.txt (current run process/timing)
- results/strategy_*.json (current iteration per-strategy results)
- results/ml_tests_results.json (Iteration 2 results)
- results/iteration_1_summary.json (Iteration 1 results)
- git log (commit history as event timeline)

Writes a self-contained HTML file (no external deps, no live fetch —
regenerate + republish via the Artifact tool whenever state changes).
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0].parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/quant_dashboard.html")


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def process_status():
    # pgrep by command name, not a remembered PID: setsid/nohup chains can
    # exec-replace into a different PID than the one $! captured, making a
    # stored PID file unreliable (looked "dead" while actually still running).
    start_file = Path("/tmp/iter3_start_ts.txt")
    try:
        out = subprocess.run(["pgrep", "-f", "ml_tests_50_robust.py"],
                              capture_output=True, text=True).stdout.strip()
        pids = [p for p in out.splitlines() if p]
        running = len(pids) > 0
    except Exception:
        running = False
        pids = []
    start_ts = None
    if start_file.exists():
        try:
            start_ts = int(start_file.read_text().strip())
        except ValueError:
            pass
    elapsed = (datetime.now(timezone.utc).timestamp() - start_ts) if start_ts else None
    return {"running": running, "pid": ",".join(pids) if pids else None, "start_ts": start_ts, "elapsed_s": elapsed}


def iteration3_results():
    files = sorted(ROOT.glob("results/strategy_*.json"))
    tests = []
    for f in files:
        d = read_json(f)
        if d:
            tests.append(d)
    passed = sum(1 for t in tests if t.get("result") == "PASS")
    failed = sum(1 for t in tests if t.get("result") == "FAIL")
    errored = sum(1 for t in tests if t.get("result") == "ERROR")
    pending = sum(1 for t in tests if t.get("result") == "PENDING_DSR")
    return {"tests": tests, "total_done": len(tests), "passed": passed, "failed": failed,
            "errored": errored, "pending": pending}


def iteration2_results():
    d = read_json(ROOT / "results" / "ml_tests_results.json")
    if not d:
        return None
    tests = list(d.values())
    passed = sum(1 for t in tests if t.get("pass"))
    return {"total": len(tests), "passed": passed,
             "best_test_sharpe": max((t.get("test_sharpe", 0) or 0) for t in tests),
             "best_dsr": max((t.get("dsr", 0) or 0) for t in tests)}


def iteration1_results():
    d = read_json(ROOT / "results" / "iteration_1_summary.json")
    if not d:
        return None
    return d


def git_events(n=12):
    try:
        out = subprocess.run(
            ["git", "log", f"-{n}", "--format=%h|%ad|%s", "--date=format:%Y-%m-%d %H:%M UTC"],
            cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        return []
    events = []
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            events.append({"hash": parts[0], "date": parts[1], "msg": parts[2]})
    return events


def fmt_duration(seconds):
    if seconds is None:
        return "—"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def main():
    proc = process_status()
    it3 = iteration3_results()
    it2 = iteration2_results()
    it1 = iteration1_results()
    events = git_events()

    avg_time_per_test = None
    if it3["total_done"] > 0 and proc.get("elapsed_s"):
        avg_time_per_test = proc["elapsed_s"] / it3["total_done"]

    est_remaining = None
    if avg_time_per_test:
        est_remaining = avg_time_per_test * (50 - it3["total_done"])

    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "proc": proc,
        "it1": it1,
        "it2": it2,
        "it3": it3,
        "avg_time_per_test": avg_time_per_test,
        "est_remaining_s": est_remaining,
        "events": events,
    }

    html = build_html(data)
    OUT.write_text(html)
    print(f"Dashboard written to {OUT}")


def build_html(d):
    proc = d["proc"]
    it1, it2, it3 = d["it1"], d["it2"], d["it3"]

    status_label = "RUNNING" if proc.get("running") else "IDLE"
    status_class = "running" if proc.get("running") else "idle"
    elapsed_str = fmt_duration(proc.get("elapsed_s"))
    remaining_str = fmt_duration(d["est_remaining_s"])
    pct = min(100, round((it3["total_done"] / 50) * 100)) if it3["total_done"] else 0
    avg_test_str = f"{d['avg_time_per_test']:.0f}s" if d["avg_time_per_test"] else "—"

    def test_rows(tests):
        rows = []
        for t in tests:
            res = t.get("result", "?")
            cls = {"PASS": "good", "FAIL": "bad", "ERROR": "warn"}.get(res, "")
            ds = t.get("design_sharpe")
            ts = t.get("test_sharpe")
            dsr = t.get("dsr")
            ds_ann = f"{ds*252**0.5:.3f}" if ds is not None else "—"
            ts_ann = f"{ts*252**0.5:.3f}" if ts is not None else "—"
            dsr_str = f"{dsr:.3f}" if dsr is not None else "—"
            rows.append(f"""<tr>
                <td class="mono">{t.get('id')}</td>
                <td>{t.get('model','?')}</td>
                <td class="mono num">{ds_ann}</td>
                <td class="mono num">{ts_ann}</td>
                <td class="mono num">{dsr_str}</td>
                <td><span class="pill {cls}">{res}</span></td>
            </tr>""")
        return "\n".join(rows) if rows else '<tr><td colspan="6" class="empty">En attente des premiers résultats…</td></tr>'

    events_html = "\n".join(
        f'<div class="event"><span class="mono muted">{e["date"]}</span>'
        f'<span class="mono hash">{e["hash"]}</span><span>{e["msg"]}</span></div>'
        for e in d["events"]
    ) or '<div class="empty">Aucun événement récent</div>'

    it1_html = ""
    if it1:
        it1_html = f"""<div class="stat"><span class="stat-label">PASS</span><span class="stat-value mono">{it1.get('passed',0)}/{it1.get('total','?')}</span></div>"""

    it2_html = ""
    if it2:
        it2_html = f"""
        <div class="stat"><span class="stat-label">PASS</span><span class="stat-value mono">{it2['passed']}/{it2['total']}</span></div>
        <div class="stat"><span class="stat-label">Meilleur Test Sharpe</span><span class="stat-value mono">{it2['best_test_sharpe']:.4f}</span></div>
        <div class="stat"><span class="stat-label">Meilleur DSR</span><span class="stat-value mono">{it2['best_dsr']:.4f}</span></div>
        """

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Quant-Trade — ML Batch Monitor</title>
<style>
:root {{
  --bg: #0b0e14;
  --surface: #131822;
  --surface-2: #1a2130;
  --border: #232a38;
  --text: #e6e9ef;
  --muted: #8891a3;
  --accent: #6c8eef;
  --good: #34c77b;
  --bad: #f0555a;
  --warn: #e6b04a;
}}
:root[data-theme="light"] {{
  --bg: #f4f6fa;
  --surface: #ffffff;
  --surface-2: #eef1f7;
  --border: #dde2ec;
  --text: #171b26;
  --muted: #5b6478;
  --accent: #3a5fd9;
  --good: #1f9d5c;
  --bad: #d5393f;
  --warn: #b8790f;
}}
@media (prefers-color-scheme: light) {{
  :root:not([data-theme="dark"]) {{
    --bg: #f4f6fa;
    --surface: #ffffff;
    --surface-2: #eef1f7;
    --border: #dde2ec;
    --text: #171b26;
    --muted: #5b6478;
    --accent: #3a5fd9;
    --good: #1f9d5c;
    --bad: #d5393f;
    --warn: #b8790f;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif;
  line-height: 1.5;
}}
.mono {{ font-family: ui-monospace, "SF Mono", "Cascadia Code", "JetBrains Mono", Consolas, monospace; }}
.num {{ font-variant-numeric: tabular-nums; }}
.wrap {{ max-width: 980px; margin: 0 auto; padding: 32px 20px 80px; }}
header {{ display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 28px; }}
h1 {{ font-size: 1.4rem; font-weight: 700; letter-spacing: -0.01em; text-wrap: balance; margin: 0; }}
.subtitle {{ color: var(--muted); font-size: 0.85rem; }}
.updated {{ color: var(--muted); font-size: 0.78rem; }}

.status-bar {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}}
.status-dot {{
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--muted);
  flex-shrink: 0;
}}
.status-dot.running {{ background: var(--warn); box-shadow: 0 0 0 4px color-mix(in srgb, var(--warn) 20%, transparent); animation: pulse 2s ease-in-out infinite; }}
.status-dot.idle {{ background: var(--muted); }}
@media (prefers-reduced-motion: no-preference) {{
  @keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
}}
.status-label {{ font-weight: 600; font-size: 0.95rem; display: flex; align-items: center; gap: 10px; }}
.progress-track {{
  flex: 1; min-width: 180px; height: 8px; border-radius: 999px;
  background: var(--surface-2); overflow: hidden; border: 1px solid var(--border);
}}
.progress-fill {{ height: 100%; background: var(--accent); border-radius: 999px; transition: width 0.3s; }}
.status-meta {{ display: flex; gap: 20px; font-size: 0.8rem; color: var(--muted); flex-wrap: wrap; }}
.status-meta b {{ color: var(--text); font-weight: 600; }}

.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 24px; }}
.card {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 18px 20px;
}}
.card h2 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin: 0 0 14px; font-weight: 600; }}
.stat {{ display: flex; justify-content: space-between; align-items: baseline; padding: 6px 0; border-bottom: 1px solid var(--border); }}
.stat:last-child {{ border-bottom: none; }}
.stat-label {{ font-size: 0.82rem; color: var(--muted); }}
.stat-value {{ font-size: 0.95rem; font-weight: 600; }}

section.panel {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; margin-bottom: 20px; }}
section.panel h2 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin: 0 0 14px; font-weight: 600; }}

.table-scroll {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
th {{ text-align: left; color: var(--muted); font-weight: 600; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 8px 10px; border-bottom: 1px solid var(--border); }}
td {{ padding: 8px 10px; border-bottom: 1px solid var(--border); }}
tr:last-child td {{ border-bottom: none; }}
.empty {{ color: var(--muted); text-align: center; padding: 20px; }}

.pill {{ display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.72rem; font-weight: 600; background: var(--surface-2); color: var(--muted); }}
.pill.good {{ background: color-mix(in srgb, var(--good) 18%, transparent); color: var(--good); }}
.pill.bad {{ background: color-mix(in srgb, var(--bad) 18%, transparent); color: var(--bad); }}
.pill.warn {{ background: color-mix(in srgb, var(--warn) 18%, transparent); color: var(--warn); }}

.event {{ display: grid; grid-template-columns: 140px 70px 1fr; gap: 12px; padding: 7px 0; font-size: 0.82rem; border-bottom: 1px solid var(--border); align-items: baseline; }}
.event:last-child {{ border-bottom: none; }}
.hash {{ color: var(--accent); }}
.muted {{ color: var(--muted); }}

footer {{ color: var(--muted); font-size: 0.75rem; text-align: center; margin-top: 32px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>Quant-Trade — Suivi des batches ML</h1>
      <div class="subtitle">Protocole anti-data-snooping · walk-forward + DSR Bonferroni</div>
    </div>
    <div class="updated">Généré {d['generated_at']}</div>
  </header>

  <div class="status-bar">
    <div class="status-label">
      <span class="status-dot {status_class}"></span>
      Iteration 3 — {status_label}
    </div>
    <div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>
    <div class="status-meta">
      <span>{it3['total_done']}/50 tests <b class="num">{pct}%</b></span>
      <span>Écoulé <b class="num">{elapsed_str}</b></span>
      <span>Restant estimé <b class="num">{remaining_str}</b></span>
      <span>Temps/test <b class="num">{avg_test_str}</b></span>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>Iteration 1 — 50 tests</h2>
      {it1_html or '<div class="empty">Crash (bug de shape), aucune donnée exploitable</div>'}
    </div>
    <div class="card">
      <h2>Iteration 2 — 10 tests</h2>
      {it2_html or '<div class="empty">Pas encore lancée</div>'}
    </div>
    <div class="card">
      <h2>Iteration 3 — 50 tests (en cours)</h2>
      <div class="stat"><span class="stat-label">En attente du DSR final</span><span class="stat-value mono">{it3['pending']}/50</span></div>
      <div class="stat"><span class="stat-label">PASS (final)</span><span class="stat-value mono">{it3['passed']}/50</span></div>
      <div class="stat"><span class="stat-label">FAIL (final)</span><span class="stat-value mono">{it3['failed']}/50</span></div>
      <div class="stat"><span class="stat-label">ERROR</span><span class="stat-value mono">{it3['errored']}/50</span></div>
    </div>
  </div>

  <section class="panel">
    <h2>Iteration 3 — détail par stratégie</h2>
    <div class="table-scroll">
      <table>
        <thead><tr><th>#</th><th>Modèle</th><th>Design (ann.)</th><th>Test (ann.)</th><th>DSR</th><th>Résultat</th></tr></thead>
        <tbody>{test_rows(it3['tests'])}</tbody>
      </table>
    </div>
  </section>

  <section class="panel">
    <h2>Journal (derniers commits)</h2>
    {events_html}
  </section>

  <footer>
    Dashboard statique régénéré à chaque étape clé — pas de flux temps réel (contrainte CSP).<br>
    Seuil de passage : Design &amp; Test Sharpe annualisés &gt; 0.55, DSR &gt; 0.95, dégradation &lt; 0.5.
  </footer>
</div>
</body>
</html>"""


if __name__ == "__main__":
    main()
