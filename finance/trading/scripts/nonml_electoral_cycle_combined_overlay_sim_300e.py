"""Simulation — 300 EUR, cycle électoral combiné (cycle #179) sur les ~3
derniers mois disponibles (NDX). Aucun paramètre retouché.

Note : 2026 EST une année de mid-term ((2026%4)==2) -- la fenêtre est
donc en régime CUT (0.5x), pas en régime pré-électoral, signalé
honnêtement (même situation que le #176).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_presidential_cycle_overlay_backtest import preelection_mask  # noqa: E402
from nonml_midterm_election_overlay_backtest import CUT, midterm_mask  # noqa: E402
from nonml_electoral_cycle_combined_overlay_backtest import CAP, COST_BPS  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63
MARKET_FILE = "nasdaq100_daily.txt"
MARKET_NAME = "NDX (40 ans)"


def mdd_pct(equity):
    running_max = np.maximum.accumulate(equity)
    return float((equity / running_max - 1.0).min() * 100)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    close = df["close"].values
    dates = pd.to_datetime(df["date"].values)
    bh_full = np.log(close[1:] / close[:-1])
    dates_r = dates[1:]

    pre_mask = preelection_mask(df["date"])[1:]
    mid_mask = midterm_mask(df["date"])[1:]
    pos_full = np.ones_like(bh_full)
    pos_full[pre_mask] = CAP
    pos_full[mid_mask] = CUT

    r = bh_full[-WINDOW_DAYS:]
    pos = pos_full[-WINDOW_DAYS:]
    dates_w = dates_r[-WINDOW_DAYS:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    # Equite composee en LOG : les series pnl_* sont des rendements log,

    # donc equity = CAPITAL0 * exp(cumsum(pnl)), pas cumprod(1+pnl).

    # Voir results/nonml_log_return_compounding_audit.md.

    eq_ov = CAPITAL0 * np.exp(np.cumsum(pnl_ov))
    eq_bh = CAPITAL0 * np.exp(np.cumsum(pnl_bh))
    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    regime = "CUT (mid-term)" if (pos == CUT).all() else ("CAP (pré-électorale)" if (pos == CAP).all() else "mixte")

    lines = [
        f"# Simulation — 300 EUR, cycle électoral combiné (cycle #179), {MARKET_NAME} (~3 derniers mois)",
        "",
        f"Période : {dates_w[0].date()} → {dates_w[-1].date()} ({len(r)} séances). "
        f"Régime sur cette fenêtre : **{regime}** (2026 est une année de mid-term).",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold | {eq_bh[-1]:.2f} EUR | {100 * (eq_bh[-1] / CAPITAL0 - 1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Cycle électoral combiné** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100 * (eq_ov[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (4/4 marchés) "
        "et de la grille de robustesse (36/36).",
    ]

    out = ROOT / "results" / "nonml_electoral_cycle_combined_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
