"""Simulation — 300 EUR dans l'overlay union ToM ∪ Halloween (NDX), ~3
derniers mois. Spécification pré-enregistrée (CAP=2.0x), aucun paramètre
retouché après les résultats précédents.
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
from nonml_tom_halloween_union_overlay_backtest import tom_mask, halloween_mask, COST_BPS, CAP  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    df_full = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_full)

    df = df_full.iloc[-(WINDOW_DAYS + 1):].reset_index(drop=True)
    close = df["close"].values
    dates = df["date"].values

    bh_full = np.log(close[1:] / close[:-1])
    mask = (tom_mask(df["date"]) | halloween_mask(df["date"]))[1:]
    pos = np.where(mask, CAP, 1.0)
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
        "# Simulation — 300 EUR, overlay union ToM ∪ Halloween (NDX, ~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances). CAP={CAP}x si ToM OU Halloween actif, 1.0x sinon.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay ToM∪Halloween** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        f"**Lecture honnête** : sur cette fenêtre de {WINDOW_DAYS} séances, la position est "
        f"levée {100*mask.mean():.1f}% du temps (union des deux fenêtres) — illustration "
        "seulement, le verdict statistique reste celui du backtest complet (PASS 4/5 marchés) "
        "et de la robustesse (plateau 4/5 constant sur la grille CAP 1.5x-3.0x)."
    ]

    out = ROOT / "results" / "nonml_tom_halloween_union_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
