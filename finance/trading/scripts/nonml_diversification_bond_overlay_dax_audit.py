"""Audit adversarial — Diversification obligataire sur DAX (#140).

1. Recalcul indépendant du rendement obligataire (taux allemand
   forward-fillé) + rendement combiné à un échantillon de dates.
2. Test anti-lookahead (mutation du futur taux allemand).
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
from nonml_diversification_bond_overlay_dax_backtest import (  # noqa: E402
    load_de10y_monthly, bund_return_proxy, MATURITY_YEARS,
)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "dax_daily.txt"))
    quality_report(df)
    dates_full = pd.to_datetime(df["date"]).iloc[1:]

    de10y = load_de10y_monthly()
    de10y_dates = list(de10y.index)
    de10y_vals = de10y.values
    de10y_daily = de10y.reindex(dates_full, method="ffill")
    r_bund_all = bund_return_proxy(de10y_daily)

    def latest_monthly_at_or_before(ts):
        idx = None
        for i in range(len(de10y_dates) - 1, -1, -1):
            if de10y_dates[i] <= ts:
                idx = i
                break
        return idx

    lines = ["# Audit adversarial — Diversification obligataire sur DAX (#140)", "",
             "## 1. Recalcul indépendant du rendement obligataire (taux allemand, forward-fill causal "
             "jour-à-jour : y_now = dernière observation mensuelle connue AU JOUR t, y_prev = dernière "
             "observation mensuelle connue AU JOUR t-1 -- identiques la plupart des jours, sauf au "
             "changement de mois)", "",
             "| Date DAX (indice) | Original | Indépendant | Concorde |",
             "|---|---|---|---|"]
    check_idx = list(range(300, len(dates_full), 800))
    all_ok = True
    n_checked = 0
    for t in check_idx:
        if t < 1:
            continue
        idx_now = latest_monthly_at_or_before(dates_full.iloc[t])
        idx_prev = latest_monthly_at_or_before(dates_full.iloc[t - 1])
        if idx_now is None or idx_prev is None:
            continue
        # bund_return_proxy(date_t) = y(date_{t-1})/252 - D_mod(y(date_{t-1}))*(y(date_t)-y(date_{t-1}))
        # ou y(date) = derniere observation MENSUELLE connue au jour "date" (forward-fill).
        y_now = de10y_vals[idx_now] / 100.0
        y_prev = de10y_vals[idx_prev] / 100.0
        d_mac = (1 + y_prev) / y_prev * (1 - 1 / (1 + y_prev) ** MATURITY_YEARS)
        d_mod = d_mac / (1 + y_prev)
        indep = y_prev / 252.0 - d_mod * (y_now - y_prev)
        orig = float(r_bund_all.iloc[t])
        concord = np.isclose(orig, indep, rtol=1e-6, equal_nan=True)
        all_ok &= bool(concord)
        n_checked += 1
        lines.append(f"| {t} | {orig:.6f} | {indep:.6f} | {'OUI' if concord else 'NON'} |")

    lines.append("")
    lines.append(f"**{'OK — recalcul indépendant confirmé (' + str(n_checked) + ' dates).' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (mutation des 20% de taux allemand les plus récents)")
    lines.append("")
    T = len(de10y)
    cut = int(T * 0.8)
    rng = np.random.default_rng(140)
    de10y_mut = de10y.copy()
    de10y_mut.iloc[cut:] = de10y_mut.iloc[cut:] * (1.0 + rng.normal(0, 0.3, T - cut))
    cut_date = de10y.index[cut]

    de10y_daily_mut = de10y_mut.reindex(dates_full, method="ffill")
    r_bund_mut = bund_return_proxy(de10y_daily_mut)

    margin_mask = dates_full < (cut_date - pd.Timedelta(days=60))
    orig_vals = r_bund_all.values[margin_mask]
    mut_vals = r_bund_mut.values[margin_mask]
    both_finite = np.isfinite(orig_vals) & np.isfinite(mut_vals)
    diff_lookahead = int(np.sum(~np.isclose(orig_vals[both_finite], mut_vals[both_finite], rtol=1e-9)))
    lines.append(f"Écart de rendement obligataire sur les séances antérieures à la mutation (marge 60j) : {diff_lookahead} / {both_finite.sum()} comparées")
    lines.append(f"**{'OK — aucune fuite, le passé est bien inchangé.' if diff_lookahead == 0 else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_diversification_bond_overlay_dax_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
