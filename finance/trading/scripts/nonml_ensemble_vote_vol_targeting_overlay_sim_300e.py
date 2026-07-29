"""Simulation — 300 EUR dans l'overlay vol-targeting gaté par vote
majoritaire (NDX), ~3 derniers mois. Spécification pré-enregistrée
(CAP=2.0x, seuil de vote 3/5), aucun paramètre retouché après les
résultats précédents.
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
from nonml_ensemble_vote_vol_targeting_overlay_backtest import (  # noqa: E402
    build_votes, combined_position, VOTE_THRESHOLD, COST_BPS,
)

CAPITAL0 = 300.0
WINDOW_DAYS = 63


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close_full = df["close"].values
    dates_full = df["date"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full_all = np.log(close_full[1:] / close_full[:-1])

    votes, _first_valid = build_votes(dates_idx)
    gate_aligned = votes >= VOTE_THRESHOLD
    pos_full_all = combined_position(bh_full_all, gate_aligned)

    bh_full = bh_full_all[-WINDOW_DAYS:]
    pos = pos_full_all[-WINDOW_DAYS:]
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
        "# Simulation — 300 EUR, overlay vol-targeting gaté vote majoritaire (NDX, ~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances, dont {n_active} avec porte active). CAP=2.0x, seuil de vote 3/5, "
        "aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **Overlay vote majoritaire** | **{equity_ov[-1]:.2f} EUR** | "
        f"**{100*(equity_ov[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_ov):.1f}% | {me_ov['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) illustrative uniquement — le verdict "
        "statistique réel n'est PAS encore établi à ce stade (Règle 9) : ce PASS niveau 1 (plateau "
        "de robustesse parfait 12/12 sur 3 grilles, meilleur delta Sharpe testé jusqu'ici) doit "
        "encore passer la batterie de validation renforcée "
        "(`nonml_pass_validation_battery.py ensemble_vote_vol_targeting_overlay`, n_trials=taille "
        "du backlog) avant toute déclaration finale — ET reste construit à partir de 5 gates "
        "choisies APRÈS avoir vu qu'elles étaient déjà PASS niveau 1 (biais de sélection assumé)."
    ]

    out = ROOT / "results" / "nonml_ensemble_vote_vol_targeting_overlay_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
