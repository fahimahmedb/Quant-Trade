"""Robustesse — Rebalancement du mécanisme #121, grille des fréquences
(REBAL_FREQ), symétrique autour du choix hebdomadaire pré-enregistré
(5j) -- PAS un retuning après avoir vu quelle fréquence "marche le
mieux".
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_weekly_rebalance_dual_engine_backtest import COST_BPS, weekly_hold_position  # noqa: E402

FREQ_GRID = [3, 5, 10, 15, 20]


def main():
    d = np.load(ROOT / "results" / "nonml_dual_engine_defensive_overlay_pnl.npz", allow_pickle=True)
    pos_daily, r = d["pos"], d["r_asset"]

    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh = trading_metrics(pnl_bh)
    ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)
    calmar_bh = ret_bh / abs(me_bh["max_drawdown_pct"] / 100)

    lines = [
        "# Robustesse — Rebalancement du mécanisme #121, grille des fréquences (PAS un retuning)",
        "",
        "Fréquence pré-enregistrée = 5j (hebdomadaire). Grille 3-20j.",
        "",
        "| REBAL_FREQ | Turnover cumulé | Sharpe ann. | Rendement total | Calmar | PASS standard | PASS Calmar |",
        "|---|---|---|---|---|---|---|",
    ]
    n_pass_std, n_pass_calmar = 0, 0
    for freq in FREQ_GRID:
        pos_f = weekly_hold_position(pos_daily, freq)
        turn = np.abs(np.diff(pos_f, prepend=1.0))
        pnl_ov = pos_f * r - turn * (COST_BPS / 1e4)
        me_ov = trading_metrics(pnl_ov)
        ret_ov = float(np.exp(pnl_ov.sum()) - 1.0)
        calmar_ov = ret_ov / abs(me_ov["max_drawdown_pct"] / 100)
        ok_std = (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)
        ok_calmar = calmar_ov > calmar_bh
        n_pass_std += int(ok_std)
        n_pass_calmar += int(ok_calmar)
        marker = " ← pré-enregistré" if freq == 5 else ""
        lines.append(
            f"| {freq}j{marker} | {turn.sum():.1f} | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{calmar_ov:.3f} | {'OUI' if ok_std else 'non'} | {'OUI' if ok_calmar else 'non'} |"
        )
    lines.append("")
    lines.append(f"Buy&Hold : Sharpe {me_bh['sharpe_ann']:+.2f}, rendement {100*ret_bh:+.1f}%, Calmar {calmar_bh:.3f}.")
    lines.append("")
    lines.append(f"Plateau : {n_pass_std}/{len(FREQ_GRID)} fréquences PASS standard, {n_pass_calmar}/{len(FREQ_GRID)} PASS Calmar.")

    out = ROOT / "results" / "nonml_weekly_rebalance_dual_engine_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
