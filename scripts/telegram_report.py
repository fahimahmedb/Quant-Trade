#!/usr/bin/env python3
"""
Build a full Telegram-formatted status report: complete list of strategies
(done / pending / running) for the CURRENT iteration + a top-10 ranking
table. Iteration-aware since iteration 4 (each iteration lives in its own
results/iterN/ folder — see scripts/ml_brute_force.py for why).

Shared by telegram_poll_once.py (instant "Actualise" reply) and the hourly
Routine notifications. Telegram messages cap at 4096 chars, so
build_full_report() returns multiple chunks.
"""
import sys
import json
import subprocess
import time
import glob
import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0].parent
sys.path.insert(0, str(ROOT / "scripts"))


def current_iteration():
    """Highest N such that scripts/iterations/iterN.py exists."""
    candidates = []
    for f in glob.glob(str(ROOT / "scripts" / "iterations" / "iter*.py")):
        stem = Path(f).stem  # "iter4"
        try:
            candidates.append(int(stem.replace("iter", "")))
        except ValueError:
            continue
    return max(candidates) if candidates else None


def load_strategies(n):
    mod = importlib.import_module(f"iterations.iter{n}")
    return mod.STRATEGIES


def load_results(n, strategies):
    """id -> result dict (or None if not yet run), for iteration n."""
    iter_dir = ROOT / "results" / f"iter{n}"
    out = {}
    for i in sorted(strategies.keys()):
        f = iter_dir / f"strategy_{i:03d}.json"
        if f.exists():
            try:
                out[i] = json.loads(f.read_text())
            except Exception:
                out[i] = None
        else:
            out[i] = None
    return out


def is_running():
    return bool(subprocess.run(["pgrep", "-f", "ml_brute_force.py"],
                                capture_output=True).stdout.strip())


def fmt_duration(seconds):
    if seconds is None:
        return "—"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s:02d}s"


def status_icon(r):
    if r is None:
        return "⏳"  # not yet run
    res = r.get("result")
    if res == "PASS":
        return "🎯"
    if res == "FAIL":
        return "❌"
    if res == "ERROR":
        return "💥"
    if res == "PENDING_DSR":
        return "✅"  # Pass-1 done, DSR pending
    return "❓"


def build_header():
    n = current_iteration()
    if n is None:
        return "⚠️ Aucune itération déclarée (scripts/iterations/ vide)"

    strategies = load_strategies(n)
    total = len(strategies)
    results = load_results(n, strategies)
    n_done = sum(1 for r in results.values() if r is not None)
    running = is_running()

    start_file = Path(f"/tmp/iter{n}_start_ts.txt")
    elapsed = remaining = None
    if start_file.exists():
        try:
            start_ts = int(start_file.read_text().strip())
            elapsed = time.time() - start_ts
            if n_done > 0:
                remaining = (elapsed / n_done) * (total - n_done)
        except ValueError:
            pass

    dot = "🟢" if running else "🔴"
    return (
        f"{dot} Itération {n} — {'EN COURS' if running else 'ARRÊTÉE'}\n"
        f"{n_done}/{total} fait(s) | Écoulé {fmt_duration(elapsed)} | Restant ~{fmt_duration(remaining)}"
    )


def build_full_list():
    """Full list of all strategies for the current iteration, with status icon."""
    n = current_iteration()
    if n is None:
        return "📋 Aucune itération déclarée"

    strategies = load_strategies(n)
    results = load_results(n, strategies)
    lines = [f"📋 LISTE COMPLÈTE — Itération {n} ({len(strategies)} stratégies)"]
    row = []
    for i in sorted(strategies.keys()):
        r = results[i]
        icon = status_icon(r)
        row.append(f"{icon}{i}")
        if len(row) == 5:
            lines.append("  ".join(row))
            row = []
    if row:
        lines.append("  ".join(row))
    lines.append("⏳ pas encore lancé · ✅ fait (DSR en attente) · 🎯 PASS · ❌ FAIL · 💥 ERROR")
    return "\n".join(lines)


def build_top10():
    """Top 10 by design Sharpe annualized, among strategies with a result,
    for the current iteration."""
    n = current_iteration()
    if n is None:
        return "🏆 TOP 10 — aucune itération déclarée"

    strategies = load_strategies(n)
    results = load_results(n, strategies)
    scored = []
    for i, r in results.items():
        if r and r.get("design_sharpe") is not None:
            ds_ann = r["design_sharpe"] * (252 ** 0.5)
            ts = r.get("test_sharpe")
            ts_ann = ts * (252 ** 0.5) if ts is not None else None
            dsr = r.get("dsr")
            name = r.get("model", strategies.get(i, (f"id{i}",))[0])
            scored.append((ds_ann, i, name, ts_ann, dsr, r.get("result")))

    scored.sort(reverse=True, key=lambda x: x[0])
    top = scored[:10]

    if not top:
        return f"🏆 TOP 10 (Itération {n}) — aucun résultat disponible pour l'instant"

    lines = [f"🏆 TOP 10 — Itération {n} (par Design Sharpe annualisé)", "```"]
    lines.append(f"{'#':>2} {'Modèle':<22} {'Design':>7} {'Test':>7} {'DSR':>6} {'Statut':<6}")
    for rank, (ds_ann, i, name, ts_ann, dsr, res) in enumerate(top, 1):
        ts_str = f"{ts_ann:.3f}" if ts_ann is not None else "—"
        dsr_str = f"{dsr:.3f}" if dsr is not None else "—"
        lines.append(f"{rank:>2} {name[:22]:<22} {ds_ann:>7.3f} {ts_str:>7} {dsr_str:>6} {res or '?':<6}")
    lines.append("```")
    return "\n".join(lines)


def build_full_report():
    """Returns a list of message chunks (Telegram caps at 4096 chars/message)."""
    return [
        build_header(),
        build_full_list(),
        build_top10(),
    ]


if __name__ == "__main__":
    for chunk in build_full_report():
        print(chunk)
        print("-" * 40)
