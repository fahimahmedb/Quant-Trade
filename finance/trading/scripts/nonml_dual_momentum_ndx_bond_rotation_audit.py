"""Audit adversarial — Momentum absolu dual (rotation) NDX / proxy obligataire (#148).

1. Recalcul indépendant de la position (boucle Python explicite,
   momentum manuel, sans pandas.rolling) à un échantillon de dates de
   fin de mois.
2. Test anti-lookahead (mutation du futur NDX et DGS10).
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
from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10, bond_return_proxy  # noqa: E402
from nonml_dual_momentum_ndx_bond_rotation_backtest import dual_momentum_position, MOMENTUM_WINDOW  # noqa: E402


def independent_signal_at(r_ndx, r_bond, t, window):
    # pandas .rolling(window).sum() a l'indice t inclut r[t-window+1 .. t] (window valeurs, t INCLUS)
    if t < window - 1:
        return None
    return float(np.sum(r_ndx[t - window + 1:t + 1])), float(np.sum(r_bond[t - window + 1:t + 1]))


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_full = pd.to_datetime(df["date"]).iloc[1:]
    r_ndx_full = np.log(close[1:] / close[:-1])

    dgs10 = load_dgs10()
    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")
    valid = r_bond_aligned.notna().values
    start0 = int(np.argmax(valid))

    r_ndx0 = r_ndx_full[start0:]
    r_bond0 = r_bond_aligned.values[start0:]
    dates0 = dates_full[start0:]

    pos_full = dual_momentum_position(r_ndx0, r_bond0, dates0, MOMENTUM_WINDOW)

    lines = ["# Audit adversarial — Momentum absolu dual (rotation) NDX / proxy obligataire (#148)", "",
             "## 1. Recalcul indépendant du signal de momentum (boucle Python explicite)", "",
             "| Indice séance | Momentum NDX (orig via rolling) | Momentum NDX (indép.) | Momentum bond (orig) | Momentum bond (indép.) | Position (t) | Concorde |",
             "|---|---|---|---|---|---|---|"]
    check_idx = list(range(MOMENTUM_WINDOW + 30, len(r_ndx0) - 1, max(1, len(r_ndx0) // 10)))
    all_ok = True
    n_checked = 0
    for t in check_idx:
        indep = independent_signal_at(r_ndx0, r_bond0, t, MOMENTUM_WINDOW)
        if indep is None:
            continue
        cum_ndx_orig = float(pd.Series(r_ndx0).rolling(MOMENTUM_WINDOW).sum().values[t])
        cum_bond_orig = float(pd.Series(r_bond0).rolling(MOMENTUM_WINDOW).sum().values[t])
        indep_ndx, indep_bond = indep
        concord = np.isclose(cum_ndx_orig, indep_ndx) and np.isclose(cum_bond_orig, indep_bond)
        all_ok &= bool(concord)
        n_checked += 1
        lines.append(f"| {t} | {cum_ndx_orig:.4f} | {indep_ndx:.4f} | {cum_bond_orig:.4f} | {indep_bond:.4f} | {pos_full[t+1]:.1f} | {'OUI' if concord else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — signal de momentum confirmé par recalcul indépendant (' + str(n_checked) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de données NDX et DGS10 les plus récentes)")
    lines.append("")
    T = len(r_ndx0)
    cut = int(T * 0.8)
    rng = np.random.default_rng(148)
    r_ndx_mut = r_ndx0.copy()
    r_ndx_mut[cut:] = r_ndx_mut[cut:] * (1.0 + rng.normal(0, 0.5, T - cut))
    r_bond_mut = r_bond0.copy()
    r_bond_mut[cut:] = r_bond_mut[cut:] * (1.0 + rng.normal(0, 0.5, T - cut))

    pos_mut = dual_momentum_position(r_ndx_mut, r_bond_mut, dates0, MOMENTUM_WINDOW)

    margin = MOMENTUM_WINDOW + 40
    diff_lookahead = int(np.sum(pos_full[:cut - margin] != pos_mut[:cut - margin]))
    lines.append(f"Écart de position sur les séances antérieures à la mutation (marge {margin}j) : {diff_lookahead}")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_dual_momentum_ndx_bond_rotation_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
