# Pré-enregistrement — Effet pré/post jour férié

**Committé AVANT tout calcul.** Cycle #7 du backlog non-ML. Soumis à la
règle de succès renforcée (Sharpe ET rendement absolu).

## Hypothèse

Ariel (1990), Lakonishok & Smidt (1988) : rendements historiquement plus
élevés la séance précédant un jour férié et/ou la séance suivante. Règle
déterministe de calendrier, aucun paramètre appris.

## Détection des jours fériés (fixée ici — méthode DATA-DRIVEN, pas de
calendrier codé en dur)

Coder en dur 40+ ans de jours fériés US (avec décalages weekend) est une
source d'erreur significative et invérifiable facilement. À la place :
un jour férié est détecté directement via un **trou anormal dans le
calendrier de séances déjà présent dans les données** — écart en jours
calendaires entre deux séances consécutives supérieur à l'écart normal
pour ce jour de la semaine :
- Écart normal lundi→jeudi : 1 jour calendaire.
- Écart normal vendredi→lundi suivant : 3 jours calendaires.
- Tout écart SUPÉRIEUR à cette norme = jour férié détecté entre les deux
  séances.

- **Séance "pré-férié"** : la séance juste AVANT un tel trou anormal.
- **Séance "post-férié"** : la séance juste APRÈS un tel trou anormal.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Stratégie et critère de succès RENFORCÉ

**Holiday-only** : position longue uniquement les séances pré-férié ET
post-férié (flat les autres jours), coût 5 bps par transaction. Doit
battre Buy & Hold **simultanément** en Sharpe ET rendement total net de
coûts, sur **au moins 4 des 5 marchés**. n_trials=1.

**Note pré-enregistrée avant résultat** : cette stratégie sera investie
une très petite fraction du temps (quelques % de l'année, similaire au
cycle #6 Santa Claus) — la même tension structurelle déjà documentée au
cycle #6 (difficile de battre le rendement composé de Buy&Hold avec une
exposition aussi faible) s'applique probablement ici aussi. Testé quand
même intégralement par discipline (n_trials=1 pré-enregistré), pas
sauté malgré l'attente d'un FAIL probable.

## Anti-cheat

Ce fichier committé avant `nonml_holiday_effect_backtest.py`, vérification
via `nonml_anti_cheat_check.py holiday_effect`.
