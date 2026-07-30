"""Lecture DSR alternative du #131 avec n_trials = nombre de FAMILLES de
mécanismes distinctes plutôt que le compte brut de lignes du backlog
(spécification pré-enregistrée dans PREREG_dsr_family_ntrials_reading.md,
committée avant ce script). PAS un nouveau backtest, ne change AUCUN
verdict Règle 9 déjà rendu -- analyse informative en réponse à la
question ouverte du #116, cycle #133.
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics, dsr  # noqa: E402
from nonml_pass_validation_battery import pnl_at_cost, approx_var_trials  # noqa: E402

# Règle de classification FIXE, ordre de priorité fixé dans le PREREG avant tout calcul.
FAMILY_RULES = [
    ("evenementiel_fondamental", ["PEAD", "surprise de résultats"]),
    ("macro_externe", ["pente", "courbe des taux", "T10Y2Y", "VIX", "macro"]),
    ("volatilite_autoreferentielle", [
        "vol-targeting", "vol réalisée", "vol cible", "GARCH", "EWMA", "Parkinson",
        "vol-of-vol", "kurtosis", "skewness de l'indice", "skewness des rendements quotidiens DE L'INDICE",
        "autocorrélation", "Sharpe glissant", "streak", "régime de vol", "range intra-séance",
        "défensif Calmar", "rebalancement HEBDOMADAIRE",
    ]),
    ("breadth_dispersion_titre", [
        "breadth", "dispersion", "corrélation moyenne", "spread de rendement décile",
        "drawdown profond", "concentration du marché", "petites capitalisations",
        "position moyenne dans le range", "betas individuels",
    ]),
    ("momentum_tendance", [
        "momentum", "SMA", "golden cross", "MACD", "Donchian", "52-semaines", "52 semaines",
        "tendance", "plus haut", "plus bas", "low-volatility", "Low-Volatility", "low-vol",
    ]),
    ("calendaire_saisonnier", [
        "tournant de mois", "turn-of-month", "jour-de-semaine", "Halloween", "Sell in May",
        "Santa Claus", "jour férié", "window dressing", "trimestre", "janvier", "cycle électoral",
        "triple witching", "weekend", "fin de semaine", "lundi",
    ]),
    ("choc_microstructure", [
        "reversal", "pullback", "rebond post-drawdown", "gap d'ouverture", "faux breakout",
        "faux breakdown", "overnight", "intraday", "spillover", "lead-lag", "pause de marché",
    ]),
    ("ensembles_combinaisons", [
        "Ensemble/vote", "moyenne de deux moteurs", "moyenne de deux expositions", "vote majoritaire",
    ]),
]


def classify(desc: str) -> str:
    for family, keywords in FAMILY_RULES:
        for kw in keywords:
            if kw.lower() in desc.lower():
                return family
    return "autre"


def main():
    backlog = (ROOT / "NONML_STRATEGY_BACKLOG.md").read_text()
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*([^|]+)\|", backlog, flags=re.MULTILINE)
    # Ne compte que les lignes 0 a 131 (avant le candidat #131 lui-meme et
    # les cycles #132/#133), coherent avec la convention officielle qui
    # utilisait n_trials = taille du backlog AVANT le candidat evalue.
    seen = {}
    for num_str, desc in rows:
        num = int(num_str)
        if num > 131 or num == 131:
            continue
        if num in seen:
            continue  # evite les doublons (ex. lignes re-listees dans plusieurs sections historiques)
        seen[num] = classify(desc.strip())

    fam_counts = {}
    for fam in seen.values():
        fam_counts[fam] = fam_counts.get(fam, 0) + 1
    n_trials_famille = len(fam_counts)

    lines = [
        "# Lecture DSR alternative — #131, n_trials par FAMILLE (cycle #133, INFORMATIF)",
        "",
        "PAS un nouveau backtest. Ne change AUCUN verdict Règle 9 déjà rendu — répond "
        "à la question ouverte du #116, méthode fixée dans le PREREG avant calcul.",
        "",
        f"Lignes classifiées : {len(seen)} (backlog #0 à #130, avant le candidat #131 lui-même).",
        "",
        "## Répartition par famille",
        "",
        "| Famille | Nombre de lignes |",
        "|---|---|",
    ]
    for fam, count in sorted(fam_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {fam} | {count} |")
    lines.append("")
    lines.append(f"**Nombre de familles distinctes peuplées : {n_trials_famille}**")
    lines.append("")

    d = np.load(ROOT / "results" / "nonml_weekly_rebalance_dual_engine_pnl.npz", allow_pickle=True)
    pos, r, cost_bps = d["pos"], d["r_asset"], float(d["cost_bps"])
    pnl_ov, _ = pnl_at_cost(pos, r, cost_bps)
    me = trading_metrics(pnl_ov)

    var_trials_annual, n_extracted = approx_var_trials()
    var_trials = var_trials_annual / 252.0

    d_official = dsr(me["sharpe_daily"], me["n"], var_trials, n_trials=125,
                      skew=me["skew"], kurt_excess=me["excess_kurt"])
    d_famille = dsr(me["sharpe_daily"], me["n"], var_trials, n_trials=n_trials_famille,
                     skew=me["skew"], kurt_excess=me["excess_kurt"])

    lines.append("## DSR du #131 — officiel (n_trials=125, brut) vs alternative (n_trials=familles)")
    lines.append("")
    lines.append("| Convention | n_trials | SR0 (journalier) | DSR |")
    lines.append("|---|---|---|---|")
    lines.append(f"| Officielle (Règle 9e, compte brut de lignes) | 125 | {d_official['sr0_daily']:.4f} | {d_official['dsr']:.4f} |")
    lines.append(f"| Alternative (nombre de familles distinctes) | {n_trials_famille} | {d_famille['sr0_daily']:.4f} | {d_famille['dsr']:.4f} |")
    lines.append("")
    lines.append(
        f"**{'La convention alternative fait PASSER le DSR>0,95 : OUI.' if d_famille['dsr'] > 0.95 else 'La convention alternative NE fait PAS passer le DSR>0,95 (reste sous le seuil malgré la réduction de n_trials).'}**"
    )
    lines.append("")
    lines.append(
        "**Ce résultat NE change PAS le verdict Règle 9 officiel du #131 (reste FAIL sous la "
        "convention n_trials=125, seule officiellement adoptée). Reste soumis à l'utilisateur : "
        "la partition en familles ci-dessus est UNE classification défendable parmi d'autres "
        "(cf. limite reconnue dans le PREREG), pas LA réponse définitive à la question ouverte du #116.**"
    )

    out = ROOT / "results" / "nonml_dsr_family_ntrials_reading.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
