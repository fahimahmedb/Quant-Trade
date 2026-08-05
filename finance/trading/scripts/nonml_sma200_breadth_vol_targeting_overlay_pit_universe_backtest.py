"""Backtest — Porte breadth SMA200 (#96), univers POINT-IN-TIME réel du
NDX-100 (spécification pré-enregistrée dans
PREREG_sma200_breadth_vol_targeting_overlay_pit_universe.md, committée
avant ce script). Réutilise STRICTEMENT (Règle 7) le mécanisme
vol-targeting du #96 (SMA_WINDOW, BREADTH_THRESHOLD, VOL_WINDOW,
TARGET_VOL_ANNUAL, CAP, COST_BPS inchangés) -- seul le panneau utilisé
pour calculer la breadth change : à CHAQUE jour de bourse, seuls les
titres RÉELLEMENT membres du NDX-100 ce jour-là entrent dans le calcul
de la fraction au-dessus de leur SMA200 (`ndx100_membership.
tickers_as_of_date`), au lieu des 99 membres 2026 appliqués
rétroactivement.

Garde-fou anti-contamination (même leçon que le #270) : les dates
antérieures à la couverture de composition (2015+) sont explicitement
exclues, et le masque NaN est appliqué directement sur la VALEUR de
breadth (pas sur une comparaison booléenne) pour éviter le piège
« NaN >= seuil renvoie False, pas NaN ».
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
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

PRICES_PIT_DIR = ROOT / "data" / "pead" / "prices_pit"
SMA_WINDOW = 200
BREADTH_THRESHOLD = 0.50
COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)
COMPOSITION_START = pd.Timestamp("2015-01-01")


def load_prices_pit():
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > SMA_WINDOW + 21:
            series[path.stem] = close
    return series


def compute_sma200_breadth_series_pit() -> pd.Series:
    series = load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    close = P.values
    sma = P.rolling(SMA_WINDOW).mean().values
    above = close > sma
    calculable = np.isfinite(sma) & np.isfinite(close)
    T, n_tickers = P.shape

    breadth = np.full(T, np.nan)
    for i in range(T):
        if P.index[i] < COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[i])
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        calc_row = calculable[i] & member_cols
        n_calc = calc_row.sum()
        if n_calc > 0:
            n_above = (above[i] & calc_row).sum()
            breadth[i] = n_above / n_calc

    return pd.Series(breadth, index=P.index)


def combined_position(close: np.ndarray, r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    gate_r = gate_aligned[:-1]
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

    breadth = compute_sma200_breadth_series_pit()
    breadth_aligned_raw = breadth.reindex(dates_idx.values, method="ffill").values
    breadth_aligned = np.nan_to_num(breadth_aligned_raw, nan=0.0)

    gate_aligned = breadth_aligned >= BREADTH_THRESHOLD
    pos_full = combined_position(close, bh_full, gate_aligned)

    first_valid = int(np.argmax(~np.isnan(breadth_aligned_raw)))
    start = max(first_valid, SMA_WINDOW, VOL_WINDOW)
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
    np.savez(ROOT / "results" / "nonml_sma200_breadth_vol_targeting_overlay_pit_universe_pnl.npz",
             pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    gate_active = (pos > 1.0)
    lines = [
        "# Résultat — Porte breadth SMA200, univers POINT-IN-TIME réel (cycle #271)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si Breadth_PIT SMA200(t) ≥{100*BREADTH_THRESHOLD:.0f}% (fraction des titres RÉELLEMENT membres "
        f"au-dessus de leur propre SMA{SMA_WINDOW}), sinon 1.0x. {len(bh_t)} séances testables "
        f"({pd.Timestamp(dates_pnl[0]).date()} → {pd.Timestamp(dates_pnl[-1]).date()}).",
        "",
        f"%j porte breadth SMA200 active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        f"Breadth SMA200 PIT moyenne (toute la période post-2015) : {100*np.nanmean(breadth.values):.1f}%",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté breadth SMA200 (PIT)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_sma200_breadth_vol_targeting_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
