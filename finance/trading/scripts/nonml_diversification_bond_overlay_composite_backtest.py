"""Backtest — Diversification obligataire (#134) sur le Composite
(échantillon pré-enregistré de référence, 5 ans) (spécification
pré-enregistrée dans PREREG_diversification_bond_overlay_composite.md,
committée avant ce script). n_trials=1, aucune dépendance ML. Règle de
succès renforcée niveau 1 -- SI PASS, résultat PAS final, voir Règle 9.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from data_loader import load_ohlc, quality_report  # noqa: E402
from prediction import trading_metrics  # noqa: E402
from nonml_defensive_calmar_vol_targeting_overlay_backtest import vol_target_position, VOL_WINDOW  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10, bond_return_proxy  # noqa: E402

COST_BPS = 5.0


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq_composite_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_full = pd.to_datetime(df["date"]).iloc[1:]
    r_full = np.log(close[1:] / close[:-1])

    pos_eq_full = vol_target_position(r_full)

    dgs10 = load_dgs10()
    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")

    valid = r_bond_aligned.notna().values
    start = max(VOL_WINDOW, int(np.argmax(valid)) if valid.any() else len(valid))

    pos_eq = pos_eq_full[start:]
    r_c = r_full[start:]
    r_bond = r_bond_aligned.values[start:]
    dates_used = dates_full.values[start:]

    r_combined = pos_eq * r_c + (1.0 - pos_eq) * r_bond
    turn = np.abs(np.diff(pos_eq, prepend=1.0))
    pnl_ov = r_combined - turn * (COST_BPS / 1e4)
    pnl_bh = r_c.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.exp(pnl_bh.sum()) - 1.0
    ret_ov = np.exp(pnl_ov.sum()) - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict_standard = sharpe_ok and ret_ok

    calmar_bh = ret_bh / abs(me_bh["max_drawdown_pct"] / 100)
    calmar_ov = ret_ov / abs(me_ov["max_drawdown_pct"] / 100)
    calmar_ok = calmar_ov > calmar_bh
    verdict = verdict_standard or calmar_ok

    lines = [
        "# Résultat — Diversification obligataire sur le Composite (échantillon de référence, pré-enregistré, deux critères)",
        "",
        f"**Limite reconnue à l'avance** : échantillon court ({len(r_c)} séances, 5 ans) vs "
        "9522-14231 pour NDX/S&P500/Russell2000 -- puissance statistique bien moindre, une seule "
        "fenêtre de crise couverte (2022).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (Composite 100%) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| **Diversification obligataire** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% | {calmar_ov:.3f} |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        f"3. Critère standard (1 ET 2) : {'PASS' if verdict_standard else 'FAIL'}",
        f"4. Critère Calmar (overlay > BH) : {'PASS' if calmar_ok else 'FAIL'}",
        "",
        f"**{'PASS (niveau 1, au moins un critère)' if verdict else 'FAIL'}**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py diversification_bond_overlay_composite`.**")

    out = ROOT / "results" / "nonml_diversification_bond_overlay_composite_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        np.savez(
            ROOT / "results" / "nonml_diversification_bond_overlay_composite_pnl.npz",
            pos=pos_eq, r_asset=r_c, r_alt=r_bond, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
