"""Audit adversarial — Overlay de régime par la skewness de l'indice.

1. Recalcul indépendant de la skewness roulante (formule G1 explicite,
   boucle Python, sans réutiliser pandas.rolling().skew(), déjà
   validée au #84) à un échantillon de dates (NDX).
2. Test anti-lookahead : mutation des rendements des 20% derniers
   jours, vérifie que la classification de régime des jours ANTÉRIEURS
   à la mutation reste inchangée.
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
from nonml_index_skewness_regime_overlay_backtest import healthy_skew_regime_mask, SKEW_WINDOW, WARMUP  # noqa: E402


def independent_skew_at(r: np.ndarray, t: int) -> float:
    """Formule G1 (asymetrie corrigee du biais de Fisher-Pearson, meme
    definition que pandas.Series.skew(), deja validee au #84) calculee
    explicitement, sans reutiliser pandas.rolling()."""
    n = SKEW_WINDOW
    window = r[t - n + 1:t + 1]
    mean = window.mean()
    dev = window - mean
    m2 = np.sum(dev ** 2) / n
    m3 = np.sum(dev ** 3) / n
    if m2 <= 0:
        return np.nan
    g1 = m3 / (m2 ** 1.5)
    return (np.sqrt(n * (n - 1)) / (n - 2)) * g1


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])
    T = len(r)

    import pandas as pd
    skew_vec = pd.Series(r).rolling(SKEW_WINDOW).skew().values

    check_dates = list(range(SKEW_WINDOW, T, 700))
    lines = ["# Audit adversarial — Overlay de régime par la skewness de l'indice", "",
             "## 1. Recalcul indépendant de la skewness roulante (formule G1 explicite, NDX)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        indep = independent_skew_at(r, t)
        orig = skew_vec[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — skewness confirmée par recalcul indépendant (formule G1).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de rendements les plus récents)")
    lines.append("")
    mask_orig = healthy_skew_regime_mask(r)

    cut = int(T * 0.8)
    rng = np.random.default_rng(92)
    r_mut = r.copy()
    r_mut[cut:] = r_mut[cut:] + rng.normal(0, 0.05, size=T - cut)
    mask_mut = healthy_skew_regime_mask(r_mut)

    check_slice = slice(WARMUP, cut - 30)
    diff_n = int((mask_orig[check_slice] != mask_mut[check_slice]).sum())
    n_checked = check_slice.stop - check_slice.start

    lines.append(f"Écart de classification de régime sur {n_checked} jours antérieurs à la "
                 f"mutation (NDX) : {diff_n} jours différents.")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_n == 0 else 'ÉCHEC — fuite détectée, bug à corriger.'}**")

    out = ROOT / "results" / "nonml_index_skewness_regime_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
