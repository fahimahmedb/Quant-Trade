# Robustesse — la conclusion du #452 hors d'un seul chiffre

**Étape 7a. Ce n'est pas un retuning** : ni la stratégie ni le seuil du
balayage ne changent. Les deux grilles étaient fixées avant exécution.

Corrélation mesurée au #452 entre la variante A et le #8 : **+0.963497**.

## Perturbation 1 — le seuil de quasi-doublon

Une perturbation de ±20 % n'a pas de sens sur une corrélation (0,9999 × 1,2 >
1). La perturbation pertinente est de **desserrer** le seuil : cela rend la
conclusion « les deux ne sont pas interchangeables » **plus difficile** à tenir.

| Seuil | Les deux séries seraient-elles appariées ? |
|---|---|
| **0.9999** | non |
| **0.999** | non |
| **0.99** | non |
| **0.98** | non |
| **0.95** | **OUI — appariées** |

**La conclusion bascule à 0.95.** À ce seuil, le balayage les
apparierait. Le seuil du dépôt reste **0,9999** et n'est pas touché : ce
tableau dit seulement à quelle distance du verdict on se trouve.

## Perturbation 2 — la période

La corrélation d'ensemble pourrait masquer un régime. Découpage en
**4 tranches** de longueur égale, déclaré avant exécution :

| Tranche | Séances | Corrélation |
|---|---|---|
| 1 | 2568 | +0.969870 |
| 2 | 2568 | +0.959460 |
| 3 | 2568 | +0.967939 |
| 4 | 2568 | +0.965398 |

- minimum : **+0.959460** — maximum : **+0.969870**

**Aucune tranche n'atteint le seuil.** La conclusion du #452 ne repose
pas sur un régime particulier : sur chaque quart de l'échantillon, les
deux séries restent distinctes.

## Ce que cette robustesse ne montre pas

Elle porte sur la **comparaison de deux séries**, pas sur la valeur de la
stratégie. Que la variante A soit distincte du #8 ne dit **rien** de sa
rentabilité : son PASS reste celui de son propre rapport, avec ses propres
réserves. Ce cycle n'a jamais prétendu la valider.


> **Rapport dépendant du dépôt** — ce document décrit l'état du dépôt à la date
> de son exécution. Il change à chaque cycle qui ajoute un fichier : c'est voulu,
> et ce n'est pas une péremption de résultat (cycles #436-#438).