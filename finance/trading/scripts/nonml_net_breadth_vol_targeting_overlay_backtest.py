"""Backtest — Overlay vol-targeting gaté par la breadth NETTE
(hauts - bas) NDX-100 (spécification pré-enregistrée dans
PREREG_net_breadth_vol_targeting_overlay.md, committée avant ce
script). Combine #77 (proximité haut) et #89 (proximité bas) en un seul
signal net. n_trials=1, aucune dépendance ML. Règle de succès renforcée.
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
INDEX_LOOKBACK = 252
INDEX_THRESHOLD_HIGH = 0.95
INDEX_THRESHOLD_LOW = 1.05
COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def load_all_prices():
    series = {}
    for path in sorted(PRICES_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > INDEX_LOOKBACK + 21:
            series[path.stem] = close
    return series


def compute_net_breadth_series() -> pd.Series:
    """Renvoie Breadth nette(t) = (n_proche_haut(t) - n_proche_bas(t)) /
    n_cotes(t), indexee sur le calendrier UNION des tickers."""
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    T, n_tickers = P.shape
    exists = np.isfinite(close)

    rolling_max = np.full((T, n_tickers), np.nan)
    rolling_min = np.full((T, n_tickers), np.nan)
    has_full = np.zeros((T, n_tickers), dtype=bool)
    for i in range(INDEX_LOOKBACK, T):
        window = close[i - INDEX_LOOKBACK + 1:i + 1]
        has_full[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_max[i] = np.nanmax(window, axis=0)
            rolling_min[i] = np.nanmin(window, axis=0)

    near_high = np.where(has_full, close >= INDEX_THRESHOLD_HIGH * rolling_max, False)
    near_low = np.where(has_full, close <= INDEX_THRESHOLD_LOW * rolling_min, False)

    n_listed = exists.sum(axis=1)
    n_near_high = (near_high & exists).sum(axis=1)
    n_near_low = (near_low & exists).sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        breadth_net = np.where(n_listed > 0, (n_near_high - n_near_low) / n_listed, np.nan)

    return pd.Series(breadth_net, index=P.index)


def combined_position(close: np.ndarray, r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens (longueur T-1). gate_aligned = porte
    breadth nette alignee sur close (longueur T, booleenne). Renvoie la
    position pour chaque rendement de r."""
    gate_r = gate_aligned[:-1]  # meme convention causale que #47/#57/#77/#89/#90/#94/#96

    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)

    pos = np.where(gate_r, vt_exposure, 1.0)
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    breadth_net = compute_net_breadth_series()
    breadth_aligned_raw = breadth_net.reindex(dates_idx.values, method="ffill").values

    gate_aligned = np.where(np.isnan(breadth_aligned_raw), False, breadth_aligned_raw > 0.0)
    pos_full = combined_position(close, bh_full, gate_aligned)

    first_valid = int(np.argmax(~np.isnan(breadth_aligned_raw)))
    start = max(first_valid, INDEX_LOOKBACK, VOL_WINDOW)
    bh_t = bh_full[start:]
    pos = pos_full[start:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * bh_t - turn * (COST_BPS / 1e4)
    pnl_bh = bh_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok

    gate_active = (pos > 1.0)
    lines = [
        "# Résultat — Overlay vol-targeting gaté par la breadth nette hauts-bas NDX-100 (pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si Breadth nette(t) > 0 (plus de titres proches de leur plus haut que de leur plus bas 252j), "
        f"sinon 1.0x. {len(bh_t)} séances testables.",
        "",
        f"%j porte breadth nette active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        f"Breadth nette moyenne (toute la période) : {100*np.nanmean(breadth_net.values):+.1f}pts",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté breadth nette** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_net_breadth_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
