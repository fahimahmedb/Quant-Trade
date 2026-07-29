# Pré-enregistrement — Effet janvier stock-level (tax-loss selling, Keim 1983)

**Committé AVANT tout calcul.** Cycle #76 du backlog non-ML. Distinct du
January Barometer (#59, PASS 5/5), qui est un signal macro/indice
appliqué à l'ANNÉE ENTIÈRE (février-décembre). Ici le signal est
stock-level et n'affecte que le mois de JANVIER lui-même : Keim (1983)
documente que les titres les plus perdants de novembre-décembre
(vendus à perte pour raisons fiscales, "tax-loss selling") rebondissent
statistiquement en janvier lorsque la pression vendeuse fiscale se
dissipe.

## Hypothèse

Un portefeuille qui reste équipondéré sur l'univers NDX-100 le reste de
l'année, mais bascule vers le DÉCILE des titres les plus perdants de
novembre-décembre PENDANT le mois de janvier suivant, pourrait battre
un portefeuille équipondéré Buy&Hold classique — le rebond de janvier
documenté par Keim (1983) devrait apparaître comme un edge net de coûts
sur cette fenêtre précise.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 déjà récupérés localement
  (`data/pead/prices/*.json`), identique au #4/#14/#73/#75.
- Pour chaque année civile Y : rendement nov-déc(ticker, Y) =
  clôture(dernier jour de bourse de décembre, Y) / clôture(premier jour
  de bourse de novembre, Y) − 1, calculé pour chaque titre disposant de
  données sur toute la fenêtre.
- Sélection du **décile** (10%) de titres avec le rendement nov-déc(Y)
  le PLUS FAIBLE (les plus perdants).
- Position pendant **janvier(Y+1)** : équipondération sur ce décile de
  titres perdants. **En dehors de janvier** : équipondération sur
  l'univers complet (identique à la référence Buy&Hold — le portefeuille
  ne diffère de Buy&Hold QUE pendant les fenêtres de janvier).
- **Coûts** : 5 bps par unité de turnover à chaque transition (entrée en
  janvier, retour à l'univers complet en février).
- Référence : portefeuille équipondéré Buy&Hold classique sur l'univers
  complet, en permanence.
- Calendrier de référence = UNION des dates de cotation (même correction
  de bug documentée au #4).

## Univers et période

`data/pead/prices/*.json` (titres NDX-100), déjà en local. Nombre
d'observations annuelles limité par l'historique disponible (2021-2026,
~4-5 janviers testables) — **prudence méthodologique déclarée a
priori**, comparable à celle du January Barometer (#59) sur les marchés
à historique court.

## Critère de succès RENFORCÉ (pré-enregistré)

Le portefeuille doit battre le Buy&Hold équipondéré **simultanément** en
Sharpe annualisé net de coûts ET en rendement total net de coûts.
n_trials=1 (fenêtre nov-déc et décile fixés a priori sur la
construction académique standard de Keim 1983, aucune grille testée
avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_january_effect_stocklevel_backtest.py`, vérification via
`nonml_anti_cheat_check.py january_effect_stocklevel`.
