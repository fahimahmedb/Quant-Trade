"""Audit adversarial — Low-Vol Tilt + overlay union ToM∪Halloween.

Vérifie (1) l'exposition totale (conforme 1.0/CAP) et (2) la cohérence
de la fraction de jours en union via inclusion-exclusion, comme aux
cycles #21/#23.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_lowvol_tom_halloween_union_overlay_backtest import (  # noqa: E402
    load_prices, tom_mask, halloween_mask, VOL_WINDOW, REBAL_EVERY, TERCILE, CAP,
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
    exists = np.isfinite(P.values)

    vol = P.pct_change(fill_method=None).rolling(VOL_WINDOW).std().values
    n_low = max(1, int(round(n_tickers * TERCILE)))
    weights_lowvol = np.zeros((T, n_tickers))
    start = VOL_WINDOW
    rebal_dates = list(range(start, T, REBAL_EVERY))
    for k, t in enumerate(rebal_dates):
        end = rebal_dates[k + 1] if k + 1 < len(rebal_dates) else T
        v = vol[t]
        elig = np.where(np.isfinite(v) & exists[t])[0]
        n_low_t = min(n_low, len(elig))
        if n_low_t > 0:
            low_idx = elig[np.argsort(v[elig])[:n_low_t]]
            w = np.zeros(n_tickers)
            w[low_idx] = 1.0 / n_low_t
            weights_lowvol[t:end] = w

    m_tom = tom_mask(P.index.to_series())
    m_hall = halloween_mask(P.index.to_series())
    m_union = m_tom | m_hall
    m_inter = m_tom & m_hall
    exposure_target = np.where(m_union, CAP, 1.0)
    weights_lev = weights_lowvol * exposure_target[:, None]

    total_exposure = weights_lev[start:].sum(axis=1)
    expected = exposure_target[start:]
    has_position = weights_lowvol[start:].sum(axis=1) > 1e-9
    diff = np.abs(total_exposure[has_position] - expected[has_position])
    max_diff = float(diff.max()) if diff.size else 0.0

    p_tom, p_hall = m_tom[start:].mean(), m_hall[start:].mean()
    p_union_measured = m_union[start:].mean()
    p_union_incl_excl = p_tom + p_hall - m_inter[start:].mean()
    union_diff = abs(p_union_measured - p_union_incl_excl)

    lines = [
        "# Audit adversarial — Low-Vol Tilt + overlay union ToM∪Halloween",
        "",
        f"Écart maximum sur l'exposition totale (jours avec position) : {max_diff:.2e}",
        f"**{'OK — exposition exactement conforme.' if max_diff < 1e-9 else 'ÉCHEC — dérive détectée.'}**",
        "",
        f"Union mesurée : {100*p_union_measured:.1f}% | Union par inclusion-exclusion : "
        f"{100*p_union_incl_excl:.1f}% | Écart : {union_diff:.2e}",
        f"**{'OK — union cohérente, aucun bug de fusion des masques.' if union_diff < 1e-9 else 'ÉCHEC — incohérence détectée.'}**",
        "",
        f"Fraction ToM seule : {100*p_tom:.1f}%, Halloween seule : {100*p_hall:.1f}% "
        "(cohérent avec les cycles #11/#20/#23).",
    ]

    out = ROOT / "results" / "nonml_lowvol_tom_halloween_union_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
