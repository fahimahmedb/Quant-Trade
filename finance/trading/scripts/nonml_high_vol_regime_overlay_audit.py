"""Audit adversarial — Overlay levé sur régime de vol élevée.

Même protocole que l'audit du cycle #9 (mutation des rendements
récents, vérifie que la classification de régime des jours ANTÉRIEURS
à la mutation reste inchangée).
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
from nonml_high_vol_regime_overlay_backtest import high_vol_regime_mask, WARMUP  # noqa: E402


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    r = np.log(close[1:] / close[:-1])
    T = len(r)

    mask_orig = high_vol_regime_mask(r)

    cut = int(T * 0.8)
    rng = np.random.default_rng(3)
    r_mut = r.copy()
    r_mut[cut:] = r_mut[cut:] + rng.normal(0, 0.05, size=T - cut)
    mask_mut = high_vol_regime_mask(r_mut)

    check_slice = slice(WARMUP, cut - 30)
    diff = int((mask_orig[check_slice] != mask_mut[check_slice]).sum())
    n_checked = check_slice.stop - check_slice.start

    lines = [
        "# Audit adversarial — Overlay levé sur régime de vol élevée",
        "",
        "## Test anti-lookahead (mutation des 20% de rendements les plus récents)",
        "",
        f"Écart de classification de régime sur {n_checked} jours antérieurs à la "
        f"mutation (NDX) : {diff} jours différents.",
        f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff == 0 else 'ÉCHEC — fuite détectée, bug à corriger.'}**",
        "",
        "**Lecture économique du FAIL** : la vol élevée persiste bien statistiquement "
        "(clustering ARCH, cf. Étape A), mais elle coïncide en pratique surtout avec des "
        "PHASES DE BAISSE ou de krach (asymétrie de la vol, effet levier documenté en "
        "finance empirique -- la vol monte quand les prix chutent), donc lever l'exposition "
        "en régime de vol élevée revient largement à lever sur les mêmes périodes que les "
        "chocs de prix déjà testés et FAIL aux cycles #13/#22/#24, pas sur une prime de "
        "risque isolée et exploitable.",
    ]

    out = ROOT / "results" / "nonml_high_vol_regime_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
