"""Backtest — Rebalancement hebdomadaire du portefeuille volatility-managed
GJR-t (#165), correction ciblée du contrôle (a) de la batterie Règle 9
(stress de coûts, ÉCHEC à 25 bps sur la position quotidienne).

Spécification figée dans `PREREG_gjr_vol_managed_weekly_rebalance.md`,
committé AVANT ce script. n_trials = 1. Réutilisation stricte (Règle 7) de
`weekly_hold_position()` du #154
(`nonml_cash_rate_correction_44_weekly_rebalance_backtest.py`) : la
position quotidienne du #165 est échantillonnée tous les REBAL_FREQ=5
jours et maintenue constante entre deux rebalancements. Aucun retuning du
signal de volatilité prévue sous-jacent.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from overlay import vol_target_exposure, walk_forward_vol_forecast  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_volatility_managed_portfolio_gjr_backtest import (  # noqa: E402
    CAP, COST_BPS, MARKET_FILE, MARKET_NAME, MODEL, REFIT_EVERY, T0,
    TARGET_VOL_ANNUAL_PCT,
)

REBAL_FREQ = 5  # identique au #154, semaine de bourse


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
    ret = float(np.exp(pnl.sum()) - 1.0)
    return me, ret, turn


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    ser = log_returns_pct(df)
    r_pct = ser.values
    dates = ser.index
    T = len(r_pct)

    fc = walk_forward_vol_forecast(r_pct, T0, REFIT_EVERY)
    pos_daily_full = vol_target_exposure(fc["vol_fcst"], TARGET_VOL_ANNUAL_PCT, CAP)

    r_t = r_pct[T0:] / 100.0
    pos_daily = pos_daily_full[T0:]
    dates_oos = dates[T0:]
    pos_weekly = weekly_hold_position(pos_daily, REBAL_FREQ)

    me_bh_5, ret_bh_5, _ = evaluate(np.ones_like(r_t), r_t, COST_BPS)
    me_d_5, ret_d_5, turn_d = evaluate(pos_daily, r_t, COST_BPS)
    me_w_5, ret_w_5, turn_w = evaluate(pos_weekly, r_t, COST_BPS)
    me_d_25, ret_d_25, _ = evaluate(pos_daily, r_t, 25.0)
    me_w_25, ret_w_25, _ = evaluate(pos_weekly, r_t, 25.0)
    me_bh_25, ret_bh_25, _ = evaluate(np.ones_like(r_t), r_t, 25.0)

    turnover_reduction = 100 * (1 - turn_w.sum() / turn_d.sum())

    ok_25 = (me_w_25["sharpe_ann"] > me_bh_25["sharpe_ann"]) and (ret_w_25 > ret_bh_25)
    ok_5_sharpe = me_w_5["sharpe_ann"] > me_bh_5["sharpe_ann"]
    ok_5_ret = ret_w_5 > ret_bh_5
    verdict = bool(ok_25 and ok_5_sharpe and ok_5_ret)

    lines = [
        "# Résultat — Rebalancement hebdomadaire du portefeuille volatility-managed GJR-t (#165, cycle #167)",
        "",
        "Spécification figée dans `PREREG_gjr_vol_managed_weekly_rebalance.md` "
        "(committé avant ce script). n_trials = 1. Correction ciblée du contrôle "
        "(a) de la batterie Règle 9 du #165 (stress de coûts, ÉCHEC à 25 bps) -- "
        "ne corrige PAS les contrôles (d) SPA et (e) DSR, structurellement "
        "indépendants du turnover (déclaré au PREREG §1).",
        "",
        f"Marché : {MARKET_NAME} (`data/{MARKET_FILE}`). Fenêtre OOS : {len(r_t)} séances, "
        f"{dates_oos[0]:%d/%m/%Y} → {dates_oos[-1]:%d/%m/%Y}. "
        f"Position quotidienne du #165 échantillonnée tous les {REBAL_FREQ} jours et "
        "maintenue constante entre deux rebalancements (`weekly_hold_position`, "
        "réutilisée à l'identique du #154).",
        "",
        f"**Turnover réduit de {turnover_reduction:.1f} %** "
        f"(quotidien : {turn_d.sum():.2f} cumulé, hebdo : {turn_w.sum():.2f} cumulé).",
        "",
        "## 1. Résultat à coût nominal (5 bps)",
        "",
        "| | Sharpe ann. | Rendement total | MDD |",
        "|---|---|---|---|",
        f"| Buy & Hold | {me_bh_5['sharpe_ann']:+.2f} | {100*ret_bh_5:+.1f}% | {me_bh_5['max_drawdown_pct']:.1f}% |",
        f"| Overlay quotidien (#165, rappel) | {me_d_5['sharpe_ann']:+.2f} | {100*ret_d_5:+.1f}% | {me_d_5['max_drawdown_pct']:.1f}% |",
        f"| **Overlay hebdomadaire** | **{me_w_5['sharpe_ann']:+.2f}** | **{100*ret_w_5:+.1f}%** | {me_w_5['max_drawdown_pct']:.1f}% |",
        "",
        f"- Sharpe hebdo > BH : {'OUI' if ok_5_sharpe else 'NON'}",
        f"- Rendement hebdo > BH : {'OUI' if ok_5_ret else 'NON'}",
        "",
        "## 2. Stress de coûts à 25 bps (le contrôle qui échouait au #165)",
        "",
        "| | Sharpe ann. | Rendement total |",
        "|---|---|---|",
        f"| Buy & Hold | {me_bh_25['sharpe_ann']:+.2f} | {100*ret_bh_25:+.1f}% |",
        f"| Overlay quotidien (#165, ÉCHEC rappelé) | {me_d_25['sharpe_ann']:+.2f} | {100*ret_d_25:+.1f}% |",
        f"| **Overlay hebdomadaire** | **{me_w_25['sharpe_ann']:+.2f}** | **{100*ret_w_25:+.1f}%** |",
        "",
        f"**Contrôle (a) à 25 bps avec la position hebdomadaire : {'OUI (corrigé)' if ok_25 else 'NON (toujours en échec)'}.**",
        "",
        "## 3. Verdict contre le critère pré-enregistré",
        "",
        f"**{'PASS' if verdict else 'FAIL'}** — contrôle (a) à 25 bps {'corrigé' if ok_25 else 'toujours en échec'} "
        f"ET verdict de niveau 1 à 5 bps {'maintenu' if (ok_5_sharpe and ok_5_ret) else 'PERDU'}.",
        "",
        "**Rappel honnête** : même en cas de PASS ici, les contrôles (d) SPA à 1 "
        "candidat (p=1,0000 au #165) et (e) DSR (n_trials=taille backlog, "
        "DSR≈0,0004 au #165) resteront en échec -- aucune réduction de turnover "
        "ne les affecte. Le score Règle 9 passera au mieux de 2/5 à 3/5, jamais "
        "à un PASS renforcé.",
    ]

    out = ROOT / "results" / "nonml_gjr_vol_managed_weekly_rebalance_result.md"
    out.write_text("\n".join(lines) + "\n")

    np.savez(
        ROOT / "results" / "nonml_gjr_vol_managed_weekly_rebalance_pnl.npz",
        pos=pos_weekly, r_asset=r_t, dates=pd.to_datetime(dates_oos).values,
        cost_bps=COST_BPS,
    )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")
    return verdict


if __name__ == "__main__":
    main()
