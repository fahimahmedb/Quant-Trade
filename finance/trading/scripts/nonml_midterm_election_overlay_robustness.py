"""Robustesse — cycle #176 (mid-term election overlay), perturbation ±20%
du plancher CUT=0.5x, annoncée implicitement par la convention déjà
établie du backlog (grille ±20% sur les paramètres non centraux au
critère). Ce n'est PAS un retuning : le verdict reste celui du point
pré-enregistré 0.5x.
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
from nonml_midterm_election_overlay_backtest import COST_BPS, CUT, MARKETS, midterm_mask  # noqa: E402

CUT_GRID = [round(CUT * 0.8, 2), CUT, round(CUT * 1.2, 2)]


def evaluate(pos, bh_full, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * bh_full - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.cumprod(1.0 + pnl)[-1] - 1.0)
    return me, ret


def main():
    lines = [
        "# Robustesse — cycle #176, perturbation ±20% du plancher CUT",
        "",
        f"Point pré-enregistré : CUT = {CUT}x. Grille : {{{', '.join(f'{c}x' for c in CUT_GRID)}}}.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré (0.5x) quelle que soit la lecture de ce tableau.",
        "",
        "| Marché | CUT | Sharpe | Rendement total | MDD | Sharpe>BH | Rdt>BH | Les deux |",
        "|---|---|---|---|---|---|---|---|",
    ]
    n_both_total, n_cells_total = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        bh_full = np.log(close[1:] / close[:-1])
        mask = midterm_mask(df["date"])[1:]

        me_bh, ret_bh = evaluate(np.ones_like(bh_full), bh_full, COST_BPS)

        for cut in CUT_GRID:
            pos = np.where(mask, cut, 1.0)
            me, ret = evaluate(pos, bh_full, COST_BPS)
            ok_s = me["sharpe_ann"] > me_bh["sharpe_ann"]
            ok_r = ret > ret_bh
            both = ok_s and ok_r
            n_cells_total += 1
            n_both_total += int(both)
            star = " **(pré-enregistré)**" if cut == CUT else ""
            lines.append(
                f"| {name} | {cut}x{star} | {me['sharpe_ann']:+.2f} | {100*ret:+.1f}% | "
                f"{me['max_drawdown_pct']:.1f}% | {'OUI' if ok_s else 'non'} | "
                f"{'OUI' if ok_r else 'non'} | {'OUI' if both else 'non'} |"
            )

    lines += [
        "",
        f"**{n_both_total}/{n_cells_total} combinaisons (marché × CUT) battent Buy & Hold sur les DEUX jambes.**",
        "",
        "Lecture : un plateau (toutes ou presque toutes les cellules) indique un mécanisme "
        "peu sensible au calibrage du plancher.",
    ]

    out = ROOT / "results" / "nonml_midterm_election_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
