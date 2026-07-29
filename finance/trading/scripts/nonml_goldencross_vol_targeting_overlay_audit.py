"""Audit adversarial — Overlay vol-targeting gaté par le golden cross.

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
from nonml_goldencross_vol_targeting_overlay_backtest import (  # noqa: E402
    combined_position, SMA_SHORT, SMA_LONG, VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_combined_position(close: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Recalcul totalement independant : boucle explicite jour par jour,
    n'utilise a l'iteration i QUE close[0..i] et r[0..i-1] (jamais de
    donnee future) pour decider la position appliquee a r[i]."""
    T = len(r)
    pos = np.ones(T)
    for i in range(SMA_LONG, T):
        sma_short_i = close[i - SMA_SHORT + 1:i + 1].mean()
        sma_long_i = close[i - SMA_LONG + 1:i + 1].mean()
        gc_i = sma_short_i > sma_long_i
        if not gc_i:
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
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par golden cross", "",
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
        start = SMA_LONG
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
        rng = np.random.default_rng(163)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        r_pert = np.log(close_pert[1:] / close_pert[:-1])
        pos_after = combined_position(close_pert, r_pert)

        check_end = cut - max(SMA_LONG, VOL_WINDOW)
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL** : la porte golden cross est active 48,8-66,8% du "
                 "temps selon le marché, une fréquence comparable à la porte 52w-high du #47. "
                 "Malgré le lissage attendu (comparaison de deux moyennes plutôt que prix/moyenne), "
                 "le golden cross n'apporte pas un edge supérieur combiné au vol-targeting -- 2 "
                 "marchés (Composite de justesse, Russell 2000) échouent contre 1 seul au #47. Le "
                 "signal 52w-high (#37/#47) reste le plus robuste des signaux de tendance testés "
                 "comme porte du mécanisme hiérarchique dans ce backlog, confirmant l'observation "
                 "déjà faite au #38/#39 (le 52w-high surperforme systématiquement les signaux "
                 "basés sur des moyennes mobiles en combinaison).")

    out = ROOT / "results" / "nonml_goldencross_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
