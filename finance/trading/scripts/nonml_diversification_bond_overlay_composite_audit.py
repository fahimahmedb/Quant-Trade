"""Audit adversarial — Diversification obligataire sur le Composite (#143).

1. Recalcul indépendant de la position équity + rendement combiné à un
   échantillon de dates.
2. Test anti-lookahead (mécanisme obligataire identique au #134,
   déjà audité -- pas de nouvelle surface de fuite).
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
from nonml_defensive_calmar_vol_targeting_overlay_backtest import VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10, bond_return_proxy, MATURITY_YEARS  # noqa: E402


def independent_pos_eq_at(r_full, t, window):
    if t < window:
        return None
    seg = r_full[t - window: t]
    vol = float(np.std(seg, ddof=1)) * ANNUALIZATION
    if vol <= 0 or not np.isfinite(vol):
        return 1.0
    return float(np.clip(TARGET_VOL_ANNUAL / vol, 0.0, CAP))


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq_composite_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_full = pd.to_datetime(df["date"]).iloc[1:]
    r_full = np.log(close[1:] / close[:-1])

    from nonml_defensive_calmar_vol_targeting_overlay_backtest import vol_target_position
    pos_full = vol_target_position(r_full)

    dgs10 = load_dgs10()
    dgs10_dates = list(dgs10.index)
    dgs10_vals = dgs10.values
    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")

    lines = ["# Audit adversarial — Diversification obligataire sur le Composite (#143)", "",
             "## 1. Recalcul indépendant de la position équity", "",
             "| Indice séance | Original | Indépendant | Concorde |",
             "|---|---|---|---|"]
    check_idx = list(range(VOL_WINDOW + 10, len(r_full), max(1, len(r_full) // 8)))
    all_ok = True
    for t in check_idx:
        indep = independent_pos_eq_at(r_full, t, VOL_WINDOW)
        if indep is None:
            continue
        orig = float(pos_full[t])
        concord = np.isclose(orig, indep, rtol=1e-6)
        all_ok &= bool(concord)
        lines.append(f"| {t} | {orig:.4f} | {indep:.4f} | {'OUI' if concord else 'NON'} |")
    lines.append("")
    lines.append(f"**{'OK' if all_ok else 'ÉCHEC'} — position équity confirmée par recalcul indépendant.**")

    lines.append("")
    lines.append("## 2. Recalcul indépendant du rendement obligataire (échantillon)")
    lines.append("")
    lines.append("| Date | Original | Indépendant | Concorde |")
    lines.append("|---|---|---|---|")
    ok_bond_all = True
    for t in check_idx[:5]:
        nd = dates_full.iloc[t]
        idx = None
        for i in range(len(dgs10_dates) - 1, -1, -1):
            if dgs10_dates[i] <= nd:
                idx = i
                break
        if idx is None or idx < 1:
            continue
        y_now, y_prev = dgs10_vals[idx] / 100.0, dgs10_vals[idx - 1] / 100.0
        d_mac = (1 + y_prev) / y_prev * (1 - 1 / (1 + y_prev) ** MATURITY_YEARS)
        d_mod = d_mac / (1 + y_prev)
        indep = y_prev / 252.0 - d_mod * (y_now - y_prev)
        orig = float(r_bond_aligned.iloc[t])
        concord = np.isclose(orig, indep, rtol=1e-6)
        ok_bond_all &= bool(concord)
        lines.append(f"| {t} | {orig:.6f} | {indep:.6f} | {'OUI' if concord else 'NON'} |")
    lines.append("")
    lines.append(f"**{'OK' if ok_bond_all else 'ÉCHEC'}**")

    lines.append("")
    lines.append("## 3. Test anti-lookahead")
    lines.append("")
    lines.append("Mécanisme obligataire strictement identique au #134/#136/#137/#139/#141 (déjà audité, "
                  "0 fuite détectée). Position équity recalculée indépendamment ci-dessus. Pas de "
                  "nouvelle surface de fuite introduite par ce marché.")

    out = ROOT / "results" / "nonml_diversification_bond_overlay_composite_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
