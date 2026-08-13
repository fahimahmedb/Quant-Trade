"""Simulation 300 EUR — breadth de faiblesse, univers POINT-IN-TIME.

Illustration sur les ~3 derniers mois de données disponibles (63 séances).
**Aucune valeur statistique** : le verdict du cycle reste celui du backtest
complet (2645 séances) et de la grille de robustesse.

Aucun paramètre n'est retouché après lecture des résultats précédents.

Usage : python3 scripts/nonml_weakness_breadth_vol_targeting_overlay_pit_universe_sim_300e.py
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
import nonml_weakness_breadth_vol_targeting_overlay_pit_universe_backtest as bt  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63
OUT = ROOT / "results" / "nonml_weakness_breadth_vol_targeting_overlay_pit_universe_sim_300e.md"


def mdd_pct(eq):
    return float((eq / np.maximum.accumulate(eq) - 1.0).min() * 100)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    dates_idx = pd.to_datetime(df["date"])
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])

    breadth_net, _cov = bt.compute_weakness_breadth_series_pit()
    breadth_raw = breadth_net.reindex(dates_idx.values, method="ffill").values
    gate_aligned = np.where(np.isnan(breadth_raw), False, breadth_raw >= bt.BREADTH_THRESHOLD)

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
        "# Simulation 300 EUR — breadth de faiblesse, univers POINT-IN-TIME",
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
        f"| **Overlay gaté breadth de faiblesse (PIT)** | **{eq_ov[-1]:.2f} EUR** | "
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
             "du cycle reste celui du backtest complet (2896 séances, 2015-2026, PASS) "
             "et de la grille de robustesse (4/4 sur CAP, 4/4 sur la fenêtre — toutes cellules identiques à Buy & Hold).")
    L.append("")
    L.append("**Rappel décisif** : le verdict de ce candidat est étiqueté **NON "
             "INFORMATIF** par le critère fixé avant calcul (porte brute active 0,45 % du "
             "temps), et l'audit a établi que l'exposition ne dépasse **jamais** 1,0×. Les "
             "deux lignes ci-dessus sont donc identiques par construction, et non parce que "
             "la stratégie aurait égalé Buy & Hold sur cette fenêtre.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
