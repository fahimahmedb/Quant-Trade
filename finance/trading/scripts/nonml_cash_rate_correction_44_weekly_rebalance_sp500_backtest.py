"""Backtest — Rebalancement hebdomadaire du #149 sur S&P 500 (complétion
du #154) (spécification pré-enregistrée dans
PREREG_cash_rate_correction_44_weekly_rebalance_sp500.md, committée
avant ce script). n_trials=1, aucune dépendance ML. Règle de succès
renforcée niveau 1 (critère IDENTIQUE au #149/#151) -- SI PASS,
résultat PAS final, voir Règle 9.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
from nonml_cash_rate_correction_44_weekly_rebalance_backtest import COST_BPS, REBAL_FREQ, weekly_hold_position  # noqa: E402

SOURCE = "nonml_cash_rate_correction_44_crossmarket_sp500_pnl.npz"


def main():
    d = np.load(ROOT / "results" / SOURCE, allow_pickle=True)
    pos_daily, r_mkt, r_bond, dates = d["pos"], d["r_asset"], d["r_alt"], d["dates"]

    pos_weekly = weekly_hold_position(pos_daily, REBAL_FREQ)

    def pnl_at(pos):
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * r_mkt + (1.0 - pos) * r_bond - turn * (COST_BPS / 1e4)
        pnl_bh = r_mkt.copy()
        pnl_bh[0] -= COST_BPS / 1e4
        return pnl_ov, pnl_bh, turn

    pnl_daily, pnl_bh, turn_daily = pnl_at(pos_daily)
    pnl_weekly, _, turn_weekly = pnl_at(pos_weekly)

    me_bh = trading_metrics(pnl_bh)
    me_daily = trading_metrics(pnl_daily)
    me_weekly = trading_metrics(pnl_weekly)
    ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)
    ret_weekly = float(np.cumprod(1.0 + pnl_weekly)[-1] - 1.0)

    sharpe_ok = me_weekly["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_weekly > ret_bh
    verdict = sharpe_ok and ret_ok
    turnover_reduction = 100 * (1 - turn_weekly.sum() / turn_daily.sum())

    lines = [
        "# Résultat — Rebalancement hebdomadaire du #149 sur S&P 500 (complétion du #154, pré-enregistré)",
        "",
        f"{len(r_mkt)} séances. Turnover réduit de {turnover_reduction:.1f}%.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (S&P 500 100%) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| Overlay quotidien (#151, rappel) | {me_daily['sharpe_ann']:+.2f} | -- | -- |",
        f"| **Overlay hebdomadaire (#157)** | **{me_weekly['sharpe_ann']:+.2f}** | "
        f"**{100*ret_weekly:+.1f}%** | {me_weekly['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay hebdo > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay hebdo > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS (niveau 1)' if verdict else 'FAIL'}**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py cash_rate_correction_44_weekly_rebalance_sp500`.**")

    out = ROOT / "results" / "nonml_cash_rate_correction_44_weekly_rebalance_sp500_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        np.savez(
            ROOT / "results" / "nonml_cash_rate_correction_44_weekly_rebalance_sp500_pnl.npz",
            pos=pos_weekly, r_asset=r_mkt, r_alt=r_bond, dates=dates, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
