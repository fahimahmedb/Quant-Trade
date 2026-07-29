# Pré-enregistrement — Effet week-end CONDITIONNEL (lundi | signe du vendredi précédent)

**Committé AVANT tout calcul.** Cycle #105 du backlog non-ML.

## Hypothèse

Le #3 (day-of-week inconditionnel) a échoué (0/5) : aucun jour de la
semaine ne montre d'edge exploitable pris isolément. La littérature
documente cependant un effet CONDITIONNEL plus fin : le rendement du
lundi serait davantage prévisible une fois conditionné au signe du
rendement du vendredi précédent (continuation du sentiment de fin de
semaine plutôt qu'un simple effet de calendrier fixe). Ce cycle teste
une INTERACTION entre deux jours consécutifs, jamais testée dans ce
backlog (tous les effets calendaires précédents étaient inconditionnels
ou basés sur des fenêtres fixes).

## Définition (fixée ici, avant tout résultat)

- Marchés : les 5 marchés OHLC déjà en local (`data/*.txt`), identique
  à la famille #3/#9/#29.
- Détection data-driven (pas de calendrier codé en dur) : une séance est
  "lundi" si `date.weekday() == 0`, "vendredi" si `date.weekday() == 4`.
- Pour chaque séance de lundi, on recherche la séance de VENDREDI la
  plus récente qui la précède (recherche arrière dans le calendrier de
  trading réel, robuste aux jours fériés qui décalent les séances).
- Porte active (overlay CAP=2.0x) UNIQUEMENT les séances de lundi dont
  le vendredi précédent a un rendement STRICTEMENT POSITIF ; **1.0x**
  tous les autres jours (y compris les lundis suivant un vendredi
  négatif ou nul, et tous les jours non-lundi).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur chaque marché.

## Univers et période

`data/*.txt` (5 marchés), déjà en local.

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy&Hold **simultanément** en Sharpe annualisé net
de coûts ET en rendement total net de coûts sur **au moins 4 des 5
marchés** (identique au seuil du #3/#9/#29). n_trials=1 (CAP=2.0x
identique à la famille, aucune grille testée avant ce résultat — la
définition de la porte elle-même, l'interaction lundi|vendredi, est le
cœur de l'hypothèse testée, pas un paramètre à faire varier).

## Robustesse prévue (SI PASS)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x}.

## Anti-cheat

Ce fichier committé avant `nonml_conditional_weekend_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py conditional_weekend_overlay`.
