# Pré-enregistrement — Overnight vs Intraday

**Committé AVANT tout calcul.** Cycle #1 du backlog non-ML
(`NONML_STRATEGY_BACKLOG.md`).

## Hypothèse

Anomalie documentée en littérature (ex. Cliff Asness/AQR, plusieurs études
sur le "overnight drift") : une large part du rendement actions provient
de la période **overnight** (clôture → ouverture du lendemain), pas de la
période **intraday** (ouverture → clôture). Cette stratégie n'est PAS du
ML — deux règles déterministes de calendrier, aucun paramètre appris.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite (5 ans), NDX-100
(40 ans), Russell 2000, S&P 500, DAX — mêmes fichiers `data/*.txt`, aucune
nouvelle donnée nécessaire.

## Définition (fixée ici, avant tout résultat)

- Rendement overnight jour *t* : `log(open_t / close_{t-1})`
- Rendement intraday jour *t* : `log(close_t / open_t)`
- **Stratégie Overnight-only** : position longue de la clôture à
  l'ouverture du lendemain seulement (flat pendant la séance).
- **Stratégie Intraday-only** : position longue de l'ouverture à la
  clôture seulement (flat la nuit).
- **Référence** : Buy & Hold classique (toujours investi, 1 seul coût
  d'entrée sur toute la période).
- **Coûts** : ces deux stratégies impliquent une transaction PAR JOUR
  (turnover maximal) — 5 bps par transaction (même convention coût que le
  reste du projet), soit un coût quotidien bien plus lourd que Buy & Hold.
  Ce n'est pas ajusté après coup : c'est la conséquence mécanique et
  attendue du design, assumée avant le résultat.

## Critère de succès (pré-enregistré)

Overnight-only OU Intraday-only bat Buy & Hold en Sharpe annualisé net de
coûts sur **au moins 4 des 5 marchés**. n_trials=1 (les deux variantes sont
rapportées ensemble comme UNE seule hypothèse symétrique "où se cache le
rendement", pas une recherche parmi elles).

## Anti-cheat

Même processus que PEAD : ce fichier committé avant `nonml_overnight_backtest.py`,
aucune grille de paramètres, vérification automatisée via
`nonml_anti_cheat_check.py` (généralisation de `pead_anti_cheat_check.py`).
