"""Verrou temporel OOS pur — #149 généralisé (S&P 500, Russell 2000) sur
les 12 derniers mois (cycle #158, pré-enregistré dans
PREREG_cash_rate_correction_44_crossmarket_oos_lockbox.md). Applique la
Règle 8, comme au #122 (#115), #138 (#134) et #153 (#149, NDX). AUCUN
paramètre modifié -- isole simplement les 252 dernières séances des
artefacts déjà committés.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
LOCKBOX_DAYS = 252

SOURCES = {
    "S&P 500": "nonml_cash_rate_correction_44_crossmarket_sp500_pnl.npz",
    "Russell 2000": "nonml_cash_rate_correction_44_crossmarket_russell2000_pnl.npz",
}


def main():
    lines = ["# Verrou temporel OOS pur — #149 généralisé (S&P 500, Russell 2000) sur les 12 derniers mois", ""]
    for name, fname in SOURCES.items():
        d = np.load(ROOT / "results" / fname, allow_pickle=True)
        pos_full, r_full, r_alt_full, cost_bps = d["pos"], d["r_asset"], d["r_alt"], float(d["cost_bps"])
        dates_full = pd.to_datetime(d["dates"])

        pos = pos_full[-LOCKBOX_DAYS:]
        r = r_full[-LOCKBOX_DAYS:]
        r_alt = r_alt_full[-LOCKBOX_DAYS:]
        dates = dates_full[-LOCKBOX_DAYS:]

        r_combined = pos * r + (1.0 - pos) * r_alt
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl_ov = r_combined - turn * (cost_bps / 1e4)
        pnl_bh = r.copy()
        pnl_bh[0] -= cost_bps / 1e4

        me_bh = trading_metrics(pnl_bh)
        me_ov = trading_metrics(pnl_ov)
        ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)
        ret_ov = float(np.exp(pnl_ov.sum()) - 1.0)
        calmar_bh = ret_bh / abs(me_bh["max_drawdown_pct"] / 100) if me_bh["max_drawdown_pct"] != 0 else float("-inf")
        calmar_ov = ret_ov / abs(me_ov["max_drawdown_pct"] / 100) if me_ov["max_drawdown_pct"] != 0 else float("-inf")
        verdict = calmar_ov > calmar_bh

        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"Fenêtre : {pd.Timestamp(dates[0]).date()} → {pd.Timestamp(dates[-1]).date()} ({LOCKBOX_DAYS} séances).")
        lines.append("")
        lines.append("| | Sharpe ann. | Rendement total net | MDD | Calmar |")
        lines.append("|---|---|---|---|---|")
        lines.append(f"| Buy&Hold | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |")
        lines.append(f"| **#149** | **{me_ov['sharpe_ann']:+.2f}** | **{100*ret_ov:+.1f}%** | "
                     f"{me_ov['max_drawdown_pct']:.1f}% | **{calmar_ov:.3f}** |")
        lines.append("")
        lines.append(f"**{'TIENT' if verdict else 'NE TIENT PAS'} — Calmar overlay > Calmar BH : {'OUI' if verdict else 'NON'}.**")
        lines.append("")

    lines.append(
        "Rapporté tel quel pour les deux marchés, conformément à la Règle 8 : aucun paramètre n'est "
        "retouché même si le résultat déçoit. Comparaison au #153 (NDX, même fenêtre relative, même "
        "critère) : le #153 avait conclu 'NE TIENT PAS' (Calmar 1,695 vs BH 2,230)."
    )

    out = ROOT / "results" / "nonml_cash_rate_correction_44_crossmarket_oos_lockbox_analysis.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
