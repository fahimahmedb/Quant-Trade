#!/usr/bin/env python3
"""
Build a full Telegram-formatted status report: complete list of all 50
strategies (done / pending / running) + a top-10 ranking table.

Shared by telegram_daemon.py (instant "Actualise" reply) and the
hourly/30min loop notifications. Telegram messages cap at 4096 chars,
so long_report() may return multiple chunks.
"""
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0].parent

# Strategy names in id order, extracted once from ml_tests_50_robust.py so
# this stays in sync without importing sklearn/pandas (daemon should be light).
STRATEGY_NAMES = {
    1: "RandomForest_d3_n100", 2: "RandomForest_d5_n100", 3: "RandomForest_d7_n100",
    4: "XGB_eta01_d3", 5: "XGB_eta05_d3", 6: "XGB_eta1_d3",
    7: "LGB_leaves15", 8: "LGB_leaves31", 9: "LGB_leaves63",
    10: "NN_deep_5", 11: "LogReg_C05", 12: "LogReg_C1", 13: "LogReg_C10",
    14: "GB_interact", 15: "SVM_rbf_C1", 16: "GB_d2_it80", 17: "GB_d4_it120",
    18: "RF_d6_n150", 19: "LogReg_C02", 20: "XGB_eta008_d2", 21: "GB_mean_rev",
    22: "RF_d4_n80", 23: "LogReg_C20", 24: "SVM_poly_C05", 25: "GB_deep_d6",
    26: "RF_d5_n120", 27: "XGB_eta02_d4", 28: "LogReg_C50", 29: "GB_interaction_v2",
    30: "SVM_rbf_C05", 31: "RF_d3_n200", 32: "GB_min_samp_30", 33: "LogReg_L1",
    34: "XGB_eta005_d5", 35: "RF_d8_n100", 36: "GB_mean_rev_v2", 37: "SVM_rbf_C10",
    38: "LogReg_C100", 39: "GB_d3_it200", 40: "RF_d4_n250", 41: "XGB_eta015_d3",
    42: "GB_robust_shrinkage", 43: "SVM_poly_C1", 44: "LogReg_C05_elasticnet",
    45: "GB_d2_it150", 46: "RF_d5_n180", 47: "XGB_balance", 48: "LogReg_regularized",
    49: "SVM_linear", 50: "GB_final",
}


def load_results():
    """id -> result dict (or None if not yet run)."""
    out = {}
    for i in range(1, 51):
        f = ROOT / "results" / f"strategy_{i:03d}.json"
        if f.exists():
            try:
                out[i] = json.loads(f.read_text())
            except Exception:
                out[i] = None
        else:
            out[i] = None
    return out


def is_running():
    return bool(subprocess.run(["pgrep", "-f", "ml_tests_50_robust.py"],
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
    results = load_results()
    n_done = sum(1 for r in results.values() if r is not None)
    running = is_running()

    start_file = Path("/tmp/iter3_start_ts.txt")
    elapsed = remaining = None
    if start_file.exists():
        try:
            start_ts = int(start_file.read_text().strip())
            elapsed = time.time() - start_ts
            if n_done > 0:
                remaining = (elapsed / n_done) * (50 - n_done)
        except ValueError:
            pass

    dot = "🟢" if running else "🔴"
    return (
        f"{dot} Iteration 3 — {'EN COURS' if running else 'ARRÊTÉE'}\n"
        f"{n_done}/50 fait(s) | Écoulé {fmt_duration(elapsed)} | Restant ~{fmt_duration(remaining)}"
    )


def build_full_list():
    """Full list of all 50 strategies with status icon, compact one-line-per-4."""
    results = load_results()
    lines = ["📋 LISTE COMPLÈTE (50 stratégies)"]
    row = []
    for i in range(1, 51):
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
    """Top 10 by design Sharpe annualized, among strategies with a result."""
    results = load_results()
    scored = []
    for i, r in results.items():
        if r and r.get("design_sharpe") is not None:
            ds_ann = r["design_sharpe"] * (252 ** 0.5)
            ts = r.get("test_sharpe")
            ts_ann = ts * (252 ** 0.5) if ts is not None else None
            dsr = r.get("dsr")
            scored.append((ds_ann, i, r.get("model", STRATEGY_NAMES.get(i, "?")), ts_ann, dsr, r.get("result")))

    scored.sort(reverse=True, key=lambda x: x[0])
    top = scored[:10]

    if not top:
        return "🏆 TOP 10 — aucun résultat disponible pour l'instant"

    lines = ["🏆 TOP 10 (par Design Sharpe annualisé)", "```"]
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
