# Étape P1 — Modèle fondamentaux (économie politique)

## 1. Description du modèle

Modèle structurel d'inspiration **Lewis-Beck & Nadeau** (1988) et **Jérôme-Speziari** (2000) :
conformément à cette littérature, on prédit le **sort du camp sortant** — la part au
**2nd tour** du **principal candidat du camp présidentiel sortant** (président sortant, ou
son parti à défaut). Elle dépend de variables fondamentales connues *avant* le scrutin :

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

1. **Croissance PIB** (gdp_growth) : -0.0967
   Théorie : + → part sortant ↑ (succès économique). Observé : ✗

2. **Chômage** (unemployment) : +0.0022
   Théorie : + → part sortant ↓ (malaise économique). Observé : ✗

3. **Approbation du camp sortant** (approval) : +0.1122
   Théorie : + → part sortant ↑ (satisfaction électorale). Observé : ✓

4. **Ancienneté du pouvoir** (tenure_years) : -0.0315
   Théorie : + → part sortant ↓ (usure du pouvoir). Observé : ✓

5. **Sortant concourt** (incumbent_running) : -0.0513
   Théorie : + → part sortant ↑ (avantage du sortant). Observé : ✗

Intercept (prior) : 0.5560
Écart-type des résidus (historique) : 0.0681

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
| 2017 | FR_pres_2017 | hamon_2017 | 0.388 | 0.13 | nan | ✗ perd |
| 2022 | FR_pres_2022 | macron_2022 | 0.482 | 0.43 | 0.586 | ✓ gagne |

**OOS (n=7)** — Brier 0.295 | log-loss 0.909 | MAE part 0.120 (n=6) | taux de bonne issue 57%

*Note : en 2017 le camp sortant (PS, référence = Hamon) est éliminé au 1er tour ; sa part
 2nd tour est indéfinie (NaN, exclue de la MAE) mais l'**issue** reste scorée — les
 fondamentaux (approbation Hollande ≈ 20) prédisent correctement que le PS ne l'emporte pas.*

## 5. Le modèle bat-il le trivial ? (baselines)

Un modèle fondamental n'a de valeur que s'il **bat des règles sans information économique**
(exigence standard de la littérature). Comparaison OOS à effectif égal (mêmes 7 plis) :

| Prédicteur | Brier | Log-loss | Bonne issue |
|---|---|---|---|
| Pile ou face (p=0.5) | 0.250 | 0.693 | 43% |
| Camp sortant gagne toujours | 0.318 | 0.888 | 57% |
| Avantage sortant si concourt | 0.216 | 0.623 | 71% |
| **Fondamentaux (ce modèle)** | 0.295 | 0.909 | 57% |

*Lecture honnête : sur 7 élections, les écarts de Brier < ~0.1 ne sont **pas**
statistiquement significatifs. Si les fondamentaux ne dominent pas nettement les baselines,
c'est le résultat réel — l'économie politique n'explique qu'une part modeste du 2nd tour,
et n≈11 interdit toute conclusion forte.*

## 6. Limitations honnêtes

⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :


1. **Faiblesse du dataset** : n=11 élections seulement. Estimation Ridge (α=0.1) nécessaire pour
   régulariser, mais amplifie aussi le biais. Intervalle de confiance large.

2. **2017 = réalignement partisan** : les fondamentaux prédisent correctement l'effondrement
   du camp sortant (PS, approbation Hollande ≈ 20), mais sont par nature **incapables de
   désigner le vainqueur émergent** (Macron, hors champ partisan classique). C'est la limite
   intrinsèque des modèles structurels : ils lisent le sort du sortant, pas les recompositions.

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
