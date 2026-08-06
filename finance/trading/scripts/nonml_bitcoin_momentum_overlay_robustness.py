"""Robustesse — cycle #344 (momentum du Bitcoin), grille jointe ±20%
sur CUT (plancher défensif) et RET_WINDOW (fenêtre de momentum), les
deux paramètres non centraux au critère de succès (le critère porte
sur le tercile expanding, pas sur leur valeur exacte). Ce n'est PAS un
retuning : le verdict reste celui du point pré-enregistré (CUT=0.5,
RET_WINDOW=21).
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
from nonml_dollar_strength_overlay_backtest import COST_BPS, CUT, MARKETS, RET_WINDOW  # noqa: E402
from nonml_bitcoin_momentum_overlay_backtest import load_btc_series  # noqa: E402

TERCILE_PCT = 100.0 / 3.0
CUT_GRID = [round(CUT * 0.8, 2), CUT, round(CUT * 1.2, 2)]
WINDOW_GRID = [int(round(RET_WINDOW * 0.8)), RET_WINDOW, int(round(RET_WINDOW * 1.2))]


def load_btc_mom_lag_window(dates: pd.DatetimeIndex, btc_series: pd.Series, window: int) -> np.ndarray:
    btc_aligned = btc_series.reindex(dates, method="ffill")
    btc_vals = btc_aligned.values
    mom = np.full(len(btc_vals), np.nan)
    mom[window:] = np.log(btc_vals[window:] / btc_vals[:-window])
    mom_series = pd.Series(mom, index=dates)
    return mom_series.shift(1).values


def expanding_tercile_cut_low(mom: np.ndarray, cut: float) -> np.ndarray:
    T = len(mom)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(mom)))
    for t in range(start, T):
        if not np.isfinite(mom[t]):
            continue
        hist = mom[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, TERCILE_PCT)
        pos[t] = cut if mom[t] <= thresh else 1.0
    return pos


def evaluate(pos, bh_full, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * bh_full - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.cumprod(1.0 + pnl)[-1] - 1.0)
    return me, ret


def main():
    lines = [
        "# Robustesse — cycle #344 (momentum du Bitcoin), grille jointe ±20% sur CUT et RET_WINDOW",
        "",
        f"Point pré-enregistré : CUT={CUT}x, RET_WINDOW={RET_WINDOW}j. "
        f"Grille CUT : {{{', '.join(f'{c}x' for c in CUT_GRID)}}}. "
        f"Grille RET_WINDOW : {{{', '.join(f'{w}j' for w in WINDOW_GRID)}}}.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré (0.5x / 21j) quelle que soit la lecture de ce tableau.",
        "",
        "| Marché | CUT | RET_WINDOW | Sharpe | Rendement total | MDD | Sharpe>BH | Rdt>BH | Les deux |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    n_both_total, n_cells_total = 0, 0

    btc_series = load_btc_series()

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        for window in WINDOW_GRID:
            mom_lag_full = load_btc_mom_lag_window(dates, btc_series, window)[1:]
            for cut in CUT_GRID:
                pos_full = expanding_tercile_cut_low(mom_lag_full, cut)
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

                marker = " (point pré-enregistré)" if (cut == CUT and window == RET_WINDOW) else ""
                lines.append(
                    f"| {name}{marker} | {cut}x | {window}j | {me['sharpe_ann']:+.2f} | "
                    f"{100*ret:+.1f}% | {me['max_drawdown_pct']:.1f}% | "
                    f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                    f"{'OUI' if both_ok else 'non'} |"
                )

    lines.append("")
    lines.append(f"**{n_both_total}/{n_cells_total} cellules de la grille battent Buy&Hold "
                 f"sur les deux jambes (Sharpe ET rendement).**")

    out = ROOT / "results" / "nonml_bitcoin_momentum_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
