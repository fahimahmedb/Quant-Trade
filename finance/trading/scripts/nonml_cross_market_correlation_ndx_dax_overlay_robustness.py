"""Robustesse — cycle #193 (corrélation cross-marché NDX-DAX), grille
jointe ±20% sur CUT (plancher défensif) et CORR_WINDOW (fenêtre de
corrélation), les deux paramètres non centraux au critère de succès (le
critère porte sur le tercile expanding, pas sur leur valeur exacte).
Ce n'est PAS un retuning : le verdict reste celui du point
pré-enregistré (CUT=0.5, CORR_WINDOW=60).
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
from nonml_cross_market_correlation_ndx_dax_overlay_backtest import (  # noqa: E402
    COST_BPS, CUT, CORR_WINDOW, TERCILE_PCT, MARKETS, log_ret_series,
)

CUT_GRID = [round(CUT * 0.8, 2), CUT, round(CUT * 1.2, 2)]
WINDOW_GRID = [int(round(CORR_WINDOW * 0.8)), CORR_WINDOW, int(round(CORR_WINDOW * 1.2))]


def build_corr_series_window(window: int) -> pd.Series:
    ndx_r = log_ret_series("nasdaq100_daily.txt")
    dax_r = log_ret_series("dax_daily.txt")
    common = ndx_r.index.intersection(dax_r.index)
    ndx_c = ndx_r.reindex(common)
    dax_c = dax_r.reindex(common)
    corr = ndx_c.rolling(window).corr(dax_c)
    return corr.dropna()


def load_corr_lag(dates: pd.DatetimeIndex, corr_series: pd.Series) -> np.ndarray:
    y = corr_series.reindex(dates, method="ffill")
    return y.shift(1).values


def expanding_tercile_cut_high(corr: np.ndarray, cut: float) -> np.ndarray:
    T = len(corr)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(corr)))
    for t in range(start, T):
        if not np.isfinite(corr[t]):
            continue
        hist = corr[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, 100.0 - TERCILE_PCT)
        pos[t] = cut if corr[t] >= thresh else 1.0
    return pos


def evaluate(pos, bh_full, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * bh_full - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.exp(pnl.sum()) - 1.0)
    return me, ret


def main():
    lines = [
        "# Robustesse — cycle #193, grille jointe ±20% sur CUT et CORR_WINDOW",
        "",
        f"Point pré-enregistré : CUT={CUT}x, CORR_WINDOW={CORR_WINDOW}j. "
        f"Grille CUT : {{{', '.join(f'{c}x' for c in CUT_GRID)}}}. "
        f"Grille CORR_WINDOW : {{{', '.join(f'{w}j' for w in WINDOW_GRID)}}}.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré (0.5x / 60j) quelle que soit la lecture de ce tableau.",
        "",
        "| Marché | CUT | CORR_WINDOW | Sharpe | Rendement total | MDD | Sharpe>BH | Rdt>BH | Les deux |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    n_both_total, n_cells_total = 0, 0

    corr_cache = {w: build_corr_series_window(w) for w in WINDOW_GRID}

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        me_bh, ret_bh = evaluate(np.ones_like(bh_full), bh_full, COST_BPS)

        for window in WINDOW_GRID:
            corr_lag_full = load_corr_lag(dates, corr_cache[window])[1:]
            for cut in CUT_GRID:
                pos_full = expanding_tercile_cut_high(corr_lag_full, cut)
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

                marker = " (point pré-enregistré)" if (cut == CUT and window == CORR_WINDOW) else ""
                lines.append(
                    f"| {name}{marker} | {cut}x | {window}j | {me['sharpe_ann']:+.2f} | "
                    f"{100*ret:+.1f}% | {me['max_drawdown_pct']:.1f}% | "
                    f"{'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} | "
                    f"{'OUI' if both_ok else 'non'} |"
                )

    lines.append("")
    lines.append(f"**{n_both_total}/{n_cells_total} cellules de la grille battent Buy&Hold "
                 f"sur les deux jambes (Sharpe ET rendement).**")

    out = ROOT / "results" / "nonml_cross_market_correlation_ndx_dax_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
