"""Audit adversarial — Overlay vol-targeting gaté par la conjonction (ET)
kurtosis + ν Student-t.

Ce cycle combine deux portes DÉJÀ auditées indépendamment et intégralement
à leurs propres cycles (#219 : kurtosis recalculée par formule directe des
moments centrés, 0 désaccord ; #237 : ν recalculé par vraisemblance
manuelle + Nelder-Mead, fragilité documentée). Cet audit se concentre donc
sur ce qui est VRAIMENT nouveau ici : la combinaison logique ET et son
application au mécanisme #46 — vérifiée par recalcul indépendant de la
conjonction et de la position, plus un test anti-lookahead sur le pipeline
complet.
"""
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, quality_report  # noqa: E402
from nonml_kurtosis_vol_targeting_overlay_backtest import calm_kurtosis_mask  # noqa: E402
from nonml_student_t_tail_vol_targeting_overlay_backtest import (  # noqa: E402
    calm_nu_mask, NU_WINDOW, MEDIAN_WINDOW,
)
from nonml_kurtosis_nu_combined_vol_targeting_overlay_backtest import (  # noqa: E402
    combined_and_gate, combined_position, MARKETS,
)


def independent_and(gate_kurt: np.ndarray, gate_nu: np.ndarray) -> np.ndarray:
    """Recalcul independant de la conjonction, boucle explicite plutot
    que l'operateur vectorise `&` utilise dans le script principal."""
    n = len(gate_kurt)
    out = np.zeros(n, dtype=bool)
    for t in range(n):
        out[t] = bool(gate_kurt[t]) and bool(gate_nu[t])
    return out


def main():
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la conjonction (ET) kurtosis + ν Student-t", "",
             "Les deux sous-portes (kurtosis #219, ν Student-t #237) ont déjà été auditées "
             "intégralement à leurs propres cycles (0 désaccord pour la kurtosis ; fragilité "
             "numérique documentée mais anti-lookahead OK pour ν). Cet audit vérifie ce qui est "
             "nouveau : la conjonction logique ET et son application au mécanisme.", "",
             "## 1. Recalcul indépendant de la conjonction (boucle explicite booléenne, sans l'opérateur `&` vectorisé)", "",
             "| Marché | Désaccords conjonction (hors marge de fenêtre) | Séances comparées |",
             "|---|---|---|"]
    all_ok = True
    start = NU_WINDOW + MEDIAN_WINDOW
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        close = df["close"].values
        r = np.log(close[1:] / close[:-1])
        if len(r) <= start:
            continue

        gate_kurt = calm_kurtosis_mask(r)
        gate_nu = calm_nu_mask(r)
        gate_orig = combined_and_gate(r)
        gate_indep = independent_and(gate_kurt, gate_nu)
        n_diff = int(np.sum(gate_orig[start:] != gate_indep[start:]))
        n_total = len(gate_orig) - start
        all_ok &= (n_diff == 0)
        lines.append(f"| {name} | {n_diff} | {n_total} |")

    lines.append("")
    lines.append(f"**{'OK — conjonction confirmée par recalcul totalement indépendant.' if all_ok else 'Désaccords détectés.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur, close, pipeline complet)")
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
        if len(r) <= start:
            continue
        gate_before = combined_and_gate(r)
        pos_before = combined_position(r, gate_before)

        cut = len(r) // 2
        rng = np.random.default_rng(73)
        r_pert = r.copy()
        r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r) - cut)
        gate_after = combined_and_gate(r_pert)
        pos_after = combined_position(r_pert, gate_after)

        check_end = cut - start
        if check_end < 10:
            lines.append(f"| {name} | (fenêtre trop courte pour tester) |")
            continue
        identical = bool(np.allclose(pos_before[start:start + check_end], pos_after[start:start + check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_kurtosis_nu_combined_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
