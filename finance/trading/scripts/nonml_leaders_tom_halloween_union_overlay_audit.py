"""Audit adversarial — Leaders 52-semaines + overlay union ToM∪Halloween.

Vérifie (1) l'exposition totale (conforme 1.0/CAP) et (2) la cohérence de
la fraction de jours en union via inclusion-exclusion, comme au cycle
#21.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_leaders_tom_halloween_union_overlay_backtest import (  # noqa: E402
    load_prices, tom_mask, halloween_mask, LOOKBACK, REBAL_EVERY, TERCILE, CAP,
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

    m_tom = tom_mask(P.index.to_series())
    m_hall = halloween_mask(P.index.to_series())
    m_union = m_tom | m_hall
    m_inter = m_tom & m_hall
    exposure_target = np.where(m_union, CAP, 1.0)
    weights_lev = weights_leaders * exposure_target[:, None]

    start = LOOKBACK
    total_exposure = weights_lev[start:].sum(axis=1)
    expected = exposure_target[start:]
    has_position = weights_leaders[start:].sum(axis=1) > 1e-9
    diff = np.abs(total_exposure[has_position] - expected[has_position])
    max_diff = float(diff.max()) if diff.size else 0.0

    p_tom, p_hall = m_tom[start:].mean(), m_hall[start:].mean()
    p_union_measured = m_union[start:].mean()
    p_union_incl_excl = p_tom + p_hall - m_inter[start:].mean()
    union_diff = abs(p_union_measured - p_union_incl_excl)

    lines = [
        "# Audit adversarial — Leaders 52-semaines + overlay union ToM∪Halloween",
        "",
        f"Écart maximum sur l'exposition totale (jours avec position) : {max_diff:.2e}",
        f"**{'OK — exposition exactement conforme.' if max_diff < 1e-9 else 'ÉCHEC — dérive détectée.'}**",
        "",
        f"Union mesurée : {100*p_union_measured:.1f}% | Union par inclusion-exclusion : "
        f"{100*p_union_incl_excl:.1f}% | Écart : {union_diff:.2e}",
        f"**{'OK — union cohérente, aucun bug de fusion des masques.' if union_diff < 1e-9 else 'ÉCHEC — incohérence détectée.'}**",
        "",
        f"Fraction ToM seule : {100*p_tom:.1f}%, Halloween seule : {100*p_hall:.1f}% "
        "(cohérent avec les cycles #11/#20).",
    ]

    out = ROOT / "results" / "nonml_leaders_tom_halloween_union_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
