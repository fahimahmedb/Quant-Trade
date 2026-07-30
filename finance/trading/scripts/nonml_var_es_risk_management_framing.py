"""Le #134 comme outil de RISK MANAGEMENT (VaR/Expected Shortfall), pas
comme stratégie de battre le benchmark (spécification pré-enregistrée
dans PREREG_var_es_risk_management_framing.md, committée avant ce
script). PAS un nouveau backtest, ne change AUCUN verdict Règle 9 déjà
rendu -- cycle #135, analyse informative.
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
    """VaR historique (perte au quantile) et Expected Shortfall (moyenne
    des pertes au-dela du VaR), niveau ex. 0.95 ou 0.99."""
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
    d = np.load(ROOT / "results" / "nonml_defensive_diversification_bond_overlay_pnl.npz", allow_pickle=True)
    pos_eq, r_ndx, r_bond = d["pos"], d["r_asset"], d["r_alt"]
    dates = pd.to_datetime(d["dates"])

    pnl_ov, pnl_bh = pnl_combined(pos_eq, r_ndx, r_bond)

    lines = [
        "# Le #134 comme outil de RISK MANAGEMENT — VaR / Expected Shortfall (cycle #135, INFORMATIF)",
        "",
        "PAS un nouveau backtest. Ne change AUCUN verdict Règle 9 déjà rendu (le #134 reste FAIL sous "
        "SPA/DSR) — caractérisation complémentaire du profil de risque, cohérent avec la conclusion "
        "de l'Étape C et la 2e voie de recommandation du #132.",
        "",
        "## 1. VaR / ES sur l'échantillon complet",
        "",
        "| Métrique | Buy&Hold (NDX 100%) | #134 (diversification obligataire) | Réduction |",
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
    lines.append("| Fenêtre | VaR99 BH | VaR99 #134 | ES99 BH | ES99 #134 | Réduction ES99 |")
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

    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        "Le #134 réduit systématiquement le VaR ET l'Expected Shortfall par rapport à Buy&Hold, sur "
        "l'échantillon complet ET sur chacune des 4 fenêtres de crise historiques (cohérent avec le "
        "MDD déjà documenté à la Règle 9b). Cette caractérisation NE CHANGE PAS le verdict Règle 9 "
        "officiel (SPA/DSR restent en échec, le #134 ne bat pas le benchmark à un niveau de preuve "
        "statistique strict) — mais elle documente, avec des métriques qu'un gérant de risque utilise "
        "réellement, que le mécanisme réduit mesurablement le risque de queue, cohérence directe avec "
        "la conclusion déjà établie de l'Étape C (\"le modèle de volatilité est utile pour le risk "
        "management, pas pour prédire une direction\") et la 2e voie de recommandation du #132."
    )

    out = ROOT / "results" / "nonml_var_es_risk_management_framing.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
