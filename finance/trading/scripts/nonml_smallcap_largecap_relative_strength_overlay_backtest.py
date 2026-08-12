"""Backtest — Force relative Russell 2000 vs S&P 500, overlay défensif
(spécification pré-enregistrée dans
PREREG_smallcap_largecap_relative_strength_overlay.md, committée avant
ce script). n_trials=1, aucune dépendance ML. Règle de succès renforcée
sur 5 marchés (≥4/5).

Réutilise la fenêtre 21j (mois), l'alignement causal ffill+shift(1) déjà
validé aux #175/#178/#186/#187/#191 (adapté ici à un signal dérivé de
deux séries OHLC au lieu d'une série de taux), CUT=0,5 et la technique
de tercile expanding déjà établie aux #169/#177/#183/#191, Règle 7.
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
CUT = 0.5
RET_WINDOW = 21
TERCILE_PCT = 100.0 / 3.0

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def rolling_ret21_series(fname: str) -> pd.Series:
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    quality_report(df)
    close = df["close"].values
    dates = pd.DatetimeIndex(df["date"].values)
    ret21 = np.full(len(close), np.nan)
    ret21[RET_WINDOW:] = np.log(close[RET_WINDOW:] / close[:-RET_WINDOW])
    return pd.Series(ret21, index=dates)


def load_rs_lag(dates: pd.DatetimeIndex, rs_series: pd.Series) -> np.ndarray:
    y = rs_series.reindex(dates, method="ffill")
    return y.shift(1).values


def expanding_tercile_cut(rs: np.ndarray) -> np.ndarray:
    T = len(rs)
    pos = np.full(T, np.nan)
    start = int(np.argmax(np.isfinite(rs)))
    for t in range(start, T):
        if not np.isfinite(rs[t]):
            continue
        hist = rs[start:t + 1]
        hist = hist[np.isfinite(hist)]
        thresh = np.percentile(hist, TERCILE_PCT)
        pos[t] = CUT if rs[t] <= thresh else 1.0
    return pos


def main():
    ret21_russell = rolling_ret21_series("russell2000_daily.txt")
    ret21_sp500 = rolling_ret21_series("sp500_daily.txt")
    common = ret21_russell.index.union(ret21_sp500.index)
    rs_series = (ret21_russell.reindex(common) - ret21_sp500.reindex(common)).dropna()

    lines = [
        "# Résultat — Force relative Russell 2000 vs S&P 500, overlay défensif (pré-enregistré)",
        "",
        f"`position(t) = {CUT}x` si RS(t)=ret21_Russell(t)-ret21_SP500(t) est dans son tercile "
        f"expanding le plus bas, `1.0x` sinon. Design purement défensif. Coûts {COST_BPS:.0f} bps.",
        "",
        "| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    n_markets, n_success = 0, 0

    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        dates = pd.DatetimeIndex(df["date"].values)
        bh_full = np.log(close[1:] / close[:-1])

        rs_lag_full = load_rs_lag(dates, rs_series)
        rs_lag = rs_lag_full[1:]
        pos_full = expanding_tercile_cut(rs_lag)

        start = int(np.argmax(np.isfinite(pos_full)))
        pos = pos_full[start:]
        bh_t = bh_full[start:]
        assert len(pos) == len(bh_t)
        assert np.isfinite(pos).all()

        frac_cut = float((pos == CUT).mean())

        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
        pnl_bh = bh_t.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = np.exp(pnl_bh.sum()) - 1.0
        ret_ov = np.exp(pnl_ov.sum()) - 1.0

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        n_markets += 1
        n_success += int(sharpe_ok and ret_ok)

        lines.append(
            f"| {name} | {len(bh_t)} | {100*frac_cut:.1f}% | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if sharpe_ok else 'non'} | {'OUI' if ret_ok else 'non'} |"
        )

    verdict = n_success >= 4
    lines.append("")
    lines.append(f"**{n_success}/{n_markets} marchés où l'overlay bat Buy&Hold en Sharpe ET rendement "
                 f"(critère renforcé : ≥4/5).**")
    lines.append("")
    lines.append(f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré "
                 f"{'atteint' if verdict else 'NON atteint'}.**")

    out = ROOT / "results" / "nonml_smallcap_largecap_relative_strength_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
