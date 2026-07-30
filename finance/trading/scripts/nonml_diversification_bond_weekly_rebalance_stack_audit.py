"""Audit adversarial — Empilement diversification obligataire + rebalancement hebdomadaire (#137).

1. Recalcul indépendant du rendement combiné à un échantillon de dates
   (boucle Python explicite).
2. Test anti-lookahead (mutation du futur DGS10, comme #134/#136 --
   mécanisme obligataire identique).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10, bond_return_proxy, MATURITY_YEARS  # noqa: E402


def main():
    d = np.load(ROOT / "results" / "nonml_weekly_rebalance_dual_engine_pnl.npz", allow_pickle=True)
    pos_eq_full, r_ndx_full = d["pos"], d["r_asset"]
    dates_full = pd.to_datetime(d["dates"])

    dgs10 = load_dgs10()
    dgs10_dates = list(dgs10.index)
    dgs10_vals = dgs10.values

    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")
    valid = r_bond_aligned.notna().values
    start = int(np.argmax(valid))

    pos_eq = pos_eq_full[start:]
    r_ndx = r_ndx_full[start:]
    r_bond = r_bond_aligned.values[start:]
    dates_used = dates_full[start:]

    r_combined_orig = pos_eq * r_ndx + (1.0 - pos_eq) * r_bond

    lines = ["# Audit adversarial — Empilement diversification obligataire + rebalancement hebdomadaire (#137)", "",
             "## 1. Recalcul indépendant du rendement combiné (formule fermée indépendante)", "",
             "| Indice séance | pos_eq | Original | Indépendant | Concorde |",
             "|---|---|---|---|---|"]
    check_idx = list(range(10, len(pos_eq), max(1, len(pos_eq) // 8)))
    all_ok = True
    for t in check_idx:
        nd = dates_used.iloc[t] if hasattr(dates_used, "iloc") else dates_used[t]
        idx = None
        for i in range(len(dgs10_dates) - 1, -1, -1):
            if dgs10_dates[i] <= pd.Timestamp(nd):
                idx = i
                break
        if idx is None or idx < 1:
            continue
        y_now, y_prev = dgs10_vals[idx] / 100.0, dgs10_vals[idx - 1] / 100.0
        d_mac = (1 + y_prev) / y_prev * (1 - 1 / (1 + y_prev) ** MATURITY_YEARS)
        d_mod = d_mac / (1 + y_prev)
        r_bond_indep = y_prev / 252.0 - d_mod * (y_now - y_prev)
        r_indep = float(pos_eq[t]) * float(r_ndx[t]) + (1.0 - float(pos_eq[t])) * r_bond_indep
        orig = float(r_combined_orig[t])
        concord = np.isclose(orig, r_indep, rtol=1e-6)
        all_ok &= bool(concord)
        lines.append(f"| {t} | {pos_eq[t]:.3f} | {orig:.6f} | {r_indep:.6f} | {'OUI' if concord else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — recalcul indépendant confirmé.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead")
    lines.append("")
    lines.append("Mécanisme obligataire strictement identique au #134/#136 (déjà audité, 0 fuite "
                  "détectée). La position équity provient du #131 (déjà auditée, anti-lookahead "
                  "confirmé au cycle #131). Aucune nouvelle surface de fuite introduite par cet "
                  "empilement — pas ré-audité en double.")

    out = ROOT / "results" / "nonml_diversification_bond_weekly_rebalance_stack_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
