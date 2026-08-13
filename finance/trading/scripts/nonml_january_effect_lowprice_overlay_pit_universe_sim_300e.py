"""Simulation 300 EUR — effet janvier (proxy prix bas), univers POINT-IN-TIME.

Illustration sur les ~3 derniers mois de données disponibles (63 séances).
**Aucune valeur statistique** : le verdict du cycle reste celui du backtest
complet (2900 séances) et de la grille de robustesse (4/4).

Portefeuille : rendements **simples** par titre, `Σ wᵢ·rᵢ`, équité par
`cumprod(1+pnl)` — convention corrigée du dépôt pour un panier.

Avertissement spécifique à cette fenêtre : l'overlay janvier n'est actif qu'au
mois de janvier. Sur une fenêtre de 3 mois qui ne contient **aucun** mois de
janvier, la stratégie est par construction **identique** à sa référence. Le
script le signale explicitement plutôt que d'afficher une égalité trompeuse.

Usage : python3 scripts/nonml_january_effect_lowprice_overlay_pit_universe_sim_300e.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
import nonml_january_effect_lowprice_overlay_pit_universe_backtest as bt  # noqa: E402
from nonml_january_effect_lowprice_overlay_pit_universe_audit import rebuild_weights  # noqa: E402

CAPITAL0 = 300.0
WINDOW_DAYS = 63
OUT = ROOT / "results" / "nonml_january_effect_lowprice_overlay_pit_universe_sim_300e.md"


def mdd_pct(eq):
    return float((eq / np.maximum.accumulate(eq) - 1.0).min() * 100)


def main():
    P, tickers, W, investable = rebuild_weights()
    is_jan = np.array([d.month == 1 for d in P.index])
    exposure = np.where(is_jan, bt.CAP, 1.0)
    W_base = bt.lag_one_day(W)
    W_lev = bt.lag_one_day(W * exposure[:, None])
    R = np.nan_to_num((P / P.shift(1) - 1.0).values, nan=0.0)

    sl = slice(len(P) - WINDOW_DAYS, len(P))
    dates_w = P.index[sl]
    pnl_b = (W_base[sl] * R[sl]).sum(axis=1)
    pnl_l = (W_lev[sl] * R[sl]).sum(axis=1)
    t_b = np.abs(np.diff(W_base[sl], axis=0, prepend=W_base[sl][:1])).sum(axis=1) / 2.0
    t_l = np.abs(np.diff(W_lev[sl], axis=0, prepend=W_lev[sl][:1])).sum(axis=1) / 2.0
    pnl_b = pnl_b - t_b * (bt.COST_BPS / 1e4)
    pnl_l = pnl_l - t_l * (bt.COST_BPS / 1e4)

    eq_b = CAPITAL0 * np.cumprod(1.0 + pnl_b)
    eq_l = CAPITAL0 * np.cumprod(1.0 + pnl_l)
    me_b = trading_metrics(np.log1p(pnl_b))
    me_l = trading_metrics(np.log1p(pnl_l))

    n_jan = int(is_jan[sl].sum())

    L = [
        "# Simulation 300 EUR — effet janvier (proxy prix bas), univers POINT-IN-TIME",
        "",
        f"Période : {dates_w[0].date()} → {dates_w[-1].date()} ({WINDOW_DAYS} séances). "
        f"Coûts {bt.COST_BPS:.0f} bps.",
        "",
        "| | Capital final | Rendement période | MDD | Sharpe ann. |",
        "|---|---|---|---|---|",
        f"| Tercile prix bas 1.0x (référence) | {eq_b[-1]:.2f} EUR | "
        f"{100*(eq_b[-1]/CAPITAL0-1):+.1f}% | {mdd_pct(eq_b):.1f}% | {me_b['sharpe_ann']:+.2f} |",
        f"| **Tercile prix bas + overlay janvier** | **{eq_l[-1]:.2f} EUR** | "
        f"**{100*(eq_l[-1]/CAPITAL0-1):+.1f}%** | {mdd_pct(eq_l):.1f}% | {me_l['sharpe_ann']:+.2f} |",
        "",
        f"Séances de janvier dans la fenêtre : **{n_jan}**.",
        "",
    ]
    if n_jan == 0:
        L.append("**La fenêtre ne contient AUCUN mois de janvier.** L'overlay n'est donc "
                 "jamais actif et la stratégie est, par construction, **strictement "
                 "identique à sa référence** sur cette période. Les deux lignes ci-dessus "
                 "sont égales pour cette raison mécanique — ce n'est ni une performance "
                 "ni une contre-performance, c'est l'absence de signal.")
    else:
        L.append(f"L'overlay est actif sur {n_jan} séances de la fenêtre.")
    L.append("")
    L.append("**Lecture honnête** : 63 séances n'ont **aucune valeur statistique**. Le "
             "verdict du cycle reste celui du backtest complet (2900 séances, 2015-2026, "
             "PASS) et de la grille de robustesse (4/4).")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
