"""Backtest — Porte dispersion cross-sectionnelle (#78), univers
POINT-IN-TIME réel du NDX-100 (spécification pré-enregistrée dans
PREREG_dispersion_vol_targeting_overlay_pit_universe.md, committée
avant ce script). Réutilise STRICTEMENT (Règle 7) le mécanisme
vol-targeting du #78 (VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, COST_BPS,
MEDIAN_WINDOW, MIN_LISTED inchangés) -- seul le panneau utilisé pour
calculer la dispersion change : à CHAQUE jour de bourse, seuls les
titres RÉELLEMENT membres du NDX-100 ce jour-là entrent dans l'écart-
type cross-sectionnel (`ndx100_membership.tickers_as_of_date`), au lieu
des 99 membres 2026 appliqués rétroactivement.
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
MEDIAN_WINDOW = 252
MIN_LISTED = 10
COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)
COMPOSITION_START = pd.Timestamp("2015-01-01")  # couverture ndx100_membership (cf. #163)


def load_prices_pit():
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > 60:
            series[path.stem] = close
    return series


def compute_dispersion_series_pit() -> pd.Series:
    """Identique à compute_dispersion_series() du #78, sauf que le
    calcul de l'écart-type cross-sectionnel au jour t se restreint aux
    titres réellement membres du NDX-100 ce jour-là."""
    series = load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    R = np.log(P / P.shift(1)).values
    R[0, :] = np.nan
    T, n_tickers = R.shape

    dispersion = np.full(T, np.nan)
    for i in range(T):
        if P.index[i] < COMPOSITION_START:
            continue  # hors couverture de la composition point-in-time (2015+)
        members = tickers_as_of_date(P.index[i])
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        r_row = R[i, member_cols]
        n_listed = np.isfinite(r_row).sum()
        if n_listed >= MIN_LISTED:
            with np.errstate(invalid="ignore"):
                dispersion[i] = np.nanstd(r_row, ddof=1)
    return pd.Series(dispersion, index=P.index)


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
    pos = np.nan_to_num(pos, nan=1.0)
    return pos


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    dispersion = compute_dispersion_series_pit()
    median_dispersion = dispersion.rolling(MEDIAN_WINDOW).median()
    # ATTENTION (bug trouvé et corrige avant tout commit de resultat) : une
    # comparaison pandas directe (dispersion >= median_dispersion) renvoie
    # False -- PAS NaN -- lorsque l'un des deux operandes est NaN. Comme le
    # panneau PIT remonte a 1970 pour certains titres (bien avant la
    # couverture de composition 2015+ et donc bien avant toute valeur de
    # dispersion valide), cela detecterait a tort un signal "disponible"
    # depuis 1970 (porte silencieusement a False). Masque explicite en NaN
    # partout ou l'un des deux operandes n'est pas fini, pour que la
    # detection de premiere date valide plus bas reste correcte.
    both_finite = np.isfinite(dispersion.values) & np.isfinite(median_dispersion.values)
    gate_values = np.where(both_finite, dispersion.values >= median_dispersion.values, np.nan)
    gate_series = pd.Series(gate_values, index=dispersion.index)
    gate_series_filled = gate_series.fillna(False).astype(bool)

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

    dates_pnl = dates_idx.values[1:][start:]
    np.savez(ROOT / "results" / "nonml_dispersion_vol_targeting_overlay_pit_universe_pnl.npz",
             pos=pos, r_asset=bh_t, dates=dates_pnl, cost_bps=COST_BPS)

    gate_active = (pos > 1.0)
    lines = [
        "# Résultat — Porte dispersion cross-sectionnelle, univers POINT-IN-TIME réel (cycle #270)",
        "",
        f"Position(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(t-1), 1.0, {CAP}x) "
        f"si Dispersion_PIT(t) ≥ sa médiane glissante {MEDIAN_WINDOW}j, sinon 1.0x. {len(bh_t)} séances testables "
        f"({pd.Timestamp(dates_pnl[0]).date()} → {pd.Timestamp(dates_pnl[-1]).date()}), "
        "dispersion calculée sur les titres réellement membres du NDX-100 chaque jour "
        "(au lieu des 99 membres 2026 fixes).",
        "",
        f"%j porte dispersion active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay vol-targeting gaté dispersion (PIT)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_dispersion_vol_targeting_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
