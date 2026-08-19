# Les littéraux périmés restants du script du #485 (pré-enregistré)

Le #520 avait réparé les 5 verdicts du dictionnaire `V`, mais
signalé sans corriger un littéral en dur trouvé en chemin. Ce
cycle reprend cette dette avec un balayage mécanique déclaré
plutôt que de ne traiter que le seul cas déjà nommé.

## Le balayage mécanique, sur le texte AVANT réparation

- occurrences de mots-nombres dans un `L.append(` : **16**

Après lecture manuelle (articles indéfinis et seuils de prédiction
figés exclus, comme déclaré), la population retenue :

| Ligne | Texte périmé | Défaut |
|---|---|---|
| 247 | « actionnable aux deux tiers » | qualitatif, calculé sur 12/17 (70,6 %) ; partition réelle 9/17 (52,9 %) |
| 284 | « une des cinq » | comptait les 5 irréparables d'origine ; il y en a 8 |
| 288 | « chacun des 12 » | comptait les 12 réparables d'origine ; il y en a 9 |

## Le geste, mesuré depuis git

- lignes changées (+ et -) dans `nonml_irreparable_figures_census_backtest.py` : **6**
  - `-    L.append("> **La dette du #479 est actionnable aux deux tiers.** Les "`
  - `+    L.append(f"> **La dette du #479 est actionnable à {fr(100 * len(rep) / len(pop))} %.** Les "`
  - `-    L.append("- **une des cinq renvoie à une question en attente d'arbitrage** — le")`
  - `+    L.append(f"- **une des {len(irrep)} renvoie à une question en attente d'arbitrage** — le")`
  - `-    L.append("  être nuisible, et chacun des 12 demande sa propre vérification.")`
  - `+    L.append(f"  être nuisible, et chacun des {len(rep)} demande sa propre vérification.")`

## Mes trois prédictions, confrontées

- lignes de contenu changées (paires +/-) : **3**

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|
| Exactement 3 littéraux périmés trouvés | 3 | 3 | **vérifiée** |
| Le nouveau texte l.247 publie < 60 % | < 60 % | 52,9 % | **vérifiée** |
| Aucun seuil de prédiction (≥5/≥8) modifié | 0 | 0 | **vérifiée** |

## Critères de succès

1. Les 3 littéraux publiés avant correction, avec ligne et défaut — **OUI**.
2. Les 3 corrigés par interpolation, aucun nouveau littéral introduit — **OUI**.
3. Rapport régénéré : aucune ligne hors les 3 corrections — **OUI**.
4. Compte final inchangé (8/9) — **OUI**.
5. Aucun script de marché exécuté — **OUI**.

**PASS** — le critère porte sur le **procédé** : des littéraux décrivant une mesure qui a changé sont remplacés par des interpolations, pour qu'ils ne se périment plus.

Simulation 300 € et robustesse **sans objet** : cycle de réparation de dépôt, aucune position, aucun paramètre numérique de stratégie.
