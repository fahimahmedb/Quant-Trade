# Pré-enregistrement — "January effect" (petites capitalisations, proxy prix) en overlay

**Committé AVANT tout calcul.** Cycle #86 du backlog non-ML. Combine un
filtre de taille (jamais utilisé jusqu'ici dans ce backlog) à une
fenêtre calendaire de janvier, sur un design overlay identique dans
l'esprit au #8/#54 (reste investi au portefeuille de base toute
l'année, ajoute un levier supplémentaire SEULEMENT pendant la fenêtre
calendaire).

## Hypothèse

La littérature (Keim 1983, Reinganum 1983) documente un "January
effect" : les titres à petite capitalisation surperforment
historiquement en janvier, attribué en partie à un dénouement des
ventes à perte fiscales de décembre (tax-loss selling) suivi d'un
rachat en début d'année. L'hypothèse testée ici est qu'un portefeuille
concentré sur le tercile de titres à plus faible taille RELATIVE de
l'univers NDX-100 bénéficie d'un supplément de rendement/Sharpe
spécifiquement en janvier, justifiant un levier temporaire.

**Limite méthodologique majeure, signalée AVANT tout calcul (prudence
forte)** : `data/pead/prices/*.json` ne contient que `close` (pas de
nombre d'actions en circulation, donc pas de vraie capitalisation
boursière). Le proxy utilisé est le **niveau de prix de clôture**
(tercile des titres au prix le PLUS FAIBLE), comme explicitement
envisagé dans la description du backlog en l'absence de market cap.
C'est un proxy connu pour être imparfait (un prix bas peut refléter un
grand nombre d'actions en circulation sur une très grande capitalisation,
pas nécessairement une "petite" entreprise) — le résultat doit être lu
comme un test du "prix bas" plutôt qu'un vrai test de taille boursière,
et ce biais potentiel est documenté ici, pas découvert après coup.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés (`data/pead/prices/*.json`),
  calendrier UNION (identique au #4/#14/#73/#82/#84).
- Portefeuille de base = tercile inférieur par PRIX DE CLÔTURE (proxy
  taille), rebalancement tous les `REBAL_EVERY=21` jours (mensuel,
  identique aux autres portefeuilles de sélection de ce backlog),
  équipondération au sein du tercile.
- Fenêtre calendaire = mois de **janvier** uniquement (détection
  data-driven via le mois calendaire de la date, `date.month == 1`, pas
  de calendrier codé en dur par plage de jours).
- Position globale(t) : **CAP=2.0x** si la date est en janvier, **1.0x**
  sinon — mécanisme overlay identique au #8/#54 (jamais en-dessous de
  1.0x, jamais de sélection différente hors fenêtre).
- **Coûts** : 5 bps par unité de turnover (rebalancement mensuel ET
  changement d'exposition à l'entrée/sortie de janvier).
- **Référence** : portefeuille tercile "prix bas" 1.0x en permanence
  (même convention que #11/#23/#33/#35/.../#85 — comparaison au
  portefeuille de base, pas au Buy&Hold généraliste).

## Univers et période

`data/pead/prices/*.json` (titres NDX-100), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay janvier doit battre le portefeuille tercile "prix bas" de
référence **simultanément** en Sharpe annualisé net de coûts ET en
rendement total net de coûts. n_trials=1 (CAP=2.0x et REBAL_EVERY=21j
repris identiques aux cycles précédents, aucune grille testée avant ce
résultat).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} —
vérifie un plateau plutôt qu'un pic isolé sur le CAP=2.0x
pré-enregistré. Le mois calendaire (janvier) et la fenêtre de
rebalancement (21j) ne sont PAS perturbés (au cœur du critère
hypothétique testé, pas des paramètres accessoires).

## Anti-cheat

Ce fichier committé avant
`nonml_january_effect_lowprice_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py january_effect_lowprice_overlay`.
