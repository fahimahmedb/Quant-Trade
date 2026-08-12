"""Backtest — Empiler diversification obligataire (#134) + rebalancement
hebdomadaire (#131) (spécification pré-enregistrée dans
PREREG_diversification_bond_weekly_rebalance_stack.md, committée avant
ce script). n_trials=1, aucune dépendance ML. Règle de succès renforcée
niveau 1 -- SI PASS, résultat PAS final, voir Règle 9
(`scripts/nonml_pass_validation_battery.py`).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10, bond_return_proxy  # noqa: E402

COST_BPS = 5.0


def main():
    d = np.load(ROOT / "results" / "nonml_weekly_rebalance_dual_engine_pnl.npz", allow_pickle=True)
    pos_eq_full, r_ndx_full, cost_bps_src = d["pos"], d["r_asset"], float(d["cost_bps"])
    dates_full = pd.to_datetime(d["dates"])
    assert cost_bps_src == COST_BPS

    dgs10 = load_dgs10()
    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")

    valid = r_bond_aligned.notna().values
    start = int(np.argmax(valid)) if valid.any() else len(valid)

    pos_eq = pos_eq_full[start:]
    r_ndx = r_ndx_full[start:]
    r_bond = r_bond_aligned.values[start:]
    dates_used = dates_full.values[start:]

    r_combined = pos_eq * r_ndx + (1.0 - pos_eq) * r_bond
    turn = np.abs(np.diff(pos_eq, prepend=1.0))
    pnl_ov = r_combined - turn * (COST_BPS / 1e4)
    pnl_bh = r_ndx.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict_standard = sharpe_ok and ret_ok

    calmar_bh = ret_bh / abs(me_bh["max_drawdown_pct"] / 100)
    calmar_ov = ret_ov / abs(me_ov["max_drawdown_pct"] / 100)
    calmar_ok = calmar_ov > calmar_bh
    verdict = verdict_standard or calmar_ok

    frac_leveraged = float((pos_eq > 1.0).mean())

    lines = [
        "# Résultat — Empilement diversification obligataire (#134) + rebalancement hebdomadaire (#131) (pré-enregistré, deux critères)",
        "",
        f"Position équity #131 (hebdomadaire, peut dépasser 1,0x) ; fraction (1-pos_eq) allouée au proxy "
        f"obligataire DGS10 du #134 (négative = financement du levier au taux obligataire quand pos_eq>1). "
        f"{len(r_ndx)} séances (fenêtre commune #131 ∩ DGS10).",
        "",
        f"Fraction du temps avec levier (pos_eq>1,0x, donc allocation obligataire négative) : {100*frac_leveraged:.1f}%",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX 100%) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| #131 seul (déjà committé) | -- | -- | -57,2%→-55,3% (cf. résultat #131) | -- |",
        f"| **#131 + diversification obligataire (#134)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% | {calmar_ov:.3f} |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        f"3. Critère standard (1 ET 2) : {'PASS' if verdict_standard else 'FAIL'}",
        f"4. Critère Calmar (overlay > BH) : {'PASS' if calmar_ok else 'FAIL'}",
        "",
        f"**{'PASS (niveau 1, au moins un critère)' if verdict else 'FAIL'}**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py diversification_bond_weekly_rebalance_stack` "
                     "(stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_diversification_bond_weekly_rebalance_stack_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        np.savez(
            ROOT / "results" / "nonml_diversification_bond_weekly_rebalance_stack_pnl.npz",
            pos=pos_eq, r_asset=r_ndx, r_alt=r_bond, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
