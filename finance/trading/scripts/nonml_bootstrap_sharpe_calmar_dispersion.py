"""Bootstrap Sharpe/Calmar du #121 (cycle #125, pré-enregistré dans
PREREG_bootstrap_sharpe_calmar_dispersion.md). PAS un nouveau backtest --
mesure la dispersion (IC 95%) des estimateurs Sharpe/Calmar via
bootstrap stationnaire, sur le pnl déjà committé du #121.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402
from volatility import _stationary_bootstrap_idx  # noqa: E402

COST_BPS = 5.0
B = 2000
MEAN_BLOCK = 20.0
SEED = 125


def sharpe_calmar(pnl: np.ndarray):
    me = trading_metrics(pnl)
    return me["sharpe_ann"], (me["calmar"] if np.isfinite(me["calmar"]) else np.nan)


def main():
    d = np.load(ROOT / "results" / "nonml_dual_engine_defensive_overlay_pnl.npz", allow_pickle=True)
    pos, r, cost_bps = d["pos"], d["r_asset"], float(d["cost_bps"])

    turn = np.abs(np.diff(pos, prepend=1.0))
    pnl_ov = pos * r - turn * (cost_bps / 1e4)
    pnl_bh = r.copy()
    pnl_bh[0] -= cost_bps / 1e4

    sharpe_ov0, calmar_ov0 = sharpe_calmar(pnl_ov)
    sharpe_bh0, calmar_bh0 = sharpe_calmar(pnl_bh)

    T = len(pnl_ov)
    rng = np.random.default_rng(SEED)
    sharpe_ov_b = np.empty(B)
    calmar_ov_b = np.empty(B)
    sharpe_bh_b = np.empty(B)
    calmar_bh_b = np.empty(B)
    for b in range(B):
        idx = _stationary_bootstrap_idx(T, MEAN_BLOCK, rng)
        pnl_ov_b = pnl_ov[idx]
        pnl_bh_b = pnl_bh[idx]
        sharpe_ov_b[b], calmar_ov_b[b] = sharpe_calmar(pnl_ov_b)
        sharpe_bh_b[b], calmar_bh_b[b] = sharpe_calmar(pnl_bh_b)

    def ci(x):
        x = x[np.isfinite(x)]
        return np.percentile(x, 2.5), np.percentile(x, 97.5)

    sharpe_ov_ci = ci(sharpe_ov_b)
    calmar_ov_ci = ci(calmar_ov_b)
    sharpe_diff_ci = ci(sharpe_ov_b - sharpe_bh_b)
    calmar_diff_ci = ci(calmar_ov_b - calmar_bh_b)
    sharpe_zero_in_ci = sharpe_diff_ci[0] < 0 < sharpe_diff_ci[1]
    calmar_zero_in_ci = calmar_diff_ci[0] < 0 < calmar_diff_ci[1]
    sharpe_ci_label = "OUI (0 dans l'IC)" if sharpe_zero_in_ci else "NON (0 hors IC)"
    calmar_ci_label = "OUI (0 dans l'IC)" if calmar_zero_in_ci else "NON (0 hors IC)"
    frac_sharpe_diff_pos = float(np.mean((sharpe_ov_b - sharpe_bh_b) > 0))
    frac_calmar_diff_pos = float(np.mean((calmar_ov_b - calmar_bh_b) > 0))

    lines = [
        "# Bootstrap Sharpe/Calmar — dispersion de l'estimateur pour le #121 (cycle #125)",
        "",
        f"Bootstrap stationnaire de Politis-Romano, B={B}, mean_block={MEAN_BLOCK:.0f}j "
        f"(mêmes paramètres que `spa_test`, aucun retuning). {T} séances (fenêtre du #121).",
        "",
        "## Point estimé (déjà committé)",
        "",
        f"Sharpe overlay = {sharpe_ov0:+.3f}, Calmar overlay = {calmar_ov0:.3f} ; "
        f"Sharpe BH = {sharpe_bh0:+.3f}, Calmar BH = {calmar_bh0:.3f}.",
        "",
        "## Intervalles de confiance bootstrap (95%)",
        "",
        "| Quantité | IC 95% | Contient 0 (ou BH) ? |",
        "|---|---|---|",
        f"| Sharpe overlay | [{sharpe_ov_ci[0]:+.3f}, {sharpe_ov_ci[1]:+.3f}] | -- |",
        f"| Calmar overlay | [{calmar_ov_ci[0]:.3f}, {calmar_ov_ci[1]:.3f}] | -- |",
        f"| Sharpe overlay - Sharpe BH | [{sharpe_diff_ci[0]:+.3f}, {sharpe_diff_ci[1]:+.3f}] | {sharpe_ci_label} |",
        f"| Calmar overlay - Calmar BH | [{calmar_diff_ci[0]:+.3f}, {calmar_diff_ci[1]:+.3f}] | {calmar_ci_label} |",
        "",
        f"Fraction des répétitions bootstrap où l'overlay bat BH en Sharpe : {100*frac_sharpe_diff_pos:.1f}%.",
        f"Fraction des répétitions bootstrap où l'overlay bat BH en Calmar : {100*frac_calmar_diff_pos:.1f}%.",
        "",
        "## Lecture honnête",
        "",
    ]
    if sharpe_zero_in_ci:
        lines.append(
            "L'IC bootstrap de la DIFFÉRENCE de Sharpe contient 0 -- cohérent avec le SPA (p=0,45, "
            "non significatif) : la dispersion de l'estimateur est trop large pour exclure que le "
            "point estimé positif soit un artefact de l'échantillon précis observé. Ne change PAS le "
            "verdict Règle 9 (déjà FAIL) mais quantifie DIRECTEMENT pourquoi : même sans test formel, "
            "l'incertitude d'estimation seule suffit à ne pas exclure une différence nulle ou négative."
        )
    else:
        lines.append(
            "L'IC bootstrap de la DIFFÉRENCE de Sharpe exclut 0 -- en tension apparente avec le SPA "
            "(p=0,45, non significatif), possible car les deux tests utilisent des statistiques et des "
            "corrections différentes (SPA corrige pour un univers de comparaison, ce bootstrap ne teste "
            "qu'un intervalle de confiance simple sur CE seul candidat). Ne change PAS le verdict Règle "
            "9 officiel (basé sur le SPA, pas ce bootstrap)."
        )

    out = ROOT / "results" / "nonml_bootstrap_sharpe_calmar_dispersion.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
