"""Backtest — Sleeve dollar-neutre composite (#349) redimensionné par
sa propre volatilité réalisée (Piste C de
RECHERCHE_dsr_par_construction.md, spécification pré-enregistrée dans
PREREG_dollar_neutral_composite_vol_targeted.md, committée avant ce
script). n_trials=1, aucune dépendance ML.

Réutilise STRICTEMENT `vol_target_position` du #46
(nonml_vol_targeting_overlay_backtest.py — TARGET_VOL_ANNUAL=0.15,
VOL_WINDOW=20, CAP=2.0 inchangés, Règle 7), appliquée au flux de
rendement déjà net de coûts du sleeve du #349
(nonml_dollar_neutral_composite_pit_pnl.npz).
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
from nonml_vol_targeting_overlay_backtest import (  # noqa: E402
    CAP, COST_BPS, TARGET_VOL_ANNUAL, VOL_WINDOW, vol_target_position,
)


def main():
    data = np.load(ROOT / "results" / "nonml_dollar_neutral_composite_pit_pnl.npz", allow_pickle=True)
    pnl_sleeve_net = data["pnl_candidate"].astype(float)
    pnl_ref = data["pnl_ref"].astype(float)
    dates = pd.to_datetime(data["dates"])

    pos_full = vol_target_position(pnl_sleeve_net)
    start = VOL_WINDOW
    r_underlying = pnl_sleeve_net[start:]
    pos = pos_full[start:]
    dates_t = dates[start:]
    ref_t = pnl_ref[start:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    r_vt = pos * r_underlying - turn * (COST_BPS / 1e4)

    me_base = trading_metrics(r_underlying)
    me_vt = trading_metrics(r_vt)
    ret_base = float(np.cumprod(1.0 + r_underlying)[-1] - 1.0)
    ret_vt = float(np.cumprod(1.0 + r_vt)[-1] - 1.0)
    me_ref = trading_metrics(ref_t)
    ret_ref = float(np.cumprod(1.0 + ref_t)[-1] - 1.0)

    sharpe_daily = r_vt.mean() / r_vt.std() if r_vt.std() > 0 else float("nan")
    tstat = sharpe_daily * np.sqrt(len(r_vt))

    ok_sharpe_pos = me_vt["sharpe_ann"] > 0
    ok_tstat = tstat > 2
    verdict = ok_sharpe_pos and ok_tstat

    lines = [
        "# Résultat — Sleeve dollar-neutre composite redimensionné par sa propre volatilité (Piste C, pré-enregistré)",
        "",
        f"`pos(t) = clip({TARGET_VOL_ANNUAL:.0%} / vol_réalisée_{VOL_WINDOW}j(sleeve, t-1), 0, {CAP:.1f}x)` "
        f"(overlay #46 réutilisé à l'identique), appliqué au rendement quotidien du sleeve du #349 "
        f"(déjà net de ses propres coûts de rebalancement). Coût supplémentaire {COST_BPS:.0f} bps sur le "
        "turnover du levier quotidien.",
        "",
        f"Échantillon : {len(r_vt)} séances ({dates_t[0].date()} → {dates_t[-1].date()}). "
        f"Position moyenne : {pos.mean():.2f}x (min {pos.min():.2f}x, max {pos.max():.2f}x).",
        "",
        "| | Sharpe ann. | Sharpe journalier | t-stat | Rendement total | MDD |",
        "|---|---|---|---|---|---|",
        f"| Buy&Hold PIT (contexte, hérité du #349) | {me_ref['sharpe_ann']:+.2f} | — | — | "
        f"{100*ret_ref:+.1f}% | {me_ref['max_drawdown_pct']:.1f}% |",
        f"| Sleeve #349 SANS vol-targeting (référence directe) | {me_base['sharpe_ann']:+.2f} | — | — | "
        f"{100*ret_base:+.1f}% | {me_base['max_drawdown_pct']:.1f}% |",
        f"| **Sleeve redimensionné par sa vol (Piste C)** | **{me_vt['sharpe_ann']:+.2f}** | "
        f"{sharpe_daily:+.4f} | **{tstat:+.2f}** | {100*ret_vt:+.1f}% | {me_vt['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe annualisé > 0 : {'OUI' if ok_sharpe_pos else 'non'}",
        f"2. t-stat > 2 : {'OUI' if ok_tstat else 'non'}",
        "",
        f"**{'PASS' if verdict else 'FAIL'} — critère pré-enregistré (Sharpe>0 ET t-stat>2, "
        f"identique au #349) {'atteint' if verdict else 'NON atteint'}.**",
    ]

    out = ROOT / "results" / "nonml_dollar_neutral_composite_vol_targeted_result.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")

    np.savez(ROOT / "results" / "nonml_dollar_neutral_composite_vol_targeted_pnl.npz",
             pnl_candidate=r_vt, pnl_ref=ref_t, dates=dates_t.values, cost_bps=COST_BPS)

    return verdict


if __name__ == "__main__":
    main()
