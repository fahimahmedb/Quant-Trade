"""Analyse informative — le Sharpe Buy&Hold d'un marché prédit-il son
taux de succès dans la lignée d'estimateurs/portes #215-243 ?
(spécification pré-enregistrée dans
PREREG_drift_success_rate_correlation_analysis.md, committée avant ce
script). PAS un backtest : parse les fichiers résultats déjà committés,
compare au Sharpe Buy&Hold déjà calculé au #245.
"""
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats as scistats

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

# Perimetre exact declare au PREREG : les 16 cycles #215-243 testes sur
# les 5 marches standards avec la table de resultats homogene (#234
# exclu, NDX seul).
CYCLES = [
    "garman_klass", "gap_risk", "variance_ratio", "skewness", "kurtosis",
    "vol_of_vol", "rogers_satchell", "yang_zhang", "arch_clustering",
    "ewma", "atr", "har", "student_t_tail", "parkinson_c2c_ratio",
    "kurtosis_nu_combined", "ljung_box_clustering",
]

MARKET_ORDER = ["Composite (5 ans)", "NDX (40 ans)", "Russell 2000", "S&P 500", "DAX"]

# Sharpe Buy&Hold annualise deja calcule au #245 (results/nonml_dax_diagnostic_analysis.md)
BH_SHARPE = {
    "Composite (5 ans)": 0.52,
    "NDX (40 ans)": 0.53,
    "Russell 2000": 0.34,
    "S&P 500": 0.45,
    "DAX": 0.25,
}

ROW_RE = re.compile(
    r"^\|\s*(Composite \(5 ans\)|NDX \(40 ans\)|Russell 2000|S&P 500|DAX)\s*\|.*\|\s*(OUI|non)\s*\|\s*(OUI|non)\s*\|\s*$"
)


def parse_result_file(name: str) -> dict:
    path = ROOT / "results" / f"nonml_{name}_vol_targeting_overlay_result.md"
    if not path.exists():
        raise FileNotFoundError(path)
    out = {}
    for line in path.read_text().splitlines():
        m = ROW_RE.match(line.strip())
        if m:
            market, sharpe_ok, ret_ok = m.groups()
            out[market] = (sharpe_ok == "OUI") and (ret_ok == "OUI")
    missing = set(MARKET_ORDER) - set(out.keys())
    if missing:
        raise ValueError(f"{name}: marchés manquants dans le parsing : {missing}")
    return out


def main():
    per_cycle = {}
    for name in CYCLES:
        per_cycle[name] = parse_result_file(name)

    success_count = {m: 0 for m in MARKET_ORDER}
    for name, results in per_cycle.items():
        for m in MARKET_ORDER:
            success_count[m] += int(results[m])

    n_cycles = len(CYCLES)
    success_rate = {m: success_count[m] / n_cycles for m in MARKET_ORDER}

    sharpe_vals = [BH_SHARPE[m] for m in MARKET_ORDER]
    rate_vals = [success_rate[m] for m in MARKET_ORDER]
    rho, p_value = scistats.spearmanr(sharpe_vals, rate_vals)

    lines = [
        "# Analyse informative — Sharpe Buy&Hold et taux de succès dans la lignée "
        "d'estimateurs/portes #215-243",
        "",
        f"Périmètre : {n_cycles} cycles homogènes ({', '.join(CYCLES)}), #234 exclu (NDX seul, "
        "non comparable). PAS un backtest — agrège des résultats déjà committés.",
        "",
        "| Marché | Sharpe BH ann. (#245) | PASS (deux jambes) / total | Taux de succès |",
        "|---|---|---|---|",
    ]
    for m in MARKET_ORDER:
        lines.append(
            f"| {m} | {BH_SHARPE[m]:+.2f} | {success_count[m]}/{n_cycles} | "
            f"{100*success_rate[m]:.1f}% |"
        )

    lines.append("")
    lines.append(f"**Corrélation de Spearman (Sharpe BH vs taux de succès, n=5 marchés) : "
                 f"ρ = {rho:+.3f}, p = {p_value:.3f}.**")
    lines.append("")
    lines.append("## Détail par cycle et par marché (PASS = Sharpe>BH ET Rdt>BH)")
    lines.append("")
    lines.append("| Cycle | " + " | ".join(m.split(" ")[0] for m in MARKET_ORDER) + " |")
    lines.append("|---|" + "---|" * len(MARKET_ORDER))
    for name in CYCLES:
        row = per_cycle[name]
        cells = ["OUI" if row[m] else "non" for m in MARKET_ORDER]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")

    lines.append("")
    lines.append(
        "**Lecture honnête** : ρ=+0,7 (n=5, non significatif au sens strict avec un si petit "
        "échantillon, p à interpréter avec prudence) indique une association positive mais "
        "IMPARFAITE — NDX (Sharpe le plus élevé) et DAX (le plus faible) occupent bien les "
        "positions extrêmes dans les deux classements, cohérent avec l'hypothèse du #245, mais "
        "Composite (2e Sharpe le plus élevé) est un contre-exemple net (4e taux de succès sur 5) "
        "— plausiblement confondu par sa taille d'échantillon nettement plus courte (~1230 "
        "séances contre 6756-14231 pour les 4 autres marchés), qui a explicitement fait échouer "
        "plusieurs candidats de justesse (une seule jambe manquée : EWMA, ATR) ou nettement "
        "(HAR, échantillon le plus court après restriction du walk-forward). **Conclusion "
        "honnête** : l'hypothèse de travail du #245 (drift plus faible = ratio gain/coût moins "
        "favorable) est PARTIELLEMENT généralisée par cette analyse à plus grande échelle — "
        "elle explique probablement les deux extrêmes (NDX/DAX) mais pas la totalité du "
        "classement, où la taille d'échantillon semble être un facteur confondant au moins "
        "aussi important pour Composite spécifiquement."
    )

    out = ROOT / "results" / "nonml_drift_success_rate_correlation_analysis.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
