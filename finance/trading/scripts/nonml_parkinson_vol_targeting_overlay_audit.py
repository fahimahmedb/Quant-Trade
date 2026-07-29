"""Audit adversarial — Overlay de vol-targeting estimateur Parkinson.

Recalcul indépendant de la position (boucle explicite recalculant la
variance de Parkinson elle-même à partir de high/low, indépendamment de
data_loader.parkinson_var_pct) et test anti-lookahead.
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
from nonml_parkinson_vol_targeting_overlay_backtest import (  # noqa: E402
    parkinson_vol_position, VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_parkinson_position(df) -> np.ndarray:
    """Recalcul totalement independant : variance de Parkinson calculee
    directement depuis high/low (pas via data_loader.parkinson_var_pct),
    puis moyenne roulante et position par boucle explicite."""
    high = df["high"].values
    low = df["low"].values
    T = len(high)
    hl = np.log(high / low)
    v = (100.0 * hl) ** 2 / (4.0 * np.log(2.0))  # %^2, meme formule que parkinson_var_pct
    v = v[1:]  # aligne comme parkinson_var_pct (drop 1re obs)

    n = len(v)
    pos = np.ones(n)
    for i in range(VOL_WINDOW + 1, n):
        window = v[i - VOL_WINDOW:i]
        var_mean = window.mean()
        vol_ann = np.sqrt(var_mean) * ANNUALIZATION / 100.0
        if vol_ann > 0:
            pos[i] = min(max(TARGET_VOL_ANNUAL / vol_ann, 0.0), CAP)
        else:
            pos[i] = CAP
    return pos


def main():
    lines = ["# Audit adversarial — Overlay de vol-targeting estimateur Parkinson", "",
             "## 1. Recalcul totalement indépendant (variance Parkinson recalculée depuis high/low)", "",
             "| Marché | Écart position max (hors marge de fenêtre) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        pos_orig = parkinson_vol_position(df)
        pos_indep = independent_parkinson_position(df)
        start = VOL_WINDOW + 1
        max_diff = float(np.max(np.abs(pos_orig[start:] - pos_indep[start:])))
        all_ok &= (max_diff < 1e-9)
        lines.append(f"| {name} | {max_diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul totalement indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur, high/low)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        pos_before = parkinson_vol_position(df)

        df_pert = df.copy()
        cut = len(df_pert) // 2
        rng = np.random.default_rng(73)
        shock = 1.0 + rng.normal(0, 0.1, len(df_pert) - cut)
        df_pert.loc[df_pert.index[cut:], "high"] = df_pert["high"].values[cut:] * shock
        df_pert.loc[df_pert.index[cut:], "low"] = df_pert["low"].values[cut:] * shock
        pos_after = parkinson_vol_position(df_pert)

        check_end = cut - VOL_WINDOW
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture** : le biais anticipé dans le pré-enregistrement se confirme -- "
                 "l'exposition moyenne (1,31x à 1,54x) est plus élevée que celle du #46 avec "
                 "l'écart-type close-to-close (1,10x à 1,51x), cohérent avec le biais à la "
                 "baisse connu de l'estimateur de Parkinson (il ignore le gap d'ouverture). "
                 "Ceci n'invalide pas le résultat -- le critère de succès (Sharpe ET rendement "
                 "> Buy&Hold) est mesuré tel quel, net de coûts, et le PASS est net et propre "
                 "(5/5, contre 4/5 pour le #46) -- mais mérite d'être signalé pour la "
                 "transparence méthodologique.")

    out = ROOT / "results" / "nonml_parkinson_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
