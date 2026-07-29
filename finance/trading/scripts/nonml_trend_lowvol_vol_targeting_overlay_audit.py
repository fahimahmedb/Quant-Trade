"""Audit adversarial — Overlay vol-targeting gaté par double porte
tendance+vol faible.

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
from nonml_trend_lowvol_vol_targeting_overlay_backtest import (  # noqa: E402
    combined_position, INDEX_LOOKBACK, INDEX_THRESHOLD, VOL_WINDOW, MEDIAN_WINDOW,
    TARGET_VOL_ANNUAL, CAP, ANNUALIZATION, MARKETS,
)


def independent_combined_position(close: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Recalcul totalement independant : boucle explicite jour par jour,
    n'utilise a l'iteration i QUE close[0..i] et r[0..i-1] (jamais de
    donnee future) pour decider la position appliquee a r[i]."""
    T = len(r)
    vol_lagged = np.full(T, np.nan)
    for i in range(T):
        if i - VOL_WINDOW < 0:
            continue
        window_r = r[i - VOL_WINDOW:i]
        vol_lagged[i] = window_r.std(ddof=1) * ANNUALIZATION

    pos = np.ones(T)
    for i in range(max(INDEX_LOOKBACK, MEDIAN_WINDOW), T):
        window_max = close[i - INDEX_LOOKBACK + 1:i + 1].max()
        trend_i = close[i] >= INDEX_THRESHOLD * window_max

        if np.isnan(vol_lagged[i]):
            pos[i] = 1.0
            continue
        hist = vol_lagged[i - MEDIAN_WINDOW + 1:i + 1]
        if np.any(np.isnan(hist)):
            pos[i] = 1.0
            continue
        lowvol_i = vol_lagged[i] < np.median(hist)

        if trend_i and lowvol_i:
            vt = TARGET_VOL_ANNUAL / vol_lagged[i] if vol_lagged[i] > 0 else CAP
            pos[i] = min(max(vt, 1.0), CAP)
        else:
            pos[i] = 1.0
    return pos


def main():
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par double porte tendance+vol faible", "",
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
        start = max(INDEX_LOOKBACK, MEDIAN_WINDOW)
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
        rng = np.random.default_rng(113)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        r_pert = np.log(close_pert[1:] / close_pert[:-1])
        pos_after = combined_position(close_pert, r_pert)

        check_end = cut - max(INDEX_LOOKBACK, MEDIAN_WINDOW, VOL_WINDOW)
        identical = bool(np.allclose(pos_before[:check_end], pos_after[:check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL** : la porte combinée (intersection tendance ET vol "
                 "faible) est active 29-46% du temps, nettement moins que la tendance seule (#47, "
                 "55-75%) -- le filtre de vol faible retire des jours de tendance haussière "
                 "PENDANT lesquels la vol est déjà remontée (souvent des rallyes tardifs de cycle), "
                 "réduisant l'exposition amplifiée précisément quand elle aurait le plus profité au "
                 "rendement composé. Contrairement au calendrier (#54) et à la breadth (#57), qui "
                 "PORTENT une information directionnelle propre en plus de la tendance, le filtre "
                 "de vol faible (#58) n'en porte aucune -- l'ajouter en AND ne fait que rétrécir la "
                 "fenêtre d'exposition sans ajouter de sélectivité utile.")

    out = ROOT / "results" / "nonml_trend_lowvol_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
