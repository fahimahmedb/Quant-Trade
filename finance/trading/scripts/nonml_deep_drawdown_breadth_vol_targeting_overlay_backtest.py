"""Backtest — Overlay vol-targeting gaté par la breadth de drawdown
PROFOND (seuil ABSOLU -20%, distinct du #89 relatif) (spécification
pré-enregistrée dans PREREG_deep_drawdown_breadth_vol_targeting_overlay.md,
committée avant ce script). n_trials=1, aucune dépendance ML. Règle de
succès renforcée niveau 1 -- SI PASS, ce résultat n'est PAS final, voir
Règle 9 (`scripts/nonml_pass_validation_battery.py`).
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
DD_THRESHOLD = 0.80  # close <= 0.80 * plus haut glissant 252j => drawdown >= 20%
MEDIAN_WINDOW = 252
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


def compute_deep_drawdown_breadth_series() -> pd.Series:
    """Renvoie Breadth_DD(t) = fraction des titres COTES ce jour-la (prix
    du jour fini) dont le prix est >=20% sous leur plus haut glissant
    252j (fenetre PLEINE requise pour marquer un titre "en drawdown
    profond"), indexee sur le calendrier UNION des tickers. Denominateur
    = tous les titres listes ce jour-la (meme convention que #89/#94/#96/
    #97), pas seulement ceux avec fenetre complete."""
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

    rolling_high = np.full((T, n_tickers), np.nan)
    has_full = np.zeros((T, n_tickers), dtype=bool)
    for i in range(INDEX_LOOKBACK, T):
        window = close[i - INDEX_LOOKBACK + 1:i + 1]
        has_full[i] = np.isfinite(window).all(axis=0)
        with np.errstate(all="ignore"):
            rolling_high[i] = np.nanmax(window, axis=0)
    deep_dd = np.where(has_full, close <= DD_THRESHOLD * rolling_high, False)

    n_listed = exists.sum(axis=1)
    n_deep_dd = (deep_dd & exists).sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        breadth = np.where(n_listed > 0, n_deep_dd / n_listed, np.nan)

    return pd.Series(breadth, index=P.index)


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

    breadth_dd = compute_deep_drawdown_breadth_series()
    median_dd = breadth_dd.rolling(MEDIAN_WINDOW).median()
    gate_series = (breadth_dd >= median_dd)
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
        "# Résultat — Overlay vol-targeting gaté par la breadth de drawdown profond, seuil absolu -20% (pré-enregistré, règle renforcée niveau 1)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si Breadth_DD(t) (fraction des titres NDX-100 ≥20% sous leur plus haut glissant 252j) "
        f"≥ sa médiane glissante {MEDIAN_WINDOW}j, sinon 1.0x. {len(bh_t)} séances testables "
        f"(échantillon restreint à la période où la breadth titre-par-titre est disponible).",
        "",
        f"%j porte drawdown profond active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        f"Breadth drawdown profond moyenne (toute la période) : {100*np.nanmean(breadth_dd.values):.1f}%",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté drawdown profond** | **{me_ov['sharpe_ann']:+.2f}** | "
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
                     "`nonml_pass_validation_battery.py deep_drawdown_breadth_vol_targeting_overlay` "
                     "(stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_deep_drawdown_breadth_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        dates_used = dates_idx.values[1:][start:]
        np.savez(
            ROOT / "results" / "nonml_deep_drawdown_breadth_vol_targeting_overlay_pnl.npz",
            pos=pos, r_asset=bh_t, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
