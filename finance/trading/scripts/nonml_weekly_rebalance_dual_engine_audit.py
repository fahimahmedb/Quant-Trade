"""Audit adversarial — Rebalancement hebdomadaire du mécanisme #121.

1. Recalcul indépendant de la position hebdomadaire (boucle Python
   explicite indépendante de `weekly_hold_position`) à un échantillon
   de dates.
2. Test anti-lookahead (mutation du futur de la position quotidienne
   source) -- le passé de la version hebdomadaire ne doit PAS bouger.
3. Vérification turnover : la version hebdomadaire ne doit changer
   qu'aux multiples de REBAL_FREQ.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_weekly_rebalance_dual_engine_backtest import REBAL_FREQ, weekly_hold_position  # noqa: E402


def independent_weekly_at(pos_daily, t, freq):
    last_rebal = (t // freq) * freq
    return pos_daily[last_rebal]


def main():
    d = np.load(ROOT / "results" / "nonml_dual_engine_defensive_overlay_pnl.npz", allow_pickle=True)
    pos_daily = d["pos"]
    T = len(pos_daily)

    pos_weekly = weekly_hold_position(pos_daily, REBAL_FREQ)

    check_idx = list(range(0, T, 733))
    lines = ["# Audit adversarial — Rebalancement hebdomadaire du mécanisme #121", "",
             "## 1. Recalcul indépendant de la position hebdomadaire (formule fermée, indépendante de la boucle du backtest)", "",
             "| Indice séance | Concorde |",
             "|---|---|"]
    all_ok = True
    for t in check_idx:
        indep = independent_weekly_at(pos_daily, t, REBAL_FREQ)
        orig = pos_weekly[t]
        concord = np.isclose(orig, indep)
        all_ok &= bool(concord)
        lines.append(f"| {t} | {'OUI' if concord else 'NON'} |")
    lines.append("")
    lines.append(f"**{'OK — position hebdomadaire confirmée par recalcul indépendant (' + str(len(check_idx)) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de positions quotidiennes les plus récentes)")
    lines.append("")
    cut = int(T * 0.8)
    rng = np.random.default_rng(131)
    pos_daily_mut = pos_daily.copy()
    pos_daily_mut[cut:] = pos_daily_mut[cut:] * (1.0 + rng.normal(0, 0.3, T - cut))
    pos_daily_mut = np.clip(pos_daily_mut, 0.0, 5.0)

    pos_weekly_mut = weekly_hold_position(pos_daily_mut, REBAL_FREQ)
    margin = REBAL_FREQ * 3
    diff_lookahead = int(np.sum(pos_weekly[: cut - margin] != pos_weekly_mut[: cut - margin]))
    lines.append(f"Écart de position hebdo sur les séances antérieures à la mutation (marge {margin} séances) : {diff_lookahead}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    lines.append("")
    lines.append("## 3. Vérification turnover : changements uniquement aux multiples de REBAL_FREQ")
    lines.append("")
    changes = np.where(np.diff(pos_weekly) != 0)[0] + 1
    bad_changes = [int(c) for c in changes if c % REBAL_FREQ != 0]
    lines.append(f"Changements de position hebdo hors multiples de {REBAL_FREQ} : {len(bad_changes)} / {len(changes)} changements totaux")
    lines.append(f"**{'OK — tous les changements tombent sur un multiple de REBAL_FREQ.' if not bad_changes else 'ÉCHEC — changement hors calendrier détecté.'}**")

    out = ROOT / "results" / "nonml_weekly_rebalance_dual_engine_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
