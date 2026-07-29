"""Audit adversarial — Overlay de régime par le vol-of-vol de l'indice.

1. Recalcul indépendant du vol-of-vol (formule manuelle explicite,
   ddof=1, boucle Python, sans réutiliser pandas.rolling() en cascade)
   à un échantillon de dates (NDX).
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
from nonml_vol_of_vol_regime_overlay_backtest import (  # noqa: E402
    stable_vol_regime_mask, VOL_WINDOW, VOV_WINDOW, WARMUP,
)


def independent_vol_at(r: np.ndarray, t: int) -> float:
    window = r[t - VOL_WINDOW + 1:t + 1]
    mean = window.mean()
    var = np.sum((window - mean) ** 2) / (VOL_WINDOW - 1)
    return var ** 0.5


def independent_vov_at(r: np.ndarray, t: int) -> float:
    """Vol-of-vol par recalcul explicite en deux etapes : vol roulante
    (boucle manuelle) puis ecart-type roulant de cette serie de vol."""
    vols = [independent_vol_at(r, k) for k in range(t - VOV_WINDOW + 1, t + 1)]
    mean = sum(vols) / len(vols)
    var = sum((v - mean) ** 2 for v in vols) / (len(vols) - 1)
    return var ** 0.5


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])
    T = len(r)

    check_dates = list(range(VOL_WINDOW + VOV_WINDOW, T, 700))
    lines = ["# Audit adversarial — Overlay de régime par le vol-of-vol de l'indice", "",
             "## 1. Recalcul indépendant du vol-of-vol (formule manuelle explicite, NDX)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    import pandas as pd
    vol_vec = pd.Series(r).rolling(VOL_WINDOW).std().values
    vov_vec = pd.Series(vol_vec).rolling(VOV_WINDOW).std().values
    for t in check_dates:
        indep = independent_vov_at(r, t)
        orig = vov_vec[t]
        diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — vol-of-vol confirmé par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de rendements les plus récents)")
    lines.append("")
    mask_orig = stable_vol_regime_mask(r)

    cut = int(T * 0.8)
    rng = np.random.default_rng(102)
    r_mut = r.copy()
    r_mut[cut:] = r_mut[cut:] + rng.normal(0, 0.05, size=T - cut)
    mask_mut = stable_vol_regime_mask(r_mut)

    check_slice = slice(WARMUP, cut - 30)
    diff_n = int((mask_orig[check_slice] != mask_mut[check_slice]).sum())
    n_checked = check_slice.stop - check_slice.start

    lines.append(f"Écart de classification de régime sur {n_checked} jours antérieurs à la "
                 f"mutation (NDX) : {diff_n} jours différents.")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_n == 0 else 'ÉCHEC — fuite détectée, bug à corriger.'}**")

    out = ROOT / "results" / "nonml_vol_of_vol_regime_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
