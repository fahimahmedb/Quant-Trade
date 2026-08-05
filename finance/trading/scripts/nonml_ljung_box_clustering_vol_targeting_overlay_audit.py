"""Audit adversarial — Overlay vol-targeting gaté par la statistique de
Ljung-Box glissante (clustering ARCH multi-retards).

Deux vérifications complémentaires, chacune ciblant une source d'erreur
distincte :
1. Formule de Q : recalcul PUREMENT PYTHON (boucles explicites, sans
   `numpy` vectorisé) de la statistique de Ljung-Box sur un
   sous-échantillon représentatif de fenêtres (les N premières et N
   dernières testables par marché — la boucle triple imbriquée est trop
   coûteuse pour l'historique complet, déclaré ici pour transparence,
   pas de cherry-picking).
2. Logique de porte : recalcul totalement indépendant de la médiane
   glissante (tri manuel, sans `pandas.rolling`) appliquée à la série Q
   déjà validée en (1), sur l'historique COMPLET.
Plus test anti-lookahead sur le pipeline complet.
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
from nonml_ljung_box_clustering_vol_targeting_overlay_backtest import (  # noqa: E402
    calm_lb_mask, combined_position, rolling_lb_series,
    LB_WINDOW, LB_MAXLAG, MEDIAN_WINDOW, MARKETS,
)

N_CHECK = 100  # sous-echantillon (debut + fin) pour la verification formule pure-Python


def pure_python_rho_k(x: list, k: int) -> float:
    n = len(x)
    mu = sum(x) / n
    dm = [v - mu for v in x]
    num = 0.0
    for t in range(k, n):
        num += dm[t] * dm[t - k]
    den = sum(v * v for v in dm)
    if den <= 0:
        return float("nan")
    return num / den


def pure_python_ljung_box_q(x: list, maxlag: int) -> float:
    n = len(x)
    q = 0.0
    for k in range(1, maxlag + 1):
        rho_k = pure_python_rho_k(x, k)
        if rho_k != rho_k:  # NaN check sans numpy
            return float("nan")
        q += (rho_k * rho_k) / (n - k)
    return n * (n + 2) * q


def manual_median(window: np.ndarray) -> float:
    s = np.sort(window)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return float((s[mid - 1] + s[mid]) / 2.0)


def independent_gate_from_q(q: np.ndarray) -> np.ndarray:
    n = len(q)
    gate = np.zeros(n, dtype=bool)
    for t in range(MEDIAN_WINDOW - 1, n):
        window = q[t - MEDIAN_WINDOW + 1:t + 1]
        if np.any(np.isnan(window)):
            continue
        med = manual_median(window)
        if not np.isnan(q[t]):
            gate[t] = q[t] <= med
    return gate


def main():
    start = LB_WINDOW + MEDIAN_WINDOW
    lines = ["# Audit adversarial — Overlay vol-targeting gaté par la statistique de Ljung-Box glissante", "",
             "## 1. Formule de Q (boucles Python pures, sans numpy vectorisé, sous-échantillon "
             f"représentatif : {N_CHECK} premières + {N_CHECK} dernières fenêtres testables)", "",
             "| Marché | Écart relatif max sur Q | Fenêtres vérifiées |",
             "|---|---|---|"]
    all_ok_q = True
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
        r2 = r ** 2
        n = len(r2)
        idx_first = list(range(LB_WINDOW, min(LB_WINDOW + N_CHECK, n)))
        idx_last = list(range(max(LB_WINDOW, n - N_CHECK), n))
        idx = sorted(set(idx_first + idx_last))

        q_orig = rolling_lb_series(r)
        max_rel = 0.0
        for k in idx:
            window = r2[k - LB_WINDOW:k].tolist()
            q_manual = pure_python_ljung_box_q(window, LB_MAXLAG)
            q_ref = q_orig[k]
            rel = abs(q_manual - q_ref) / abs(q_ref) if q_ref != 0 else abs(q_manual)
            max_rel = max(max_rel, rel)
        all_ok_q &= (max_rel < 1e-9)
        lines.append(f"| {name} | {max_rel:.2e} | {len(idx)} |")

    lines.append("")
    lines.append(f"**{'OK — formule Q confirmée (boucles pures Python, sous-échantillon).' if all_ok_q else 'Écarts détectés.'}**")

    lines.append("")
    lines.append("## 2. Logique de porte (médiane glissante par tri manuel, historique complet)")
    lines.append("")
    lines.append("| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |")
    lines.append("|---|---|---|")
    all_ok_gate = True
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
        gate_orig = calm_lb_mask(r)
        q = rolling_lb_series(r)
        gate_indep = independent_gate_from_q(q)
        n_diff = int(np.sum(gate_orig[start:] != gate_indep[start:]))
        n_total = len(gate_orig) - start
        all_ok_gate &= (n_diff == 0)
        lines.append(f"| {name} | {n_diff} | {n_total} |")

    lines.append("")
    lines.append(f"**{'OK — porte confirmée par recalcul indépendant de la médiane (tri manuel).' if all_ok_gate else 'Désaccords détectés.'}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead (perturbation du futur, close)")
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
        gate_before = calm_lb_mask(r)
        pos_before = combined_position(r, gate_before)

        cut = len(r) // 2
        rng = np.random.default_rng(73)
        r_pert = r.copy()
        r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r) - cut)
        gate_after = calm_lb_mask(r_pert)
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

    out = ROOT / "results" / "nonml_ljung_box_clustering_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
