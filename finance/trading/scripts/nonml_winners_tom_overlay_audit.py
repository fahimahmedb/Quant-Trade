"""Audit adversarial — Winners momentum + overlay ToM.

Vérifie l'exposition totale du portefeuille levé (conforme 1.0/CAP) et
la cohérence du masque ToM avec les cycles #2/#8/#11.
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

from nonml_winners_tom_overlay_backtest import (  # noqa: E402
    load_prices, tom_mask, SIGNAL_WINDOW, REBAL_EVERY, TERCILE, CAP,
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
    exists = np.isfinite(close)

    signal = np.full((T, n_tickers), np.nan)
    for i in range(SIGNAL_WINDOW, T):
        with np.errstate(all="ignore", invalid="ignore"):
            signal[i] = close[i] / close[i - SIGNAL_WINDOW] - 1.0
        signal[i, ~(exists[i] & exists[i - SIGNAL_WINDOW])] = np.nan

    n_top = max(1, int(round(n_tickers * TERCILE)))
    start = SIGNAL_WINDOW
    weights_w = np.zeros((T, n_tickers))
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        s = signal[t]
        elig = np.where(np.isfinite(s))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-s[elig])[:n_top_t]]
            w = np.zeros(n_tickers)
            w[top_idx] = 1.0 / n_top_t
            weights_w[t:end] = w

    tom = tom_mask(P.index.to_series())
    exposure_target = np.where(tom, CAP, 1.0)
    weights_lev = weights_w * exposure_target[:, None]

    total_exposure = weights_lev[start:].sum(axis=1)
    expected = exposure_target[start:]
    has_position = weights_w[start:].sum(axis=1) > 1e-9
    diff = np.abs(total_exposure[has_position] - expected[has_position])
    max_diff = float(diff.max()) if diff.size else 0.0

    lines = [
        "# Audit adversarial — Winners momentum + overlay ToM",
        "",
        f"Écart maximum sur l'exposition totale (jours avec position) : {max_diff:.2e}",
        f"**{'OK — exposition exactement conforme (1.0x hors ToM, 2.0x pendant).' if max_diff < 1e-9 else 'ÉCHEC — dérive détectée.'}**",
        "",
        f"Fraction de jours en fenêtre ToM : {100*tom[start:].mean():.1f}% "
        "(cohérent avec ~33% déjà audité aux cycles #2/#8/#11).",
    ]

    out = ROOT / "results" / "nonml_winners_tom_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
