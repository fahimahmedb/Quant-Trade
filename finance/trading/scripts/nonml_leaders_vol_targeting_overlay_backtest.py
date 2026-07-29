"""Backtest — Leaders 52-semaines + overlay de vol-targeting continu
(spécification pré-enregistrée dans
PREREG_leaders_vol_targeting_overlay.md, committée avant ce script).
Combine les cycles #4 et #43. n_trials=1, aucune dépendance ML. Règle de
succès renforcée -- référence = leaders 1.0x (cycle #4), pas Buy&Hold.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

PRICES_DIR = ROOT / "data" / "pead" / "prices"
LOOKBACK = 252
REBAL_EVERY = 21
COST_BPS = 5.0
TERCILE = 1.0 / 3.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.15
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
        if len(close) > LOOKBACK + REBAL_EVERY:
            series[path.stem] = close
    return series


def vol_target_exposure(r: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens du PORTEFEUILLE (pas d'un titre).
    Renvoie l'exposition continue clip(vol_cible / vol_realisee(t-1), 0,
    CAP), causale (vol connue a t-1, appliquee au rendement t). Identique
    au mecanisme du #43."""
    vol_ann = pd.Series(r).rolling(VOL_WINDOW).std().values * ANNUALIZATION
    vol_lagged = np.roll(vol_ann, 1)
    vol_lagged[0] = np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        exposure = TARGET_VOL_ANNUAL / vol_lagged
    exposure = np.clip(exposure, 0.0, CAP)
    exposure = np.nan_to_num(exposure, nan=1.0)
    return exposure


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
    R = np.nan_to_num(np.log(P / P.shift(1)).values, nan=0.0)
    R[0, :] = 0.0

    rolling_max = np.full((T, n_tickers), np.nan)
    has_full = np.zeros((T, n_tickers), dtype=bool)
    for i in range(LOOKBACK, T):
        window = close[i - LOOKBACK + 1:i + 1]
        has_full[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_max[i] = np.nanmax(window, axis=0)
    ratio = np.where(has_full, close / rolling_max, np.nan)

    n_top = max(1, int(round(n_tickers * TERCILE)))
    weights_leaders = np.zeros((T, n_tickers))
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        r = ratio[t]
        elig = np.where(np.isfinite(r))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-r[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_leaders[t:end] = w

    # rendement quotidien du portefeuille Leaders LUI-MEME (avant overlay), pour le vol-targeting
    pnl_leaders_raw = (weights_leaders * R).sum(axis=1)
    exposure = vol_target_exposure(pnl_leaders_raw)

    weights_base = weights_leaders
    weights_lev = weights_leaders * exposure[:, None]

    start = LOOKBACK + VOL_WINDOW
    pnl_base = (weights_base[start:] * R[start:]).sum(axis=1)
    pnl_lev = (weights_lev[start:] * R[start:]).sum(axis=1)

    turn_base = np.abs(np.diff(weights_base[start:], axis=0, prepend=weights_base[start:start+1])).sum(axis=1) / 2.0
    turn_lev = np.abs(np.diff(weights_lev[start:], axis=0, prepend=weights_lev[start:start+1])).sum(axis=1) / 2.0
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
        "# Résultat — Leaders 52-semaines + overlay de vol-targeting continu (pré-enregistré, combinaison #4+#43)",
        "",
        f"Référence = portefeuille leaders 1.0x (cycle #4), PAS Buy&Hold. "
        f"{T - start} séances testables ({P.index[start].date()} → {P.index[-1].date()}). "
        f"Exposition moyenne = {exposure[start:].mean():.2f}x (vol cible {TARGET_VOL_ANNUAL:.0%}, "
        f"vol réalisée du portefeuille Leaders lui-même).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Leaders 1.0x (référence, cycle #4) | {me_base['sharpe_ann']:+.2f} | {100*ret_base:+.1f}% | "
        f"{me_base['max_drawdown_pct']:.1f}% |",
        f"| **Leaders + overlay vol-targeting** | **{me_lev['sharpe_ann']:+.2f}** | "
        f"**{100*ret_lev:+.1f}%** | {me_lev['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > référence : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > référence : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_leaders_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
