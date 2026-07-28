"""Audit adversarial — Barbell overlay sur régime de vol calme.

Test anti-lookahead : mutation des rendements des 20% derniers jours,
vérifie que la classification de régime (calme/non-calme) des jours
ANTÉRIEURS à la mutation reste inchangée (le seuil causal expansif ne
doit dépendre que du passé à chaque date).
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
from nonml_vol_regime_overlay_backtest import calm_regime_mask, WARMUP  # noqa: E402


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])
    T = len(r)

    mask_orig = calm_regime_mask(r)

    cut = int(T * 0.8)
    rng = np.random.default_rng(3)
    r_mut = r.copy()
    r_mut[cut:] = r_mut[cut:] + rng.normal(0, 0.05, size=T - cut)
    mask_mut = calm_regime_mask(r_mut)

    check_slice = slice(WARMUP, cut - 30)  # bien avant la mutation
    diff = int((mask_orig[check_slice] != mask_mut[check_slice]).sum())
    n_checked = check_slice.stop - check_slice.start

    lines = [
        "# Audit adversarial — Barbell overlay sur régime de vol calme",
        "",
        "## Test anti-lookahead (mutation des 20% de rendements les plus récents)",
        "",
        f"Écart de classification de régime sur {n_checked} jours antérieurs à la "
        f"mutation (NDX) : {diff} jours différents.",
        f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff == 0 else 'ÉCHEC — fuite détectée, bug à corriger.'}**",
    ]

    out = ROOT / "results" / "nonml_vol_regime_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
