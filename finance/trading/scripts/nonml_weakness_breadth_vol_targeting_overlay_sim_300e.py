"""Simulation — 300 EUR, overlay vol-targeting gaté par la breadth de
faiblesse (NDX), ~3 derniers mois. Spécification pré-enregistrée
(CAP=2.0x), aucun paramètre retouché après les résultats précédents.

Attendu (voir backtest/audit/robustesse) : la porte n'est quasiment
jamais active sur l'échantillon complet -- cette simulation devrait
donc être quasi identique à Buy&Hold.
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
from nonml_weakness_breadth_vol_targeting_overlay_backtest import (  # noqa: E402
    compute_weakness_breadth_series, combined_position, COST_BPS,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close_full = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full_all = np.log(close_full[1:] / close_full[:-1])

    breadth = compute_weakness_breadth_series()
    breadth_aligned_raw = breadth.reindex(dates_idx.values, method="ffill").values
    breadth_aligned = np.nan_to_num(breadth_aligned_raw, nan=0.0)
    pos_full_all = combined_position(close_full, bh_full_all, breadth_aligned)

    bh_full = bh_full_all[-WINDOW_DAYS:]
    pos = pos_full_all[-WINDOW_DAYS:]
    dates_full = df["date"].values
    dates = dates_full[-(WINDOW_DAYS + 1):]

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
    n_active = int((pos > 1.0).sum())

    lines = [
        "# Simulation — 300 EUR, overlay vol-targeting gaté par la breadth de faiblesse (NDX, ~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances, dont {n_active} avec porte active). CAP=2.0x, aucun paramètre "
        "retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay breadth de faiblesse** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : comme attendu (voir avertissement du backtest/audit/robustesse), "
        f"la porte est active {n_active} jour(s) sur {len(bh_full)} dans cette fenêtre récente — "
        "le résultat est quasi identique à Buy&Hold, confirmant que le \"PASS\" pré-enregistré "
        "n'est pas un edge exploitable en pratique, seulement l'absence d'activation du mécanisme."
    ]

    out = ROOT / "results" / "nonml_weakness_breadth_vol_targeting_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
