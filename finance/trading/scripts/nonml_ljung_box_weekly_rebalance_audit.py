"""Audit adversarial — Rebalancement hebdomadaire de la porte Ljung-Box
(#242).

La porte Ljung-Box elle-même a déjà son propre audit complet au #242
(formule Q vérifiée par boucles Python pures, logique de porte par
médiane manuelle, 0 désaccord). Cet audit se concentre sur ce qui est
nouveau ici : le ré-échantillonnage hebdomadaire lui-même — recalcul
indépendant de `weekly_hold_position` (boucle explicite alternative) et
test anti-lookahead sur le pipeline complet.
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
    calm_lb_mask, combined_position, LB_WINDOW, MEDIAN_WINDOW,
)
from nonml_ljung_box_weekly_rebalance_backtest import (  # noqa: E402
    weekly_hold_position, MARKET_FILE, REBAL_FREQ,
)


def independent_weekly_hold(pos_daily: np.ndarray, freq: int) -> np.ndarray:
    """Recalcul independant : reconstruit les dates de rebalancement par
    liste explicite (range) plutot que le test de modulo `t % freq == 0`,
    puis propage forward par np.repeat/troncature (methode differente)."""
    T = len(pos_daily)
    rebal_idx = list(range(0, T, freq))
    pos_w = np.empty(T)
    for i, idx0 in enumerate(rebal_idx):
        idx1 = rebal_idx[i + 1] if i + 1 < len(rebal_idx) else T
        pos_w[idx0:idx1] = pos_daily[idx0]
    return pos_w


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    close = df["close"].values
    r_full = np.log(close[1:] / close[:-1])
    start = LB_WINDOW + MEDIAN_WINDOW

    gate = calm_lb_mask(r_full)
    pos_daily_full = combined_position(r_full, gate)
    pos_daily = pos_daily_full[start:]

    pos_weekly_orig = weekly_hold_position(pos_daily, REBAL_FREQ)
    pos_weekly_indep = independent_weekly_hold(pos_daily, REBAL_FREQ)
    max_diff = float(np.max(np.abs(pos_weekly_orig - pos_weekly_indep)))

    lines = ["# Audit adversarial — Rebalancement hebdomadaire de la porte Ljung-Box (#242)", "",
             "## 1. Recalcul indépendant du ré-échantillonnage hebdomadaire (reconstruction "
             "explicite des dates de rebalancement, méthode différente du test modulo)", "",
             f"Écart position max : {max_diff:.2e}",
             "",
             f"**{'OK — ré-échantillonnage confirmé par recalcul indépendant.' if max_diff < 1e-12 else 'ÉCHEC.'}**",
             "",
             "## 2. Test anti-lookahead (perturbation du futur, close, pipeline complet)",
             ""]

    cut = len(r_full) // 2
    rng = np.random.default_rng(73)
    r_pert = r_full.copy()
    r_pert[cut:] = r_pert[cut:] + rng.normal(0, 0.02, len(r_full) - cut)

    gate_before = calm_lb_mask(r_full)
    pos_before_daily = combined_position(r_full, gate_before)[start:]
    pos_before_weekly = weekly_hold_position(pos_before_daily, REBAL_FREQ)

    gate_after = calm_lb_mask(r_pert)
    pos_after_daily = combined_position(r_pert, gate_after)[start:]
    pos_after_weekly = weekly_hold_position(pos_after_daily, REBAL_FREQ)

    check_end = cut - start
    identical = bool(np.allclose(pos_before_weekly[:check_end], pos_after_weekly[:check_end]))
    lines.append(f"Décisions passées identiques après perturbation future : {'OUI' if identical else 'NON — FUITE DETECTEE'}")
    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if identical else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_ljung_box_weekly_rebalance_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
