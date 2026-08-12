"""Simulation — 300 EUR, overlay combinaison ET breakeven inflation +
demandes continues + balance commerciale (cycle #333) sur les ~3
derniers mois disponibles (NDX). Aucun paramètre retouché.
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
from nonml_inflation_breakeven_overlay_backtest import (  # noqa: E402
    COST_BPS, load_t10yie_lag, expanding_tercile_cut_high as t10yie_gate_high,
)
from nonml_continuing_claims_overlay_backtest import (  # noqa: E402
    build_continuing_claims_yoy_series, load_continuing_claims_yoy_lag,
)
from nonml_trade_balance_overlay_backtest import (  # noqa: E402
    build_trade_balance_series, load_trade_balance_lag,
)
from nonml_jobless_claims_overlay_backtest import (  # noqa: E402
    expanding_tercile_cut_high as claims_gate_high,
)
from nonml_m2_growth_overlay_backtest import (  # noqa: E402
    expanding_tercile_cut_low as trade_gate_low,
)
from nonml_macro_combo_and_breakeven_claims_trade_overlay_backtest import CUT, and_3_of_3  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63
MARKET_FILE = "nasdaq100_daily.txt"
MARKET_NAME = "NDX (40 ans)"


def mdd_pct(equity):
    running_max = np.maximum.accumulate(equity)
    return float((equity / running_max - 1.0).min() * 100)


def main():
    claims_series = build_continuing_claims_yoy_series()
    trade_series = build_trade_balance_series()

    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    close = df["close"].values
    dates = pd.DatetimeIndex(df["date"].values)
    bh_full = np.log(close[1:] / close[:-1])
    dates_r = dates[1:]

    t10yie_lag = load_t10yie_lag(dates)[1:]
    claims_lag = load_continuing_claims_yoy_lag(dates, claims_series)[1:]
    trade_lag = load_trade_balance_lag(dates, trade_series)[1:]
    gate1 = t10yie_gate_high(t10yie_lag)
    gate2 = claims_gate_high(claims_lag)
    gate3 = trade_gate_low(trade_lag)
    valid = np.isfinite(gate1) & np.isfinite(gate2) & np.isfinite(gate3)
    start = int(np.argmax(valid)) if valid.any() else len(valid)

    pos_active_full = and_3_of_3(gate1[start:], gate2[start:], gate3[start:])
    pos_full = np.where(pos_active_full, CUT, 1.0)
    bh_full_valid = bh_full[start:]
    dates_valid = dates_r[start:]

    r = bh_full_valid[-WINDOW_DAYS:]
    pos = pos_full[-WINDOW_DAYS:]
    dates_w = dates_valid[-WINDOW_DAYS:]
    assert len(r) == WINDOW_DAYS, "fenêtre récente doit être entièrement dans la zone de données valides"

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

    frac_cut = float((pos < 1.0).mean())

    lines = [
        f"# Simulation — 300 EUR, overlay combinaison ET breakeven+CCSA+balance commerciale (cycle #333), {MARKET_NAME} (~3 derniers mois)",
        "",
        f"Période : {dates_w[0].date()} → {dates_w[-1].date()} ({len(r)} séances). "
        f"{100*frac_cut:.0f}% de la fenêtre est en régime coupé (les 3 signaux simultanément défavorables).",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy & Hold | {eq_bh[-1]:.2f} EUR | {100 * (eq_bh[-1] / CAPITAL0 - 1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay combinaison ET** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100 * (eq_ov[-1] / CAPITAL0 - 1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre purement illustrative de 63 séances, sans valeur "
        "statistique — le verdict du cycle reste celui du backtest complet (4/5 marchés) "
        "et de la grille de robustesse (12/15, plateau parfait sur les 4 marchés gagnants).",
    ]

    out = ROOT / "results" / "nonml_macro_combo_and_breakeven_claims_trade_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
