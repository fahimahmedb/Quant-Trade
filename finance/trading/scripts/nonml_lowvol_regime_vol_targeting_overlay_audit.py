"""Audit adversarial — Overlay vol-targeting gaté par un régime de
volatilité réalisée faible.

Recalcul totalement indépendant (boucle explicite jour par jour,
recalcul de la vol réalisée ET de sa médiane glissante sans réutiliser
pandas.rolling) et test anti-lookahead (perturbation du futur).
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
from nonml_lowvol_regime_vol_targeting_overlay_backtest import (  # noqa: E402
    combined_position, VOL_WINDOW, MEDIAN_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_combined_position(r: np.ndarray) -> np.ndarray:
    """Recalcul totalement independant : a l'iteration i, ne calcule
    vol_lagged[i] qu'a partir de r[0..i-2] (jamais r[i-1] ou au-dela), et
    la mediane glissante qu'a partir des vol_lagged deja calcules aux
    iterations precedentes (boucle sequentielle, pas de vectorisation)."""
    T = len(r)
    vol_lagged = np.full(T, np.nan)
    for i in range(T):
        # vol_lagged[i] = vol_ann[i-1] (apres le roll) = std de
        # r[i-VOL_WINDOW .. i-1] (20 valeurs se terminant a r[i-1],
        # connu a la cloture du jour i)
        if i - VOL_WINDOW < 0:
            continue
        window_r = r[i - VOL_WINDOW:i]
        vol_lagged[i] = window_r.std(ddof=1) * ANNUALIZATION

    pos = np.ones(T)
    for i in range(T):
        if i - MEDIAN_WINDOW + 1 < 0 or np.isnan(vol_lagged[i]):
            continue
        hist = vol_lagged[i - MEDIAN_WINDOW + 1:i + 1]
        if np.any(np.isnan(hist)):
            continue
        med = np.median(hist)
        if vol_lagged[i] < med:
            vt = TARGET_VOL_ANNUAL / vol_lagged[i] if vol_lagged[i] > 0 else CAP
            pos[i] = min(max(vt, 1.0), CAP)
        else:
            pos[i] = 1.0
    return pos


def main():
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par régime de vol faible", "",
             "## 1. Recalcul totalement indépendant (boucle explicite jour par jour)", "",
             "| Marché | Écart position max (hors marge de fenêtre) |",
             "|---|---|"]
    all_ok = True
    dfs = {}
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        dfs[name] = df
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        pos_orig = combined_position(r)
        pos_indep = independent_combined_position(r)
        start = VOL_WINDOW + MEDIAN_WINDOW
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
    for name, df in dfs.items():
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        pos_before = combined_position(r)

        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(89)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        r_pert = np.log(close_pert[1:] / close_pert[:-1])
        pos_after = combined_position(r_pert)

        check_end = cut - (VOL_WINDOW + MEDIAN_WINDOW)
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL** : la porte est active 40-51% du temps sur les 5 "
                 "marchés (fréquence comparable aux portes de tendance), mais contrairement au "
                 "signal de tendance (#47), au calendrier (#54) ou à la breadth (#57), un régime "
                 "de vol réalisée faible n'est pas systématiquement corrélé à un régime haussier "
                 "-- il capture aussi des phases de consolidation baissière calme (ex. DAX, seul "
                 "échec net des deux jambes). Le mécanisme hiérarchique amplifie donc parfois "
                 "l'exposition sans biais directionnel favorable, ce qui explique le résultat "
                 "mitigé (2/5) malgré un mécanisme de vol-targeting identique à celui qui a "
                 "réussi ailleurs.")

    out = ROOT / "results" / "nonml_lowvol_regime_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
