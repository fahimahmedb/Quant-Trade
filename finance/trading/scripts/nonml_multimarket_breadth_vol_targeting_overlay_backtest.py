"""Backtest — Overlay vol-targeting gaté par la confirmation
multi-marché ÉLARGIE (5 marchés) sur NDX (spécification pré-enregistrée
dans PREREG_multimarket_breadth_vol_targeting_overlay.md, committée
avant ce script). n_trials=1, aucune dépendance ML. Règle de succès
renforcée.
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

SMA_WINDOW = 200
BREADTH_THRESHOLD = 0.6
COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)

MARKETS = {
    "Composite (5 ans)": "nasdaq_composite_daily.txt",
    "NDX (40 ans)": "nasdaq100_daily.txt",
    "Russell 2000": "russell2000_daily.txt",
    "S&P 500": "sp500_daily.txt",
    "DAX": "dax_daily.txt",
}


def market_trend_series(fname: str) -> pd.Series:
    df = load_ohlc(str(REPO_ROOT / "data" / fname))
    quality_report(df)
    close = df["close"].values
    sma = pd.Series(close).rolling(SMA_WINDOW).mean().values
    above = close > sma
    dates = pd.to_datetime(df["date"]).values
    return pd.Series(above, index=dates)


def compute_multimarket_breadth_series(dates_ndx: pd.DatetimeIndex) -> pd.Series:
    """Renvoie Breadth(t) = fraction des 5 marchés en tendance
    haussiere SMA200 simultanement, alignee sur le calendrier NDX
    (ffill causal par marche)."""
    trend_series = {name: market_trend_series(fname) for name, fname in MARKETS.items()}
    aligned = pd.DataFrame({
        name: s.reindex(dates_ndx, method="ffill") for name, s in trend_series.items()
    })
    n_markets = aligned.shape[1]
    n_calc = aligned.notna().sum(axis=1)
    n_up = aligned.fillna(False).sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        breadth = np.where(n_calc == n_markets, n_up / n_markets, np.nan)
    return pd.Series(breadth, index=dates_ndx)


def combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    """r = rendements log quotidiens (longueur T-1). gate_aligned = porte
    multi-marche alignee sur close (longueur T, booleenne). Renvoie la
    position pour chaque rendement de r."""
    gate_r = gate_aligned[:-1]  # meme convention causale que #47/#57/#78/#89/#90/#94/#96/#97/#98/#99/#100

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
    df_ndx = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df_ndx)
    close = df_ndx["close"].values
    dates_idx = pd.to_datetime(df_ndx["date"])
    bh_full = np.log(close[1:] / close[:-1])

    breadth = compute_multimarket_breadth_series(dates_idx)
    breadth_raw = breadth.values
    gate_aligned = np.where(np.isnan(breadth_raw), False, breadth_raw >= BREADTH_THRESHOLD)

    pos_full = combined_position(bh_full, gate_aligned)

    first_valid = int(np.argmax(~np.isnan(breadth_raw)))
    start = max(first_valid, SMA_WINDOW, VOL_WINDOW)
    bh_t = bh_full[start:]
    pos = pos_full[start:]

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
    verdict = sharpe_ok and ret_ok

    gate_active = (pos > 1.0)
    lines = [
        "# Résultat — Overlay vol-targeting gaté par la confirmation multi-marché élargie (5 marchés, pré-enregistré, règle renforcée)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_NDX_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si Breadth 5-marchés(t) ≥{100*BREADTH_THRESHOLD:.0f}% (au moins 3 des 5 marchés en tendance "
        f"haussière SMA200), sinon 1.0x. {len(bh_t)} séances testables.",
        "",
        f"%j porte multi-marché active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        f"Breadth multi-marché moyenne (toute la période) : {100*np.nanmean(breadth_raw):.1f}%",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté breadth 5-marchés** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_multimarket_breadth_vol_targeting_overlay_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
