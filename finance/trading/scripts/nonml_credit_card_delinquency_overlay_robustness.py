"""Robustesse — cycle #284 (taux de défaut cartes de crédit), perturbation
±20% du plancher CUT=0.5x, seul paramètre non central au critère de
succès (le critère porte sur le tercile expanding, pas sur la valeur
exacte du plancher). Ce n'est PAS un retuning : le verdict reste celui
du point pré-enregistré 0.5x. Grille réutilisée telle quelle du #200
(Règle 7).
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
from nonml_credit_card_delinquency_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, MARKETS, load_delinquency_lag, build_delinquency_series, TERCILE_PCT,
)

CUT_GRID = [round(CUT * 0.8, 2), CUT, round(CUT * 1.2, 2)]


def expanding_tercile_cut_high(level: np.ndarray, cut: float) -> np.ndarray:
    T = len(level)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(level)))
    for t in range(start, T):
        if not np.isfinite(level[t]):
            continue
        hist = level[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, 100.0 - TERCILE_PCT)
        pos[t] = cut if level[t] >= thresh else 1.0
    return pos


def evaluate(pos, bh_full, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * bh_full - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.exp(pnl.sum()) - 1.0)
    return me, ret


def main():
    delinq_series = build_delinquency_series()

    lines = [
        "# Robustesse — cycle #284, perturbation ±20% du plancher CUT",
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
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        delinq_lag_full = load_delinquency_lag(dates, delinq_series)[1:]

        for cut in CUT_GRID:
            pos_full = expanding_tercile_cut_high(delinq_lag_full, cut)
            start = int(np.argmax(np.isfinite(pos_full)))
            pos = pos_full[start:]
            bh_t = bh_full[start:]

            me, ret = evaluate(pos, bh_t, COST_BPS)
            me_bh_local, ret_bh_local = evaluate(np.ones_like(bh_t), bh_t, COST_BPS)

            sharpe_ok = me["sharpe_ann"] > me_bh_local["sharpe_ann"]
            ret_ok = ret > ret_bh_local
            both_ok = sharpe_ok and ret_ok
            n_cells_total += 1
            n_both_total += int(both_ok)

            marker = " (point pré-enregistré)" if cut == CUT else ""
            lines.append(
                f"| {name}{marker} | {cut}x | {me['sharpe_ann']:+.2f} | "
                f"{100*ret:+.1f}% | {me['max_drawdown_pct']:.1f}% | "
                f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                f"{'OUI' if both_ok else 'non'} |"
            )

    lines.append("")
    lines.append(f"**{n_both_total}/{n_cells_total} cellules de la grille battent Buy&Hold "
                 f"sur les deux jambes (Sharpe ET rendement).**")

    out = ROOT / "results" / "nonml_credit_card_delinquency_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
