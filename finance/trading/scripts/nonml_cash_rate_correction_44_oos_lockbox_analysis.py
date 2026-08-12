"""Verrou temporel OOS pur — #149 sur les 12 derniers mois (cycle #153,
pré-enregistré dans PREREG_cash_rate_correction_44_oos_lockbox.md).
Applique la Règle 8 de PROTOCOLE_ANTI_SNOOPING.md, comme au #122 (#115)
et au #138 (#134). AUCUN paramètre du #149 n'est modifié -- isole
simplement les 252 dernières séances de l'artefact déjà committé.
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
LOCKBOX_DAYS = 252  # ~12 mois de bourse


def main():
    d = np.load(ROOT / "results" / "nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz", allow_pickle=True)
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

    lines = [
        "# Verrou temporel OOS pur — #149 (cible 15% + diversification obligataire) sur les 12 derniers mois",
        "",
        f"Fenêtre : {pd.Timestamp(dates[0]).date()} → {pd.Timestamp(dates[-1]).date()} ({LOCKBOX_DAYS} séances), "
        "AUCUN paramètre du #149 modifié (position #44 inchangée, TARGET_VOL_ANNUAL=15%, + proxy DGS10, "
        "MATURITY_YEARS=10).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| **#149 (cible 15% + diversification)** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% | **{calmar_ov:.3f}** |",
        "",
        f"**{'TIENT' if verdict else 'NE TIENT PAS'} sur cette fenêtre OOS pure — Calmar overlay > Calmar BH : "
        f"{'OUI' if verdict else 'NON'}.**",
        "",
        "Rapporté tel quel, conformément à la Règle 8 (verrou temporel) : aucun paramètre n'est "
        "retouché même si le résultat déçoit sur cette fenêtre.",
        "",
        "Comparaison au #138 (même fenêtre, même critère, sur le #134 cible 20%) : le #138 avait conclu "
        "'NE TIENT PAS' (Calmar 1,961 vs BH 2,230). Ce cycle répond à la question 'le mécanisme plus "
        "agressivement défensif (cible 15%) change-t-il cette conclusion sur la MÊME fenêtre ?'.",
    ]

    out = ROOT / "results" / "nonml_cash_rate_correction_44_oos_lockbox_analysis.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
