"""Robustesse — cycle #182, perturbation ±20% du CAP=2.0x (seul paramètre
numérique du mécanisme, les deux masques calendaires sont des règles
fixes sans fenêtre à perturber). Perturbation, PAS retuning : le verdict
du cycle reste celui du point pré-enregistré CAP=2.0x.
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
from nonml_presidential_cycle_overlay_backtest import preelection_mask  # noqa: E402
from nonml_halloween_preelection_and_overlay_backtest import CAP, COST_BPS, MARKETS  # noqa: E402

CAP_GRID = [round(CAP * 0.8, 2), CAP, round(CAP * 1.2, 2)]


def evaluate(pos, bh_full, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * bh_full - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.exp(pnl.sum()) - 1.0)
    return me, ret


def main():
    lines = [
        "# Robustesse — cycle #182, perturbation ±20% du CAP",
        "",
        f"Point pré-enregistré : CAP = {CAP}x. Grille : {{{', '.join(f'{c}x' for c in CAP_GRID)}}}.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré (2.0x) quelle que soit la lecture de ce tableau.",
        "",
        "| Marché | CAP | Sharpe | Rendement total | MDD | Sharpe>BH | Rdt>BH | Les deux |",
        "|---|---|---|---|---|---|---|---|",
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
        pre_mask = preelection_mask(df["date"])[1:]
        mask = is_winter & pre_mask

        me_bh, ret_bh = evaluate(np.ones_like(bh_full), bh_full, COST_BPS)

        for cap in CAP_GRID:
            pos = np.where(mask, cap, 1.0)
            me, ret = evaluate(pos, bh_full, COST_BPS)
            ok_s = me["sharpe_ann"] > me_bh["sharpe_ann"]
            ok_r = ret > ret_bh
            both = ok_s and ok_r
            n_cells += 1
            n_both += int(both)
            star = " **(pré-enregistré)**" if cap == CAP else ""
            lines.append(
                f"| {name} | {cap}x{star} | {me['sharpe_ann']:+.2f} | {100*ret:+.1f}% | "
                f"{me['max_drawdown_pct']:.1f}% | {'OUI' if ok_s else 'non'} | "
                f"{'OUI' if ok_r else 'non'} | {'OUI' if both else 'non'} |"
            )

    lines += [
        "",
        f"**{n_both}/{n_cells} combinaisons (marché × CAP) battent Buy & Hold sur les DEUX jambes.**",
    ]

    out = ROOT / "results" / "nonml_halloween_preelection_and_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
