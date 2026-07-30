"""Test SPA famille-entière sur la sous-famille NDX de la diversification
obligataire (spécification pré-enregistrée dans
PREREG_family_spa_diversification_bond_ndx.md, committée avant ce
script). PAS un nouveau backtest indépendant -- analyse complémentaire
aux DSR individuels déjà calculés. Cycle #150, aucune dépendance ML.
Portée réduite à 5 membres NDX (limite mécanique de spa_test, cf.
PREREG).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from volatility import spa_test  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import bond_return_proxy, load_dgs10  # noqa: E402

COST_BPS = 5.0


def pnl_from_npz(fname):
    d = np.load(ROOT / "results" / fname, allow_pickle=True)
    pos, r, r_alt = d["pos"], d["r_asset"], d["r_alt"]
    dates = pd.to_datetime(d["dates"])
    r_combined = pos * r + (1.0 - pos) * r_alt
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = r_combined - turn * (COST_BPS / 1e4)
    return pd.Series(pnl, index=dates)


def main():
    # #134 (DGS10) et bases pour les proxys courts du #141
    d134 = np.load(ROOT / "results" / "nonml_defensive_diversification_bond_overlay_pnl.npz", allow_pickle=True)
    pos134, r134 = d134["pos"], d134["r_asset"]
    dates134 = pd.to_datetime(d134["dates"])

    dgs3mo = pd.read_csv(FINANCE_ROOT.parent / "data" / "dgs3mo_daily.csv")
    dgs3mo["observation_date"] = pd.to_datetime(dgs3mo["observation_date"])
    dgs3mo["DGS3MO"] = pd.to_numeric(dgs3mo["DGS3MO"], errors="coerce")
    s_dgs3mo = pd.Series(dgs3mo["DGS3MO"].values, index=dgs3mo["observation_date"]).dropna()
    s_dgs3mo = s_dgs3mo[~s_dgs3mo.index.duplicated(keep="first")].sort_index()

    dgs1 = pd.read_csv(FINANCE_ROOT.parent / "data" / "dgs1_daily.csv")
    dgs1["observation_date"] = pd.to_datetime(dgs1["observation_date"])
    dgs1["DGS1"] = pd.to_numeric(dgs1["DGS1"], errors="coerce")
    s_dgs1 = pd.Series(dgs1["DGS1"].values, index=dgs1["observation_date"]).dropna()
    s_dgs1 = s_dgs1[~s_dgs1.index.duplicated(keep="first")].sort_index()

    r_3mo_all = bond_return_proxy(s_dgs3mo, maturity_years=0.25)
    r_1y_all = bond_return_proxy(s_dgs1, maturity_years=1.0)
    r_3mo_aligned = r_3mo_all.reindex(dates134, method="ffill")
    r_1y_aligned = r_1y_all.reindex(dates134, method="ffill")

    r_10y_aligned = bond_return_proxy(load_dgs10()).reindex(dates134, method="ffill")
    turn134 = np.abs(np.diff(pos134, prepend=1.0))
    pnl_134 = pd.Series(pos134 * r134 + (1.0 - pos134) * r_10y_aligned.values - turn134 * (COST_BPS / 1e4), index=dates134)
    pnl_3mo = pd.Series(pos134 * r134 + (1.0 - pos134) * r_3mo_aligned.values - turn134 * (COST_BPS / 1e4), index=dates134)
    pnl_1y = pd.Series(pos134 * r134 + (1.0 - pos134) * r_1y_aligned.values - turn134 * (COST_BPS / 1e4), index=dates134)
    pnl_bh_134 = pd.Series(r134.copy(), index=dates134)
    pnl_bh_134.iloc[0] -= COST_BPS / 1e4

    pnl_137 = pnl_from_npz("nonml_diversification_bond_weekly_rebalance_stack_pnl.npz")
    pnl_139 = pnl_from_npz("nonml_diversification_bond_triple_engine_stack_pnl.npz")

    d137 = np.load(ROOT / "results" / "nonml_diversification_bond_weekly_rebalance_stack_pnl.npz", allow_pickle=True)
    r137, dates137 = d137["r_asset"], pd.to_datetime(d137["dates"])
    pnl_bh_137 = pd.Series(r137.copy(), index=dates137)
    pnl_bh_137.iloc[0] -= COST_BPS / 1e4

    common_dates = dates137  # la plus courte fenetre (9522 seances, 1988-09-20+), imposee par #137/#139
    losses = {
        "BuyHold": -pnl_bh_137.reindex(common_dates).values,
        "134_DGS10": -pnl_134.reindex(common_dates).values,
        "141_3mo": -pnl_3mo.reindex(common_dates).values,
        "141_1an": -pnl_1y.reindex(common_dates).values,
        "137_hebdo": -pnl_137.reindex(common_dates).values,
        "139_ensemble3": -pnl_139.reindex(common_dates).values,
    }
    assert all(np.isfinite(v).all() for v in losses.values()), "NaN residuel apres alignement"

    res = spa_test(losses, bench="BuyHold")

    lines = [
        "# Test SPA famille-entière — sous-famille NDX de la diversification obligataire (cycle #150)",
        "",
        "PAS un nouveau backtest indépendant. Portée RÉDUITE à 5 membres NDX partageant un horizon "
        "commun (limite mécanique de `spa_test`, exige le même T pour tous les modèles) — les "
        "variantes cross-marché (#136 S&P 500/Russell 2000, #140 DAX, #143 Composite) et le #149 "
        "(base équity différente) sont EXCLUES, documenté explicitement dans le PREREG.",
        "",
        f"Fenêtre commune : {common_dates[0].date()} → {common_dates[-1].date()} ({len(common_dates)} séances).",
        "",
        "| Membre | t-stat (vs BuyHold) |",
        "|---|---|",
    ]
    for m, t in res["t_by_model"].items():
        lines.append(f"| {m} | {t:+.3f} |")
    lines.append("")
    lines.append(f"**Meilleur membre (t-stat max)** : {res['best_model']}")
    lines.append(f"**t_SPA = {res['t_spa']:.3f}, p-value SPA = {res['p_value']:.4f}**")
    lines.append("")
    ok = res["p_value"] < 0.05
    if ok:
        verdict_txt = "OK — significatif à 5% : la sous-famille bat le benchmark de façon conjointement significative."
    else:
        verdict_txt = ("ÉCHEC — non significatif à 5% : même en ne gardant que 5 variantes NDX de la "
                        "famille, le SPA famille ne rejette PAS H0.")
    lines.append(f"**{verdict_txt}**")
    lines.append("")
    lines.append(
        "Cette portée réduite (5 membres, sélectionnés parce qu'ils sont NDX-compatibles, pas "
        "au hasard) reste plus généreuse pour la famille qu'un test à 11+ membres cross-marché "
        "aurait été (moins de correction pour comparaisons multiples) — un résultat non significatif "
        "ici est donc d'autant plus honnête. Ne change AUCUN verdict Règle 9 déjà rendu."
    )

    out = ROOT / "results" / "nonml_family_spa_diversification_bond_ndx.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
