"""Audit adversarial — Overlay de vol-targeting défensif uniquement.

Même protocole que l'audit du #43 (recalcul indépendant avec ddof=1
correct dès le départ cette fois, test anti-lookahead).
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
from nonml_defensive_vol_targeting_overlay_backtest import (  # noqa: E402
    vol_target_position, VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_vol_target_position(r: np.ndarray) -> np.ndarray:
    T = len(r)
    pos = np.ones(T)
    for t in range(VOL_WINDOW + 1, T):
        window = r[t - VOL_WINDOW:t]
        vol_ann = window.std(ddof=1) * ANNUALIZATION  # ddof=1 : coherent avec pandas.Series.std()
        if vol_ann > 0:
            pos[t] = min(max(TARGET_VOL_ANNUAL / vol_ann, 0.0), CAP)
        else:
            pos[t] = CAP
    return pos


def main():
    lines = ["# Audit adversarial — Overlay de vol-targeting défensif uniquement", "",
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
        rng = np.random.default_rng(47)
        r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r_pert) - cut)
        pos_after = vol_target_position(r_pert)
        check_end = cut - VOL_WINDOW
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL (0/5)** : en retirant toute possibilité de "
                 "levier (CAP=1.0x au lieu de 2.0x au #43), le mécanisme perd exactement les "
                 "épisodes d'exposition amplifiée qui permettaient au #43 de battre le rendement "
                 "Buy&Hold sur 3/5 marchés -- confirme le même écueil structurel déjà identifié "
                 "en tout début de backlog (cycles #2/#6/#8) : un design qui ne peut JAMAIS "
                 "dépasser 1.0x d'exposition ne peut pas battre le rendement composé de "
                 "Buy&Hold, même en réduisant fortement le MDD (ici Sharpe amélioré sur 5/5, "
                 "MDD massivement réduit partout, mais rendement systématiquement inférieur).")

    out = ROOT / "results" / "nonml_defensive_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
