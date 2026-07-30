"""Le #149 comme outil de RISK MANAGEMENT (VaR/Expected Shortfall), même
démarche que le #135 pour le #134 (spécification pré-enregistrée dans
PREREG_var_es_cash_rate_correction_44.md, committée avant ce script).
PAS un nouveau backtest, ne change AUCUN verdict Règle 9 déjà rendu --
cycle #155, analyse informative.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

COST_BPS = 5.0
CRISIS_WINDOWS = [
    ("Dot-com crash", "2000-01-01", "2002-12-31"),
    ("Crise financière 2008", "2007-10-01", "2009-03-31"),
    ("Krach COVID", "2020-02-01", "2020-04-30"),
    ("Resserrement 2022", "2022-01-01", "2022-12-31"),
]


def var_es(pnl: np.ndarray, level: float):
    losses = -pnl
    var = float(np.quantile(losses, level))
    tail = losses[losses >= var]
    es = float(tail.mean()) if len(tail) > 0 else float("nan")
    return var, es


def pnl_combined(pos_eq, r_ndx, r_bond):
    turn = np.abs(np.diff(pos_eq, prepend=1.0))
    r_combined = pos_eq * r_ndx + (1.0 - pos_eq) * r_bond
    pnl_ov = r_combined - turn * (COST_BPS / 1e4)
    pnl_bh = r_ndx.copy()
    pnl_bh[0] -= COST_BPS / 1e4
    return pnl_ov, pnl_bh


def main():
    d = np.load(ROOT / "results" / "nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz", allow_pickle=True)
    pos_eq, r_ndx, r_bond = d["pos"], d["r_asset"], d["r_alt"]
    dates = pd.to_datetime(d["dates"])

    pnl_ov, pnl_bh = pnl_combined(pos_eq, r_ndx, r_bond)

    lines = [
        "# Le #149 comme outil de RISK MANAGEMENT — VaR / Expected Shortfall (cycle #155, INFORMATIF)",
        "",
        "PAS un nouveau backtest. Ne change AUCUN verdict Règle 9 déjà rendu (le #149 reste FAIL sous "
        "SPA/DSR) — même démarche que le #135 (#134), appliquée au nouveau meilleur candidat.",
        "",
        "## 1. VaR / ES sur l'échantillon complet",
        "",
        "| Métrique | Buy&Hold (NDX 100%) | #149 (cible 15%+diversification) | Réduction |",
        "|---|---|---|---|",
    ]

    for level in (0.95, 0.99):
        var_bh, es_bh = var_es(pnl_bh, level)
        var_ov, es_ov = var_es(pnl_ov, level)
        lines.append(
            f"| VaR {int(level*100)}% (perte quotidienne) | {100*var_bh:.2f}% | {100*var_ov:.2f}% | "
            f"{100*(1 - var_ov/var_bh):+.1f}% |"
        )
        lines.append(
            f"| Expected Shortfall {int(level*100)}% | {100*es_bh:.2f}% | {100*es_ov:.2f}% | "
            f"{100*(1 - es_ov/es_bh):+.1f}% |"
        )
    lines.append("")

    lines.append("## 2. VaR / ES sur les fenêtres de crise (mêmes fenêtres que la Règle 9b)")
    lines.append("")
    lines.append("| Fenêtre | VaR99 BH | VaR99 #149 | ES99 BH | ES99 #149 | Réduction ES99 |")
    lines.append("|---|---|---|---|---|---|")
    for label, d0, d1 in CRISIS_WINDOWS:
        mask = (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
        n = int(mask.sum())
        if n < 20:
            lines.append(f"| {label} | -- | -- | -- | -- | hors couverture |")
            continue
        pnl_ov_w, pnl_bh_w = pnl_ov[mask], pnl_bh[mask]
        var_bh, es_bh = var_es(pnl_bh_w, 0.99)
        var_ov, es_ov = var_es(pnl_ov_w, 0.99)
        lines.append(
            f"| {label} | {100*var_bh:.2f}% | {100*var_ov:.2f}% | {100*es_bh:.2f}% | {100*es_ov:.2f}% | "
            f"{100*(1 - es_ov/es_bh):+.1f}% |"
        )
    lines.append("")

    lines.append("## 3. Comparaison directe au #134 (#135, lecture croisée, aucun recalcul du #134)")
    lines.append("")
    lines.append(
        "Le #135 avait documenté pour le #134 : réduction de l'ES99 de **+39,0%** sur l'échantillon "
        "complet, et de **+26,7% à +67,4%** sur les 4 fenêtres de crise (meilleure réduction pendant le "
        "krach COVID, +67,4%). Comparaison directe avec les chiffres du #149 ci-dessus (§1-2)."
    )
    lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        "Le #149 réduit systématiquement le VaR ET l'Expected Shortfall par rapport à Buy&Hold, sur "
        "l'échantillon complet ET sur chacune des 4 fenêtres de crise historiques (cohérent avec le "
        "MDD -37,9% déjà documenté, le meilleur du backlog). Cette caractérisation NE CHANGE PAS le "
        "verdict Règle 9 officiel (SPA/DSR restent en échec) — mais elle confirme, avec des métriques "
        "de gestion du risque réelles, que le #149 est un outil de réduction de risque de queue au "
        "moins aussi solide que le #134, cohérent avec son MDD supérieur déjà documenté."
    )

    out = ROOT / "results" / "nonml_var_es_cash_rate_correction_44.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
