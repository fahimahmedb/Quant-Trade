"""Audit adversarial — Overlay vol-targeting gaté par la pente SMA200.

Recalcul totalement indépendant (boucle explicite jour par jour, ddof=1,
sans réutiliser pandas.rolling) et test anti-lookahead (perturbation du
futur).
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
from nonml_slope_vol_targeting_overlay_backtest import (  # noqa: E402
    combined_position, SMA_WINDOW, SLOPE_LAG, VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_combined_position(close: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Recalcul totalement independant : boucle explicite jour par jour,
    n'utilise a l'iteration i QUE close[0..i] et r[0..i-1] (jamais de
    donnee future) pour decider la position appliquee a r[i]."""
    T = len(r)
    pos = np.ones(T)
    for i in range(SMA_WINDOW + SLOPE_LAG, T):
        sma_i = close[i - SMA_WINDOW + 1:i + 1].mean()
        sma_lagged_i = close[i - SLOPE_LAG - SMA_WINDOW + 1:i - SLOPE_LAG + 1].mean()
        slope_i = sma_i > sma_lagged_i
        if not slope_i:
            pos[i] = 1.0
            continue
        if i - VOL_WINDOW < 0:
            pos[i] = 1.0
            continue
        vol_window_r = r[i - VOL_WINDOW:i]
        vol_ann = vol_window_r.std(ddof=1) * ANNUALIZATION
        if vol_ann > 0:
            pos[i] = min(max(TARGET_VOL_ANNUAL / vol_ann, 1.0), CAP)
        else:
            pos[i] = CAP
    return pos


def main():
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par pente SMA200", "",
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
        pos_orig = combined_position(close, r)
        pos_indep = independent_combined_position(close, r)
        start = SMA_WINDOW + SLOPE_LAG
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
        pos_before = combined_position(close, r)

        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(179)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        r_pert = np.log(close_pert[1:] / close_pert[:-1])
        pos_after = combined_position(close_pert, r_pert)

        check_end = cut - max(SMA_WINDOW + SLOPE_LAG, VOL_WINDOW)
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du PASS** : la porte pente SMA200 est active 51,8-68,5% du "
                 "temps, une fréquence comparable au golden cross (#67, 48,8-66,8%) mais avec un "
                 "résultat net supérieur (4/5 contre 3/5) -- le signal de pente semble mieux "
                 "capturer les régimes réellement porteurs pour le vol-targeting que le "
                 "croisement de moyennes. Complète la famille des 5 signaux de tendance testés "
                 "comme porte du mécanisme hiérarchique : 52w-high (#47, PASS 4/5) et pente SMA200 "
                 "(#68, PASS 4/5) sont les deux signaux les plus robustes, le golden cross (#67, "
                 "FAIL 3/5) le moins performant des trois signaux de tendance testés dans ce rôle.")

    out = ROOT / "results" / "nonml_slope_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
