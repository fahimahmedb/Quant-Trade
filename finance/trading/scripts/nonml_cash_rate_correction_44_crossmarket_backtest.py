"""Backtest — Correction taux réaliste sur le #44 généralisée à S&P 500
et Russell 2000 (spécification pré-enregistrée dans
PREREG_cash_rate_correction_44_crossmarket.md, committée avant ce
script). n_trials=1 par marché, aucune dépendance ML. Règle de succès
renforcée niveau 1 (critère IDENTIQUE au #44/#149) -- SI PASS, résultat
PAS final, voir Règle 9.
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
MARKETS = {"S&P 500": "sp500_daily.txt", "Russell 2000": "russell2000_daily.txt"}


def main():
    dgs10 = load_dgs10()
    r_bond_all = bond_return_proxy(dgs10)

    lines = [
        "# Résultat — Correction taux réaliste sur le #44 généralisée cross-marché (pré-enregistré, Règle 3)",
        "",
        "Mécanisme IDENTIQUE au #149 (position #44 sans retuning + proxy DGS10), appliqué "
        "sans modification à 2 marchés indépendants de NDX.",
        "",
        "| Marché | Séances | BH Sharpe | BH Rdt | BH MDD | Overlay Sharpe | Overlay Rdt | Overlay MDD | PASS |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    any_pass = {}
    for name, fname in MARKETS.items():
        df = load_ohlc(str(REPO_ROOT / "data" / fname))
        quality_report(df)
        close = df["close"].values
        dates_full = pd.to_datetime(df["date"]).iloc[1:]
        r_full = np.log(close[1:] / close[:-1])

        pos_eq_full = vol_target_position(r_full)
        r_bond_aligned = r_bond_all.reindex(dates_full, method="ffill")
        valid = r_bond_aligned.notna().values
        start = max(VOL_WINDOW, int(np.argmax(valid)) if valid.any() else len(valid))

        pos_eq = pos_eq_full[start:]
        r_mkt = r_full[start:]
        r_bond = r_bond_aligned.values[start:]
        dates_used = dates_full.values[start:]

        r_combined = pos_eq * r_mkt + (1.0 - pos_eq) * r_bond
        turn = np.abs(np.diff(pos_eq, prepend=1.0))
        pnl_ov = r_combined - turn * (COST_BPS / 1e4)
        pnl_bh = r_mkt.copy()
        pnl_bh[0] -= COST_BPS / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)
        ret_ov = float(np.cumprod(1.0 + pnl_ov)[-1] - 1.0)

        sharpe_ok = me_ov["sharpe_ann"] > me_bh["sharpe_ann"]
        ret_ok = ret_ov > ret_bh
        verdict = sharpe_ok and ret_ok
        any_pass[name] = (verdict, pos_eq, r_mkt, r_bond, dates_used)

        lines.append(
            f"| {name} | {len(r_mkt)} | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | "
            f"{me_bh['max_drawdown_pct']:.1f}% | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{me_ov['max_drawdown_pct']:.1f}% | {'OUI' if verdict else 'non'} |"
        )

    n_pass = sum(1 for v in any_pass.values() if v[0])
    lines.append("")
    lines.append(f"**{n_pass}/{len(MARKETS)} marchés PASS niveau 1.**")

    out = ROOT / "results" / "nonml_cash_rate_correction_44_crossmarket_result.md"
    out.write_text("\n".join(lines) + "\n")

    slugs = {"S&P 500": "sp500", "Russell 2000": "russell2000"}
    for name, (verdict, pos_eq, r_mkt, r_bond, dates_used) in any_pass.items():
        if verdict:
            slug = slugs[name]
            np.savez(
                ROOT / "results" / f"nonml_cash_rate_correction_44_crossmarket_{slug}_pnl.npz",
                pos=pos_eq, r_asset=r_mkt, r_alt=r_bond, dates=dates_used, cost_bps=COST_BPS,
            )

    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
