"""Simulation — 300 EUR dans l'overlay de confirmation multi-marché
NDX+Russell2000, ~3 derniers mois. Spécification pré-enregistrée
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
from nonml_breadth_confirmation_overlay_backtest import near_high_series, COST_BPS, CAP, INDEX_LOOKBACK, INDEX_THRESHOLD  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    df_primary = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_primary)
    df_confirm = load_ohlc(str(REPO_ROOT / "data" / "russell2000_daily.txt"))
    quality_report(df_confirm)

    signal_a = near_high_series(df_primary)
    signal_b = near_high_series(df_confirm)
    dates_primary = pd.to_datetime(df_primary["date"])
    b_aligned_full = signal_b.reindex(dates_primary.values, method="ffill").fillna(False).values.astype(bool)
    a_aligned_full = signal_a.values.astype(bool)
    both_full = a_aligned_full & b_aligned_full

    close_full = df_primary["close"].values
    bh_full_all = np.log(close_full[1:] / close_full[:-1])
    mask_full = both_full[:-1]

    bh_full = bh_full_all[-WINDOW_DAYS:]
    mask = mask_full[-WINDOW_DAYS:]
    dates = dates_primary.values[-(WINDOW_DAYS + 1):]

    pos = np.where(mask, CAP, 1.0)
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
        "# Simulation — 300 EUR, overlay confirmation multi-marché NDX+Russell2000 (~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances). CAP={CAP}x si NDX ET Russell 2000 ≥{100*INDEX_THRESHOLD:.0f}% "
        f"de leur plus haut {INDEX_LOOKBACK}j, 1.0x sinon.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold (NDX) | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay confirmation multi-marché** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        f"**Lecture honnête** : sur cette fenêtre de {WINDOW_DAYS} séances, la position est "
        f"levée {100*mask.mean():.1f}% du temps — illustration seulement, le verdict statistique "
        "reste celui du backtest complet (PASS marginal, marge de Sharpe très fine +0,01) et de "
        "la robustesse (échoue déjà à CAP=3.0x sur le Sharpe — résultat fragile, à nuancer "
        "fortement par rapport aux plateaux parfaits d'autres cycles comme #37/#38)."
    ]

    out = ROOT / "results" / "nonml_breadth_confirmation_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
