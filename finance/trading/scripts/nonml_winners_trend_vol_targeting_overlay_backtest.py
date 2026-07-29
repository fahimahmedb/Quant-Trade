"""Backtest — Winners momentum court terme + overlay combiné tendance +
vol-targeting (spécification pré-enregistrée dans
PREREG_winners_trend_vol_targeting_overlay.md, committée avant ce
script). Combine les cycles #14 et #47. n_trials=1, aucune dépendance
ML. Règle de succès renforcée -- référence = Winners 1.0x (cycle #14),
pas Buy&Hold. **Prudence forte héritée du #14.**
"""
import json
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

PRICES_DIR = ROOT / "data" / "pead" / "prices"
SIGNAL_WINDOW = 5
REBAL_EVERY = 5
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAP = 2.0
INDEX_LOOKBACK = 252
INDEX_THRESHOLD = 0.95
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def load_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > SIGNAL_WINDOW + REBAL_EVERY + 10:
            series[path.stem] = close
    return series


def index_trend_series() -> pd.Series:
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    rolling_max = pd.Series(close).rolling(INDEX_LOOKBACK).max().values
    near_high = close >= INDEX_THRESHOLD * rolling_max
    dates = pd.to_datetime(df["date"]).values
    return pd.Series(near_high, index=dates)


def main():
    series = load_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n_tickers = P.shape
    close = P.values
    exists = np.isfinite(close)
    R = np.log(P / P.shift(1)).values
    R[0, :] = 0.0
    R_safe = np.nan_to_num(R, nan=0.0)

    signal = np.full((T, n_tickers), np.nan)
    for i in range(SIGNAL_WINDOW, T):
        with np.errstate(all="ignore", invalid="ignore"):
            signal[i] = close[i] / close[i - SIGNAL_WINDOW] - 1.0
        signal[i, ~(exists[i] & exists[i - SIGNAL_WINDOW])] = np.nan

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_winners = np.zeros((T, n_tickers))
    start = SIGNAL_WINDOW
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        s = signal[t]
        elig = np.where(np.isfinite(s))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-s[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_winners[t:end] = w

    trend = index_trend_series()
    trend_aligned = trend.reindex(P.index, method="ffill").fillna(False).values.astype(bool)

    pnl_winners_raw = (weights_winners * R_safe).sum(axis=1)
    vol_ann = pd.Series(pnl_winners_raw).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    exposure = np.where(trend_aligned, vt_exposure, 1.0)

    weights_base = weights_winners
    weights_lev = weights_winners * exposure[:, None]

    start2 = max(start, VOL_WINDOW)
    pnl_base = (weights_base[start2:] * R_safe[start2:]).sum(axis=1)
    pnl_lev = (weights_lev[start2:] * R_safe[start2:]).sum(axis=1)

    turn_base = np.abs(np.diff(weights_base[start2:], axis=0, prepend=weights_base[start2:start2+1])).sum(axis=1) / 2.0
    turn_lev = np.abs(np.diff(weights_lev[start2:], axis=0, prepend=weights_lev[start2:start2+1])).sum(axis=1) / 2.0
    pnl_base = pnl_base - turn_base * (COST_BPS / 1e4)
    pnl_lev = pnl_lev - turn_lev * (COST_BPS / 1e4)

    me_base = trading_metrics(pnl_base)
    me_lev = trading_metrics(pnl_lev)
    ret_base = np.cumprod(1.0 + pnl_base)[-1] - 1.0
    ret_lev = np.cumprod(1.0 + pnl_lev)[-1] - 1.0

    sharpe_ok = me_lev["sharpe_ann"] > me_base["sharpe_ann"]
    ret_ok = ret_lev > ret_base
    verdict = sharpe_ok and ret_ok

    lines = [
        "# Résultat — Winners momentum court terme + overlay combiné tendance + vol-targeting (pré-enregistré, combinaison #14+#47)",
        "",
        f"Référence = portefeuille Winners 1.0x (cycle #14), PAS Buy&Hold. "
        f"{T - start2} séances testables ({P.index[start2].date()} → {P.index[-1].date()}). "
        f"Overlay actif {100*trend_aligned[start2:].mean():.1f}% du temps en tendance haussière.",
        "",
        "**Prudence forte héritée du #14** : le portefeuille Winners affiche un edge "
        "extrême potentiellement propre au bull market IA/semiconducteurs 2021-2026, "
        "généralisabilité non garantie.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Winners 1.0x (référence, cycle #14) | {me_base['sharpe_ann']:+.2f} | {100*ret_base:+.1f}% | "
        f"{me_base['max_drawdown_pct']:.1f}% |",
        f"| **Winners + overlay tendance+vol-targeting** | **{me_lev['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lev:+.1f}%** | {me_lev['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_winners_trend_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
