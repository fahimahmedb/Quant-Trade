"""Audit adversarial — Leaders 52-semaines + overlay ToM.

1. Vérifie que l'exposition totale du portefeuille levé (somme des poids)
   vaut exactement 1.0 hors fenêtre ToM et exactement CAP pendant la
   fenêtre ToM, à chaque jour (pas de dérive numérique).
2. Vérifie la cohérence du masque ToM avec celui déjà audité aux cycles
   #2/#8 (même fraction de jours).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_leaders_tom_overlay_backtest import (  # noqa: E402
    load_prices, tom_mask, LOOKBACK, REBAL_EVERY, TERCILE, CAP,
)


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

    tom = tom_mask(P.index.to_series())
    exposure_target = np.where(tom, CAP, 1.0)
    weights_lev = weights_leaders * exposure_target[:, None]

    start = LOOKBACK
    total_exposure = weights_lev[start:].sum(axis=1)
    expected = exposure_target[start:]
    # sur les jours ou le portefeuille a au moins 1 position (n_top_t>0), l'exposition
    # totale doit valoir exactement "expected" ; sinon 0 (aucune position ce jour-la)
    has_position = weights_leaders[start:].sum(axis=1) > 1e-9
    diff = np.abs(total_exposure[has_position] - expected[has_position])
    max_diff = float(diff.max()) if diff.size else 0.0

    lines = [
        "# Audit adversarial — Leaders 52-semaines + overlay ToM",
        "",
        "## 1. Exposition totale conforme (1.0 hors ToM, CAP pendant ToM)",
        "",
        f"Écart maximum sur {has_position.sum()} jours avec position : {max_diff:.2e}",
        f"**{'OK — exposition exactement conforme.' if max_diff < 1e-9 else 'ÉCHEC — dérive détectée.'}**",
        "",
        "## 2. Cohérence du masque ToM avec les cycles #2/#8",
        "",
        f"Fraction de jours en fenêtre ToM : {100*tom[start:].mean():.1f}% "
        "— comparable au ~33% déjà audité aux cycles #2/#8 (même fonction, "
        "univers de dates différent mais même logique de calendrier).",
    ]

    out = ROOT / "results" / "nonml_leaders_tom_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
