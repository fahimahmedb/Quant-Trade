"""Verrou temporel OOS pur — #115 sur les 12 derniers mois (cycle #122,
pré-enregistré dans PREREG_ndx_defensive_oos_lockbox.md). Applique la
Règle 8 de PROTOCOLE_ANTI_SNOOPING.md pour la première fois dans ce
backlog. AUCUN paramètre du #115 n'est modifié -- isole simplement les
252 dernières séances de l'artefact déjà committé.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0
LOCKBOX_DAYS = 252  # ~12 mois de bourse


def main():
    d = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    pos_full, r_full, cost_bps = d["pos"], d["r_asset"], float(d["cost_bps"])
    dates_full = pd.to_datetime(d["dates"])

    pos = pos_full[-LOCKBOX_DAYS:]
    r = r_full[-LOCKBOX_DAYS:]
    dates = dates_full[-LOCKBOX_DAYS:]

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (cost_bps / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= cost_bps / 1e4

    me_bh = trading_metrics(pnl_bh)
    me_ov = trading_metrics(pnl_ov)
    ret_bh = float(np.exp(pnl_bh.sum()) - 1.0)
    ret_ov = float(np.exp(pnl_ov.sum()) - 1.0)
    calmar_bh = me_bh["calmar"] if np.isfinite(me_bh["calmar"]) else -np.inf
    calmar_ov = me_ov["calmar"] if np.isfinite(me_ov["calmar"]) else -np.inf
    verdict = calmar_ov > calmar_bh

    lines = [
        "# Verrou temporel OOS pur — #115 (défensif Calmar) sur les 12 derniers mois",
        "",
        f"Fenêtre : {dates[0].date()} → {dates[-1].date()} ({LOCKBOX_DAYS} séances), "
        f"AUCUN paramètre du #115 modifié (TARGET_VOL_ANNUAL=20%, VOL_WINDOW=20j, CAP=1.0x, floor=0.0x).",
        "",
        "| | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold (NDX) | {me_bh['sharpe_ann']:+.2f} | {100*ret_bh:+.1f}% | {me_bh['max_drawdown_pct']:.1f}% | {calmar_bh:.3f} |",
        f"| **Overlay défensif #115** | **{me_ov['sharpe_ann']:+.2f}** | "
        f"**{100*ret_ov:+.1f}%** | {me_ov['max_drawdown_pct']:.1f}% | **{calmar_ov:.3f}** |",
        "",
        f"**{'TIENT' if verdict else 'NE TIENT PAS'} sur cette fenêtre OOS pure — Calmar overlay > Calmar BH : "
        f"{'OUI' if verdict else 'NON'}.**",
        "",
        "Rapporté tel quel, conformément à la Règle 8 (verrou temporel) : aucun paramètre n'est "
        "retouché même si le résultat déçoit sur cette fenêtre.",
    ]

    out = ROOT / "results" / "nonml_ndx_defensive_oos_lockbox_analysis.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
