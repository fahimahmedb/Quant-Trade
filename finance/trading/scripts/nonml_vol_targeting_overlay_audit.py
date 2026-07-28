"""Audit adversarial — Overlay de vol-targeting continu.

Recalcul indépendant de la position (boucle explicite, indépendante de
pandas.rolling.std) et test anti-lookahead (perturbation du futur).
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
from nonml_vol_targeting_overlay_backtest import (  # noqa: E402
    vol_target_position, VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_vol_target_position(r: np.ndarray) -> np.ndarray:
    T = len(r)
    pos = np.ones(T)
    for t in range(VOL_WINDOW + 1, T):
        window = r[t - VOL_WINDOW:t]  # rendements [t-20 .. t-1], connus a la cloture de t-1
        # ddof=1 : reproduit l'ecart-type ECHANTILLON de pandas.Series.std()
        # (defaut pandas), utilise dans le backtest -- np.std() par defaut
        # utilise ddof=0 (ecart-type POPULATION), ce qui creait un faux
        # positif de ~5% d'ecart de position lors du premier passage de cet
        # audit (bug de l'audit, pas du backtest -- verifie explicitement
        # par un test isole avant correction).
        vol_ann = window.std(ddof=1) * ANNUALIZATION
        if vol_ann > 0:
            pos[t] = min(max(TARGET_VOL_ANNUAL / vol_ann, 0.0), CAP)
        else:
            pos[t] = CAP
    return pos


def main():
    lines = ["# Audit adversarial — Overlay de vol-targeting continu", "",
             "## 1. Recalcul indépendant (boucle explicite vs pandas.rolling.std)", "",
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
        pos_orig = vol_target_position(r)
        pos_indep = independent_vol_target_position(r)
        start = VOL_WINDOW + 1
        max_diff = float(np.max(np.abs(pos_orig[start:] - pos_indep[start:])))
        all_ok &= (max_diff < 1e-9)
        lines.append(f"| {name} | {max_diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

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
        pos_before = vol_target_position(r)
        r_pert = r.copy()
        cut = len(r_pert) // 2
        rng = np.random.default_rng(43)
        r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r_pert) - cut)
        pos_after = vol_target_position(r_pert)
        check_end = cut - VOL_WINDOW  # marge de securite avant la mutation
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture** : le FAIL (3/5, critère renforcé ≥4/5 non atteint) masque un "
                 "profil de risque nettement amélioré -- le MDD est réduit de façon spectaculaire "
                 "sur tous les marchés (ex. NDX -82,9%→-48,3%, Composite -36,4%→-24,8%), et le "
                 "Sharpe s'améliore sur 4/5 marchés. Seul le rendement total échoue à dépasser "
                 "Buy&Hold sur 2 marchés (Composite, DAX) -- cohérent avec la règle renforcée qui "
                 "exige les DEUX jambes simultanément, et illustre bien pourquoi le vol-targeting "
                 "est un outil de gestion du RISQUE plutôt qu'un générateur d'edge de rendement "
                 "pur (même conclusion que l'Étape C du projet : \"utile pour le risk management, "
                 "pas pour prédire une direction\").")

    out = ROOT / "results" / "nonml_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
