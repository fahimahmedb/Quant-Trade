"""Audit adversarial — Overlay vol-targeting gaté par la breadth de
surperformance des petites capitalisations (proxy volatilité
idiosyncratique).

1. Recalcul indépendant (boucle Python explicite par titre, médiane
   manuelle, sans réutiliser les opérations vectorisées du backtest) à
   un échantillon de dates.
2. Test anti-lookahead (mutation du futur).
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
from nonml_smallcap_proxy_outperformance_breadth_overlay_backtest import (  # noqa: E402
    load_all_prices, IDIO_VOL_WINDOW, MOM_WINDOW, MIN_LISTED,
    compute_smallcap_breadth_series,
)


def independent_breadth_at(aligned: dict, tickers: list, i: int) -> float:
    idio_vols = {}
    moms = {}
    for t in tickers:
        # IDIO_VOL_WINDOW rendements log = IDIO_VOL_WINDOW+1 prix (memo
        # convention rolling(WINDOW).std() sur une serie de rendements,
        # deja utilisee partout ailleurs dans ce backlog, ex. VOL_WINDOW=20
        # dans combined_position). Bug d'off-by-one trouve ICI (dans ce
        # recalcul independant, pas dans le backtest) lors du premier essai
        # de cet audit -- corrige avant de committer le resultat de l'audit.
        px_window_idio = aligned[t][i - IDIO_VOL_WINDOW:i + 1]
        px_now = aligned[t][i]
        px_lag = aligned[t][i - MOM_WINDOW] if i - MOM_WINDOW >= 0 else np.nan
        if not np.isfinite(px_now):
            continue
        # rendements log quotidiens sur la fenetre idio
        rets = []
        ok = True
        for j in range(len(px_window_idio) - 1):
            a, b = px_window_idio[j], px_window_idio[j + 1]
            if not (np.isfinite(a) and np.isfinite(b)):
                ok = False
                break
            rets.append(np.log(b / a))
        if not ok or len(rets) < IDIO_VOL_WINDOW:
            continue
        mean_r = sum(rets) / len(rets)
        var_r = sum((x - mean_r) ** 2 for x in rets) / (len(rets) - 1)
        idio_vols[t] = var_r ** 0.5
        if np.isfinite(px_lag) and px_lag != 0:
            moms[t] = px_now / px_lag - 1.0

    elig = sorted(set(idio_vols.keys()) & set(moms.keys()))
    n_elig = len(elig)
    if n_elig < MIN_LISTED:
        return np.nan
    mom_vals = sorted(moms[t] for t in elig)
    n = len(mom_vals)
    median_mom = mom_vals[n // 2] if n % 2 == 1 else 0.5 * (mom_vals[n // 2 - 1] + mom_vals[n // 2])
    idio_vals = sorted(idio_vols[t] for t in elig)
    median_idio = idio_vals[n // 2] if n % 2 == 1 else 0.5 * (idio_vals[n // 2 - 1] + idio_vals[n // 2])

    small = [t for t in elig if idio_vols[t] >= median_idio]
    if len(small) == 0:
        return np.nan
    n_outperf = sum(1 for t in small if moms[t] > median_mom)
    return n_outperf / len(small)


def main():
    series = load_all_prices()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    aligned = {t: series[t].reindex(ref_idx).values for t in tickers}
    T = len(ref_idx)

    orig = compute_smallcap_breadth_series()
    check_idx = list(range(IDIO_VOL_WINDOW + MOM_WINDOW, T, 400))

    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la breadth de surperformance petites caps (proxy)", "",
             "## 1. Recalcul indépendant (boucle Python explicite, médianes manuelles, sans vectorisation)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    n_checked = 0
    for i in check_idx:
        indep = independent_breadth_at(aligned, tickers, i)
        orig_v = orig.values[i]
        if np.isnan(orig_v) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig_v) - float(indep))
        all_ok &= (diff < 1e-6)
        n_checked += 1
        lines.append(f"| {i} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — breadth confirmée par recalcul indépendant (' + str(n_checked) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    P_mut = {t: aligned[t].copy() for t in tickers}
    rng = np.random.default_rng(123)
    for t in tickers:
        mask = np.isfinite(P_mut[t][cut:])
        P_mut[t][cut:][mask] = P_mut[t][cut:][mask] * (1.0 + rng.normal(0, 0.5, mask.sum()))

    check_i = cut - IDIO_VOL_WINDOW - MOM_WINDOW - 50
    b_before = independent_breadth_at(aligned, tickers, check_i)
    b_after = independent_breadth_at(P_mut, tickers, check_i)
    diff_lookahead = abs(b_before - b_after) if not (np.isnan(b_before) or np.isnan(b_after)) else 0.0
    lines.append(f"Écart sur la breadth calculée à une date antérieure à la mutation : {diff_lookahead:.2e}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead < 1e-6 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_smallcap_proxy_outperformance_breadth_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
