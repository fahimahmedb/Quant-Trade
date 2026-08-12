"""Simulation — 300 EUR dans l'overlay de confirmation multi-marché
internationale NDX+DAX, ~3 derniers mois. Spécification pré-enregistrée
(CAP=2.0x), aucun paramètre retouché après les résultats précédents.
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
from nonml_intl_breadth_confirmation_overlay_backtest import near_high_series, COST_BPS, CAP, INDEX_LOOKBACK  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    df_primary = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_primary)
    df_confirm = load_ohlc(str(REPO_ROOT / "data" / "dax_daily.txt"))
    quality_report(df_confirm)

    signal_a = near_high_series(df_primary)
    signal_b = near_high_series(df_confirm)
    dates_primary = pd.to_datetime(df_primary["date"])
    b_aligned = signal_b.reindex(dates_primary.values, method="ffill").fillna(False).values.astype(bool)
    a_aligned = signal_a.values.astype(bool)
    both = a_aligned & b_aligned

    close_full = df_primary["close"].values
    dates_full = df_primary["date"].values
    bh_full_all = np.log(close_full[1:] / close_full[:-1])
    pos_full_all = np.where(both[:-1], CAP, 1.0)

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
        "# Simulation — 300 EUR, overlay confirmation multi-marché internationale NDX+DAX (~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances). CAP={CAP}x quand NDX ET DAX sont simultanément proches de leur "
        "plus haut annuel.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay confirmation internationale** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        f"**Lecture honnête** : sur cette fenêtre de {WINDOW_DAYS} séances, l'exposition moyenne "
        f"est de {pos.mean():.2f}x — illustration seulement, le verdict statistique reste celui "
        "du backtest complet (PASS sur NDX, MDD exactement préservé) et de la robustesse "
        "(plateau parfait 4/4 sur la grille CAP 1.5x-3.0x)."
    ]

    out = ROOT / "results" / "nonml_intl_breadth_confirmation_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
