"""Analyse de sensibilité DSR (cycle #116, pré-enregistré dans
PREREG_dsr_sensitivity_analysis.md). PAS un backtest PASS/FAIL --
calcule, pour chaque candidat déjà committé (#111-115), le Sharpe
journalier minimal qu'il faudrait pour DSR>0,95 à n_trials=110, et
compare à des repères académiques connus.
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics, dsr, expected_max_sharpe  # noqa: E402

CANDIDATES = {
    "deep_drawdown_breadth_vol_targeting_overlay": "#111 drawdown profond",
    "momentum_decile_spread_vol_targeting_overlay": "#112 spread décile momentum",
    "ensemble_vote_vol_targeting_overlay": "#113 vote majoritaire",
    "yield_curve_slope_vol_targeting_overlay": "#114 pente courbe des taux",
    "defensive_calmar_vol_targeting_overlay": "#115 défensif Calmar",
}

ANNUALIZATION = np.sqrt(252)
N_TRIALS = 110

# Reperes academiques CONNUS AVANT ce calcul (Sharpe annualise)
BENCHMARKS = [
    ("Prime de risque actions US, long terme", 0.40, 0.50),
    ("Facteurs Fama-French (value/momentum)", 0.30, 0.50),
    ("CTA / trend-following systematique", 0.50, 0.80),
    ("Meilleurs fonds quant. multi-strategies (exception, freq. differente)", 2.00, None),
]


def approx_var_trials_daily():
    backlog = (ROOT / "NONML_STRATEGY_BACKLOG.md").read_text()
    pairs = re.findall(r"Sharpe\s+([+-][0-9.,]+)\s*→\s*([+-][0-9.,]+)", backlog)
    vals = []
    for _, after in pairs:
        try:
            vals.append(float(after.rstrip(",").replace(",", ".")))
        except ValueError:
            continue
    var_annual = float(np.var(np.array(vals), ddof=1))
    return var_annual / 252.0, len(vals)


def solve_sr_min(T, var_trials, skew, kurt_excess, target_dsr=0.95, tol=1e-8):
    """Recherche par bissection du sr_hat_daily minimal tel que
    dsr(...) == target_dsr. dsr() est monotone croissante en
    sr_hat_daily (verifie empiriquement avant la bissection)."""
    lo, hi = -1.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        d = dsr(mid, T, var_trials, n_trials=N_TRIALS, skew=skew, kurt_excess=kurt_excess)["dsr"]
        if d < target_dsr:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def main():
    var_trials, n_extracted = approx_var_trials_daily()
    lines = [
        "# Analyse de sensibilité DSR (Règle 9e) — cycle #116",
        "",
        f"var_trials (échelle journalière, {n_extracted} Sharpe extraits du backlog) = {var_trials:.6f}. "
        f"n_trials = {N_TRIALS} (taille du backlog, comme toute la batterie Règle 9).",
        "",
        "## 1. Sharpe minimal requis (DSR=0,95) par candidat déjà testé",
        "",
        "| Candidat | Séances (T) | Sharpe journalier requis | Sharpe ANNUALISÉ requis | Sharpe annualisé RÉEL obtenu |",
        "|---|---|---|---|---|",
    ]

    results = []
    for fname, label in CANDIDATES.items():
        npz_path = ROOT / "results" / f"nonml_{fname}_pnl.npz"
        if not npz_path.exists():
            continue
        data = np.load(npz_path, allow_pickle=True)
        pos, r, cost_bps = data["pos"], data["r_asset"], float(data["cost_bps"])
        turn = np.abs(np.diff(pos, prepend=1.0))
        pnl = pos * r - turn * (cost_bps / 1e4)
        me = trading_metrics(pnl)
        T = me["n"]
        sr_min_daily = solve_sr_min(T, var_trials, me["skew"], me["excess_kurt"])
        sr_min_annual = sr_min_daily * ANNUALIZATION
        results.append((label, T, sr_min_daily, sr_min_annual, me["sharpe_ann"]))
        lines.append(f"| {label} | {T} | {sr_min_daily:.4f} | {sr_min_annual:.2f} | {me['sharpe_ann']:+.2f} |")

    lines.append("")
    ratio_min = min(r[3] / r[4] for r in results if r[4] > 0)
    ratio_max = max(r[3] / r[4] for r in results if r[4] > 0)
    lines.append(f"Le Sharpe annualisé requis dépasse le Sharpe RÉELLEMENT obtenu d'un facteur "
                 f"{ratio_min:.1f}x à {ratio_max:.1f}x selon le candidat (plus l'échantillon T est "
                 f"court, plus le facteur requis est élevé).")

    lines += [
        "",
        "## 2. Comparaison à des repères académiques (fixés avant ce calcul, voir PREREG)",
        "",
        "| Repère | Sharpe annualisé typique |",
        "|---|---|",
    ]
    for name, lo, hi in BENCHMARKS:
        rng_str = f"{lo:.2f}-{hi:.2f}" if hi else f">{lo:.2f} (cas exceptionnel)"
        lines.append(f"| {name} | {rng_str} |")

    sr_min_range = [r[3] for r in results]
    lines += [
        "",
        f"Le Sharpe annualisé REQUIS par la Règle 9e pour ces candidats ({min(sr_min_range):.2f} à "
        f"{max(sr_min_range):.2f}) est **supérieur à TOUS les repères académiques standards** "
        f"(prime de risque, facteurs, CTA), et se rapproche seulement de la catégorie \"fonds "
        f"quantitatifs d'exception\" -- qui opèrent à une fréquence et une diversification sans "
        f"rapport avec un signal quotidien unique sur un seul indice.",
        "",
        "## 3. Interprétation (ne change RIEN à la Règle 9e ni aux verdicts #111-115 déjà rendus)",
        "",
        "Deux lectures possibles, non tranchées ici :",
        "",
        "1. **La barre est correctement calibrée et ce type de stratégie (overlay directionnel "
        "quotidien sur un seul indice, mécanisme déterministe non-ML) n'a simplement pas l'edge "
        "nécessaire pour survivre à une correction honnête de n_trials=110** -- cohérent avec la "
        "conclusion de l'Étape B (aucun signal ne bat Buy&Hold à DSR>0,95) et de la validation "
        "SPA/DSR familiale du 29/07.",
        "2. **n_trials=110 (comptage brut des lignes du backlog) surestime le nombre réel d'essais "
        "INDÉPENDANTS** -- beaucoup des 110 hypothèses sont des variations mineures d'un même "
        "mécanisme (la famille vol-targeting hiérarchique comptait déjà ~15 membres fortement "
        "corrélés, cf. audit du 29/07). Une correction par FAMILLE (comme le SPA à 13 membres) "
        "plutôt que par ligne de backlog serait méthodologiquement plus juste, mais réduirait "
        "aussi mécaniquement la sévérité du test -- **tout changement dans ce sens nécessite une "
        "justification explicite et l'accord de l'utilisateur, pas une décision unilatérale prise "
        "ici pour obtenir un résultat plus favorable.**",
        "",
        "**Recommandation (pas une décision) : la Règle 9e reste inchangée pour l'instant.** Le "
        "point 2 mérite d'être posé explicitement à l'utilisateur plutôt que résolu silencieusement "
        "dans un sens ou l'autre.",
    ]

    out = ROOT / "results" / "nonml_dsr_sensitivity_analysis.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
