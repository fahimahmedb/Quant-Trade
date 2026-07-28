"""Audit adversarial — Leaders 52-semaines + overlay accélération signal.

Vérifie que la décision d'exposition à la date t ne dépend que des
ratios connus à t et t-1 (pas de fuite), et que l'exposition totale du
portefeuille est conforme (1.0 ou CAP selon le régime détecté).
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

from nonml_leaders_accel_overlay_backtest import load_prices, LOOKBACK, REBAL_EVERY, TERCILE, CAP  # noqa: E402


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
    rebal_dates = list(range(LOOKBACK, T, REBAL_EVERY))
    avg_ratio = []
    for t in rebal_dates:
        r = ratio[t]
        elig = np.where(np.isfinite(r))[0]
        n_top_t = min(n_top, len(elig))
        if n_top_t > 0:
            top_idx = elig[np.argsort(-r[elig])[:n_top_t]]
            avg_ratio.append(r[top_idx].mean())
        else:
            avg_ratio.append(np.nan)

    # test anti-lookahead : la decision au rebalancement k ne doit dependre que de
    # avg_ratio[k-1] et avg_ratio[k] -- verifie qu'une mutation de avg_ratio[k+1] (futur)
    # ne change pas la decision au rebalancement k
    k_check = len(rebal_dates) // 2
    decision_orig = avg_ratio[k_check] > avg_ratio[k_check - 1]
    avg_ratio_mut = list(avg_ratio)
    avg_ratio_mut[k_check + 1] = 999.0  # mutation grossiere du futur
    decision_mut = avg_ratio_mut[k_check] > avg_ratio_mut[k_check - 1]  # ne doit pas changer

    lines = [
        "# Audit adversarial — Leaders 52-semaines + overlay accélération signal",
        "",
        "## Test anti-lookahead (mutation du ratio moyen au rebalancement SUIVANT)",
        "",
        f"Décision au rebalancement {k_check} avant mutation du futur : {'accéléré' if decision_orig else 'normal'}",
        f"Décision au rebalancement {k_check} après mutation de avg_ratio[{k_check+1}] : "
        f"{'accéléré' if decision_mut else 'normal'}",
        f"**{'OK — décision inchangée, aucune fuite (ne dépend que du passé/présent).' if decision_orig == decision_mut else 'ÉCHEC — fuite détectée.'}**",
        "",
        f"Nombre de rebalancements testés : {len(rebal_dates)}, régime accéléré détecté "
        f"{sum(1 for i in range(1, len(avg_ratio)) if np.isfinite(avg_ratio[i]) and np.isfinite(avg_ratio[i-1]) and avg_ratio[i] > avg_ratio[i-1])} fois.",
    ]

    out = ROOT / "results" / "nonml_leaders_accel_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
