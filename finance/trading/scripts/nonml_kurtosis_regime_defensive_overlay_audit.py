"""Audit adversarial — Overlay défensif gaté par la kurtosis de l'indice.

1. Recalcul indépendant de la kurtosis roulante (formule explicite du
   quatrième moment corrigé du biais, définition Fisher/pandas,
   boucle Python, sans réutiliser pandas.rolling().kurt()) à un
   échantillon de dates (NDX).
2. Test anti-lookahead : mutation des rendements des 20% derniers
   jours, vérifie que la classification de régime des jours ANTÉRIEURS
   à la mutation reste inchangée.
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
from nonml_kurtosis_regime_defensive_overlay_backtest import (  # noqa: E402
    high_kurtosis_regime_mask, KURT_WINDOW, WARMUP,
)


def independent_kurt_at(r: np.ndarray, t: int) -> float:
    """Kurtosis en exces corrigee du biais (definition Fisher, meme
    formule que pandas.Series.kurt()) calculee explicitement, sans
    reutiliser pandas.rolling()."""
    n = KURT_WINDOW
    window = r[t - n + 1:t + 1]
    mean = window.mean()
    dev = window - mean
    m2 = np.sum(dev ** 2) / n
    m4 = np.sum(dev ** 4) / n
    if m2 <= 0:
        return np.nan
    g2 = m4 / (m2 ** 2) - 3.0  # kurtosis en exces (non corrigee du biais)
    # correction du biais (formule pandas/scipy bias=False pour la kurtosis)
    num = (n - 1) * ((n + 1) * g2 + 6)
    den = (n - 2) * (n - 3)
    return num / den


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])
    T = len(r)

    kurt_vec = pd.Series(r).rolling(KURT_WINDOW).kurt().values

    check_dates = list(range(KURT_WINDOW, T, 700))
    lines = ["# Audit adversarial — Overlay défensif gaté par la kurtosis de l'indice", "",
             "## 1. Recalcul indépendant de la kurtosis roulante (formule explicite, NDX)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        indep = independent_kurt_at(r, t)
        orig = kurt_vec[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-6)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — kurtosis confirmée par recalcul indépendant (formule Fisher corrigée du biais).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de rendements les plus récents)")
    lines.append("")
    mask_orig = high_kurtosis_regime_mask(r)

    cut = int(T * 0.8)
    rng = np.random.default_rng(93)
    r_mut = r.copy()
    r_mut[cut:] = r_mut[cut:] + rng.normal(0, 0.05, size=T - cut)
    mask_mut = high_kurtosis_regime_mask(r_mut)

    check_slice = slice(WARMUP, cut - 30)
    diff_n = int((mask_orig[check_slice] != mask_mut[check_slice]).sum())
    n_checked = check_slice.stop - check_slice.start

    lines.append(f"Écart de classification de régime sur {n_checked} jours antérieurs à la "
                 f"mutation (NDX) : {diff_n} jours différents.")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_n == 0 else 'ÉCHEC — fuite détectée, bug à corriger.'}**")

    out = ROOT / "results" / "nonml_kurtosis_regime_defensive_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
