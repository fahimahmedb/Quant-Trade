"""Simulation — 300 EUR dans la stratégie ToM-only (NDX), ~3 derniers mois
de données disponibles. Spécification pré-enregistrée (4j/3j), aucun
paramètre retouché après le résultat du backtest/robustesse.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
LAST_N_DAYS = 4
FIRST_N_DAYS = 3
CAPITAL0 = 300.0
WINDOW_DAYS = 63  # ~3 mois de seances boursieres


def tom_mask(dates: pd.Series) -> np.ndarray:
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ym"] = df["date"].dt.to_period("M")
    df["rank_asc"] = df.groupby("ym").cumcount() + 1
    df["rank_desc"] = df.groupby("ym")["date"].transform(lambda s: len(s)) - df["rank_asc"] + 1
    mask = (df["rank_asc"] <= FIRST_N_DAYS) | (df["rank_desc"] <= LAST_N_DAYS)
    return mask.values


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close_full = df["close"].values
    mask_full = tom_mask(df["date"])

    # fenetre des WINDOW_DAYS dernieres seances (masque calcule sur le calendrier
    # complet pour ne pas fausser les rangs de debut/fin de mois en bord de fenetre)
    close = close_full[-(WINDOW_DAYS + 1):]
    mask = mask_full[-(WINDOW_DAYS + 1):]
    dates = df["date"].values[-(WINDOW_DAYS + 1):]

    bh_full = np.log(close[1:] / close[:-1])
    pos = mask[1:].astype(float)
    turn = np.abs(np.diff(pos, prepend=0.0))
    pnl_tom = pos * bh_full - turn * (COST_BPS / 1e4)
    pnl_bh = bh_full.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    equity_tom = CAPITAL0 * np.cumprod(1.0 + pnl_tom)
    equity_bh = CAPITAL0 * np.cumprod(1.0 + pnl_bh)

    def mdd(equity):
        running_max = np.maximum.accumulate(equity)
        return (equity / running_max - 1.0).min() * 100

    me_tom = trading_metrics(pnl_tom)
    me_bh = trading_metrics(pnl_bh)

    lines = [
        "# Simulation — 300 EUR, stratégie Tournant-de-mois (NDX, ~3 derniers mois)",
        "",
        f"Période : {pd.Timestamp(dates[1]).date()} → {pd.Timestamp(dates[-1]).date()} "
        f"({len(bh_full)} séances, {WINDOW_DAYS} demandées). Spécification 4j/3j "
        "pré-enregistrée, aucun paramètre retouché après les résultats précédents.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| BuyHold | {equity_bh[-1]:.2f} EUR | {100*(equity_bh[-1]/CAPITAL0-1):+.1f}% | "
        f"{mdd(equity_bh):.1f}% | {me_bh['sharpe_ann']:+.2f} |",
        f"| **ToM-only** | **{equity_tom[-1]:.2f} EUR** | "
        f"**{100*(equity_tom[-1]/CAPITAL0-1):+.1f}%** | {mdd(equity_tom):.1f}% | "
        f"{me_tom['sharpe_ann']:+.2f} |",
        "",
        "**Lecture honnête** : fenêtre courte (~3 mois) — un seul cycle mensuel et demi "
        "de turn-of-month observé ici, échantillon bien trop petit pour juger quoi que "
        "ce soit seul ; à lire uniquement comme illustration, le verdict statistique "
        "réel reste celui du backtest complet (`results/nonml_turn_of_month_result.md`, "
        "PASS 4/5 marchés) et du test de robustesse (plateau modéré, pas parfaitement "
        "stable : 3/5, 4/5, 3/5 selon la largeur de fenêtre)."
    ]

    out = ROOT / "results" / "nonml_turn_of_month_sim_300e.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
