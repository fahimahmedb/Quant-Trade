"""Backtest — Rebalancement HEBDOMADAIRE (échantillonnage-et-maintien,
REBAL_FREQ=5j) du mécanisme #121 (moyenne de deux moteurs de volatilité
indépendants), pour réduire le turnover et la sensibilité aux coûts
(spécification pré-enregistrée dans
PREREG_weekly_rebalance_dual_engine.md, committée avant ce script).
n_trials=1, aucune dépendance ML. Règle de succès renforcée niveau 1 --
SI PASS, ce résultat n'est PAS final, voir Règle 9
(`scripts/nonml_pass_validation_battery.py`).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
REBAL_FREQ = 5


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
    d = np.load(ROOT / "results" / "nonml_dual_engine_defensive_overlay_pnl.npz", allow_pickle=True)
    pos_daily, r, cost_bps_src = d["pos"], d["r_asset"], float(d["cost_bps"])
    dates_used = d["dates"]
    assert cost_bps_src == COST_BPS

    pos_weekly = weekly_hold_position(pos_daily, REBAL_FREQ)

    def pnl_and_metrics(pos, r):
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = pos * r - turn * (COST_BPS / 1e4)
        pnl_bh = r.copy()
        pnl_bh[0] -= COST_BPS / 1e4
        return pnl_ov, pnl_bh, trading_metrics(pnl_ov), trading_metrics(pnl_bh)

    pnl_daily, pnl_bh, me_daily, me_bh = pnl_and_metrics(pos_daily, r)
    pnl_weekly, _, me_weekly, _ = pnl_and_metrics(pos_weekly, r)

    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_daily = np.exp(pnl_daily.sum()) - 1.0
    ret_weekly = np.exp(pnl_weekly.sum()) - 1.0

    turn_daily = np.abs(np.diff(pos_daily, prepend=1.0)).sum()
    turn_weekly = np.abs(np.diff(pos_weekly, prepend=1.0)).sum()

    sharpe_ok = me_weekly["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_weekly > ret_bh
    verdict_standard = sharpe_ok and ret_ok

    calmar_bh = (ret_bh) / abs(me_bh["max_drawdown_pct"] / 100) if me_bh["max_drawdown_pct"] != 0 else np.nan
    calmar_weekly = (ret_weekly) / abs(me_weekly["max_drawdown_pct"] / 100) if me_weekly["max_drawdown_pct"] != 0 else np.nan
    calmar_ok = calmar_weekly > calmar_bh
    verdict = verdict_standard or calmar_ok

    lines = [
        "# Résultat — Rebalancement hebdomadaire du mécanisme #121 (pré-enregistré, deux critères)",
        "",
        f"Position(t) = échantillonnage-et-maintien de la position quotidienne du #121, "
        f"rafraîchie tous les {REBAL_FREQ} séances. {len(r)} séances (fenêtre commune #121, "
        f"20/09/1988→13/07/2026).",
        "",
        f"Turnover cumulé quotidien (#121 original) : {turn_daily:.1f}",
        f"Turnover cumulé hebdomadaire : {turn_weekly:.1f} "
        f"({100*(1 - turn_weekly/turn_daily):.1f}% de réduction)",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| #121 original (quotidien) | {me_daily['sharpe_ann']:+.2f} | {100*ret_daily:+.1f}% | {me_daily['max_drawdown_pct']:.1f}% | -- |",
        f"| **Rebalancement hebdomadaire** | **{me_weekly['sharpe_ann']:+.2f}** | "
        f"**{100*ret_weekly:+.1f}%** | {me_weekly['max_drawdown_pct']:.1f}% | {calmar_weekly:.3f} |",
        "",
        f"1. Sharpe hebdo > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement hebdo > BH : {'OUI' if ret_ok else 'non'}",
        f"3. Critère standard (1 ET 2) : {'PASS' if verdict_standard else 'FAIL'}",
        f"4. Critère Calmar (hebdo > BH) : {'PASS' if calmar_ok else 'FAIL'}",
        "",
        f"**{'PASS (niveau 1, au moins un critère)' if verdict else 'FAIL'}**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py weekly_rebalance_dual_engine` "
                     "(stress coûts/crise, stabilité temporelle, SPA, DSR à n_trials=backlog).**")

    out = ROOT / "results" / "nonml_weekly_rebalance_dual_engine_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        np.savez(
            ROOT / "results" / "nonml_weekly_rebalance_dual_engine_pnl.npz",
            pos=pos_weekly, r_asset=r, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
