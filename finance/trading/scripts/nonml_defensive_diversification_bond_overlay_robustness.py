"""Robustesse — Diversification obligataire du #115, grille de la maturité
de référence dans la formule de duration (PAS un retuning de pos_eq, qui
reste strictement celle du #115).
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
from nonml_defensive_diversification_bond_overlay_backtest import COST_BPS, load_dgs10, bond_return_proxy  # noqa: E402

MATURITY_GRID = [5, 10, 20]


def main():
    d = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    pos_eq_full, r_ndx_full = d["pos"], d["r_asset"]
    dates_full = pd.to_datetime(d["dates"])

    dgs10 = load_dgs10()

    lines = [
        "# Robustesse — Diversification obligataire du #115, grille de maturité de référence (PAS un retuning)",
        "",
        "Maturité pré-enregistrée = 10 ans. Grille 5-20 ans (position équity #115 strictement inchangée).",
        "",
        "| Maturité | Sharpe ann. | Rendement total | MDD | Calmar | PASS standard | PASS Calmar |",
        "|---|---|---|---|---|---|---|",
    ]
    n_pass_std, n_pass_calmar = 0, 0
    for maturity in MATURITY_GRID:
        r_bond_all = bond_return_proxy(dgs10, maturity_years=maturity)
        r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")
        valid = r_bond_aligned.notna().values
        start = int(np.argmax(valid)) if valid.any() else len(valid)

        pos_eq = pos_eq_full[start:]
        r_ndx = r_ndx_full[start:]
        r_bond = r_bond_aligned.values[start:]

        r_combined = pos_eq * r_ndx + (1.0 - pos_eq) * r_bond
        turn = np.abs(np.diff(pos_eq, prepend=1.0))
        pnl_ov = r_combined - turn * (COST_BPS / 1e4)
        pnl_bh = r_ndx.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_ov, me_bh = trading_metrics(pnl_ov), trading_metrics(pnl_bh)
        ret_ov = float(np.cumprod(1.0 + pnl_ov)[-1] - 1.0)
        ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)
        calmar_ov = ret_ov / abs(me_ov["max_drawdown_pct"] / 100)
        calmar_bh = ret_bh / abs(me_bh["max_drawdown_pct"] / 100)
        ok_std = (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)
        ok_calmar = calmar_ov > calmar_bh
        n_pass_std += int(ok_std)
        n_pass_calmar += int(ok_calmar)
        marker = " ← pré-enregistré" if maturity == 10 else ""
        lines.append(
            f"| {maturity} ans{marker} | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {calmar_ov:.3f} | {'OUI' if ok_std else 'non'} | {'OUI' if ok_calmar else 'non'} |"
        )
    lines.append("")
    lines.append(f"Plateau : {n_pass_std}/{len(MATURITY_GRID)} maturités PASS standard, {n_pass_calmar}/{len(MATURITY_GRID)} PASS Calmar.")

    out = ROOT / "results" / "nonml_defensive_diversification_bond_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
