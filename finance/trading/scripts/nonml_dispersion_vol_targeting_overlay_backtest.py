"""Backtest — Overlay vol-targeting gaté par la dispersion cross-sectionnelle
NDX-100 (spécification pré-enregistrée dans
PREREG_dispersion_vol_targeting_overlay.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée.

NOTE (leçon du cycle #77) : la dispersion cross-sectionnelle n'est
disponible que depuis le début de l'historique des titres NDX-100
(~2021), bien plus court que l'historique de l'indice (40 ans) --
l'échantillon testable est explicitement restreint à la période où le
signal est réellement disponible, pour éviter de tester silencieusement
sur une porte désactivée par construction.
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
        if len(close) > 60:
            series[path.stem] = close
    return series


def compute_dispersion_series() -> pd.Series:
    """Renvoie Dispersion(t) = ecart-type cross-sectionnel des rendements
    log quotidiens des titres cotes au jour t (NaN si <MIN_LISTED
    titres), indexee sur le calendrier UNION des tickers."""
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    # .copy() : sous pandas >= 3 (copy-on-write) `.values` renvoie une vue en
    # lecture seule, l'affectation ci-dessous echouerait sans copie explicite.
    R = np.log(P / P.shift(1)).values.copy()
    R[0, :] = np.nan  # premier jour : pas de rendement defini

    n_listed = np.isfinite(R).sum(axis=1)
    with np.errstate(invalid="ignore"):
        dispersion = np.nanstd(R, axis=1, ddof=1)
    dispersion = np.where(n_listed >= MIN_LISTED, dispersion, np.nan)
    return pd.Series(dispersion, index=P.index)


def combined_position(close: np.ndarray, r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens (longueur T-1). gate_aligned = porte
    dispersion alignee sur close (longueur T, booleenne). Renvoie la
    position pour chaque rendement de r."""
    gate_r = gate_aligned[:-1]  # meme convention causale que #47/#57/#77

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

    dispersion = compute_dispersion_series()
    median_dispersion = dispersion.rolling(MEDIAN_WINDOW).median()
    gate_series = (dispersion >= median_dispersion)
    # NaN (avant la fenetre mediane) -> porte inactive par defaut
    gate_series_filled = gate_series.fillna(False)

    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series_filled.reindex(dates_idx.values, method="ffill").fillna(False).values.astype(bool)

    pos_full = combined_position(close, bh_full, gate_aligned)

    # restreint l'echantillon a la periode ou le signal dispersion est
    # reellement disponible (leçon du #77) : premier indice non-NaN dans
    # gate_aligned_raw (avant le fillna/ffill par defaut a False)
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

    dates_pnl = dates_idx.values[1:][start:]
    np.savez(ROOT / "results" / "nonml_dispersion_vol_targeting_overlay_pnl.npz",
             pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    gate_active = (pos > 1.0)
    lines = [
        "# Résultat — Overlay vol-targeting gaté par la dispersion cross-sectionnelle NDX-100 (pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si Dispersion(t) ≥ sa médiane glissante {MEDIAN_WINDOW}j, sinon 1.0x. {len(bh_t)} séances testables "
        f"(échantillon restreint à la période où la dispersion cross-sectionnelle est disponible).",
        "",
        f"%j porte dispersion active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté dispersion** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_dispersion_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
