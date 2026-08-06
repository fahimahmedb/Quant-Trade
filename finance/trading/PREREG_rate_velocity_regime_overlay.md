# Pré-enregistrement — Overlay défensif "vitesse du taux court" (DGS3MO)

**Committé AVANT tout calcul.** Cycle #280 du backlog non-ML.

## Distinction explicite avec le #175 (vérification anti-doublon,
leçon directe des erreurs #276/#277 de ce backlog)

Le #175 ("régime de niveau des taux courts") calcule en réalité un
`delta = taux(t-1) - taux(t-1-63j)` — c'est DÉJÀ une variation sur
fenêtre glissante, pas un niveau brut. Il utilise cependant le **SIGNE**
brut de ce delta (`CUT=0,5x` si `delta>0` quelle que soit son ampleur,
`CAP=2,0x` si `delta<0`) — **FAIL NET, contre-productif** : diagnostic
du PREREG d'origine confirmé par le résultat, "les baisses de taux
surviennent souvent EN RÉPONSE à une crise déjà en cours (le plafond
2,0x amplifie les pertes)".

Ce cycle teste une construction **méthodologiquement distincte**, pas
un retuning du #175 :
1. **Magnitude, pas signe** : tercile expanding de `delta` (comme la
   quasi-totalité des autres signaux macro-défensifs du backlog —
   #191/#193/#195/#198/#199/#200/#202/#203/#204/#205/#206 — TOUS
   utilisent une magnitude relative par tercile, jamais un signe brut ;
   #175 et #178 sont les deux SEULES exceptions à cette convention).
   Seules les hausses les plus RAPIDES (tercile le plus haut de
   `delta`, pas n'importe quelle hausse) déclenchent la position
   défensive.
2. **Design purement défensif, sans jambe d'amplification** : `1,0x`
   sinon, JAMAIS `2,0x` sur baisse de taux — retire explicitement le
   mécanisme diagnostiqué comme la cause du caractère "contre-productif"
   du #175 (le plafond 2,0x qui amplifiait les crises en cours).

Ces deux changements de construction (magnitude vs signe, suppression
de la jambe d'amplification) sont déclarés ICI, avant tout calcul — pas
après avoir vu un résultat. Si ce test échoue aussi, il n'invaliderait
pas la distinction : il confirmerait simplement que même une
construction plus rigoureuse ne sauve pas le signal DGS3MO.

## Hypothèse

"Don't fight the Fed" documente l'effet du RYTHME de resserrement
monétaire (pas seulement son niveau ou sa direction) sur les actifs
risqués — un resserrement RAPIDE (choc de politique monétaire) est
documenté comme plus perturbateur qu'un resserrement graduel anticipé
par le marché.

## Définition (fixée ici, AVANT tout calcul, réutilisation Règle 7)

- `delta(t) = DGS3MO_lag(t) - DGS3MO_lag(t-63)` (fenêtre 63j réutilisée
  du #175, alignement causal ffill+shift(1) réutilisé de `load_rate_lag`
  du #175/#178).
- **Position** : `CUT=0,5x` si `delta(t)` est dans son tercile expanding
  le PLUS HAUT (resserrement le plus rapide observé jusqu'à présent),
  `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée nécessaire.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1.

## Anti-cheat

Ce fichier committé avant `nonml_rate_velocity_regime_overlay_backtest.py`.
Vérification prévue : recalcul indépendant par boucle+searchsorted
manuel (même méthode que #191/#193/#195/#198/#199), anti-lookahead
vérifié par troncature. Sortie :
`results/nonml_rate_velocity_regime_overlay_result.md`.
