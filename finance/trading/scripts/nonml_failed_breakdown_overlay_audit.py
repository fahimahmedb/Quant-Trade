"""Audit adversarial — Overlay levé faux breakdown Donchian.

Recalcul indépendant (union d'intervalles d'amplification, fenêtre
glissante calculée par slicing explicite, PAS pandas.rolling) et test
anti-lookahead (perturbation du futur).
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
from nonml_failed_breakdown_overlay_backtest import (  # noqa: E402
    failed_breakdown_position, DONCHIAN_WINDOW, CONFIRM_WINDOW, DEFENSE_LEN, CAP, MARKETS,
)


def independent_failed_breakdown_position(close: np.ndarray) -> np.ndarray:
    """Reconstruction indépendante : plus bas glissant calculé par
    slicing explicite, faux breakdowns détectés par une boucle séparée,
    fenêtres d'amplification construites comme une UNION d'intervalles
    [t', t'+DEFENSE_LEN-1] plutôt que par un compte à rebours à état
    mutable -- architecture différente du backtest original."""
    T = len(close)
    trigger_days = []
    breakdown_day, breakdown_level = None, None

    for t in range(DONCHIAN_WINDOW, T):
        window_min = close[t - DONCHIAN_WINDOW + 1:t + 1].min()
        if close[t] <= window_min:
            breakdown_day, breakdown_level = t, window_min

        if breakdown_day is not None and 1 <= (t - breakdown_day) <= CONFIRM_WINDOW:
            if close[t] > breakdown_level:
                trigger_days.append(t)
                breakdown_day = None

    boosted = np.zeros(T, dtype=bool)
    for t0 in trigger_days:
        boosted[t0:min(t0 + DEFENSE_LEN, T)] = True

    return np.where(boosted, CAP, 1.0)


def main():
    lines = ["# Audit adversarial — Overlay levé faux breakdown Donchian", "",
             "## 1. Recalcul indépendant (union d'intervalles vs compte à rebours à état)", "",
             "| Marché | Écart position (nb j., hors 20 premiers) |",
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
        p_orig = failed_breakdown_position(close)
        p_indep = independent_failed_breakdown_position(close)
        diff = int(np.sum(p_orig[DONCHIAN_WINDOW:] != p_indep[DONCHIAN_WINDOW:]))
        all_ok &= (diff == 0)
        lines.append(f"| {name} | {diff} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, df in dfs.items():
        close = df["close"].values
        p_before = failed_breakdown_position(close)
        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(127)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        p_after = failed_breakdown_position(close_pert)
        identical = bool(np.array_equal(p_before[:cut], p_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL** : le signal se déclenche 20-24% du temps sur tous "
                 "les marchés (fréquence homogène), mais l'amplification qui en résulte coïncide "
                 "systématiquement avec un MDD massivement dégradé (ex. NDX -82,9%→-94,2%) -- "
                 "confirmant, comme au #22 (pullback rebound), qu'une récupération de court terme "
                 "après une cassure de plus bas glissant est un marqueur de marché en stress "
                 "PROLONGÉ (souvent le début ou une pause dans un krach) plutôt qu'un signal de "
                 "capitulation fiable. Ni le miroir haussier (#62) ni le miroir baissier (#55) de "
                 "ce pattern Donchian ne passent le critère renforcé -- les deux confirment que le "
                 "backlog ne trouve aucun edge exploitable dans les signaux de prix à horizon "
                 "court (2-20j), qu'ils soient utilisés en amplification ou en réduction.")

    out = ROOT / "results" / "nonml_failed_breakdown_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
