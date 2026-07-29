"""Audit adversarial — Overlay défensif faux breakout Donchian.

Recalcul indépendant (fenêtre glissante calculée à la main, PAS
pandas.rolling, et logique d'état ré-écrite indépendamment sous forme
d'union d'intervalles défensifs plutôt qu'un compte à rebours) et test
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
from nonml_failed_breakout_overlay_backtest import (  # noqa: E402
    failed_breakout_position, DONCHIAN_WINDOW, CONFIRM_WINDOW, DEFENSE_LEN, FLOOR, MARKETS,
)


def independent_failed_breakout_position(close: np.ndarray) -> np.ndarray:
    """Reconstruction indépendante : (1) plus haut glissant calculé par
    slicing explicite (pas pandas.rolling.max), (2) détection des faux
    breakouts par une boucle séparée, (3) fenêtres défensives construites
    comme une UNION d'intervalles [t', t'+DEFENSE_LEN-1] plutôt que par un
    compte à rebours à état mutable -- une architecture différente du
    backtest original pour maximiser l'indépendance du recalcul."""
    T = len(close)
    trigger_days = []
    breakout_day, breakout_level = None, None

    for t in range(DONCHIAN_WINDOW, T):
        window_max = close[t - DONCHIAN_WINDOW + 1:t + 1].max()
        if close[t] >= window_max:
            breakout_day, breakout_level = t, window_max

        if breakout_day is not None and 1 <= (t - breakout_day) <= CONFIRM_WINDOW:
            if close[t] < breakout_level:
                trigger_days.append(t)
                breakout_day = None

    defensive = np.zeros(T, dtype=bool)
    for t0 in trigger_days:
        defensive[t0:min(t0 + DEFENSE_LEN, T)] = True

    return np.where(defensive, FLOOR, 1.0)


def main():
    lines = ["# Audit adversarial — Overlay défensif faux breakout Donchian", "",
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
        p_orig = failed_breakout_position(close)
        p_indep = independent_failed_breakout_position(close)
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
        p_before = failed_breakout_position(close)
        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(37)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        p_after = failed_breakout_position(close_pert)
        identical = bool(np.array_equal(p_before[:cut], p_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture économique du FAIL** : le signal se déclenche ~35-37% du temps sur "
                 "tous les marchés (fréquence homogène, cohérente avec un breakout Donchian 20j "
                 "étant un événement fréquent -- cf. #40) mais la réduction défensive à 0.5x coupe "
                 "l'exposition sur des phases qui restent en moyenne haussières (Buy&Hold reste "
                 "positif sur le long terme sur les 5 marchés) : le coût d'opportunité du manque à "
                 "gagner dépasse largement la protection de drawdown apportée (MDD quasi inchangé "
                 "voire légèrement amélioré, jamais suffisant pour compenser le rendement total "
                 "perdu). Seul le DAX, le marché le plus erratique/le moins tendanciel de "
                 "l'échantillon, bénéficie marginalement de la réduction défensive.")

    out = ROOT / "results" / "nonml_failed_breakout_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
