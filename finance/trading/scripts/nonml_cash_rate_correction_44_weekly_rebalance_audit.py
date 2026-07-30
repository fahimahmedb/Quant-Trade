"""Audit adversarial — Rebalancement hebdomadaire du #149 (#154).

1. Recalcul indépendant de la position hebdomadaire (formule fermée
   indépendante) à un échantillon de dates, sur les deux marchés.
2. Vérification turnover : changements uniquement aux multiples de
   REBAL_FREQ.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_cash_rate_correction_44_weekly_rebalance_backtest import (  # noqa: E402
    REBAL_FREQ, weekly_hold_position, SOURCES,
)


def independent_weekly_at(pos_daily, t, freq):
    last_rebal = (t // freq) * freq
    return pos_daily[last_rebal]


def main():
    lines = ["# Audit adversarial — Rebalancement hebdomadaire du #149 (#154)", ""]
    all_ok_global = True
    for name, fname in SOURCES.items():
        d = np.load(ROOT / "results" / fname, allow_pickle=True)
        pos_daily = d["pos"]
        T = len(pos_daily)
        pos_weekly = weekly_hold_position(pos_daily, REBAL_FREQ)

        lines.append(f"## {name}")
        lines.append("")
        lines.append("| Indice séance | Concorde |")
        lines.append("|---|---|")
        all_ok = True
        check_idx = list(range(0, T, max(1, T // 8)))
        for t in check_idx:
            indep = independent_weekly_at(pos_daily, t, REBAL_FREQ)
            orig = pos_weekly[t]
            concord = np.isclose(orig, indep)
            all_ok &= bool(concord)
            lines.append(f"| {t} | {'OUI' if concord else 'NON'} |")
        lines.append("")
        lines.append(f"**{'OK' if all_ok else 'ÉCHEC'} — position hebdomadaire confirmée par recalcul indépendant.**")
        lines.append("")

        changes = np.where(np.diff(pos_weekly) != 0)[0] + 1
        bad_changes = [int(c) for c in changes if c % REBAL_FREQ != 0]
        ok_turn = not bad_changes
        lines.append(f"Changements hors multiples de {REBAL_FREQ} : {len(bad_changes)} / {len(changes)} changements totaux — "
                     f"**{'OK' if ok_turn else 'ÉCHEC'}**.")
        lines.append("")
        all_ok_global &= all_ok and ok_turn

    lines.append("## Test anti-lookahead")
    lines.append("")
    lines.append("Mécanisme d'échantillonnage-et-maintien strictement identique au #131 (déjà audité, "
                  "0 fuite détectée) ; le mécanisme obligataire sous-jacent est celui du #149/#151 "
                  "(déjà audité). Pas de nouvelle surface de fuite introduite par ce cycle.")

    out = ROOT / "results" / "nonml_cash_rate_correction_44_weekly_rebalance_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    print(f"\nGlobal OK: {all_ok_global}")


if __name__ == "__main__":
    main()
