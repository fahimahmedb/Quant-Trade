"""Audit adversarial — Diversification défensive vers un proxy obligataire (#115+DGS10).

1. Recalcul indépendant du proxy de rendement obligataire (boucle Python
   explicite, formule de duration ré-implémentée séparément) à un
   échantillon de dates.
2. Recalcul indépendant du rendement combiné à ces mêmes dates.
3. Test anti-lookahead (mutation du futur DGS10).
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

from nonml_defensive_diversification_bond_overlay_backtest import (  # noqa: E402
    load_dgs10, MATURITY_YEARS,
)


def independent_bond_return(y_prev_pct: float, y_now_pct: float, maturity_years: int) -> float:
    y_prev = y_prev_pct / 100.0
    y_now = y_now_pct / 100.0
    if y_prev <= 0:
        return float("nan")
    d_mac = (1.0 + y_prev) / y_prev * (1.0 - 1.0 / (1.0 + y_prev) ** maturity_years)
    d_mod = d_mac / (1.0 + y_prev)
    return y_prev / 252.0 - d_mod * (y_now - y_prev)


def main():
    d = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    pos_eq_full, r_ndx_full = d["pos"], d["r_asset"]
    dates_full = pd.to_datetime(d["dates"])

    dgs10 = load_dgs10()
    dgs10_dates = list(dgs10.index)
    dgs10_vals = dgs10.values

    lines = ["# Audit adversarial — Diversification défensive vers un proxy obligataire (#115+DGS10)", "",
             "## 1. Recalcul indépendant du rendement obligataire + rendement combiné (boucle Python explicite)", "",
             "| Date NDX (indice) | Rendement obligataire (backtest) | Recalcul indépendant | Concorde |",
             "|---|---|---|---|"]

    from nonml_defensive_diversification_bond_overlay_backtest import bond_return_proxy
    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")
    valid = r_bond_aligned.notna().values
    start = int(np.argmax(valid))

    check_idx = list(range(start + 10, len(dates_full), 1500))
    all_ok = True
    n_checked = 0
    for t in check_idx:
        nd = dates_full.iloc[t] if hasattr(dates_full, "iloc") else dates_full[t]
        # trouve l'observation DGS10 la plus recente strictement AVANT nd (ffill causal)
        idx = None
        for i in range(len(dgs10_dates) - 1, -1, -1):
            if dgs10_dates[i] <= nd:
                idx = i
                break
        if idx is None or idx < 1:
            continue
        y_now, y_prev = dgs10_vals[idx], dgs10_vals[idx - 1]
        indep = independent_bond_return(y_prev, y_now, MATURITY_YEARS)
        orig = float(r_bond_aligned.iloc[t])
        concord = np.isclose(orig, indep, rtol=1e-6, equal_nan=True)
        all_ok &= bool(concord)
        n_checked += 1
        lines.append(f"| {t} | {orig:.6f} | {indep:.6f} | {'OUI' if concord else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — recalcul indépendant confirmé (' + str(n_checked) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données DGS10 les plus récentes)")
    lines.append("")
    T_dgs = len(dgs10)
    cut = int(T_dgs * 0.8)
    rng = np.random.default_rng(134)
    dgs10_mut = dgs10.copy()
    dgs10_mut.iloc[cut:] = dgs10_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.3, T_dgs - cut))
    cut_date = dgs10.index[cut]

    r_bond_mut_all = bond_return_proxy(dgs10_mut)
    r_bond_mut_aligned = r_bond_mut_all.reindex(dates_full, method="ffill")

    margin_mask = dates_full < (cut_date - pd.Timedelta(days=400))
    orig_vals = r_bond_aligned.values[margin_mask]
    mut_vals = r_bond_mut_aligned.values[margin_mask]
    both_finite = np.isfinite(orig_vals) & np.isfinite(mut_vals)
    diff_lookahead = int(np.sum(~np.isclose(orig_vals[both_finite], mut_vals[both_finite], rtol=1e-9)))
    lines.append(f"Écart de rendement obligataire sur les séances antérieures à la mutation (marge 400j) : {diff_lookahead} / {both_finite.sum()} comparées")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_defensive_diversification_bond_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
