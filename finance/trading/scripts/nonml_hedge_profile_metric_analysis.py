"""Analyse du profil de couverture pour #115 (cycle #117, pré-enregistré
dans PREREG_hedge_profile_metric_analysis.md). PAS un nouveau backtest --
partitionne le pnl DÉJÀ committé de #115 en séances "crise" vs "calme"
(mêmes 4 fenêtres que la Règle 9b) pour documenter pourquoi le SPA
standard (edge régulier) est structurellement mal adapté à un profil
de couverture (coût faible en période calme, gain concentré en crise).
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

CRISIS_WINDOWS = [
    ("Dot-com crash", "2000-01-01", "2002-12-31"),
    ("Crise financière 2008", "2007-10-01", "2009-03-31"),
    ("Krach COVID", "2020-02-01", "2020-04-30"),
    ("Resserrement 2022", "2022-01-01", "2022-12-31"),
]


def main():
    npz_path = ROOT / "results" / "nonml_defensive_calmar_vol_targeting_overlay_pnl.npz"
    data = np.load(npz_path, allow_pickle=True)
    pos, r, cost_bps = data["pos"], data["r_asset"], float(data["cost_bps"])
    dates = pd.to_datetime(data["dates"])

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (cost_bps / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= cost_bps / 1e4
    diff = pnl_ov - pnl_bh

    crisis_mask = np.zeros(len(dates), dtype=bool)
    for _, d0, d1 in CRISIS_WINDOWS:
        crisis_mask |= (dates >= pd.Timestamp(d0)) & (dates <= pd.Timestamp(d1))
    calm_mask = ~crisis_mask

    n_crisis, n_calm = int(crisis_mask.sum()), int(calm_mask.sum())

    def stats_for(mask, label):
        pnl_ov_m, pnl_bh_m, diff_m = pnl_ov[mask], pnl_bh[mask], diff[mask]
        me_ov, me_bh = trading_metrics(pnl_ov_m), trading_metrics(pnl_bh_m)
        ret_ov = float(np.cumprod(1.0 + pnl_ov_m)[-1] - 1.0)
        ret_bh = float(np.cumprod(1.0 + pnl_bh_m)[-1] - 1.0)
        return {
            "label": label, "n": int(mask.sum()),
            "sharpe_ov": me_ov["sharpe_ann"], "sharpe_bh": me_bh["sharpe_ann"],
            "ret_ov": ret_ov, "ret_bh": ret_bh,
            "mdd_ov": me_ov["max_drawdown_pct"], "mdd_bh": me_bh["max_drawdown_pct"],
            "diff_mean_daily": float(diff_m.mean()),
        }

    s_crisis = stats_for(crisis_mask, "Crise (4 fenêtres)")
    s_calm = stats_for(calm_mask, "Calme (reste)")

    ratio = abs(s_crisis["diff_mean_daily"] / s_calm["diff_mean_daily"]) if s_calm["diff_mean_daily"] != 0 else float("inf")

    lines = [
        "# Analyse du profil de couverture — #115 (défensif Calmar) — cycle #117",
        "",
        f"Partition : {n_crisis} séances \"crise\" (4 fenêtres, Règle 9b) vs {n_calm} séances "
        f"\"calme\" (le reste), sur le pnl déjà committé (NDX, 40 ans).",
        "",
        "| Groupe | Séances | Sharpe overlay | Sharpe BH | Rendement overlay | Rendement BH | MDD overlay | MDD BH | Diff. moyen/séance |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in (s_crisis, s_calm):
        lines.append(
            f"| {s['label']} | {s['n']} | {s['sharpe_ov']:+.2f} | {s['sharpe_bh']:+.2f} | "
            f"{100*s['ret_ov']:+.1f}% | {100*s['ret_bh']:+.1f}% | {s['mdd_ov']:.1f}% | {s['mdd_bh']:.1f}% | "
            f"{10000*s['diff_mean_daily']:+.2f} bps |"
        )

    lines += [
        "",
        "## Lecture \"coût d'assurance / prime\"",
        "",
        f"Coût moyen par séance CALME (overlay moins BH) : {10000*s_calm['diff_mean_daily']:+.2f} bps/j.",
        f"Gain moyen par séance de CRISE (overlay moins BH) : {10000*s_crisis['diff_mean_daily']:+.2f} bps/j.",
        f"Ratio |gain crise| / |coût calme| : {ratio:.1f}x.",
        "",
        f"L'overlay {'coûte' if s_calm['diff_mean_daily'] < 0 else 'rapporte déjà'} "
        f"{'un peu' if abs(s_calm['diff_mean_daily']) < 0.0005 else 'significativement'} en période "
        f"calme ({n_calm} séances, la grande majorité de l'historique) mais {'protège nettement' if s_crisis['diff_mean_daily'] > 0 else 'ne protège pas'} "
        f"pendant les {n_crisis} séances de crise -- profil cohérent avec une COUVERTURE (petite prime "
        f"payée en continu, gros versement rare et concentré), pas un edge homogène dans le temps.",
        "",
        "## Pourquoi le SPA standard pénalise ce profil",
        "",
        "Le SPA studentise le différentiel moyen de perte par son écart-type de long terme estimé par "
        "bootstrap stationnaire. Un profil de couverture a une variance du différentiel DOMINÉE par les "
        f"{n_crisis} séances de crise (peu nombreuses, écarts extrêmes) au regard des "
        f"{n_calm} séances calmes (nombreuses, écarts faibles mais non nuls) -- ce qui gonfle l'écart-type "
        "long terme relativement à la moyenne, et fait mécaniquement baisser la statistique de test, "
        "même si le profil économique (payer peu, gagner beaucoup rarement) est exactement celui "
        "recherché pour une couverture de portefeuille. **Ceci documente une limite de l'OUTIL pour CE "
        "type de profil, PAS une invalidation du verdict Règle 9 déjà rendu sur #115 (qui reste FAIL "
        "sous la barre actuelle) ni un nouveau test statistique de substitution.**",
    ]

    out = ROOT / "results" / "nonml_hedge_profile_metric_analysis.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
