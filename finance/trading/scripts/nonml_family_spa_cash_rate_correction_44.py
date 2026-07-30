"""Test SPA famille sur la famille #149 (spécification pré-enregistrée
dans PREREG_family_spa_cash_rate_correction_44.md, committée avant ce
script). PAS un nouveau backtest indépendant. Cycle #159, aucune
dépendance ML. Portée corrigée avant calcul : DEUX tests séparés par
marché (limite mécanique de spa_test, cf. PREREG).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from volatility import spa_test  # noqa: E402

COST_BPS = 5.0


def pnl_from_npz(fname):
    d = np.load(ROOT / "results" / fname, allow_pickle=True)
    pos, r, r_alt = d["pos"], d["r_asset"], d["r_alt"]
    dates = pd.to_datetime(d["dates"])
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r + (1.0 - pos) * r_alt - turn * (COST_BPS / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    return pd.Series(pnl_ov, index=dates), pd.Series(pnl_bh, index=dates)


def run_family(label, daily_fname, weekly_fname):
    pnl_daily, pnl_bh_daily = pnl_from_npz(daily_fname)
    pnl_weekly, pnl_bh_weekly = pnl_from_npz(weekly_fname)

    common_dates = pnl_daily.index.intersection(pnl_weekly.index)
    losses = {
        "BuyHold": -pnl_bh_daily.reindex(common_dates).values,
        "quotidien": -pnl_daily.reindex(common_dates).values,
        "hebdomadaire": -pnl_weekly.reindex(common_dates).values,
    }
    assert all(np.isfinite(v).all() for v in losses.values())
    res = spa_test(losses, bench="BuyHold")
    return common_dates, res


def main():
    lines = [
        "# Test SPA famille — famille #149 (cycle #159, portée corrigée avant calcul)",
        "",
        "PAS un nouveau backtest indépendant. Portée corrigée AVANT tout calcul : deux tests SPA "
        "séparés par marché (limite mécanique de `spa_test`, ne peut pas mélanger des benchmarks "
        "d'actifs différents — même limite déjà rencontrée au #150).",
        "",
    ]

    ndx_dates, ndx_res = run_family(
        "NDX",
        "nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz",
        "nonml_cash_rate_correction_44_weekly_rebalance_ndx_pnl.npz",
    )
    lines.append("## Famille NDX (#149 quotidien + #154 hebdomadaire)")
    lines.append("")
    lines.append(f"Fenêtre commune : {ndx_dates[0].date()} → {ndx_dates[-1].date()} ({len(ndx_dates)} séances).")
    lines.append("")
    lines.append("| Membre | t-stat (vs BuyHold) |")
    lines.append("|---|---|")
    for m, t in ndx_res["t_by_model"].items():
        lines.append(f"| {m} | {t:+.3f} |")
    lines.append("")
    lines.append(f"**Meilleur membre** : {ndx_res['best_model']} — t_SPA={ndx_res['t_spa']:.3f}, "
                 f"p-value SPA = {ndx_res['p_value']:.4f}")
    lines.append("")

    sp_dates, sp_res = run_family(
        "S&P 500",
        "nonml_cash_rate_correction_44_crossmarket_sp500_pnl.npz",
        "nonml_cash_rate_correction_44_weekly_rebalance_sp500_pnl.npz",
    )
    lines.append("## Famille S&P 500 (#151 quotidien + #157 hebdomadaire)")
    lines.append("")
    lines.append(f"Fenêtre commune : {sp_dates[0].date()} → {sp_dates[-1].date()} ({len(sp_dates)} séances).")
    lines.append("")
    lines.append("| Membre | t-stat (vs BuyHold) |")
    lines.append("|---|---|")
    for m, t in sp_res["t_by_model"].items():
        lines.append(f"| {m} | {t:+.3f} |")
    lines.append("")
    lines.append(f"**Meilleur membre** : {sp_res['best_model']} — t_SPA={sp_res['t_spa']:.3f}, "
                 f"p-value SPA = {sp_res['p_value']:.4f}")
    lines.append("")

    ok_ndx = ndx_res["p_value"] < 0.05
    ok_sp = sp_res["p_value"] < 0.05
    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        f"Famille NDX : {'significatif' if ok_ndx else 'NON significatif'} à 5% (p={ndx_res['p_value']:.4f}). "
        f"Famille S&P 500 : {'significatif' if ok_sp else 'NON significatif'} à 5% (p={sp_res['p_value']:.4f}). "
        "Cohérent avec les DSR individuels déjà calculés (tous ≈0 à n_trials=backlog). Ne change AUCUN "
        "verdict Règle 9 déjà rendu."
    )

    out = ROOT / "results" / "nonml_family_spa_cash_rate_correction_44.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
