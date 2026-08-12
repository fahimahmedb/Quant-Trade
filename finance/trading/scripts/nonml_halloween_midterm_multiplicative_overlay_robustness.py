"""Robustesse — cycle #184, grille jointe ±20% sur CAP (Halloween) et CUT
(mid-term), annoncée pour vérifier que la combinaison multiplicative
elle-même est robuste. Perturbation, PAS retuning : le verdict reste
celui du point pré-enregistré CAP=2.0x/CUT=0.5x.
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
from nonml_midterm_election_overlay_backtest import midterm_mask  # noqa: E402
from nonml_halloween_midterm_multiplicative_overlay_backtest import CAP, COST_BPS, MARKETS  # noqa: E402
from nonml_midterm_election_overlay_backtest import CUT  # noqa: E402

CAP_GRID = [round(CAP * 0.8, 2), CAP, round(CAP * 1.2, 2)]
CUT_GRID = [round(CUT * 0.8, 2), CUT, round(CUT * 1.2, 2)]


def evaluate(pos, bh_full, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * bh_full - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.exp(pnl.sum()) - 1.0)
    return me, ret


def main():
    lines = [
        "# Robustesse — cycle #184, grille jointe ±20% CAP × CUT",
        "",
        f"Point pré-enregistré : CAP={CAP}x, CUT={CUT}x. Grille : "
        f"CAP∈{{{', '.join(f'{c}x' for c in CAP_GRID)}}} × CUT∈{{{', '.join(f'{c}x' for c in CUT_GRID)}}}.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré (2.0x/0.5x) quelle que soit la lecture de ce tableau.",
        "",
        "| Marché | CAP | CUT | Sharpe | Rendement total | MDD | Sharpe>BH | Rdt>BH | Les deux |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    n_both, n_cells = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.to_datetime(df["date"])
        bh_full = np.log(close[1:] / close[:-1])
        month = dates.dt.month.values[1:]
        is_winter = (month >= 11) | (month <= 4)
        mid_mask = midterm_mask(df["date"])[1:]
        halloween_only = is_winter & ~mid_mask
        midterm_only = mid_mask & ~is_winter
        overlap = is_winter & mid_mask

        me_bh, ret_bh = evaluate(np.ones_like(bh_full), bh_full, COST_BPS)

        for cap in CAP_GRID:
            for cut in CUT_GRID:
                pos = np.ones_like(bh_full)
                pos[halloween_only] = cap
                pos[midterm_only] = cut
                pos[overlap] = cap * cut
                me, ret = evaluate(pos, bh_full, COST_BPS)
                ok_s = me["sharpe_ann"] > me_bh["sharpe_ann"]
                ok_r = ret > ret_bh
                both = ok_s and ok_r
                n_cells += 1
                n_both += int(both)
                star = " **(pré-enr.)**" if (cap == CAP and cut == CUT) else ""
                lines.append(
                    f"| {name} | {cap}x | {cut}x{star} | {me['sharpe_ann']:+.2f} | "
                    f"{100*ret:+.1f}% | {me['max_drawdown_pct']:.1f}% | "
                    f"{'OUI' if ok_s else 'non'} | {'OUI' if ok_r else 'non'} | "
                    f"{'OUI' if both else 'non'} |"
                )

    lines += [
        "",
        f"**{n_both}/{n_cells} combinaisons (marché × CAP × CUT) battent Buy & Hold sur les DEUX jambes.**",
    ]

    out = ROOT / "results" / "nonml_halloween_midterm_multiplicative_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
