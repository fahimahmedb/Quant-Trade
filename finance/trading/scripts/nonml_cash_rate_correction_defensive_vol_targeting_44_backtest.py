"""Backtest — Correction "taux réaliste sur cash" appliquée au #44
(vol-targeting défensif, cible 15%) (spécification pré-enregistrée
dans PREREG_cash_rate_correction_defensive_vol_targeting_44.md,
committée avant ce script). n_trials=1, aucune dépendance ML. Règle de
succès renforcée niveau 1 (critère IDENTIQUE au #44 original) -- SI
PASS, résultat PAS final, voir Règle 9.
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
from nonml_defensive_vol_targeting_overlay_backtest import vol_target_position, VOL_WINDOW  # noqa: E402
from nonml_defensive_diversification_bond_overlay_backtest import load_dgs10, bond_return_proxy  # noqa: E402

COST_BPS = 5.0


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / "nasdaq100_daily.txt"))
    quality_report(df)
    close = df["close"].values
    dates_full = pd.to_datetime(df["date"]).iloc[1:]
    r_ndx_full = np.log(close[1:] / close[:-1])

    pos_eq_full = vol_target_position(r_ndx_full)

    dgs10 = load_dgs10()
    r_bond_all = bond_return_proxy(dgs10)
    r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")

    valid = r_bond_aligned.notna().values
    start = max(VOL_WINDOW, int(np.argmax(valid)) if valid.any() else len(valid))

    pos_eq = pos_eq_full[start:]
    r_ndx = r_ndx_full[start:]
    r_bond = r_bond_aligned.values[start:]
    dates_used = dates_full.values[start:]

    r_combined = pos_eq * r_ndx + (1.0 - pos_eq) * r_bond
    turn = np.abs(np.diff(pos_eq, prepend=1.0))
    pnl_ov = r_combined - turn * (COST_BPS / 1e4)
    pnl_bh = r_ndx.copy()
    pnl_bh[0] -= COST_BPS / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = np.cumprod(1.0 + pnl_bh)[-1] - 1.0
    ret_ov = np.cumprod(1.0 + pnl_ov)[-1] - 1.0

    sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
    ret_ok = ret_ov > ret_bh
    verdict = sharpe_ok and ret_ok  # critere IDENTIQUE au #44 original

    lines = [
        "# Résultat — Correction taux réaliste sur cash appliquée au #44 (vol-targeting défensif cible 15%, NDX) (pré-enregistré)",
        "",
        f"Position équity #44 STRICTEMENT INCHANGÉE (TARGET_VOL_ANNUAL=15%, CAP=1.0x) ; fraction "
        f"(1-pos_eq) allouée au proxy obligataire DGS10 au lieu du cash à 0%. {len(r_ndx)} séances "
        f"(fenêtre commune NDX ∩ DGS10).",
        "",
        f"Position équity moyenne : {pos_eq.mean():.2f}x",
        "",
        "| | Sharpe ann. | Rendement total net | MDD |",
        "|---|---|---|---|",
        f"| Buy&Hold (NDX 100%) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% |",
        f"| **#44 + correction taux réaliste** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% |",
        "",
        f"1. Sharpe overlay > BH : {'OUI' if sharpe_ok else 'non'}",
        f"2. Rendement overlay > BH : {'OUI' if ret_ok else 'non'}",
        "",
        f"**{'PASS (niveau 1)' if verdict else 'FAIL'} — critère renforcé (IDENTIQUE au #44 original) "
        f"{'atteint' if verdict else 'NON atteint'}.**",
    ]
    if verdict:
        lines.append("")
        lines.append("**PASS niveau 1 seulement -- pas un verdict final (Règle 9). Doit encore passer "
                     "`nonml_pass_validation_battery.py cash_rate_correction_defensive_vol_targeting_44`.**")

    out = ROOT / "results" / "nonml_cash_rate_correction_defensive_vol_targeting_44_result.md"
    out.write_text("\n".join(lines) + "\n")

    if verdict:
        np.savez(
            ROOT / "results" / "nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz",
            pos=pos_eq, r_asset=r_ndx, r_alt=r_bond, dates=dates_used, cost_bps=COST_BPS,
        )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
