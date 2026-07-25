# Synthèse du projet Quant-Trade (pour lecteur non spécialiste)

*Sources : les six fichiers `results/etape_{A,B,C}_*.md`. Deux jeux de données : NASDAQ Composite (5 ans, 2021–2026) et NASDAQ-100 « NDX » (40 ans, 1985–2026). L'Étape D (overlay défensif) est en cours : aucun résultat chiffré n'existe encore.*

## 1. Ce qui a été construit

Imaginez un bilan médical avant traitement. **L'Étape A** est le diagnostic : le marché est-il prévisible ? **L'Étape B** est la tentative de traitement : des modèles qui décident quand acheter ou rester à l'écart. **L'Étape C** est le tensiomètre : elle ne prédit pas la direction du marché, mais l'ampleur de ses secousses à venir (la volatilité). **L'Étape D**, à venir, combinera B et C pour piloter la taille des positions et réduire les dégâts dans les tempêtes.

## 2. La question centrale : est-ce que ça gagne de l'argent ?

Réponse honnête : **pas mieux qu'un simple achat-conservation (« Buy & Hold »), pour l'instant.**

- Sur 5 ans (Composite), le diagnostic conclut que les prix suivent essentiellement une marche aléatoire : rien d'exploitable dans la direction. Aucun des trois signaux actifs testés ne bat le Buy & Hold ; deux perdent de l'argent net de frais.
- Sur 40 ans (NDX), une très légère prévisibilité est détectée (retour à la moyenne, p=0,007). Le meilleur signal actif (régression logistique) est **rentable net de coûts** : Sharpe +0,30, précision directionnelle 53,7 %, et il supporterait des frais de ~17 points de base alors que 5 sont facturés. Mais après correction du biais de sélection (DSR — probabilité que la performance ne soit pas due au hasard), il reste **derrière le Buy & Hold** : DSR 0,372 contre 0,842, aucun ne franchissant le seuil de crédibilité de 0,95.
- En revanche, **la prévision du risque fonctionne** : sur 40 ans, le modèle GJR-GARCH-t prévoit la volatilité mieux que le modèle de référence, et cet avantage **survit au test anti-hasard le plus sévère** (SPA, p=0,0000 à 1 jour, p=0,0034 à 5 jours). Sur 5 ans seulement, ce même avantage existe mais n'est pas statistiquement tranché (SPA p≈0,11–0,15, échantillon trop court).

En résumé : le projet ne sait pas (encore) prédire *où* va le marché mieux que ne rien faire, mais il sait prédire *à quel point il va secouer* — et c'est cette brique-là qui est solide.

## 3. Tableau comparatif (NDX, 40 ans hors échantillon, net de frais)

*Sharpe = rendement gagné par unité de risque pris (plus haut = mieux ; ~0,5 est ordinaire, >1 est bon). MDD = « max drawdown », la pire chute depuis un sommet.*

| Stratégie | Sharpe | Rendement annualisé | MDD | En clair |
|---|---|---|---|---|
| Buy & Hold | +0,52 | +14,5 % | −82,9 % | Le plus rentable, mais on a perdu 83 % au pire moment |
| Momentum 10 j | −0,28 | −7,1 % | −97,6 % | Perd de l'argent, quasi-ruine au pire |
| Logistique L2 | +0,30 | +8,3 % | −64,2 % | Rentable, chute moins, mais gagne nettement moins |
| Gradient boosting | +0,23 | +6,1 % | −77,7 % | Rentable mais dominé partout |

Sur 5 ans (Composite) : Buy & Hold +18,9 %/an (Sharpe +0,78, MDD −24,3 %) ; les signaux actifs font entre −14,2 % et +1,0 %/an. Même verdict.

**Overlay défensif (Étape D)** : pas encore de chiffres — ligne à compléter après exécution.

## 4. Le risque, expliqué simplement

Dire « peu importe le risque, le Buy & Hold gagne » ignore le vécu : sur l'historique long, le NDX a chuté de **−82,9 %** depuis son sommet (krach dot-com 2000-2002). Concrètement, 100 000 € devenaient ~17 000 €, et il faut ensuite près de +500 % de hausse pour revenir à zéro — des années d'attente que peu d'investisseurs tiennent sans vendre au pire moment. C'est exactement là que la brique C devient utile : puisqu'on sait prévoir les régimes de fortes secousses (volatilité prédite entre 8,6 % et 111 % annualisés sur l'OOS), l'Étape D vise à **réduire l'exposition quand la tempête est probable**, pour garder l'essentiel du rendement du Buy & Hold avec une pire chute nettement moins profonde. C'est un objectif, pas encore un résultat.

## 5. Prochaines pistes réalistes

Terminer et évaluer l'Étape D (vol-targeting + coupe en régime extrême) sous le même protocole figé et test anti-hasard ; pour la direction (B), viser de meilleures données (intraday, sentiment) plutôt que plus de modèles ; affiner C avec de la volatilité réalisée intraday.

---

*Notes de cohérence : les titres des fichiers `*_ndx100.md` (A et B) disent « NASDAQ Composite » alors que le contenu porte sur le NDX (étiquette non mise à jour). `CLAUDE.md` évoque ν≈4,8 « dans les deux cas » alors que `etape_A_ndx100.md` donne ν=2,84 pour le NDX (4,78 pour le Composite). Sur le NDX à 1 jour, le meilleur QLIKE est HAR-P mais le modèle adopté reste GJR-t (choix pré-enregistré, expliqué dans le fichier).*
