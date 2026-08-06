# Audit adversarial — Volume anormal de l'indice comme porte défensive

## 1. Recalcul indépendant de la porte (tri manuel, sans np.percentile)

Échantillon d'une date sur 250 (tri Python pur sur l'historique complet à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du #282/#296).

| Marché | % actif | Dates échantillonnées | Désaccords |
|---|---|---|---|
| NDX (40 ans) | 83.4% | 42 | 0 |
| Russell 2000 | 89.0% | 40 | 0 |
| S&P 500 | 93.1% | 58 | 0 |
| DAX | 40.5% | 28 | 0 |

**OK — recalcul indépendant identique sur l’échantillon (0 désaccord).**

## 2. Non-stationnarité du volume brut (confirme le taux de coupure élevé, pas un bug)

Moyenne du volume sur les 5 premières années vs les 5 dernières années disponibles :

| Marché | Vol. moyen 5 premières années | Vol. moyen 5 dernières années | Ratio |
|---|---|---|---|
| NDX (40 ans) | 44,400,188 | 1,004,989,157 | 22.6× |
| Russell 2000 | 172,556,504 | 4,490,777,160 | 26.0× |
| S&P 500 | 14,680,680 | 4,500,033,566 | 306.5× |
| DAX | 74,605,149 | 68,304,718 | 0.9× |

**Confirmé** : NDX, Russell 2000 et S&P 500 (historiques longs, plusieurs décennies) montrent une croissance séculaire massive du volume brut (13-306×) — le tercile EXPANDING, calculé depuis le tout début de l'historique, classe alors mécaniquement la quasi-totalité des séances récentes dans le tercile le plus haut (83-93% actif), un artefact de NON-STATIONNARITÉ du niveau de volume, PAS un bug de calcul (le recalcul indépendant ci-dessus confirme 0 désaccord). DAX (volume quasi stable sur son historique plus court) montre un taux de coupure normal (~40%), cohérent avec cette explication.

## 3. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 9000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.**
