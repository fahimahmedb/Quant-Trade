"""Audit adversarial — Overlay combiné tendance + vol-targeting.

Un bug de fuite d'un jour a été trouvé et corrigé DANS LE BACKTEST
lui-même avant tout calcul committé (trend_r utilisait trend[1:] au
lieu de trend[:-1], utilisant la tendance du jour i+1 -- connue
seulement à la clôture du jour i+1 -- pour décider la position du jour
i). Cet audit revérifie explicitement l'alignement causal après
correction, en plus du recalcul indépendant standard et du test
anti-lookahead par perturbation.
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
from nonml_trend_vol_targeting_overlay_backtest import (  # noqa: E402
    combined_position, near_high_mask, INDEX_LOOKBACK, INDEX_THRESHOLD,
    VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_combined_position(close: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Recalcul totalement independant : boucle explicite jour par jour,
    n'utilise a l'iteration i QUE close[0..i] (jamais close[i+1] ou
    au-dela) pour decider la position appliquee a r[i] = rendement de i
    a i+1."""
    T = len(r)
    pos = np.ones(T)
    for i in range(INDEX_LOOKBACK, T):
        # tendance connue a la cloture du jour i : n'utilise que close[0..i]
        window_max = close[i - INDEX_LOOKBACK + 1:i + 1].max()
        trend_i = close[i] >= INDEX_THRESHOLD * window_max
        if not trend_i:
            pos[i] = 1.0
            continue
        if i - VOL_WINDOW < 0:
            pos[i] = 1.0
            continue
        vol_window_r = r[i - VOL_WINDOW:i]  # rendements r[i-20..i-1], le dernier (r[i-1]) est connu a la cloture du jour i
        vol_ann = vol_window_r.std(ddof=1) * ANNUALIZATION
        if vol_ann > 0:
            pos[i] = min(max(TARGET_VOL_ANNUAL / vol_ann, 1.0), CAP)
        else:
            pos[i] = CAP
    return pos


def main():
    lines = ["# Audit adversarial — Overlay combiné tendance + vol-targeting", "",
             "## 1. Recalcul totalement indépendant (boucle explicite jour par jour)", "",
             "| Marché | Écart position max (hors marge de fenêtre) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        pos_orig = combined_position(close, r)
        pos_indep = independent_combined_position(close, r)
        start = INDEX_LOOKBACK
        max_diff = float(np.max(np.abs(pos_orig[start:] - pos_indep[start:])))
        all_ok &= (max_diff < 1e-9)
        lines.append(f"| {name} | {max_diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul totalement indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur)")
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
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        pos_before = combined_position(close, r)

        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(61)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        r_pert = np.log(close_pert[1:] / close_pert[:-1])
        pos_after = combined_position(close_pert, r_pert)

        check_end = cut - max(INDEX_LOOKBACK, VOL_WINDOW)
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Note sur le bug initial** : la première version du backtest utilisait "
                 "`trend[1:]` au lieu de `trend[:-1]` pour aligner le signal de tendance sur "
                 "les rendements -- cela appliquait la tendance du jour i+1 (qui dépend de "
                 "close[i+1], inconnu à la clôture du jour i) à la décision du jour i. Bug "
                 "trouvé et corrigé AVANT toute exécution committée (aucun résultat basé sur "
                 "la version buguée n'a été généré ni committé) ; ce audit confirme l'absence "
                 "de fuite résiduelle par une seconde méthode de calcul indépendante.")

    out = ROOT / "results" / "nonml_trend_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
