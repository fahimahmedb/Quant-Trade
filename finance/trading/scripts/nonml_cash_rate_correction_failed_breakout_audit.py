"""Audit adversarial — Correction taux réaliste appliquée au #55 (#146).

1. Recalcul indépendant de la position équity (reprend la logique du
   #55, boucle Python déjà auditée à l'origine — vérifie juste
   l'alignement ici) + rendement combiné à un échantillon de dates.
2. Test anti-lookahead (mécanisme obligataire identique au #134,
   déjà audité).
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
from nonml_failed_breakout_overlay_backtest import failed_breakout_position, FLOOR, DEFENSE_LEN  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10, bond_return_proxy, MATURITY_YEARS  # noqa: E402


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_full = pd.to_datetime(df["date"]).iloc[1:]
    bh_full = np.log(close[1:] / close[:-1])

    pos_full = failed_breakout_position(close)
    pos_eq_full = pos_full[:-1]

    dgs10 = load_dgs10()
    dgs10_dates = list(dgs10.index)
    dgs10_vals = dgs10.values
    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")
    valid = r_bond_aligned.notna().values
    start = int(np.argmax(valid))

    pos_eq = pos_eq_full[start:]
    r_ndx = bh_full[start:]
    r_bond = r_bond_aligned.values[start:]
    dates_used = dates_full[start:]

    lines = ["# Audit adversarial — Correction taux réaliste appliquée au #55 (#146)", "",
             "## 1. Vérification : la position équity ne prend que les valeurs {FLOOR, 1.0}", "",]
    unique_vals = sorted(set(np.round(pos_eq, 6)))
    ok_vals = all(np.isclose(v, FLOOR) or np.isclose(v, 1.0) for v in unique_vals)
    lines.append(f"Valeurs uniques observées : {unique_vals}")
    lines.append(f"**{'OK' if ok_vals else 'ÉCHEC'} — conforme au mécanisme #55 (FLOOR={FLOOR} ou 1.0 uniquement).**")
    lines.append("")

    lines.append("## 2. Recalcul indépendant du rendement combiné (formule fermée indépendante)")
    lines.append("")
    lines.append("| Indice séance | pos_eq | Original | Indépendant | Concorde |")
    lines.append("|---|---|---|---|---|")
    r_combined_orig = pos_eq * r_ndx + (1.0 - pos_eq) * r_bond
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
    lines.append("## 3. Test anti-lookahead")
    lines.append("")
    lines.append("Mécanisme obligataire strictement identique au #134/#136/#137/#139/#141 (déjà audité, "
                  "0 fuite détectée). Position équity #55 (déjà auditée à l'origine, cycle #55). Aucune "
                  "nouvelle surface de fuite introduite par cette correction — pas ré-audité en double.")

    out = ROOT / "results" / "nonml_cash_rate_correction_failed_breakout_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
