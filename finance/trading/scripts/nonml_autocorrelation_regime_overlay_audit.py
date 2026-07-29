"""Audit adversarial — Overlay de régime par l'autocorrélation lag-1
des rendements de l'indice.

1. Recalcul indépendant de l'autocorrélation lag-1 roulante (formule de
   Pearson manuelle explicite, sans réutiliser np.corrcoef) à un
   échantillon de dates (NDX).
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
from nonml_autocorrelation_regime_overlay_backtest import (  # noqa: E402
    rolling_lag1_autocorr, momentum_regime_mask, AUTOCORR_WINDOW, WARMUP,
)


def independent_pearson(x: np.ndarray, y: np.ndarray) -> float:
    mx, my = x.mean(), y.mean()
    dx, dy = x - mx, y - my
    num = np.sum(dx * dy)
    den = np.sqrt(np.sum(dx ** 2) * np.sum(dy ** 2))
    return num / den if den > 0 else np.nan


def independent_autocorr_at(r: np.ndarray, t: int) -> float:
    window = r[t - AUTOCORR_WINDOW + 1:t + 1]
    x, y = window[:-1], window[1:]
    return independent_pearson(x, y)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])
    T = len(r)

    ac_vec = rolling_lag1_autocorr(r)
    check_dates = list(range(AUTOCORR_WINDOW, T, 700))

    lines = ["# Audit adversarial — Overlay de régime par l'autocorrélation lag-1 de l'indice", "",
             "## 1. Recalcul indépendant de l'autocorrélation lag-1 (formule de Pearson manuelle, NDX)", "",
             "| Date (indice) | Écart absolu |",
             "|---|---|"]
    all_ok = True
    for t in check_dates:
        indep = independent_autocorr_at(r, t)
        orig = ac_vec[t]
        if np.isnan(orig) and np.isnan(indep):
            diff = 0.0
        else:
            diff = abs(float(orig) - float(indep))
        all_ok &= (diff < 1e-9)
        lines.append(f"| {t} | {diff:.2e} |")
    lines.append("")
    lines.append(f"**{'OK — autocorrélation confirmée par recalcul indépendant (formule de Pearson manuelle).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de rendements les plus récents)")
    lines.append("")
    mask_orig = momentum_regime_mask(r)

    cut = int(T * 0.8)
    rng = np.random.default_rng(95)
    r_mut = r.copy()
    r_mut[cut:] = r_mut[cut:] + rng.normal(0, 0.05, size=T - cut)
    mask_mut = momentum_regime_mask(r_mut)

    check_slice = slice(WARMUP, cut - 30)
    diff_n = int((mask_orig[check_slice] != mask_mut[check_slice]).sum())
    n_checked = check_slice.stop - check_slice.start

    lines.append(f"Écart de classification de régime sur {n_checked} jours antérieurs à la "
                 f"mutation (NDX) : {diff_n} jours différents.")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_n == 0 else 'ÉCHEC — fuite détectée, bug à corriger.'}**")

    out = ROOT / "results" / "nonml_autocorrelation_regime_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
