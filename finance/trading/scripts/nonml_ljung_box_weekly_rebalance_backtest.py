"""Backtest — Rebalancement hebdomadaire de la porte Ljung-Box (#242),
correction mécanique ciblée du contrôle Règle 9 (coûts + stabilité,
#243, 2/5). Spécification pré-enregistrée dans
PREREG_ljung_box_weekly_rebalance.md, committée avant ce script.
Réutilise `weekly_hold_position` du #154 (Règle 7) sans modification, et
le signal Ljung-Box du #242 sans modification. n_trials=1 (évaluation de
l'amélioration Règle 9, pas un nouveau PASS niveau 1 — signal inchangé).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_ljung_box_clustering_vol_targeting_overlay_backtest import (  # noqa: E402
    calm_lb_mask, combined_position, COST_BPS, LB_WINDOW, MEDIAN_WINDOW,
)

MARKET_FILE = "nasdaq100_daily.txt"
MARKET_NAME = "NDX (40 ans)"
REBAL_FREQ = 5  # identique au #154/#167, semaine de bourse


def weekly_hold_position(pos_daily: np.ndarray, freq: int) -> np.ndarray:
    T = len(pos_daily)
    pos_w = np.empty(T)
    last = pos_daily[0]
    for t in range(T):
        if t % freq == 0:
            last = pos_daily[t]
        pos_w[t] = last
    return pos_w


def evaluate(pos, r_t, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * r_t - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.cumprod(1.0 + pnl)[-1] - 1.0)
    return me, ret


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    close = df["close"].values
    dates = df["date"].values
    r_full = np.log(close[1:] / close[:-1])

    start = LB_WINDOW + MEDIAN_WINDOW
    gate = calm_lb_mask(r_full)
    pos_daily_full = combined_position(r_full, gate)

    r_t = r_full[start:]
    pos_daily = pos_daily_full[start:]
    pos_weekly = weekly_hold_position(pos_daily, REBAL_FREQ)

    # Buy&Hold : cout unique a l'entree, comme le reste du backlog
    pnl_bh = r_t.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh = trading_metrics(pnl_bh)
    ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)

    me_daily, ret_daily = evaluate(pos_daily, r_t, COST_BPS)
    me_weekly, ret_weekly = evaluate(pos_weekly, r_t, COST_BPS)

    turn_daily = np.abs(np.diff(pos_daily, prepend=1.0))
    turn_weekly = np.abs(np.diff(pos_weekly, prepend=1.0))

    sharpe_ok = me_weekly["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_weekly > ret_bh
    verdict_niveau1 = bool(sharpe_ok and ret_ok)

    lines = [
        "# Résultat — Rebalancement hebdomadaire de la porte Ljung-Box (#242), correction "
        "ciblée Règle 9 (pré-enregistré)",
        "",
        f"Position quotidienne du #242 échantillonnée tous les {REBAL_FREQ}j et maintenue "
        f"constante entre deux rebalancements (`weekly_hold_position`, réutilisée du #154/#167, "
        f"Règle 7). Signal Ljung-Box et mécanisme #46 sous-jacent INCHANGÉS. Marché : {MARKET_NAME}, "
        f"{len(r_t)} séances testables.",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Turnover moyen/j |",
        "|---|---|---|---|---|",
        f"| Buy&Hold | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | — |",
        f"| Porte Ljung-Box, quotidien (#242) | {me_daily['sharpe_ann']:+.2f} | {100*ret_daily:+.1f}% | "
        f"{me_daily['max_drawdown_pct']:.1f}% | {turn_daily.mean():.4f} |",
        f"| **Porte Ljung-Box, hebdomadaire** | **{me_weekly['sharpe_ann']:+.2f}** | "
        f"**{100*ret_weekly:+.1f}%** | {me_weekly['max_drawdown_pct']:.1f}% | {turn_weekly.mean():.4f} |",
        "",
        f"Réduction du turnover moyen : {100*(1 - turn_weekly.mean()/turn_daily.mean()):.1f}%.",
        "",
        f"1. Sharpe hebdomadaire > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement hebdomadaire > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**PASS niveau 1 {'maintenu' if verdict_niveau1 else 'PERDU'} après passage à un "
        f"rebalancement hebdomadaire.**",
    ]

    out = ROOT / "results" / "nonml_ljung_box_weekly_rebalance_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")

    # npz pour la batterie Règle 9 (comparaison directe avec le #243)
    np.savez(ROOT / "results" / "nonml_ljung_box_weekly_rebalance_pnl.npz",
             pos=pos_weekly, r_asset=r_t, dates=dates[1:][start:], cost_bps=COST_BPS)


if __name__ == "__main__":
    main()
