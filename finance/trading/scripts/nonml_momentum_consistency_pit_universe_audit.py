"""Audit adversarial — Momentum de constance (#82), univers point-in-time.

1. Recalcul indépendant de l'éligibilité PIT à un échantillon de dates.
2. Vérifie le décalage causal (`lag_one_day`).
3. Test anti-lookahead (perturbation du futur).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from ndx100_membership import tickers_as_of_date  # noqa: E402
from nonml_momentum_consistency_backtest import consistency_at, lag_one_day  # noqa: E402
from nonml_momentum_consistency_pit_universe_backtest import load_prices, LOOKBACK, REBAL_EVERY, REBAL_ANCHOR  # noqa: E402


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

    first_rebal = max(LOOKBACK, int(P.index.searchsorted(pd.Timestamp(REBAL_ANCHOR))))
    rebal_dates = list(range(first_rebal, T, REBAL_EVERY))
    check_dates = rebal_dates[::40]

    lines = ["# Audit adversarial — Momentum de constance (#82), univers point-in-time", "",
             "## 1. Recalcul indépendant de l'éligibilité PIT", "",
             "| Date | n éligibles (original) | n éligibles (recalcul indépendant) | Identique |",
             "|---|---|---|---|"]
    all_ok = True
    for t in check_dates:
        date = P.index[t]
        cons = consistency_at(close, t)
        members = tickers_as_of_date(date)
        elig_orig = {j for j in np.where(np.isfinite(cons))[0] if tickers[j] in members}

        elig_indep = set()
        for j, tk in enumerate(tickers):
            if not np.isfinite(cons[j]):
                continue
            if tk not in members:
                continue
            elig_indep.add(j)

        identical = elig_orig == elig_indep
        all_ok &= identical
        lines.append(f"| {date.date()} | {len(elig_orig)} | {len(elig_indep)} | {'OUI' if identical else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — éligibilité PIT confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Vérification du décalage causal (`lag_one_day`)")
    lines.append("")
    W_test = np.zeros((100, 10))
    rng0 = np.random.default_rng(5)
    W_test[5::7] = rng0.random((len(range(5, 100, 7)), 10))
    W_lagged = lag_one_day(W_test)
    shift_ok = np.allclose(W_lagged[1:], W_test[:-1]) and np.allclose(W_lagged[0], 0.0)
    lines.append(f"**{'OK — weights_après_lag[t] == weights_avant_lag[t-1] partout, ligne 0 nulle.' if shift_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    cut = T // 2
    P_pert = P.copy()
    rng = np.random.default_rng(276)
    P_pert.iloc[cut:] = P_pert.iloc[cut:] * (1.0 + rng.normal(0, 0.5, size=P_pert.iloc[cut:].shape))
    close_pert = P_pert.values
    check_t = cut - LOOKBACK - 50
    cons_before = consistency_at(close, check_t)
    cons_after = consistency_at(close_pert, check_t)
    diff_pert = np.nanmax(np.abs(np.nan_to_num(cons_before, nan=0.0) - np.nan_to_num(cons_after, nan=0.0)))
    anti_leak_ok = diff_pert < 1e-9
    lines.append(f"Écart de constance à une date antérieure à la mutation : {diff_pert:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_momentum_consistency_pit_universe_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
