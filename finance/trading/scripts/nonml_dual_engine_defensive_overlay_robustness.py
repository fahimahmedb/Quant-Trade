"""Robustesse — Overlay défensif combiné (#115 + GARCH). Grille du poids
de la moyenne (seul paramètre libre de cette construction), symétrique
autour de 0.5 pré-enregistré -- PAS un retuning après avoir vu quel
poids "marche le mieux".
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
WEIGHT_GRID = [0.3, 0.4, 0.5, 0.6, 0.7]  # poids de #115 ; poids GARCH = 1-w


def main():
    d1 = np.load(ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz", allow_pickle=True)
    d2 = np.load(ROOT / "results" / "nonml_etape_d_garch_defensive_overlay_pnl.npz", allow_pickle=True)
    dates1 = pd.to_datetime(d1["dates"])
    dates2 = pd.to_datetime(d2["dates"])
    s_pos1 = pd.Series(d1["pos"], index=dates1)
    s_pos2 = pd.Series(d2["pos"], index=dates2)
    s_r1 = pd.Series(d1["r_asset"], index=dates1)

    common = dates1.intersection(dates2).sort_values()
    pos1 = s_pos1.reindex(common).values
    pos2 = s_pos2.reindex(common).values
    r = s_r1.reindex(common).values

    pnl_bh = r.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    me_bh = trading_metrics(pnl_bh)
    ret_bh = float(np.cumprod(1.0 + pnl_bh)[-1] - 1.0)
    calmar_bh = me_bh["calmar"] if np.isfinite(me_bh["calmar"]) else -np.inf

    lines = [
        "# Robustesse — Overlay défensif combiné, grille du poids de la moyenne (PAS un retuning)",
        "",
        "Poids pré-enregistré = 0.5/0.5 (moyenne simple). Grille symétrique 0.3-0.7.",
        "",
        "| Poids #115 | Poids GARCH | Sharpe ann. | Rendement total | Calmar | PASS standard | PASS Calmar |",
        "|---|---|---|---|---|---|---|",
    ]
    for w in WEIGHT_GRID:
        pos_combined = w * pos1 + (1 - w) * pos2
        turn = np.abs(np.diff(pos_combined, prepend=1.0))
        pnl_ov = pos_combined * r - turn * (COST_BPS / 1e4)
        me_ov = trading_metrics(pnl_ov)
        ret_ov = float(np.cumprod(1.0 + pnl_ov)[-1] - 1.0)
        calmar_ov = me_ov["calmar"] if np.isfinite(me_ov["calmar"]) else -np.inf
        ok_std = (me_ov["sharpe_ann"] > me_bh["sharpe_ann"]) and (ret_ov > ret_bh)
        ok_calmar = calmar_ov > calmar_bh
        marker = " ← pré-enregistré" if w == 0.5 else ""
        lines.append(
            f"| {w:.1f} | {1-w:.1f} | {me_ov['sharpe_ann']:+.2f} | {100*ret_ov:+.1f}% | "
            f"{calmar_ov:.3f} | {'OUI' if ok_std else 'non'} | {'OUI' if ok_calmar else 'non'}{marker} |"
        )

    out = ROOT / "results" / "nonml_dual_engine_defensive_overlay_robustness.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
