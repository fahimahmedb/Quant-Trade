# Que faudrait-il pour que le modèle soit le plus significatif / prédictif possible ?

Synthèse de la littérature (académique + praticiens) confrontée à l'état réel du
dépôt. Objectif : lister, par ordre d'impact prouvé, ce qui manque pour passer
d'une skill de *downscaling* significative à une **vraie prévision** robuste.

## A. Ce que dit la littérature (ce qui fait qu'un modèle prédit bien)

1. **Le vote précédent + le swing dominent** tout le reste à la maille locale.
   Une étude ML sur les sièges australiens (Int. J. Forecasting 2025) montre que
   les modèles reposent d'abord sur le *pendulum* (swing) et la part du parti au
   scrutin précédent ; les variables **socio-éco ajoutent de façon INCOHÉRENTE**
   (utiles certaines élections, nuisibles d'autres) → il faut les *élaguer*, pas
   les empiler. **Bonne nouvelle : notre P9 utilise déjà le vote précédent — d'où
   sa significativité.**
2. **Les modèles hybrides gagnent** : combiner fondamentaux + sondages/marchés
   réduit l'erreur de **19–24 %** (Graefe ; Hummel & Rothschild). « Quand
   fondamentaux et sondages divergent, la vérité est entre les deux. »
3. **Ensembles (Gradient Boosting / Random Forest)** = meilleure précision quand
   on combine des signaux (confirme notre choix de GB).
4. **MRP** (régression multiniveau + post-stratification sur recensement) = étalon
   pour estimer des circonscriptions à partir d'un signal national/sondages.
5. **L'incertitude calibrée est centrale** (Gelman/Economist) : intervalles de
   prédiction, erreurs corrélées, effets-maison, biais de non-réponse — un bon
   modèle **quantifie** son incertitude et sa **couverture** est vérifiée.
6. **Le timing** : plus on approche du scrutin, plus le signal (sondages/marchés)
   est fiable → mise à jour dynamique.

## B. Où on en est (vérifié dans le code)

| Ingrédient littérature | État |
|---|---|
| Vote précédent + swing | ✅ P9 (c'est ce qui rend significatif) |
| Ensemble (GB) | ✅ P9 |
| **Vraie prévision hors-échantillon (multi-scrutins)** | ❌ P9 = 1 seule transition 2017→2022 (*downscaling*, pas prévision) |
| **Hybride (national × spatial)** | ❌ E4 désagrège au swing proportionnel, **pas** au ML ; fusion nationale dormante |
| **Incertitude calibrée + couverture** | ❌ P9 = points + MAE, aucun intervalle testé |
| Compositionnel (Dirichlet, somme=100) | ❌ régressions 1D par parti, indépendantes |
| Socio-éco (INSEE) | ❌ absent — mais impact *incertain* selon la littérature |
| Turnout / abstention différentielle | ❌ ignoré (or clé des modèles législatifs FR) |

## C. Feuille de route, par impact prouvé

### Tier 1 — fort impact, à faire (en cours / prioritaire)
1. **Vraie prévision temporelle** *(en cours — données 2012 par circo en
   récupération)*. Entraîner sur 2012→2017, tester sur 2017→2022 : convertit le
   *downscaling* en **prévision inter-scrutins** sur des circos ET une transition
   jamais vues. C'est LE chaînon qui rend la significativité *prédictive* et pas
   seulement descriptive.
2. **Hybride national × spatial** : brancher réellement le modèle spatial de
   circonscription sous une prévision nationale (fondamentaux/marchés/sondages).
   Le national donne le **niveau**, le modèle de circo donne la **distribution**.
   C'est le levier n°1 de la littérature (−19–24 % d'erreur) et il **active enfin
   honnêtement** la fusion (aujourd'hui dormante).
3. **Incertitude calibrée** : passer aux prédictions par **quantiles** (GB pinball
   loss) et **vérifier la couverture** (un intervalle 80 % doit contenir la vérité
   ~80 % du temps) en validation croisée. Point central de Gelman.

### Tier 2 — impact modéré / preuves mitigées
4. **Modélisation compositionnelle (Dirichlet)** : respecter somme=100 et propager
   l'incertitude jointe entre partis (Hanretty 2021) ; gain surtout en cohérence.
5. **Covariables socio-éco (INSEE)** par circonscription : à tester **comme une
   expérience**, PAS comme un acquis — la littérature dit que leur apport est
   incohérent une fois le vote précédent inclus. Élaguer si aucun gain OOS.
6. **Turnout / abstention différentielle** : ajouter la participation par circo
   comme variable (les modèles législatifs FR en font un pivot).

### Tier 3 — pour le réel 2027
7. **Sondages/marchés live** intégrés à l'approche du scrutin (le signal
   s'améliore avec le temps) — et effets-maison / erreurs corrélées si sondages.

## D. Réponse courte à « que faudrait-il encore »

Le modèle est **déjà maximalement significatif au sens statistique** sur sa tâche
actuelle (downscaling, p≈0). Pour le rendre le plus **prédictivement** significatif :
il faut surtout **(1) une vraie validation multi-scrutins**, **(2) l'hybridation
national×spatial**, **(3) une incertitude calibrée** — dans cet ordre. Les
covariables socio-éco, contre-intuitivement, sont **secondaires** : le vote
précédent fait déjà l'essentiel du travail.

*Sources : Hummel & Rothschild (fundamentals) ; Graefe et al. (combinaison) ;
Gelman/Morris (Economist, incertitude) ; Hanretty 2021 (Dirichlet) ; étude ML
sièges australiens, IJF 2025 (vote précédent > socio-éco) ; MRP (Wikipedia/Langer).*
