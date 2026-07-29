"""Simulation — 300 EUR dans l'overlay défensif combiné (#115+GARCH)/2,
NDX, ~3 derniers mois. Spécification pré-enregistrée (poids 0.5/0.5),
aucun paramètre retouché après les résultats précédents.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    d1 = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    d2 = np.load(ROOT / "results" / "nonml_etape_d_garch_defensive_overlay_pnl.npz", allow_pickle=True)
    dates1 = pd.to_datetime(d1["dates"])
    dates2 = pd.to_datetime(d2["dates"])
    s_pos1 = pd.Series(d1["pos"], index=dates1)
    s_pos2 = pd.Series(d2["pos"], index=dates2)
    s_r1 = pd.Series(d1["r_asset"], index=dates1)

    common = dates1.intersection(dates2).sort_values()
    pos_full = (0.5 * s_pos1.reindex(common) + 0.5 * s_pos2.reindex(common)).values
    r_full = s_r1.reindex(common).values

    bh_full = r_full[-WINDOW_DAYS:]
    pos = pos_full[-WINDOW_DAYS:]
    dates_window = common[-(WINDOW_DAYS + 1):]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh = bh_full.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    equity_ov = CAPITAL0 * np.cumprod(1.0 + pnl_ov)
    equity_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    lines = [
        "# Simulation — 300 EUR, overlay défensif combiné (#115+GARCH)/2 (NDX, ~3 derniers mois)",
        "",
        f"Période : {dates_window[1].date()} → {dates_window[-1].date()} "
        f"({len(bh_full)} séances). Poids 0.5/0.5, aucun paramètre retouché après les "
        "résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay combiné** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement, régime calme -- le "
        "verdict statistique réel reste celui du backtest complet (PASS standard ET Calmar sur 40 ans) "
        "et de la robustesse (plateau parfait 5/5 sur la grille de poids). Doit encore passer la "
        "batterie Règle 9 (`nonml_pass_validation_battery.py dual_engine_defensive_overlay`) avant "
        "toute déclaration finale."
    ]

    out = ROOT / "results" / "nonml_dual_engine_defensive_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
