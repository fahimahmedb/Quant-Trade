# Pré-enregistrement — Mise à jour du guide de formalisation (v2, cycles #258-262)

**Committé AVANT toute rédaction.** Cycle #263 du backlog non-ML. Pas un
nouveau backtest — mise à jour du guide
`results/nonml_meilleurs_candidats_guide_deploiement.md` (rédigé au
#251, corrigé au #252), qui n'a plus été touché depuis et ne reflète pas
les cycles #253-262.

## Motivation

Le guide actuel cite Candidat A (#149, MDD) et Candidat B (#237/#238,
significativité) comme les deux seuls candidats restants après le
retrait du Candidat C (#38/#163) au #252. Depuis :
- le balayage d'intégrité même barre (#253-260) a corrigé 8+ candidats
  stock-selection supplémentaires (dont les batteries historiques
  #161/#162 elles-mêmes, #260) ;
- une catégorie de données entièrement nouvelle (volume) a produit
  **deux PASS** (#258 Lee & Swaminathan, #261 Amihud illiquidité) ;
- le #261, soumis à la Règle 9 au #262, obtient **4/5 — DSR=0,2731,
  SPA p=0,0034** : un DSR **22× supérieur** au Candidat A (0,0122) et
  **2700× supérieur** au Candidat B (0,0001), avec un score Règle 9
  identique à B (4/5) et un SPA meilleur que A (1,00) tout en restant
  proche de B (0,0022).

Le #261 mérite d'être intégré au guide comme nouveau candidat — sa
qualité relative sur l'axe DSR/SPA en fait le meilleur candidat du
guide sur cette dimension précise, sans remplacer A ou B (objectifs
différents, non comparables terme à terme).

## Méthode

Lecture des résultats déjà committés (#258-262), aucune nouvelle donnée
ni nouveau calcul. Mise à jour du guide : ajout d'un « Candidat C (v2) »
distinct de l'ancien C retiré (mécanisme totalement différent — prime de
liquidité, pas momentum/survivorship), mise à jour de la section
« plafond structurel » avec n_trials=269 (au lieu de 252), mise à jour
du décompte des hypothèses testées en tête de document.

## Anti-cheat

Ce fichier committé avant toute rédaction. Sortie :
`results/nonml_meilleurs_candidats_guide_deploiement.md` (mise à jour en
place, même fichier que #251/#252 — pas un nouveau document, pour éviter
la prolifération de guides concurrents). Pas de vérification anti-cheat
automatisée applicable (pas de backtest).
