"""Robustesse — effet janvier (proxy prix bas), univers POINT-IN-TIME.

Grille de perturbation **identique** à celle du cycle d'origine
(`nonml_january_effect_lowprice_overlay_robustness.py`) : CAP de l'overlay
janvier. **Ce n'est PAS un retuning** — le tercile (1/3), la périodicité de
rebalancement (21j) et la définition du signal (mois de janvier) restent figés.
On vérifie seulement que le PASS obtenu sur univers point-in-time est un plateau
et non un pic isolé.

La grille étant reprise telle quelle de l'origine, elle est fixée avant toute
exécution.

Usage : python3 scripts/nonml_january_effect_lowprice_overlay_pit_universe_robustness.py
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

CAP_GRID = [1.5, 2.0, 2.5, 3.0]
OUT = ROOT / "results" / "nonml_january_effect_lowprice_overlay_pit_universe_robustness.md"


def evaluate(P, W, investable, cap):
    is_jan = np.array([d.month == 1 for d in P.index])
    exposure = np.where(is_jan, cap, 1.0)
    W_base = bt.lag_one_day(W)
    W_lev = bt.lag_one_day(W * exposure[:, None])
    inv_lag = np.concatenate(([False], investable[:-1]))
    first = int(np.argmax(inv_lag)) if inv_lag.any() else len(P)
    s = max(bt.REBAL_EVERY, first)

    R = np.nan_to_num((P / P.shift(1) - 1.0).values, nan=0.0)
    pnl_b = (W_base[s:] * R[s:]).sum(axis=1)
    pnl_l = (W_lev[s:] * R[s:]).sum(axis=1)
    t_b = np.abs(np.diff(W_base[s:], axis=0, prepend=W_base[s:s + 1])).sum(axis=1) / 2.0
    t_l = np.abs(np.diff(W_lev[s:], axis=0, prepend=W_lev[s:s + 1])).sum(axis=1) / 2.0
    pnl_b = pnl_b - t_b * (bt.COST_BPS / 1e4)
    pnl_l = pnl_l - t_l * (bt.COST_BPS / 1e4)

    me_b = trading_metrics(np.log1p(pnl_b))
    me_l = trading_metrics(np.log1p(pnl_l))
    ret_b = np.cumprod(1.0 + pnl_b)[-1] - 1.0
    ret_l = np.cumprod(1.0 + pnl_l)[-1] - 1.0
    return (me_l["sharpe_ann"] > me_b["sharpe_ann"], ret_l > ret_b,
            me_l["sharpe_ann"], ret_l, me_l["max_drawdown_pct"])


def main():
    P, tickers, W, investable = rebuild_weights()

    L = ["# Robustesse — effet janvier (proxy prix bas), univers POINT-IN-TIME", ""]
    L.append("Grille **identique** à celle du cycle d'origine, donc fixée avant exécution.")
    L.append("**Pas un retuning** : le tercile (1/3), le rebalancement (21j) et la")
    L.append("définition du signal (mois de janvier) restent figés.")
    L.append("")
    L.append(f"CAP pré-enregistré = {bt.CAP}x.")
    L.append("")
    L.append("| CAP | Sharpe>réf | Rendement>réf | PASS | Sharpe | Rendement total | MDD |")
    L.append("|---|---|---|---|---|---|---|")
    n_ok = 0
    for cap in CAP_GRID:
        s_ok, r_ok, sh, ret, mdd = evaluate(P, W, investable, cap)
        ok = s_ok and r_ok
        n_ok += int(ok)
        mark = " ← CAP pré-enregistré" if cap == bt.CAP else ""
        L.append(f"| {cap}x{mark} | {'OUI' if s_ok else 'non'} | {'OUI' if r_ok else 'non'} | "
                 f"{'OUI' if ok else 'non'} | {sh:+.2f} | {100*ret:+.1f}% | {mdd:.1f}% |")
    L.append("")
    L.append(f"**{n_ok}/{len(CAP_GRID)} cellules PASS.** Rapporté tel quel, sans réajustement.")
    L.append("")
    L.append("Pour mémoire, le cycle d'origine (univers biaisé par le survivant) obtenait")
    L.append("**3/4** sur cette même grille, la cellule CAP=3,0x échouant sur le Sharpe.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
