# Q30 — voie 2 — spécification pré-enregistrée du modèle de coûts

Date : 2026-10-08. Statut : `PREREGISTERED_SPECIFICATION_NOT_EXECUTED`.

## 1. Objet et frontière

La voie 2 mesure la **robustesse des décisions paper/shadow aux frictions supposées**
et améliore la chaîne `VET -> SIZE -> RISK -> FILLS`. Elle ne cherche pas une
nouvelle expression, ne réouvre aucune fenêtre dépensée et ne produit ni découverte,
ni validation indépendante, ni autorité de capital.

Le dépôt ne contient ni historique de spread coté, ni taux d'emprunt observé, ni
financement réalisé. Ces quantités ne seront donc pas dites « estimées » ou
« calibrées ». Elles sont des **hypothèses étiquetées**, fixées avant tout calcul.

## 2. Unité d'analyse et variables observables

L'unité est une transition de position paper/shadow sur un instrument et une séance.
Le calcul conserve séparément, sans compensation entre postes :

- `notional_t` : valeur absolue exécutée à l'ouverture ajustée de `t` ;
- `delta_weight_t` et `turnover_t = |delta_weight_t|` ;
- `side_t` : achat, vente, vente à découvert ou couverture ;
- `gross_exposure_t`, `short_exposure_t` et jours de détention ;
- `adv20_t` : moyenne causale sur 20 séances du prix de clôture multiplié par le
  volume, calculée avec l'information disponible à la date du signal ;
- `participation_t = notional_t / adv20_t`, avec refus si l'ADV manque ou vaut zéro ;
- rendement brut ouverture ajustée à ouverture ajustée ;
- P&L brut, P&L net et shortfall, par instrument, séance, stratégie et Book.

Les variables dérivées obligatoires sont : coût total en points de base et en unité
monétaire, part de chaque poste, coût par unité de turnover, break-even total et par
poste, rendement net composé, Sharpe net, statistique t nette, drawdown, contribution
par instrument, concentration annuelle et sensibilité au multiplicateur de coûts.

## 3. Hypothèses étiquetées — jamais présentées comme mesures

Chaque résultat porte `COST_INPUT_KIND = ASSUMED_NOT_ESTIMATED` et le scénario exact.

| Poste | Central | Stress | Étiquette obligatoire |
|---|---:|---:|---|
| commission, par unité de turnover | 0,5 pb | 1 pb | `ASSUMED_COMMISSION_BPS` |
| demi-spread, par unité de turnover | 1 pb | 5 pb | `ASSUMED_HALF_SPREAD_BPS` |
| impact à 5 % de participation | 10 pb | 25 pb | `ASSUMED_IMPACT_BPS_AT_5PCT` |
| borrow annualisé, exposition short | 100 pb | 300 pb | `ASSUMED_BORROW_BPS_YEAR` |
| financement annualisé, exposition brute | 0 pb | 500 pb | `ASSUMED_FINANCING_BPS_YEAR` |

L'impact suit, sans ajustement après résultat,
`impact_bps = impact_at_5pct * sqrt(min(participation, 1) / 0,05)` ; une
participation supérieure à 5 % est tronquée à 5 % et signalée. Commission, spread et
impact s'appliquent à la variation absolue complète des poids, y compris une inversion
de signe. Borrow et financement sont débités par séance selon `taux / 252`.

Le financement central à zéro est un **cas de continuité du modèle actuel**, pas une
affirmation économique. Le stress à 500 pb est une hypothèse de sensibilité, pas un
taux de marché. Aucune valeur ne peut être remplacée après observation sans nouveau
pré-enregistrement et nouveau compteur de décision.

## 4. Calculs et sorties obligatoires

Pour le scénario central et le stress, le moteur publie :

1. P&L brut et net, coûts cumulés et ventilation par poste ;
2. turnover, exposition brute/short, participation et troncatures de capacité ;
3. métriques nettes et attribution par instrument, période et stratégie ;
4. `break_even_half_spread_bps`, `break_even_borrow_bps_year` et
   `break_even_financing_bps_year`, un poste variant à la fois ;
5. grille déterministe `0x, 0,5x, 1x, 2x, 3x` appliquée conjointement aux hypothèses
   centrales, sans sélectionner le multiplicateur le plus favorable ;
6. comparaison avec le modèle historique de 5 pb par turnover, clairement étiquetée
   comme diagnostic de modèle et non comme nouvelle preuve économique.

Les octets d'entrée, versions, commande, commit, empreintes avant/après, code retour
et résultat complet sont persistés. Le moteur ne télécharge rien, ne modifie aucune
donnée, ne lit aucune barre réservée au desk et ne choisit aucune expression.

## 5. Critères de décision fixés avant observation

Une stratégie ou un candidat évalué reçoit un seul statut :

- `COST_ROBUST`: tous ses critères économiques déjà pré-enregistrés restent vrais
  dans le scénario central **et** le stress, sans troncature de capacité ;
- `COST_SENSITIVE`: le central reste admissible mais le stress échoue, ou un seul
  poste consomme au moins 50 % du P&L brut positif ;
- `COST_INFEASIBLE`: le central est net non positif, un critère économique existant
  échoue sous le central, ou la capacité tronque une position nécessaire ;
- `COST_UNDETERMINED`: donnée causale requise absente, ADV nul, identité divergente,
  statut hors domaine ou réconciliation comptable impossible.

`COST_UNDETERMINED` et toute erreur sont fail-closed. Aucun statut ne peut promouvoir
une stratégie rejetée, recycler une validation dépensée ou remplacer les seuils
statistiques déjà enregistrés. Sur B2 et B4, la voie 2 est **descriptive seulement** :
elle peut expliquer combien les coûts contribuent au rejet, jamais changer le rejet.

## 6. Critères de conformité du futur livrable

Avant toute exécution, des tests synthétiques doivent établir : causalité ADV ;
inversion facturée sur le turnover complet ; borrow seulement sur exposition short ;
financement sur exposition brute ; monotonie des coûts ; troncature à 5 % ;
réconciliation exacte `gross P&L - postes = net P&L` ; échec fermé sur donnée absente ;
zéro lecture shadow ; et zéro écriture hors résultat.

```text
DOCUMENT_STATUS = PREREGISTERED_SPECIFICATION_NOT_EXECUTED
COST_INPUT_KIND = ASSUMED_NOT_ESTIMATED
NEW_MARKET_DATA_USED = FALSE
DISCOVERY_CLAIM = FALSE
VALIDATION_CLAIM = FALSE
STRATEGY_PROMOTION_AUTHORIZED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```

`NEXT_ACTION`: Builder — contre-lire adversarialement cette spécification, puis
proposer un harnais non exécuté et ses tests synthétiques sur une branche distincte.

`CHALLENGE`: chercher toute hypothèse présentée comme observation, tout double compte
de turnover, toute compensation entre postes et tout chemin permettant à un résultat
de coûts de sélectionner une expression.

`WAKE_EVENT`: contre-lecture adverse ou publication du harnais non exécuté.
