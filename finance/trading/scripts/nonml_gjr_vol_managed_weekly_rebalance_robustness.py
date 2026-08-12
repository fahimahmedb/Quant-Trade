"""Robustesse — grille de fréquences de rebalancement pour le cycle #167
(rebalancement hebdomadaire du #165). Perturbation annoncée au §5 du
PREREG AVANT tout calcul : REBAL_FREQ ∈ {3, 5, 10, 21} jours.

**Ce n'est PAS un retuning** : le verdict du cycle reste celui du point
pré-enregistré REBAL_FREQ=5, quoi que montre cette grille.

La prévision de volatilité GJR-t ne dépend PAS de REBAL_FREQ : le
walk-forward n'est calculé qu'une seule fois, la grille ne fait que
ré-échantillonner la même position quotidienne à des fréquences différentes.
"""
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import vol_target_exposure, walk_forward_vol_forecast  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_volatility_managed_portfolio_gjr_backtest import (
    CAP, COST_BPS, MARKET_FILE, REFIT_EVERY, T0, TARGET_VOL_ANNUAL_PCT,
)
from nonml_gjr_vol_managed_weekly_rebalance_backtest import (
    REBAL_FREQ, weekly_hold_position,
)

FREQ_GRID = [3, 5, 10, 21]


def evaluate(pos, r_t, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl = pos * r_t - turn * (cost_bps / 1e4)
    me = trading_metrics(pnl)
    ret = float(np.exp(pnl.sum()) - 1.0)
    return me, ret


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    r_pct = log_returns_pct(df).values
    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    pos_daily_full = vol_target_exposure(fc["vol_fcst"], TARGET_VOL_ANNUAL_PCT, CAP)
    r_t = r_pct[T0:] / 100.0
    pos_daily = pos_daily_full[T0:]

    me_bh, ret_bh = evaluate(np.ones_like(r_t), r_t, COST_BPS)
    me_bh25, ret_bh25 = evaluate(np.ones_like(r_t), r_t, 25.0)

    lines = [
        "# Robustesse — cycle #167, grille de fréquences de rebalancement",
        "",
        f"Point pré-enregistré : REBAL_FREQ = {REBAL_FREQ} jours. Grille annoncée au §5 "
        f"du PREREG : {{{', '.join(str(f) for f in FREQ_GRID)}}} jours.",
        "",
        "**Perturbation, pas retuning** : le verdict du cycle reste celui du point "
        "pré-enregistré (5 jours) quelle que soit la lecture de ce tableau.",
        "",
        f"Référence Buy & Hold : Sharpe {me_bh['sharpe_ann']:+.2f} / rendement "
        f"{100*ret_bh:+.1f}% (5 bps), Sharpe {me_bh25['sharpe_ann']:+.2f} / rendement "
        f"{100*ret_bh25:+.1f}% (25 bps).",
        "",
        "| Fréquence | Turnover réduit | Sharpe (5bps) | Rdt (5bps) | Sharpe (25bps) | Rdt (25bps) | 5bps OK | 25bps OK |",
        "|---|---|---|---|---|---|---|---|",
    ]
    turn_daily = np.abs(np.diff(pos_daily, prepend=1.0)).sum()
    n_ok_25 = 0
    for freq in FREQ_GRID:
        pos_w = weekly_hold_position(pos_daily, freq)
        turn_w = np.abs(np.diff(pos_w, prepend=1.0)).sum()
        reduction = 100 * (1 - turn_w / turn_daily)
        me5, ret5 = evaluate(pos_w, r_t, COST_BPS)
        me25, ret25 = evaluate(pos_w, r_t, 25.0)
        ok5 = (me5["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret5 > ret_bh)
        ok25 = (me25["sharpe_ann"] > me_bh25["sharpe_ann"]) and (ret25 > ret_bh25)
        n_ok_25 += int(ok25)
        star = " **(pré-enregistré)**" if freq == REBAL_FREQ else ""
        lines.append(
            f"| {freq}j{star} | {reduction:.1f}% | {me5['sharpe_ann']:+.2f} | {100*ret5:+.1f}% | "
            f"{me25['sharpe_ann']:+.2f} | {100*ret25:+.1f}% | {'OUI' if ok5 else 'non'} | "
            f"{'OUI' if ok25 else 'non'} |"
        )
    lines += [
        "",
        f"**{n_ok_25}/{len(FREQ_GRID)} fréquences de la grille corrigent le stress de coûts à 25 bps.**",
        "",
        "Lecture : un plateau indique que la correction n'est pas spécifique au choix "
        "5j, mais générale à toute réduction significative de turnover.",
    ]

    out = ROOT / "results" / "nonml_gjr_vol_managed_weekly_rebalance_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
