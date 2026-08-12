"""Simulation — 300 EUR dans le vol-targeting défensif (critère Calmar,
NDX), ~3 derniers mois. Spécification pré-enregistrée (TARGET_VOL=20%),
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
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_defensive_calmar_vol_targeting_overlay_backtest import (  # noqa: E402
    vol_target_position, MARKETS, COST_BPS,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKETS["NDX (40 ans)"]))
    quality_report(df)
    close_full = df["close"].values
    dates_full = df["date"].values
    bh_full_all = np.log(close_full[1:] / close_full[:-1])

    pos_full_all = vol_target_position(bh_full_all)

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
    calmar_ov = me_ov["calmar"] if np.isfinite(me_ov["calmar"]) else float("nan")
    calmar_bh = me_bh["calmar"] if np.isfinite(me_bh["calmar"]) else float("nan")

    lines = [
        "# Simulation — 300 EUR, vol-targeting défensif critère Calmar (NDX, ~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances). TARGET_VOL_ANNUAL=20%, jamais de levier, aucun paramètre "
        "retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. | Calmar |",
        "|---|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} | {calmar_bh:.3f} |",
        f"| **Overlay défensif** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} | "
        f"**{calmar_ov:.3f}** |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement, régime haussier calme "
        "(peu de coupes défensives attendues sur une fenêtre sans stress) — le verdict statistique réel "
        "reste celui du backtest complet (PASS Calmar 4/5, Sharpe ET MDD améliorés sur tous les "
        "marchés testés) et de la robustesse (plateau parfait 8/8 sur les deux grilles). Doit encore "
        "passer la batterie Règle 9 (`nonml_pass_validation_battery.py "
        "defensive_calmar_vol_targeting_overlay`), avec la nuance explicite que ses contrôles sont "
        "bâtis sur le critère Sharpe/rendement standard, pas Calmar."
    ]

    out = ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
