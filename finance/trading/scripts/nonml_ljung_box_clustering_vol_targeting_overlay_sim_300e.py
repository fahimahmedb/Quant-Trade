"""Simulation — 300 EUR dans l'overlay vol-targeting gaté par la
statistique de Ljung-Box glissante (NDX), ~3 derniers mois.
Spécification pré-enregistrée (LB_WINDOW=252, LB_MAXLAG=22,
MEDIAN_WINDOW=252, CAP=2.0x, VOL_WINDOW=20), aucun paramètre retouché
après les résultats précédents.
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
from nonml_ljung_box_clustering_vol_targeting_overlay_backtest import (  # noqa: E402
    calm_lb_mask, combined_position, COST_BPS, CAP, VOL_WINDOW,
    TARGET_VOL_ANNUAL, LB_WINDOW, LB_MAXLAG, MEDIAN_WINDOW,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close_full = df["close"].values
    dates_full = df["date"].values

    bh_full_all = np.log(close_full[1:] / close_full[:-1])
    gate_all = calm_lb_mask(bh_full_all)
    pos_full_all = combined_position(bh_full_all, gate_all)

    bh_full = bh_full_all[-WINDOW_DAYS:]
    pos = pos_full_all[-WINDOW_DAYS:]
    dates = dates_full[-(WINDOW_DAYS + 1):]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh = bh_full.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    # Equite composee en LOG : les series pnl_* sont des rendements log,

    # donc equity = CAPITAL0 * exp(cumsum(pnl)), pas cumprod(1+pnl).

    # Voir results/nonml_log_return_compounding_audit.md.

    equity_ov = CAPITAL0 * np.exp(np.cumsum(pnl_ov))
    equity_bh = CAPITAL0 * np.exp(np.cumsum(pnl_bh))

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    lines = [
        "# Simulation — 300 EUR, overlay vol-targeting gaté par la statistique de Ljung-Box "
        "glissante (NDX, ~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances). Fenêtre Q/médiane {LB_WINDOW}j/{MEDIAN_WINDOW}j "
        f"(Q(maxlag={LB_MAXLAG})), vol cible {TARGET_VOL_ANNUAL:.0%}, fenêtre vol {VOL_WINDOW}j, "
        f"CAP={CAP}x.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay Ljung-Box gaté** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        f"**Lecture honnête** : sur cette fenêtre de {WINDOW_DAYS} séances, la porte est active "
        f"{100*(pos[:-1]>1.0).mean():.1f}% du temps (position moyenne {pos.mean():.2f}x) — illustration "
        "seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés, seul "
        "DAX échoue) et de la robustesse (plateau relativement fragile : grille CAP 3-4/5 avec un "
        "seul point à 4/5, grille fenêtre de vol 2-4/5 avec la valeur pré-enregistrée isolée)."
    ]

    out = ROOT / "results" / "nonml_ljung_box_clustering_vol_targeting_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
