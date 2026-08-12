"""Robustesse — Rebalancement hebdomadaire du #149 sur S&P 500 (#157),
grille des fréquences (identique au #131/#154, PAS un retuning).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_cash_rate_correction_44_weekly_rebalance_backtest import COST_BPS, weekly_hold_position  # noqa: E402
from nonml_cash_rate_correction_44_weekly_rebalance_sp500_backtest import SOURCE  # noqa: E402

FREQ_GRID = [3, 5, 10, 15, 20]


def main():
    d = np.load(ROOT / "results" / SOURCE, allow_pickle=True)
    pos_daily, r_mkt, r_bond = d["pos"], d["r_asset"], d["r_alt"]

    pnl_bh = r_mkt.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh = trading_metrics(pnl_bh)
    ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)

    lines = [
        "# Robustesse — Rebalancement hebdomadaire du #149 sur S&P 500 (#157), grille des fréquences (PAS un retuning)",
        "",
        "Fréquence pré-enregistrée = 5j. Grille 3-20j.",
        "",
        "| REBAL_FREQ | Sharpe ann. | Rendement total | MDD | PASS |",
        "|---|---|---|---|---|",
    ]
    n_pass = 0
    for freq in FREQ_GRID:
        pos_f = weekly_hold_position(pos_daily, freq)
        turn = np.abs(np.diff(pos_f, prepend=1.0))
        pnl_ov = pos_f * r_mkt + (1.0 - pos_f) * r_bond - turn * (COST_BPS / 1e4)
        me_ov = trading_metrics(pnl_ov)
        ret_ov = float(np.exp(pnl_ov.sum()) - 1.0)
        ok = (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)
        n_pass += int(ok)
        marker = " ← pré-enregistré" if freq == 5 else ""
        lines.append(
            f"| {freq}j{marker} | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if ok else 'non'} |"
        )
    lines.append("")
    lines.append(f"Plateau : {n_pass}/{len(FREQ_GRID)} fréquences PASS.")

    out = ROOT / "results" / "nonml_cash_rate_correction_44_weekly_rebalance_sp500_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
