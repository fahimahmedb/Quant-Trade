"""Backtest — Overlay vol-targeting gaté par le spread décile de
momentum (queue de distribution, distinct du #100 qui utilise
l'écart-type global) (spécification pré-enregistrée dans
PREREG_momentum_decile_spread_vol_targeting_overlay.md, committée avant
ce script). n_trials=1, aucune dépendance ML. Règle de succès renforcée
niveau 1 -- SI PASS, ce résultat n'est PAS final, voir Règle 9
(`scripts/nonml_pass_validation_battery.py`).
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
LOOKBACK = 252
SKIP = 21
MEDIAN_WINDOW = 252
MIN_LISTED = 10
DECILE_FRACTION = 0.10
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
        if len(close) > LOOKBACK + 21:
            series[path.stem] = close
    return series


def _momentum_matrix():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    T, n_tickers = P.shape

    c_skip = np.full((T, n_tickers), np.nan)
    c_lookback = np.full((T, n_tickers), np.nan)
    c_skip[SKIP:] = close[:-SKIP]
    c_lookback[LOOKBACK:] = close[:-LOOKBACK]

    with np.errstate(invalid="ignore", divide="ignore"):
        momentum = c_skip / c_lookback - 1.0
    momentum_valid = np.isfinite(c_skip) & np.isfinite(c_lookback)
    momentum = np.where(momentum_valid, momentum, np.nan)
    return momentum, P.index


def compute_decile_spread_series() -> pd.Series:
    """Renvoie Spread(t) = moyenne(decile_size titres au momentum le
    plus FORT) - moyenne(decile_size titres au momentum le plus
    FAIBLE), decile_size = round(10% des titres eligibles), NaN si
    <MIN_LISTED titres eligibles. Mesure de QUEUE, distincte de
    l'ecart-type global (#100)."""
    momentum, idx = _momentum_matrix()
    T = momentum.shape[0]
    spread = np.full(T, np.nan)
    for i in range(T):
        row = momentum[i]
        row = row[np.isfinite(row)]
        n = len(row)
        if n < MIN_LISTED:
            continue
        decile_size = max(1, round(n * DECILE_FRACTION))
        row_sorted = np.sort(row)
        top = row_sorted[-decile_size:]
        bottom = row_sorted[:decile_size]
        spread[i] = top.mean() - bottom.mean()
    return pd.Series(spread, index=idx)


def combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    gate_r = gate_aligned[:-1]
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        vt_exposure = TARGET_VOL_ANNUAL / vol_lagged
    vt_exposure = np.clip(vt_exposure, 1.0, CAP)
    vt_exposure = np.nan_to_num(vt_exposure, nan=1.0)
    pos = np.where(gate_r, vt_exposure, 1.0)
    return np.nan_to_num(pos, nan=1.0)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    spread = compute_decile_spread_series()
    median_spread = spread.rolling(MEDIAN_WINDOW).median()
    gate_series = (spread >= median_spread)
    gate_series_filled = gate_series.fillna(False)

    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series_filled.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    pos_full = combined_position(bh_full, gate_aligned)

    valid_mask = gate_aligned_raw.notna().values
    first_valid = int(np.argmax(valid_mask)) if valid_mask.any() else len(valid_mask)
    start = max(first_valid, VOL_WINDOW)

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
        "# Résultat — Overlay vol-targeting gaté par le spread décile de momentum (pré-enregistré, règle renforcée niveau 1)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si Spread décile momentum(t) (D10-D1, queues de distribution) ≥ sa médiane glissante "
        f"{MEDIAN_WINDOW}j, sinon 1.0x. {len(bh_t)} séances testables (échantillon restreint à la "
        f"période où le signal titre-par-titre est disponible).",
        "",
        f"%j porte spread décile active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        f"Spread décile moyen (toute la période) : {100*np.nanmean(spread.values):.1f} pts de %",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté spread décile** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS (niveau 1)' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py momentum_decile_spread_vol_targeting_overlay` "
                     "(stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_momentum_decile_spread_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        dates_used = dates_idx.values[1:][start:]
        np.savez(
            ROOT / "results" / "nonml_momentum_decile_spread_vol_targeting_overlay_pnl.npz",
            pos=pos, r_asset=bh_t, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
