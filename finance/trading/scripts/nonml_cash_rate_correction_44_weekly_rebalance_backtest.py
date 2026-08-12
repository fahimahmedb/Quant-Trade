"""Backtest — Rebalancement hebdomadaire du #149 (correction ciblée de
la fissure coûts Russell 2000 diagnostiquée au #151) (spécification
pré-enregistrée dans PREREG_cash_rate_correction_44_weekly_rebalance.md,
committée avant ce script). n_trials=1 par marché, aucune dépendance
ML. Règle de succès renforcée niveau 1 (critère IDENTIQUE au #149) --
SI PASS, résultat PAS final, voir Règle 9.
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

COST_BPS = 5.0
REBAL_FREQ = 5

SOURCES = {
    "Russell 2000": "nonml_cash_rate_correction_44_crossmarket_russell2000_pnl.npz",
    "NDX": "nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz",
}


def weekly_hold_position(pos_daily: np.ndarray, freq: int) -> np.ndarray:
    T = len(pos_daily)
    pos_w = np.empty(T)
    last = pos_daily[0]
    for t in range(T):
        if t % freq == 0:
            last = pos_daily[t]
        pos_w[t] = last
    return pos_w


def main():
    lines = [
        "# Résultat — Rebalancement hebdomadaire du #149 (pré-enregistré, correction ciblée fissure coûts)",
        "",
        "| Marché | Séances | BH Sharpe | BH Rdt | Overlay quotidien Sharpe | Overlay hebdo Sharpe | Overlay hebdo Rdt | Overlay hebdo MDD | Turnover réduit | PASS |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    any_pass = {}
    for name, fname in SOURCES.items():
        d = np.load(ROOT / "results" / fname, allow_pickle=True)
        pos_daily, r_mkt, r_bond = d["pos"], d["r_asset"], d["r_alt"]
        dates = d["dates"]

        pos_weekly = weekly_hold_position(pos_daily, REBAL_FREQ)

        def pnl_at(pos, r, r_alt):
            turn = np.abs(np.diff(pos, prepend=1.0))
            pnl_ov = pos * r + (1.0 - pos) * r_alt - turn * (COST_BPS / 1e4)
            pnl_bh = r.copy()
            pnl_bh[0] -= COST_BPS / 1e4
            return pnl_ov, pnl_bh, turn

        pnl_daily, pnl_bh, turn_daily = pnl_at(pos_daily, r_mkt, r_bond)
        pnl_weekly, _, turn_weekly = pnl_at(pos_weekly, r_mkt, r_bond)

        me_bh = trading_metrics(pnl_bh)
        me_daily = trading_metrics(pnl_daily)
        me_weekly = trading_metrics(pnl_weekly)
        ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)
        ret_weekly = float(np.exp(pnl_weekly.sum()) - 1.0)

        sharpe_ok = me_weekly["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_weekly > ret_bh
        verdict = sharpe_ok and ret_ok
        turnover_reduction = 100 * (1 - turn_weekly.sum() / turn_daily.sum())

        any_pass[name] = (verdict, pos_weekly, r_mkt, r_bond, dates)

        lines.append(
            f"| {name} | {len(r_mkt)} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_daily['sharpe_ann']:+.2f} | {me_weekly['sharpe_ann']:+.2f} | {100*ret_weekly:+.1f}% | "
            f"{me_weekly['max_drawdown_pct']:.1f}% | {turnover_reduction:.1f}% | {'OUI' if verdict else 'non'} |"
        )

    lines.append("")
    lines.append(
        "**Contrôle ciblé** : ce cycle répond spécifiquement à la question 'le rebalancement "
        "hebdomadaire répare-t-il l'échec du stress de coûts à 5x du #149 sur Russell 2000 (#151, "
        "2/5) ?' — réponse dans la batterie Règle 9 ci-après (volet a), pas dans ce tableau PASS/FAIL "
        "niveau 1 (critère standard Sharpe+rendement, différent du stress de coûts)."
    )

    out = ROOT / "results" / "nonml_cash_rate_correction_44_weekly_rebalance_result.md"
    out.write_text("\n".join(lines) + "\n")

    slugs = {"Russell 2000": "russell2000", "NDX": "ndx"}
    for name, (verdict, pos_weekly, r_mkt, r_bond, dates) in any_pass.items():
        if verdict:
            slug = slugs[name]
            np.savez(
                ROOT / "results" / f"nonml_cash_rate_correction_44_weekly_rebalance_{slug}_pnl.npz",
                pos=pos_weekly, r_asset=r_mkt, r_alt=r_bond, dates=dates, cost_bps=COST_BPS,
            )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
