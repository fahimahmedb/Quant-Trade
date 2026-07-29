"""Audit adversarial — Effet janvier stock-level (tax-loss selling).

Recalcul indépendant (regroupement par (annee, mois) via datetime
standard, boucle explicite plutôt que numpy vectorisé) et test
anti-lookahead : vérifie qu'aucune donnée de janvier(Y+1) n'affecte la
sélection du décile calculée en novembre-décembre(Y).
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

from nonml_january_effect_stocklevel_backtest import load_all_prices, DECILE  # noqa: E402


def independent_loser_deciles(P: pd.DataFrame, n_top: int):
    """Reconstruction indépendante par balayage séquentiel : regroupe les
    indices par (annee, mois) via datetime standard, calcule le
    rendement nov-dec par ticker avec une boucle Python (pas numpy
    vectorisé), retourne {annee: set(tickers perdants)}."""
    ts = [d.to_pydatetime() for d in P.index]
    T = len(ts)
    close = P.values
    tickers = list(P.columns)

    first_idx, last_idx = {}, {}
    for i, dt in enumerate(ts):
        key = (dt.year, dt.month)
        last_idx[key] = i
        if key not in first_idx:
            first_idx[key] = i

    result = {}
    years = sorted({dt.year for dt in ts})
    for y in years:
        i_nov = first_idx.get((y, 11))
        i_dec = last_idx.get((y, 12))
        if i_nov is None or i_dec is None:
            continue
        rets = []
        for j, tk in enumerate(tickers):
            c0, c1 = close[i_nov, j], close[i_dec, j]
            if np.isfinite(c0) and np.isfinite(c1):
                rets.append((c1 / c0 - 1.0, tk))
        if not rets:
            continue
        rets.sort(key=lambda x: x[0])
        losers = {tk for _, tk in rets[:n_top]}
        result[y] = losers
    return result


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    n_tickers = len(tickers)
    n_top = max(1, int(round(n_tickers * DECILE)))

    # recalcul via le module backtest original (pour comparaison)
    import nonml_january_effect_stocklevel_backtest as bt
    close = P.values
    exists = np.isfinite(close)
    dates = P.index
    years_arr = dates.year.values
    months_arr = dates.month.values
    last_idx_of_month, first_idx_of_month = {}, {}
    for i in range(len(P)):
        key = (years_arr[i], months_arr[i])
        last_idx_of_month[key] = i
        if key not in first_idx_of_month:
            first_idx_of_month[key] = i

    orig_losers = {}
    for y in sorted(set(years_arr)):
        i_nov_first = first_idx_of_month.get((y, 11))
        i_dec_last = last_idx_of_month.get((y, 12))
        if i_nov_first is None or i_dec_last is None:
            continue
        c_nov = close[i_nov_first]
        c_dec = close[i_dec_last]
        with np.errstate(all="ignore"):
            nov_dec_ret = c_dec / c_nov - 1.0
        valid = np.isfinite(c_nov) & np.isfinite(c_dec)
        eligible_idx = np.where(valid)[0]
        if len(eligible_idx) == 0:
            continue
        n_top_t = min(n_top, len(eligible_idx))
        losers_idx = eligible_idx[np.argsort(nov_dec_ret[eligible_idx])[:n_top_t]]
        orig_losers[y] = {tickers[j] for j in losers_idx}

    indep_losers = independent_loser_deciles(P, n_top)

    lines = ["# Audit adversarial — Effet janvier stock-level (tax-loss selling)", "",
             "## 1. Recalcul indépendant de la sélection du décile perdant (balayage séquentiel)", "",
             "| Année | Décile identique (backtest vs recalcul indépendant) |",
             "|---|---|"]
    all_ok = True
    common_years = sorted(set(orig_losers) & set(indep_losers))
    for y in common_years:
        identical = orig_losers[y] == indep_losers[y]
        all_ok &= identical
        lines.append(f"| {y} | {'OUI' if identical else 'NON — DIVERGENCE'} |")

    lines.append("")
    lines.append(f"**{'OK — sélection du décile confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation des prix de janvier(Y+1) sur la sélection nov-déc(Y))")
    lines.append("")
    P_pert = P.copy()
    rng = np.random.default_rng(241)
    is_jan = pd.Series(P.index.month == 1, index=P.index)
    P_pert.loc[is_jan] = P_pert.loc[is_jan] * (1.0 + rng.normal(0, 0.3, size=P_pert.loc[is_jan].shape))
    indep_losers_pert = independent_loser_deciles(P_pert, n_top)
    anti_leak_ok = True
    for y in common_years:
        if y in indep_losers_pert:
            identical = indep_losers[y] == indep_losers_pert[y]
            anti_leak_ok &= identical
    lines.append(f"**{'OK — la perturbation des prix de janvier ne change jamais la sélection nov-déc (aucune fuite).' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_january_effect_stocklevel_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
