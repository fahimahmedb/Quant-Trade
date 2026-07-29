"""Backtest — Overlay vol-targeting gaté par la breadth de surperformance
des "petites capitalisations" (proxy volatilité idiosyncratique, aucune
donnée de capitalisation disponible -- limite déclarée dans
PREREG_smallcap_proxy_outperformance_breadth_overlay.md, committée avant
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
IDIO_VOL_WINDOW = 60
MOM_WINDOW = 21
MEDIAN_WINDOW = 252
MIN_LISTED = 10
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
        if len(close) > IDIO_VOL_WINDOW + MOM_WINDOW + 21:
            series[path.stem] = close
    return series


def compute_smallcap_breadth_series() -> pd.Series:
    """Renvoie Breadth_Small(t) = fraction des titres du groupe "PETIT"
    (moitie superieure par volatilite idiosyncratique glissante 60j,
    proxy de petite capitalisation) dont le rendement 21j est superieur
    a la mediane cross-sectionnelle de TOUT l'univers eligible."""
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    T, n_tickers = P.shape

    log_ret = np.log(P / P.shift(1)).values

    idio_vol = np.full((T, n_tickers), np.nan)
    for i in range(IDIO_VOL_WINDOW, T):
        window = log_ret[i - IDIO_VOL_WINDOW + 1:i + 1]
        with np.errstate(all="ignore"):
            idio_vol[i] = np.nanstd(window, axis=0, ddof=1)

    mom = np.full((T, n_tickers), np.nan)
    c_lag = np.full((T, n_tickers), np.nan)
    c_lag[MOM_WINDOW:] = close[:-MOM_WINDOW]
    with np.errstate(invalid="ignore", divide="ignore"):
        mom_raw = close / c_lag - 1.0
    mom_valid = np.isfinite(close) & np.isfinite(c_lag)
    mom = np.where(mom_valid, mom_raw, np.nan)

    breadth = np.full(T, np.nan)
    for i in range(T):
        elig = np.isfinite(idio_vol[i]) & np.isfinite(mom[i])
        n_elig = int(elig.sum())
        if n_elig < MIN_LISTED:
            continue
        idio_elig = idio_vol[i][elig]
        mom_elig = mom[i][elig]
        median_mom_all = np.median(mom_elig)
        # moitie superieure par IdioVol = groupe "petit" (proxy)
        thresh_idio = np.median(idio_elig)
        small_mask = idio_elig >= thresh_idio
        n_small = int(small_mask.sum())
        if n_small == 0:
            continue
        n_small_outperf = int((mom_elig[small_mask] > median_mom_all).sum())
        breadth[i] = n_small_outperf / n_small

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

    breadth_small = compute_smallcap_breadth_series()
    median_small = breadth_small.rolling(MEDIAN_WINDOW).median()
    gate_series = (breadth_small >= median_small)
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
        "# Résultat — Overlay vol-targeting gaté par la breadth de surperformance petites caps (proxy vol idiosyncratique) (pré-enregistré, règle renforcée niveau 1)",
        "",
        "**Limite de données assumée** : aucune capitalisation boursière disponible ; "
        "\"petite capitalisation\" est un PROXY (moitié supérieure par volatilité "
        "idiosyncratique glissante 60j), pas une mesure directe.",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si Breadth_Small(t) (fraction du groupe proxy petite cap surperformant la médiane du "
        f"marché sur 21j) ≥ sa médiane glissante {MEDIAN_WINDOW}j, sinon 1.0x. {len(bh_t)} séances "
        f"testables (échantillon restreint à la période où le signal titre-par-titre est disponible).",
        "",
        f"%j porte surperformance petites caps active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        f"Breadth surperformance moyenne (toute la période) : {100*np.nanmean(breadth_small.values):.1f}%",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté surperformance petites caps** | **{me_ov['sharpe_ann']:+.2f}** | "
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
                     "`nonml_pass_validation_battery.py smallcap_proxy_outperformance_breadth_overlay` "
                     "(stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_smallcap_proxy_outperformance_breadth_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        dates_used = dates_idx.values[1:][start:]
        np.savez(
            ROOT / "results" / "nonml_smallcap_proxy_outperformance_breadth_overlay_pnl.npz",
            pos=pos, r_asset=bh_t, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
