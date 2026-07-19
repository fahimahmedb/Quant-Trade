# Étape P1 — Modèle fondamentaux (économie politique)

## 1. Description du modèle

Modèle structurel d'inspiration **Lewis-Beck & Nadeau** (1988) et **Jérôme-Speziari** (2000) :
la part du candidat de **continuité** (camp sortant ou héritier) au **2nd tour** de
l'élection présidentielle française dépend de quatre variables fondamentales :

| Variable | Source | Interprétation politique |
|---|---|---|
| **Croissance PIB réelle** (%) | INSEE, moyenne pré-électorale | Évaluation du sortant sur le bilan économique |
| **Taux de chômage** (%) | INSEE BIT, date de prévision | Malaise économique → pénalité du sortant |
| **Approbation du camp sortant** (% satisfaits) | Moyennes sondages pré-électoraux | Satisfaction électorale directe |
| **Ancienneté du pouvoir** (années) | Calcul à partir date accession | Usure du pouvoir (effet terme) |
| **Sortant concourt** (0/1) | Contexte politique | Avantage présidentiel si président sortant |

**Target** : part 2nd tour de la référence (dans [0.15, 0.85]).

## 2. Méthodologie d'entraînement

- **Régression Ridge** (α=0.1, petit pour n=11) sur features standardisées
- **Historique** : 11 élections (1965→2022), filtré aux cas où la référence est finaliste au 2nd tour
- **Standardisation** : moyenne/écart-type d'entraînement mémorisés, appliqués identiquement en prédiction
- **Incertitude** : écart-type des résidus hors-échantillon OOS, avec plancher de 0.03 pour la stabilité
- **Fallback prior** : si historique < 3 obs ou features manquantes → prior 0.50 ± 0.02 (sortant), sd=0.08

## 3. Coefficients du modèle (régressé sur l'historique complet)


### Interprétation structurelle des coefficients

Variables standardisées. Les coefficients attendus (théorie économique politique) :

1. **Croissance PIB** (gdp_growth) : -0.0865
   Théorie : + → part sortant ↑ (succès économique). Observé : ✗

2. **Chômage** (unemployment) : -0.0119
   Théorie : + → part sortant ↓ (malaise économique). Observé : ✓

3. **Approbation du camp sortant** (approval) : +0.0817
   Théorie : + → part sortant ↑ (satisfaction électorale). Observé : ✓

4. **Ancienneté du pouvoir** (tenure_years) : -0.0542
   Théorie : + → part sortant ↓ (usure du pouvoir). Observé : ✓

5. **Sortant concourt** (incumbent_running) : -0.0517
   Théorie : + → part sortant ↑ (avantage du sortant). Observé : ✗

Intercept (prior) : 0.5656
Écart-type des résidus (historique) : 0.0787

## 4. Backtest hors-échantillon (OOS)

**Protocole anti-data-snooping** (fenêtre expansive) :

- Pour prédire l'élection T, le modèle est entraîné UNIQUEMENT sur les élections d'année < T
- Les paramètres et la standardisation changent à chaque pli

| Annee | Election | Reference | Part prevue | P(victoire) | Part reelle | Issue |
|---|---|---|---|---|---|---|
| 1988 | FR_pres_1988 | mitterrand_1988 | 0.577 | 0.94 | 0.540 | ✓ gagne |
| 1995 | FR_pres_1995 | jospin_1995 | 0.490 | 0.42 | 0.474 | ✗ perd |
| 2002 | FR_pres_2002 | chirac_2002 | 0.465 | 0.24 | 0.822 | ✓ gagne |
| 2007 | FR_pres_2007 | sarkozy_2007 | 0.567 | 0.75 | 0.531 | ✓ gagne |
| 2012 | FR_pres_2012 | sarkozy_2012 | 0.655 | 0.95 | 0.484 | ✗ perd |
| 2017 | FR_pres_2017 | macron_2017 | 0.388 | 0.13 | 0.661 | ✓ gagne |
| 2022 | FR_pres_2022 | macron_2022 | 0.564 | 0.70 | 0.586 | ✓ gagne |

**OOS (n=7)** — Brier 0.368 | log-loss 1.114 | MAE part 0.130 | taux de bonne issue 57%

## 5. Limitations honnêtes

⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :


1. **Faiblesse du dataset** : n=11 élections seulement. Estimation Ridge (α=0.1) nécessaire pour
   régulariser, mais amplifie aussi le biais. Intervalle de confiance large.

2. **2017 = réalignement partisan** : le modèle échoue à capturer le basculement 2016-2017
   (Macron émergent hors champ politique classique). Les fondamentaux seuls ne suffisent pas
   en cas de rupture systémique.

3. **Variables macroéconomiques approximatives** : croissance/chômage/approbation sont des
   agrégations publiques, non des séries mensuelles rigoureuses. À remplacer par sources
   primaires (Eurostat, INSEE raw, sondage harmonisé) avant publication.

4. **Absence de variables de structure** : pas de 1er tour (dispersé, multi-candidats);
   pas de géographie (régional / professions); pas de vagues NLP (sentiment discours)
   → les 2/3 de la variance 2nd tour restent inexpliqués.

5. **OOS délicat avec n petit** : un seul 2nd tour « raté » (ex. 2002, Le Pen finaliste)
   pourrait biaiser les métriques. Voir la variance des plis individuellement.

**Conclusion** : ce modèle est un **composant d'un ensemble** (fusion avec marchés, NLP).
Seul, il ne fait pas une prévision robuste. À utiliser pour mesurer le poids de l'économie
politique, pas comme oracle électoral.
