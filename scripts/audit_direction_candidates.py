"""Audit adversarial — DSR corrige pour les candidats de direction deja
cross-valides (results/cross_market_confirmations.md).

Contexte : la boucle de brute-force ML (scripts/ml_brute_force.py) a teste
au moins 1200 strategies automatisees (24 iterations x 50) plus quelques
essais manuels anterieurs. 21 candidats "quasi-PASS" sur NDX ont ete
re-testes hors-echantillon sur 3 marches independants jamais touches
(Russell 2000, S&P 500, DAX), via scripts/cross_validate_candidate.py
(walk-forward purge/embargo=21j, cout 5 bps, Sharpe NET de couts). 11/21
montrent un Sharpe positif et coherent sur les 3 marches -- mais le DSR
affiche dans le log n'est calcule QUE pour la paire design/test sur NDX,
avec n_trials = la famille de l'iteration (50), PAS la taille reelle de
la campagne complete (>=1200). Erreur de raisonnement multi-tests
identique a celle deja trouvee et corrigee pour l'Etape D
(ADVERSARIAL_AUDIT_v2.md, section 1) : "un seul candidat deploye" ne veut
pas dire "aucune inflation" -- il faut compter TOUS les essais qui ont
menE0 a sa selection.

Ce script recalcule le DSR de chaque candidat, sur CHAQUE marche externe,
avec n_trials=1200 (taille reelle de la campagne, legerement sous-estimee,
cf. results/campaign_trial_variance.json) et var_trials estime empiriquement
sur les essais dont les donnees brutes existent encore (349/1200 -- les
iterations 11-27 ont perdu leurs fichiers bruts individuels, gitignores et
ephemeres, cf. meme fichier json). Skew/kurtosis excedentaire fixes a 0
(hypothese neutre/gaussienne, pas ajustee pour gonfler ou degonfler le DSR).

AUCUNE selection post-hoc : les 21 candidats deja logges sont TOUS
rapportes ici, pas seulement ceux qui semblent bons. Verdict "outil
valide" seulement si DSR corrige > 0.95 SIMULTANEMENT sur Russell, S&P 500
ET DAX.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "finance" / "src"))
from prediction import expected_max_sharpe  # noqa: E402

LOG_PATH = ROOT / "results" / "cross_market_confirmations.md"
VAR_PATH = ROOT / "results" / "campaign_trial_variance.json"
N_TRIALS = 1200  # cf. campaign_trial_variance.json pour la justification

MARKETS = ["Russell 2000", "S&P 500", "DAX"]


def dsr_corrige(sharpe_ann: float, T: int, var_trials: float, n_trials: int) -> dict:
    sr_hat_daily = sharpe_ann / np.sqrt(252)
    sr0 = expected_max_sharpe(var_trials, n_trials)
    denom = np.sqrt(max(1e-12, 1.0))  # skew=0, kurt_excess=0 (hypothese neutre)
    z = (sr_hat_daily - sr0) * np.sqrt(max(T - 1, 1)) / denom
    return {"sr0_daily": float(sr0), "z": float(z), "dsr": float(stats.norm.cdf(z))}


def parse_log(text: str):
    blocks = text.split("\n---\n")
    records = []
    header_re = re.compile(r"^## Itération (\d+), id (\d+) — (.+)$", re.MULTILINE)
    market_re = re.compile(
        r"- (Russell 2000|S&P 500|DAX): n=(\d+), OOS obs=(\d+), Sharpe ann = ([+-]?\d+\.\d+)"
    )
    ndx_re = re.compile(
        r"NDX \(référence.*?\): design_ann=([\d.eE+-]+|None), "
        r"test_ann=([\d.eE+-]+|None), degradation=([\d.eE+-]+|None), dsr=([\d.eE+-]+|None)"
    )
    for block in blocks:
        h = header_re.search(block)
        if not h:
            continue
        iteration, sid, name = h.group(1), h.group(2), h.group(3).strip()
        markets = {m: (int(n), int(oos), float(sh)) for m, n, oos, sh in market_re.findall(block)}
        if len(markets) != 3:
            continue  # entree incomplete (fichier absent / historique trop court) : hors perimetre
        ndx = ndx_re.search(block)
        ndx_dsr_orig = None
        if ndx and ndx.group(4) != "None":
            try:
                ndx_dsr_orig = float(ndx.group(4))
            except ValueError:
                pass
        records.append({
            "iteration": iteration, "id": sid, "name": name,
            "markets": markets, "ndx_dsr_orig": ndx_dsr_orig,
        })
    return records


def main():
    var_info = json.loads(VAR_PATH.read_text())
    var_trials = var_info["var_trials_daily"]

    records = parse_log(LOG_PATH.read_text())

    lines = [
        "# Audit — DSR corrigé des candidats de direction cross-validés",
        "",
        f"n_trials utilisé = **{N_TRIALS}** (taille réelle de la campagne de brute-force, "
        "voir `results/campaign_trial_variance.json` pour la provenance et les limites). "
        f"var_trials (Sharpe quotidien, non annualisé) = **{var_trials:.6f}**, estimée sur "
        f"{var_info['n_pooled']}/{N_TRIALS} essais dont les données brutes existent encore "
        "(iter4–10 ; iter11–27 ont perdu leurs fichiers individuels, gitignorés et éphémères — "
        "**proxy partiel, pas la population complète**, signalé et non masqué).",
        "",
        f"Les {len(records)} candidats ci-dessous sont **TOUS** ceux déjà logués dans "
        "`cross_market_confirmations.md` (aucune sélection post-hoc pour ce rapport) — "
        "y compris ceux qui répliquent mal.",
        "",
        "| Itération/id | Modèle | Russell DSR corr. | S&P500 DSR corr. | DAX DSR corr. | 3/3 > 0.95 ? |",
        "|---|---|---|---|---|---|",
    ]

    n_pass_all3 = 0
    for rec in records:
        dsrs = {}
        for m in MARKETS:
            n, oos, sh = rec["markets"][m]
            dsrs[m] = dsr_corrige(sh, oos, var_trials, N_TRIALS)["dsr"]
        ok = all(dsrs[m] > 0.95 for m in MARKETS)
        n_pass_all3 += int(ok)
        lines.append(
            f"| {rec['iteration']}/{rec['id']} | {rec['name']} | "
            f"{dsrs['Russell 2000']:.3f} | {dsrs['S&P 500']:.3f} | {dsrs['DAX']:.3f} | "
            f"{'**OUI**' if ok else 'non'} |"
        )

    lines.append("")
    lines.append(f"**{n_pass_all3}/{len(records)} candidats atteignent DSR corrigé > 0.95 "
                  "simultanément sur les 3 marchés externes.**")
    lines.append("")
    lines.append(
        "**Lecture honnête** : le DSR corrigé ici utilise n_trials=1200 (la charge réelle "
        "de la campagne, pas la famille locale de 50 utilisée dans le log original) — c'est "
        "beaucoup plus sévère, et c'est le bon calcul (même erreur de raisonnement que celle "
        "déjà trouvée et corrigée pour l'overlay Étape D, cf. ADVERSARIAL_AUDIT_v2.md §1). "
        "Un DSR élevé ici signifierait qu'un signal a un Sharpe net-de-coûts sur un marché "
        "totalement externe qui est *statistiquement surprenant même après avoir payé le prix "
        "de 1200 tentatives* — c'est une barre volontairement très haute. "
        "Limite assumée : var_trials est estimée sur seulement 349/1200 essais (les fichiers "
        "bruts des itérations 11–27 ont été perdus, gitignorés et éphémères) — un vrai calcul "
        "définitif nécessiterait de relancer la campagne en conservant cette fois un résumé "
        "léger (Sharpe seul, pas les modèles) pour CHAQUE essai, committé, pas gitignoré."
    )

    out = ROOT / "results" / "audit_direction_candidates_dsr_corrige.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
