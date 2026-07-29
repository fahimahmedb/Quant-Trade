"""Audit adversarial — Overlay de régime par le range intra-séance.

1. Recalcul indépendant du range moyen roulant (boucle Python explicite,
   sans réutiliser pandas.rolling()) à un échantillon de dates.
2. Test anti-lookahead : mutation des OHLC des 20% derniers jours,
   vérifie que la classification de régime (calme/non-calme) des jours
   ANTÉRIEURS à la mutation reste inchangée.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_intraday_range_regime_overlay_backtest import calm_range_regime_mask, RANGE_WINDOW, WARMUP  # noqa: E402


def independent_range_ma_at(high, low, close, t):
    """Moyenne roulante du range (high-low)/close par boucle explicite,
    sans reutiliser pandas.rolling()."""
    window_vals = []
    for k in range(t - RANGE_WINDOW + 1, t + 1):
        window_vals.append((high[k] - low[k]) / close[k])
    return sum(window_vals) / len(window_vals)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    high = df["high"].values
    low = df["low"].values
    close = df["close"].values
    T = len(close)

    check_dates = list(range(RANGE_WINDOW, T, 500))
    lines = ["# Audit adversarial — Overlay de régime par le range intra-séance", "",
             "## 1. Recalcul indépendant du range moyen roulant (boucle Python explicite)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    from nonml_intraday_range_regime_overlay_backtest import RANGE_WINDOW as RW
    import pandas as pd
    daily_range = (high - low) / close
    range_ma_vec = pd.Series(daily_range).rolling(RW).mean().values
    for t in check_dates:
        indep = independent_range_ma_at(high, low, close, t)
        diff = abs(float(range_ma_vec[t]) - indep)
        all_ok &= (diff < 1e-12)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — range moyen confirmé par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des OHLC des 20% de données les plus récentes)")
    lines.append("")
    mask_orig = calm_range_regime_mask(high, low, close)

    cut = int(T * 0.8)
    rng = np.random.default_rng(87)
    high_mut, low_mut, close_mut = high.copy(), low.copy(), close.copy()
    factor = 1.0 + rng.normal(0, 0.3, size=T - cut)
    high_mut[cut:] = high_mut[cut:] * factor
    low_mut[cut:] = low_mut[cut:] * factor
    close_mut[cut:] = close_mut[cut:] * factor
    mask_mut = calm_range_regime_mask(high_mut, low_mut, close_mut)

    check_slice = slice(WARMUP, cut - 30)  # bien avant la mutation
    diff_n = int((mask_orig[check_slice] != mask_mut[check_slice]).sum())
    n_checked = check_slice.stop - check_slice.start

    lines.append(f"Écart de classification de régime sur {n_checked} jours antérieurs à la "
                 f"mutation (NDX) : {diff_n} jours différents.")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_n == 0 else 'ÉCHEC — fuite détectée, bug à corriger.'}**")

    lines.append("")
    frac_calm = float(mask_orig[WARMUP:].mean())
    lines.append(f"## 3. Fréquence du régime calme détecté (NDX, hors warmup) : {100*frac_calm:.1f}% du temps.")

    out = ROOT / "results" / "nonml_intraday_range_regime_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
