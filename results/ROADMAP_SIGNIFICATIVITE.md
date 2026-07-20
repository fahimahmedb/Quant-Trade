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

### Tier 1 — fort impact
1. **Vraie prévision temporelle** ✅ *FAIT (Étape P10) — résultat capital et
   contre-intuitif*. En entraînant sur 2012→2017 et en testant sur 2017→2022
   (transition inédite), **aucun ML ne bat le swing proportionnel** (MAE 1.05) :
   le Gradient Boosting **sur-apprend** (2.41). La skill de P9 était du
   *downscaling* (résultat 2022 vu à l'entraînement), elle **ne se transfère pas**
   à la prévision. **Conséquence directe : le levier de significativité N'EST PAS
   un modèle spatial plus complexe** — le vote précédent + swing proportionnel est
   une baseline quasi imbattable localement (conforme à l'étude ML australienne).
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

## D. Réponse courte à « que faudrait-il encore » (mise à jour après P10)

Vérification faite (P10), la réponse change de nature. Le modèle spatial est
**significatif en downscaling** (p≈0) mais **ne prévoit pas** mieux qu'un swing
proportionnel une élection inédite — la complexité ML **sur-apprend**. Donc :

- **Ce qu'il NE faut PAS faire** : empiler de la complexité spatiale (ML plus
  riche, plus de covariables socio-éco). P10 + littérature convergent : ça
  n'améliore pas la prévision, ça la dégrade.
- **Ce qui reste le vrai levier**, dans l'ordre :
  1. **La qualité de la prévision NATIONALE** (fondamentaux + sondages + marchés,
     hybridés) — c'est là que se joue 90 % de la significativité prédictive, et
     c'est le maillon faible actuel (fondamentaux seuls, non significatifs).
  2. **Descente aux circos par swing proportionnel** (simple, robuste, champion).
  3. **Incertitude calibrée** (quantiles + couverture vérifiée) — encore à faire.
  4. **Plus de scrutins** (législatives, européennes) pour moyenner la skill de
     prévision et, éventuellement, une **régression de Dirichlet** compositionnelle.

Autrement dit : le modèle est aussi significatif qu'il peut l'être *localement* ;
le gain restant est **national**, pas spatial.

*Sources : Hummel & Rothschild (fundamentals) ; Graefe et al. (combinaison) ;
Gelman/Morris (Economist, incertitude) ; Hanretty 2021 (Dirichlet) ; étude ML
sièges australiens, IJF 2025 (vote précédent > socio-éco) ; MRP (Wikipedia/Langer).*
