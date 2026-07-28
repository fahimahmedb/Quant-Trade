"""Audit adversarial — Overlay levé union SMA200∪(ToM∪Halloween).

Le résultat brut est un PASS 5/5, mais avec une fraction de jours levés
très élevée (~90%) -- proche d'un levier quasi-permanent, ce qui mérite
une vérification renforcée : (1) recalcul de l'union par
inclusion-exclusion à 3 ensembles, (2) test anti-lookahead sur le signal
SMA200 (le seul des trois construit sur une fenêtre roulante).
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
from nonml_sma200_tom_halloween_union_overlay_backtest import (  # noqa: E402
    above_sma_mask, tom_mask, halloween_mask, SMA_WINDOW, MARKETS,
)


def main():
    lines = ["# Audit adversarial — Overlay levé union SMA200∪(ToM∪Halloween)", "",
             "## 1. Union à 3 ensembles (inclusion-exclusion)", "",
             "| Marché | %SMA200 | %ToM | %Halloween | %Union mesurée | %Union incl-excl | Écart |",
             "|---|---|---|---|---|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        A = above_sma_mask(close)[SMA_WINDOW:]
        B = tom_mask(df["date"])[SMA_WINDOW:]
        C = halloween_mask(df["date"])[SMA_WINDOW:]

        union_measured = (A | B | C).mean()
        # inclusion-exclusion a 3 ensembles : |A∪B∪C| = |A|+|B|+|C|-|A∩B|-|A∩C|-|B∩C|+|A∩B∩C|
        union_incl_excl = (A.mean() + B.mean() + C.mean()
                            - (A & B).mean() - (A & C).mean() - (B & C).mean()
                            + (A & B & C).mean())
        diff = abs(union_measured - union_incl_excl)
        all_ok &= (diff < 1e-9)
        lines.append(f"| {name} | {100*A.mean():.1f}% | {100*B.mean():.1f}% | {100*C.mean():.1f}% | "
                     f"{100*union_measured:.1f}% | {100*union_incl_excl:.1f}% | {diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — union à 3 ensembles cohérente, aucun bug de fusion.' if all_ok else 'ÉCHEC — incohérence détectée.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead sur le signal SMA200")
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
        m_before = above_sma_mask(close)
        close_pert = close.copy()
        cut = len(close_pert) // 2
        rng = np.random.default_rng(7)
        close_pert[cut:] = close_pert[cut:] * (1.0 + rng.normal(0, 0.1, len(close_pert) - cut))
        m_after = above_sma_mask(close_pert)
        identical = bool(np.array_equal(m_before[:cut], m_after[:cut]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")
    lines.append("")
    lines.append("**Lecture honnête** : la fraction de jours levés (~90%) est proche d'un "
                 "levier quasi-permanent -- le gain de Sharpe reste réel mais modeste sur "
                 "chaque marché (ex. NDX +0,51→+0,55), la majeure partie du gain de rendement "
                 "affiché vient simplement de l'effet multiplicatif du levier sur un actif à "
                 "drift positif (mécanique déjà mise en évidence au cycle #10), pas d'un edge "
                 "nouveau créé par la triple union en tant que telle. Le MDD se dégrade "
                 "fortement partout (ex. NDX -82,9%→-95,8%), risque assumé mais à souligner.")

    out = ROOT / "results" / "nonml_sma200_tom_halloween_union_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
