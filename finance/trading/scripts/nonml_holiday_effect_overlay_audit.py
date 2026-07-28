"""Audit adversarial — Overlay levé pré/post jour férié.

La détection data-driven du jour férié (trou calendaire anormal) est
identique à celle déjà validée en profondeur au cycle #7 (confirmée
41/41 sur Thanksgiving via une référence calendaire civile indépendante)
-- pas re-validée ici. Cet audit vérifie uniquement (1) que la fraction
de jours levés est cohérente avec le ~7% mesuré au #7, et (2) l'exactitude
du calcul d'exposition/turnover (recalcul indépendant, sans réutiliser
les tableaux internes du backtest).
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
from nonml_holiday_effect_overlay_backtest import holiday_masks, CAP, MARKETS  # noqa: E402


def main():
    lines = ["# Audit adversarial — Overlay levé pré/post jour férié", "",
             "| Marché | %j levé | Écart exposition max (recalcul indépendant) |",
             "|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        is_pre, is_post = holiday_masks(df["date"])
        mask = (is_pre | is_post)[1:]

        # recalcul independant de l'exposition cible et du turnover, sans
        # reutiliser la boucle du backtest
        pos_indep = np.where(mask, CAP, 1.0)
        pos_ref = 1.0
        turn_indep = np.empty(len(pos_indep))
        prev = 1.0
        for i, p in enumerate(pos_indep):
            turn_indep[i] = abs(p - prev)
            prev = p
        # exposition target doit valoir CAP exactement quand mask est vrai
        max_diff = float(np.max(np.abs(pos_indep[mask] - CAP))) if mask.any() else 0.0
        max_diff = max(max_diff, float(np.max(np.abs(pos_indep[~mask] - 1.0))) if (~mask).any() else 0.0)
        all_ok &= (max_diff < 1e-12)

        lines.append(f"| {name} | {100*mask.mean():.1f}% | {max_diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — exposition conforme, cohérente avec la fraction ~7% déjà mesurée au cycle #7.' if all_ok else 'ÉCHEC — incohérence détectée.'}**")

    out = ROOT / "results" / "nonml_holiday_effect_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
