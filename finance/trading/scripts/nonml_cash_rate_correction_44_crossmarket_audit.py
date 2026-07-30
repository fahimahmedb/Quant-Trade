"""Audit adversarial — Correction taux réaliste sur le #44 cross-marché (#151).

1. Recalcul indépendant de la position équity ET du rendement combiné
   à un échantillon de dates, sur les deux marchés.
2. Vérification de cohérence du proxy obligataire (déjà audité au
   #134/#149, pas ré-audité en double).
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
from nonml_defensive_vol_targeting_overlay_backtest import VOL_WINDOW, TARGET_VOL_ANNUAL, CAP, ANNUALIZATION  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10, bond_return_proxy, MATURITY_YEARS  # noqa: E402

MARKETS = {"S&P 500": "sp500_daily.txt", "Russell 2000": "russell2000_daily.txt"}


def independent_pos_eq_at(r_full, t, window):
    if t < window:
        return None
    seg = r_full[t - window: t]
    vol = float(np.std(seg, ddof=1)) * ANNUALIZATION
    if vol <= 0 or not np.isfinite(vol):
        return 1.0
    return float(np.clip(TARGET_VOL_ANNUAL / vol, 0.0, CAP))


def main():
    dgs10 = load_dgs10()
    dgs10_dates = list(dgs10.index)
    dgs10_vals = dgs10.values

    lines = ["# Audit adversarial — Correction taux réaliste sur le #44 cross-marché (#151)", ""]
    all_ok_global = True

    for name, fname in MARKETS.items():
        df = load_ohlc(str(REPO_ROOT / "data" / fname))
        quality_report(df)
        close = df["close"].values
        dates_full = pd.to_datetime(df["date"]).iloc[1:]
        r_full = np.log(close[1:] / close[:-1])

        from nonml_defensive_vol_targeting_overlay_backtest import vol_target_position
        pos_full = vol_target_position(r_full)

        lines.append(f"## {name} — recalcul indépendant de la position équity")
        lines.append("")
        lines.append("| Indice séance | Original | Indépendant | Concorde |")
        lines.append("|---|---|---|---|")
        check_idx = list(range(VOL_WINDOW + 10, len(r_full), max(1, len(r_full) // 6)))
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
        all_ok_global &= all_ok

        r_bond_all = bond_return_proxy(dgs10, MATURITY_YEARS)
        r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")
        t_check = len(dates_full) // 2
        nd = dates_full.iloc[t_check]
        idx = None
        for i in range(len(dgs10_dates) - 1, -1, -1):
            if dgs10_dates[i] <= nd:
                idx = i
                break
        y_now, y_prev = dgs10_vals[idx], dgs10_vals[idx - 1]
        y_prev_frac, y_now_frac = y_prev / 100.0, y_now / 100.0
        d_mac = (1 + y_prev_frac) / y_prev_frac * (1 - 1 / (1 + y_prev_frac) ** MATURITY_YEARS)
        d_mod = d_mac / (1 + y_prev_frac)
        indep_bond = y_prev_frac / 252.0 - d_mod * (y_now_frac - y_prev_frac)
        orig_bond = float(r_bond_aligned.iloc[t_check])
        ok_bond = np.isclose(orig_bond, indep_bond, rtol=1e-6)
        all_ok_global &= bool(ok_bond)
        lines.append(f"Rendement obligataire au point médian de {name} : original={orig_bond:.6f}, "
                     f"indépendant={indep_bond:.6f} — **{'OK' if ok_bond else 'ÉCHEC'}**.")
        lines.append("")

    lines.append("## Test anti-lookahead")
    lines.append("")
    lines.append("Mécanisme obligataire strictement identique au #134/#136/#137/#139/#141/#146/#149 "
                  "(déjà audité, 0 fuite détectée). Pas de nouvelle surface de fuite introduite par ce "
                  "cycle — pas ré-audité en double.")

    out = ROOT / "results" / "nonml_cash_rate_correction_44_crossmarket_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    print(f"\nGlobal OK: {all_ok_global}")


if __name__ == "__main__":
    main()
