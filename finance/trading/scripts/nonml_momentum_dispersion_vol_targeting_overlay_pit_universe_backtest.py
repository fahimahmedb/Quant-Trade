"""Backtest — Overlay vol-targeting gaté par le dispersion du momentum,
univers de titres POINT-IN-TIME (spécification pré-enregistrée dans
`PREREG_momentum_dispersion_vol_targeting_overlay_pit_universe.md`,
committée avant ce script).

Réutilisation stricte (Règle 7) du cycle d'origine (#100) : **aucun paramètre
modifié**. Seul l’univers servant à calculer la dispersion change — à chaque date,
seuls les titres réellement membres du NDX-100 entrent dans l'écart-type transversal.

Le P&L n'est **pas** un panier : les deux jambes sont l'indice NDX-100 lui-même.
L'univers titres n'alimente que la porte. Conventions de P&L rétablies au #404
(rendements log, `exp(Σ) − 1`, `trading_metrics` sur la série log).

Le masque explicite du piège du #396 est présent dès la première exécution,
comme exigé par le pré-enregistrement.
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
COMPOSITION_START = pd.Timestamp("2015-01-01")

# --- Parametres REPRIS A L'IDENTIQUE du cycle d'origine (Regle 7) ---
LOOKBACK = 252
SKIP = 21
MEDIAN_WINDOW = 252
MIN_LISTED = 10
COST_BPS = 5.0
CAP = 2.0
VOL_WINDOW = 20
TARGET_VOL_ANNUAL = 0.20
ANNUALIZATION = np.sqrt(252)


def load_all_prices_pit():
    series = {}
    for path in sorted(PRICES_PIT_DIR.glob("*.json")):
        payload = json.loads(path.read_text())
        if "error" in payload:
            continue
        ts = pd.to_datetime(payload["ts"], unit="s").normalize()
        close = pd.Series(payload["close"], index=ts, dtype=float).dropna()
        close = close[~close.index.duplicated(keep="first")].sort_index()
        if len(close) > LOOKBACK + 21:
            series[path.stem] = close
    return series


def _momentum_matrix_pit():
    series = load_all_prices_pit()
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
    momentum = np.where(np.isfinite(c_skip) & np.isfinite(c_lookback), momentum, np.nan)
    return momentum, P.index, list(P.columns)


def compute_momentum_dispersion_series_pit():
    """Dispersion(t) = ecart-type transversal (ddof=1) des scores de momentum
    12-1 mois, calcule sur les seuls MEMBRES du NDX-100 a la date t.

    NaN avant le 01/01/2015 ou si moins de MIN_LISTED membres eligibles.
    Retourne aussi la couverture moyenne.
    """
    momentum, idx, tickers = _momentum_matrix_pit()
    T = momentum.shape[0]
    n_tickers = len(tickers)
    disp = np.full(T, np.nan)
    coverage = []
    for i in range(T):
        if idx[i] < COMPOSITION_START:
            continue
        members = tickers_as_of_date(idx[i])
        if not members:
            continue
        member_cols = np.array([tickers[j] in members for j in range(n_tickers)])
        row = momentum[i]
        elig = np.isfinite(row) & member_cols
        vals = row[elig]
        n = len(vals)
        if n < MIN_LISTED:
            continue
        disp[i] = float(np.std(vals, ddof=1))
        coverage.append(n / max(1, len(members)))
    cov = float(np.mean(coverage)) if coverage else float("nan")
    return pd.Series(disp, index=idx), cov


def combined_position(r: np.ndarray, gate_aligned: np.ndarray) -> np.ndarray:
    """INCHANGE par rapport au cycle d'origine."""
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


def build_gate(disp):
    """Porte + masque EXPLICITE du piege du #396, present des la premiere
    execution comme exige par le pre-enregistrement."""
    median_disp = disp.rolling(MEDIAN_WINDOW).median()
    signal_defined = disp.notna() & median_disp.notna()
    return (disp >= median_disp).where(signal_defined)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_idx = pd.to_datetime(df["date"])
    bh_full = np.log(close[1:] / close[:-1])

    disp, cov = compute_momentum_dispersion_series_pit()
    gate_series = build_gate(disp)

    gate_aligned_raw = gate_series.reindex(dates_idx.values, method="ffill")
    gate_aligned = gate_series.fillna(False).reindex(
        dates_idx.values, method="ffill").fillna(False).values.astype(bool)

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
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok
    gate_active = (pos > 1.0)

    lines = [
        "# Résultat — dispersion du momentum, univers POINT-IN-TIME (pré-enregistré)",
        "",
        "Réutilisation stricte (Règle 7) du cycle d'origine (#100) : **aucun paramètre "
        "modifié**. Seul l’univers servant à calculer la dispersion change — à chaque date, "
        "seuls les titres réellement membres du NDX-100 entrent dans l'écart-type transversal.",
        "",
        "**Le P&L n'est pas un panier** : les deux jambes sont l'indice NDX-100 lui-même. "
        "L'univers titres n'alimente que la porte — c'est le seul canal par lequel le biais "
        "du survivant peut agir ici.",
        "",
        f"Couverture moyenne (titres éligibles / membres réels) : {100*cov:.1f}%. "
        f"{len(bh_t)} séances testables ({dates_idx.iloc[1:].iloc[start].date()} → "
        f"{dates_idx.iloc[-1].date()}).",
        "",
        f"%j porte dispersion active : {100*gate_active.mean():.1f}%",
        f"Position moyenne : {pos.mean():.2f}x",
        f"Dispersion du momentum moyenne observée : {np.nanmean(disp.values):.3f}",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
        f"{me_bh['max_drawdown_pct']:.1f}% |",
        f"| **Overlay gaté dispersion (PIT)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS (niveau 1)' if verdict else 'FAIL'} — critère renforcé "
        f"{'atteint' if verdict else 'NON atteint'} sur univers point-in-time.**",
        "",
    ]
    if verdict:
        lines.append("**PASS niveau 1 seulement — pas un verdict final (Règle 9).**")
        lines.append("")
    lines.append("Ce résultat ne remplace pas celui du cycle d'origine : les deux coexistent. "
                 "Leur comparaison mesure l'effet du biais du survivant sur ce candidat.")
    lines.append("")

    out = ROOT / "results" / "nonml_momentum_dispersion_vol_targeting_overlay_pit_universe_result.md"
    out.write_text("\n".join(lines), encoding="utf-8")

    np.savez(
        ROOT / "results" / "nonml_momentum_dispersion_vol_targeting_overlay_pit_universe_pnl.npz",
        pos=pos, r_asset=bh_t, dates=dates_idx.values[1:][start:], cost_bps=COST_BPS,
    )

    print("\n".join(lines))
    print(f"Écrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
