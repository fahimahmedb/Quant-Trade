# Synthèse finale — Prédiction politique FR : jusqu'où c'est significatif, et pourquoi

Une page pour clore le projet. Renvoie aux documents détaillés :
`AUDIT.md`, `AUDIT_GLOBAL.md`, `ROADMAP_SIGNIFICATIVITE.md`, et les étapes P1–P11.

## Le verdict en trois phrases

1. **Ce qui est statistiquement significatif** : le *downscaling* par
   circonscription — répartir un résultat national **connu** vers les 577 circos,
   par parti (LFI explicite). Un Gradient Boosting bat la meilleure baseline
   (swing proportionnel) avec p ≈ 0 sur 5094 prédictions (P9).
2. **Ce qui ne l'est PAS** : la **prévision** d'un scrutin inédit. Testé
   proprement (apprendre 2012→2017, prédire 2017→2022), **aucun ML ne bat le swing
   proportionnel** — le GB sur-apprend (P10). Le vote précédent + swing est une
   baseline quasi imbattable localement (conforme à la littérature).
3. **Où se gagne le reste** : au **national** (meilleure prévision d'ensemble) et
   dans la **calibration de l'incertitude** — pas dans plus de complexité spatiale.

## Ce qu'on a prouvé, étape par étape

| Question | Réponse établie (par la mesure) |
|---|---|
| Un modèle national (11 élections) peut-il être significatif ? | **Non** — n trop petit ; ne bat pas une heuristique d'1 ligne (P1). |
| Le hindsight gonflait-il les scores ? | **Oui** — snapshots marchés/NLP rétrospectifs supprimés (AUDIT). |
| La circonscription apporte-t-elle un signal réel ? | **Oui**, fort — LFI en tête dans 105 circos ; erreur locale ÷2 (P7). |
| Peut-on lire les reports de voix (2nd tour) dans les agrégats ? | **Non** — sophisme écologique, non identifiable (P8). |
| Le ML par circo est-il significatif (downscaling) ? | **Oui**, massivement (p≈0, 9 partis, P9). |
| Le ML prévoit-il un scrutin inédit mieux que le swing ? | **Non** — il sur-apprend ; le swing proportionnel gagne (P10). |
| Peut-on calibrer l'incertitude de façon fiable ? | **En moyenne oui, par parti non** — LFI sous-couvert (P11). |
| Peut-on ajouter des scrutins pour lever ces limites ? | **Non au niveau circo moderne** — plafond 2012-2022 (redécoupage 2010). |

## Réponse définitive à « que faudrait-il pour qu'il soit le plus significatif possible »

Le modèle est **déjà à son maximum de significativité *possible*** sur les données
disponibles :
- **maximal en downscaling** (p≈0, prouvé) ;
- **borné en prévision** par une baseline (swing proportionnel) que la complexité
  ne bat pas — un résultat, pas un échec ;
- **borné en incertitude** par le nombre de transitions (2), qui est un **plafond
  de données dur** (pré-2012 non comparable).

Les seuls leviers restants, tous **hors modélisation spatiale** :
1. **Un vrai signal national** (sondages/marchés live), branchable tel quel dans le
   pipeline P11 — c'est 90 % de la significativité prédictive.
2. **Plus de scrutins** (2027 et au-delà) → calibration fiable + test de prévision
   moyennable.
3. **Incertitude** : le pipeline P11 la propage déjà (Monte-Carlo) ; sa fiabilité
   s'améliorera mécaniquement avec (2).

## Bottom line

Ce projet ne « prédit » pas 2027 — et il **explique honnêtement pourquoi** aucun
modèle sérieux ne le peut aujourd'hui sans un signal national live. Sa valeur est
d'être **calibré sur ce qui est vrai** : significatif là où c'est démontrable
(downscaling par parti, LFI explicite), lucide là où ça ne l'est pas (prévision,
reports), et **prêt à s'améliorer par les données, pas par la complexité**.
