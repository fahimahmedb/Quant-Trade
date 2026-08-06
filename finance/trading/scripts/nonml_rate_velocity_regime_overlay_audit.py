"""Audit adversarial — Overlay défensif vitesse du taux court DGS3MO.

1. Recalcul indépendant du delta et du tercile par boucle explicite
   distincte (sans np.percentile, tri manuel + interpolation), même
   esprit que #191/#193/#195/#198/#199.
2. Vérification anti-lookahead par troncature de l'historique.
"""
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
from nonml_rate_velocity_regime_overlay_backtest import (  # noqa: E402
    load_rate_lag, delta_series, expanding_tercile_cut_high, MARKETS, N, CUT,
)


def independent_percentile(sorted_vals: np.ndarray, pct: float) -> float:
    """Recalcul manuel du percentile par tri+interpolation lineaire,
    independant de np.percentile."""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    rank = (pct / 100.0) * (n - 1)
    lo = int(np.floor(rank))
    hi = int(np.ceil(rank))
    if lo == hi:
        return sorted_vals[lo]
    frac = rank - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def independent_position_at(delta: np.ndarray, start: int, t: int) -> float:
    """Meme calcul que expanding_tercile_cut_high, mais pour un seul
    indice t, par tri+interpolation manuelle (independant de
    np.percentile) -- echantillonne, pas la sequence complete (le tri
    Python pur sur des dizaines de milliers d'elements a chaque pas
    serait prohibitif)."""
    if not np.isfinite(delta[t]):
        return np.nan
    hist = [v for v in delta[start:t + 1] if np.isfinite(v)]
    hist_sorted = sorted(hist)
    thresh = independent_percentile(np.array(hist_sorted), 100.0 - 100.0 / 3.0)
    return CUT if delta[t] >= thresh else 1.0


def main():
    lines = ["# Audit adversarial — Overlay défensif vitesse du taux court DGS3MO", "",
             "## 1. Recalcul indépendant (tri+interpolation manuelle, sans np.percentile)", "",
             "Échantillon d'une date sur 300 (tri Python pur sur l'historique complet à chaque "
             "pas serait prohibitif — même logique d'échantillonnage que les audits PIT "
             "(`check_dates = post_2015[::400]`)).",
             "",
             "| Marché | Séances | Dates échantillonnées | Désaccords |",
             "|---|---|---|---|"]
    all_ok = True
    ndx_dates = None
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dates = pd.DatetimeIndex(df["date"].values)

        rate_lag = load_rate_lag(dates)
        delta = delta_series(rate_lag)
        pos_orig = expanding_tercile_cut_high(delta)
        start = int(np.argmax(np.isfinite(delta)))

        sample_idx = list(range(start, len(delta), 300))
        n_diff = 0
        for t in sample_idx:
            indep = independent_position_at(delta, start, t)
            orig = pos_orig[t]
            if np.isfinite(orig) != np.isfinite(indep):
                n_diff += 1
            elif np.isfinite(orig) and not np.isclose(orig, indep, atol=1e-9):
                n_diff += 1
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {len(dates)} | {len(sample_idx)} | {n_diff} |")

        if name == "NDX (40 ans)":
            ndx_dates = dates

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul indépendant (0 désaccord sur l’échantillon).' if all_ok else 'ÉCHEC — désaccord détecté.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (troncature de l'historique)")
    lines.append("")
    N_CHECK = 2000
    TRUNC_POINTS = [4000, 7000, 9000]
    rate_lag_full = load_rate_lag(ndx_dates)
    delta_full = delta_series(rate_lag_full)
    pos_full = expanding_tercile_cut_high(delta_full)

    all_trunc_ok = True
    for cut in TRUNC_POINTS:
        dates_trunc = ndx_dates[:cut]
        rate_lag_trunc = load_rate_lag(dates_trunc)
        delta_trunc = delta_series(rate_lag_trunc)
        pos_trunc = expanding_tercile_cut_high(delta_trunc)
        n = min(N_CHECK, len(pos_trunc), cut - N - 1)
        match = np.allclose(pos_full[:n], pos_trunc[:n], equal_nan=True)
        all_trunc_ok &= match
        lines.append(f"Troncature à {cut} séances, comparaison sur les {n} premières positions : "
                     f"{'identique' if match else 'DIFFÉRENT'}.")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.' if all_trunc_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_rate_velocity_regime_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
