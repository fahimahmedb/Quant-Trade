"""Simulation 300 EUR — concentration du marché (HHI), univers POINT-IN-TIME.

Illustration sur les ~3 derniers mois de données disponibles (63 séances).
**Aucune valeur statistique** : le verdict du cycle reste celui du backtest
complet (2645 séances) et de la grille de robustesse.

Aucun paramètre n'est retouché après lecture des résultats précédents.

Usage : python3 scripts/nonml_market_concentration_vol_targeting_overlay_pit_universe_sim_300e.py
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
import nonml_market_concentration_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63
OUT = ROOT / "results" / "nonml_market_concentration_vol_targeting_overlay_pit_universe_sim_300e.md"


def mdd_pct(eq):
    return float((eq / np.maximum.accumulate(eq) - 1.0).min() * 100)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    dates_idx = pd.to_datetime(df["date"])
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])

    conc, _cov, _n = bt.compute_concentration_series_pit()
    
    
    gate_series = bt.build_gate(conc)
    gate_aligned = gate_series.fillna(False).reindex(
        dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    pos_full = bt.combined_position(r, gate_aligned)

    sl = slice(len(r) - WINDOW_DAYS, len(r))
    dates_w = dates_idx.values[1:][sl]
    r_w = r[sl]
    pos_w = pos_full[sl]

    turn = np.abs(np.diff(pos_w, prepend=1.0))
    pnl_ov = pos_w * r_w - turn * (bt.COST_BPS / 1e4)
    pnl_bh = r_w.copy()
    pnl_bh[0] -= bt.COST_BPS / 1e4

    eq_bh = CAPITAL0 * np.exp(np.cumsum(pnl_bh))
    eq_ov = CAPITAL0 * np.exp(np.cumsum(pnl_ov))
    me_bh, me_ov = trading_metrics(pnl_bh), trading_metrics(pnl_ov)
    n_active = int((pos_w > 1.0).sum())

    L = [
        "# Simulation 300 EUR — concentration du marché (HHI), univers POINT-IN-TIME",
        "",
        f"Période : {pd.Timestamp(dates_w[0]).date()} → {pd.Timestamp(dates_w[-1]).date()} "
        f"({WINDOW_DAYS} séances, dont **{n_active}** avec porte active). "
        f"Coûts {bt.COST_BPS:.0f} bps. Aucun paramètre retouché après lecture des résultats "
        f"précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX) | {eq_bh[-1]:.2f} EUR | {100*(eq_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd_pct(eq_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay gaté concentration (PIT)** | **{eq_ov[-1]:.2f} EUR** | "
        f"**{100*(eq_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd_pct(eq_ov):.1f}% | "
        f"{me_ov['sharpe_ann']:+.2f} |",
        "",
    ]
    if n_active == 0:
        L.append("**La porte n'est jamais active sur cette fenêtre.** La stratégie est donc "
                 "par construction identique à Buy & Hold ici — ce n'est ni une performance "
                 "ni une contre-performance, c'est l'absence de signal.")
        L.append("")
    L.append("**Lecture honnête** : 63 séances n'ont **aucune valeur statistique**. Le verdict "
             "du cycle reste celui du backtest complet (2645 séances, 2016-2026, PASS) "
             "et de la grille de robustesse (4/4 sur CAP, 4/4 sur la fenêtre de vol).")
    L.append("")
    L.append("Rappel : un PASS de niveau 1 n'est **pas** un verdict final (Règle 9).")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
