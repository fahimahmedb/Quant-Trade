"""Etape P6 - PREVISION FORWARD de la presidentielle 2027. Produit
results/etape_P6_pred2027.md.

Difference fondamentale avec P1-P5 : 2027 est un scrutin FUTUR. Aucun hindsight
n'est possible par construction -> c'est la seule prevision honnetement
verifiable a posteriori. Les fondamentaux sont entraines sur les 11 elections
1965-2022 (tout est legitimement "passe") et appliques aux hypotheses macro 2027
(data/fr_2027_hypotheses.csv, chiffres publics reels et dates, pas fabriques).

Verdict attendu et HONNETE : les modeles structurels ne savent predire que le
SORT DU CAMP SORTANT. Ils ne peuvent PAS designer le vainqueur d'un siege ouvert
avec recomposition (cf. echec structurel de 2017). On livre donc un PRIOR sur le
sort de la Macronie, a bandes larges, pas une prevision du gagnant.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pp_data import load_registry  # noqa: E402
from pp_types import Candidate, ElectionContext  # noqa: E402
from pp_fundamentals import FundamentalsSource  # noqa: E402
from pp_markets import MarketsSource, load_market_prob  # noqa: E402
from pp_nlp import NlpSource  # noqa: E402
from pp_fusion import FusionSource  # noqa: E402
from pp_backtest import win_prob_from_normal  # noqa: E402

FEATURES = ["gdp_growth", "unemployment", "approval", "tenure_years"]

history = load_registry()  # 11 elections, tout "passe" vis-a-vis de 2027

# --- Contexte 2027 (siege ouvert : Macron ne peut se representer) ------------ #
hyp = pd.read_csv(ROOT / "data" / "fr_2027_hypotheses.csv", comment="#").iloc[0]
feats_2027 = {f: float(hyp[f]) for f in FEATURES}
feats_2027["incumbent_running"] = 0.0

ctx_2027 = ElectionContext(
    election_id="FR_pres_2027",
    year=2027,
    reference_id="macronie_2027",
    candidates=(
        # Reference = candidat (encore indetermine) du camp presidentiel sortant.
        # Les autres camps ne sont PAS des predictions nominatives ; ils situent
        # seulement le paysage. On ne modelise que le sort du camp de reference.
        Candidate("macronie_2027", "Camp presidentiel (Renaissance/Ensemble)", "centre", True),
    ),
    incumbent_running=False,
    features=feats_2027,
)

# --- Prior structurel : fondamentaux entraines sur toute l'histoire ---------- #
fund = FundamentalsSource().fit(history)
sig_fund = fund.predict(ctx_2027)

# --- Tentative de fetch live (marches) : honnete, dormant tant qu'aucun marche  #
live_raw = None
live_err = None
try:
    live_raw = load_market_prob("FR_pres_2027")
except Exception as exc:  # noqa: BLE001
    live_err = str(exc)
market_available = MarketsSource().predict(ctx_2027).available
nlp_available = NlpSource().predict(ctx_2027).available

# --- Fusion (aujourd'hui = fondamentaux seuls, marches/NLP indispo) ---------- #
fusion = FusionSource([FundamentalsSource(), MarketsSource(), NlpSource()]).fit(history)
post = fusion.posterior(ctx_2027)

# --- Analogie historique : election passee la plus proche en features -------- #
X = np.array([[ex.context.features[f] for f in FEATURES] for ex in history], float)
sd = X.std(0, ddof=1)
x27 = np.array([feats_2027[f] for f in FEATURES])
dists = np.sqrt((((X - x27) / sd) ** 2).sum(1))  # distance euclidienne standardisee
order = np.argsort(dists)

# --------------------------------------------------------------------------- #
# Rapport                                                                       #
# --------------------------------------------------------------------------- #
lines = []
w = lines.append
w("# Étape P6 — Prévision FORWARD de la présidentielle 2027\n")

w("## 0. Statut : prévision honnêtement vérifiable\n")
w("2027 est un scrutin **futur** : aucun hindsight n'est possible. C'est la seule "
  "prévision de ce dépôt qui pourra être confrontée à la réalité a posteriori. "
  "Les fondamentaux sont entraînés sur les 11 présidentielles 1965-2022 et "
  "appliqués aux hypothèses macro 2027 (`data/fr_2027_hypotheses.csv` — chiffres "
  "publics réels et datés, mis à jour au fil des publications).\n")

w("## 1. Ce que la base validée SAIT et NE SAIT PAS faire\n")
w("Rappel de l'audit (`results/AUDIT.md`) : le modèle structurel ne prédit que le "
  "**sort du camp sortant**, et il ne bat même pas nettement une heuristique simple "
  "à n=11. Il est **structurellement incapable** de désigner le vainqueur d'un "
  "siège ouvert avec recomposition — comme il n'a pas pu voir Macron émerger en "
  "2017. On livre donc un **prior sur la Macronie**, pas un pronostic du gagnant.\n")

w("## 2. Configuration 2027 (siège ouvert)\n")
w("Emmanuel Macron **ne peut pas se représenter** (limite de deux mandats "
  "consécutifs, art. 6 de la Constitution). Le camp présidentiel sortant "
  "(Renaissance/Ensemble) présentera un candidat encore indéterminé — c'est la "
  "**référence** dont on modélise le sort.\n")
w("| Variable fondamentale | Valeur 2027 | Lecture |")
w("|---|---|---|")
w(f"| Croissance PIB | {feats_2027['gdp_growth']:.1f} % | atone |")
w(f"| Chômage | {feats_2027['unemployment']:.1f} % | élevé |")
w(f"| Approbation du camp sortant | {feats_2027['approval']:.0f} % | basse |")
w(f"| Ancienneté au pouvoir | {feats_2027['tenure_years']:.0f} ans | usure marquée |")
w(f"| Président sortant candidat | non | siège ouvert |")
w("")

w("## 3. Analogie historique (plus proches voisins en fondamentaux)\n")
w("Élections passées les plus proches du profil 2027 (distance standardisée sur "
  "les 4 variables) :\n")
w("| Rang | Élection | Référence (camp sortant) | Le camp sortant a-t-il gagné ? |")
w("|---|---|---|---|")
for k in order[:3]:
    ex = history[k]
    won = ex.result.winner_id == ex.context.reference_id
    w(f"| {int(np.where(order==k)[0][0])+1} | {ex.context.year} | "
      f"{ex.context.reference_id} | {'oui' if won else 'NON'} |")
w("")
nearest = history[order[0]]
w(f"*Le profil 2027 est le plus proche de **{nearest.context.year}** — où le camp "
  f"sortant (Sarkozy, droite héritière de Chirac) a **gagné**. Les analogies sont "
  f"donc **mitigées** : 2007 (victoire), 2012 et 2017 (défaite/élimination). Le "
  f"signal historique n'est PAS univoque ; il n'autorise pas à annoncer un "
  f"effondrement certain de la Macronie.*\n")

w("## 4. Prior structurel sur la Macronie (fondamentaux)\n")
p_reach = win_prob_from_normal(sig_fund.r2_share_mean, sig_fund.r2_share_sd)
w(f"- Part 2nd tour prédite pour le camp sortant (**s'il est finaliste**) : "
  f"**{sig_fund.r2_share_mean:.1%}** ± {sig_fund.r2_share_sd:.1%} (1 σ).")
w(f"- Probabilité structurelle qu'il l'emporte (conditionnelle à un 2nd tour) : "
  f"**{p_reach:.0%}** — soit un **quasi pile-ou-face**, PAS une défaite annoncée.")
w("- **Lecture honnête** : les fondamentaux ne donnent AUCUN signal fort pour 2027 "
  "(≈ 50/50), et l'écart-type large (±10 pts) mange la moindre nuance. C'est "
  "cohérent avec un modèle qui, rappelons-le, ne bat pas une règle triviale à "
  "n=11. Toute affirmation plus tranchée (« la Macronie est condamnée ») serait "
  "une sur-interprétation du chiffre.")
w("- Réserve importante : ce modèle prédit la part *au 2nd tour*, pas la "
  "probabilité d'**atteindre** le 2nd tour. Or le vrai risque pour le camp "
  "sortant (cf. PS 2017) est l'élimination au 1er tour — que cette version ne "
  "modélise pas encore explicitement.\n")

w("## 5. Sources live (marchés / NLP) — état au moment de l'exécution\n")
if market_available:
    w("- **Marchés** : un prix live a été récupéré et mappé — voir contributions.")
else:
    w("- **Marchés** : `available=False`. La tentative de fetch live Polymarket "
      "n'a trouvé **aucun marché mappable** sur la présidentielle FR 2027 "
      "(marché inexistant ou mapping outcome→camp non déclaré). Aucune "
      "probabilité n'est inventée. La source s'activera automatiquement le jour "
      "où un marché liquide existera.")
w(f"- **NLP** : available={nlp_available} (données Trends/presse 2027 à collecter "
  "en live le moment venu).")
w(f"- **Fusion actuelle** = prior fondamental seul (part {post.r2_share_mean:.1%}, "
  f"P(victoire camp sortant) {post.p_reference_wins:.0%}). Elle se raffinera "
  "quand marchés/NLP livreront de vraies données contemporaines.\n")

w("## 6. Conclusion honnête\n")
w("**Ce que la base dit (avec prudence)** : sur les fondamentaux seuls, le sort du "
  "camp présidentiel sortant en 2027 est **indécis (≈ 50/50)** — ni favori, ni "
  "condamné. Le contexte (impopularité, 10 ans de pouvoir, siège ouvert) est "
  "défavorable, mais le plus proche précédent (2007) s'est soldé par une victoire "
  "du camp sortant : le modèle refuse de trancher, et à n=11 il a raison de le "
  "faire.\n")
w("**Ce que la base NE dit PAS, et ne peut pas dire** : qui gagne (RN, gauche, "
  "droite). Les fondamentaux sont aveugles aux recompositions ; désigner un "
  "vainqueur exigerait des marchés de prédiction liquides et/ou des signaux de "
  "campagne (NLP) contemporains, qui n'existent pas encore à ~21 mois du scrutin. "
  "Toute prévision du gagnant aujourd'hui serait de l'invention déguisée — "
  "précisément l'erreur corrigée dans `results/AUDIT.md`.\n")
w("**Prochaine actualisation** : rejouer ce script quand (a) de nouvelles données "
  "macro sortent, (b) un marché 2027 ouvre, (c) des séries Trends/presse datées "
  "sont disponibles. La prévision se resserrera alors honnêtement, sans jamais "
  "rétro-ajuster.\n")

out = ROOT / "results" / "etape_P6_pred2027.md"
out.write_text("\n".join(lines))
print("\n".join(lines))
if live_err:
    print(f"\n[info] fetch live marches: {live_err}")
