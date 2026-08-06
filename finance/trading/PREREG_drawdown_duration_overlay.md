# Pré-enregistrement — Overlay défensif "durée du drawdown" (temps sous l'eau)

**Committé AVANT tout calcul.** Cycle #279 du backlog non-ML.

## Hypothèse

La DURÉE écoulée depuis le dernier plus haut glissant (nombre de
séances de bourse consécutives sans nouveau record) est documentée en
gestion de risque comme un indicateur de persistance de régime baissier
— indépendamment de la PROFONDEUR du creux (déjà testée au #111, seuil
absolu en %, RECLASSÉ FAIL en Règle 9) et de la VITESSE de rebond
(#120, FAIL). Une phase de repli prolongée, même peu profonde, est
documentée comme précédant souvent une volatilité accrue plutôt qu'un
rebond imminent — **direction DÉFENSIVE, à l'opposé de la logique
contrarian-amplificatrice du #111** (qui pariait sur un rebond depuis un
creux profond). Cette direction est déclarée ICI, avant tout calcul.

## Définition (fixée ici, AVANT tout calcul, réutilisation de la
technique de tercile expanding déjà établie aux #169/#177/#183/#191/
#192/#193/#195, Règle 7)

- `running_max(t)` = maximum glissant causal de `close` sur `[0, t]`
  (inclusif).
- `duration(t)` = nombre de séances depuis le dernier nouveau record :
  `duration(t) = 0` si `close(t) >= running_max(t)` (nouveau record),
  sinon `duration(t) = duration(t-1) + 1`.
- Alignement causal : `duration(t)` (connu à la clôture du jour t) est
  décalé d'un jour (`shift(1)`, même convention que tout le reste du
  backlog) pour piloter la position du jour t+1.
- **Position** : `CUT=0,5x` (réutilisé de la famille macro-externe
  défensive, Règle 7) si `duration(t-1)` est dans son tercile expanding
  le PLUS HAUT (les phases de repli les plus longues observées jusqu'à
  présent), `1,0x` sinon (jamais de levier — design purement défensif,
  cohérent avec la direction déclarée).

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée nécessaire.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule définition testée : tercile expanding, CUT=0,5x — aucune
grille de largeur/seuil à ce stade).

## Anti-cheat

Ce fichier committé avant `nonml_drawdown_duration_overlay_backtest.py`.
Vérification prévue : recalcul indépendant de `duration(t)` par boucle
explicite, vérification anti-lookahead par troncature de l'historique
(position identique sur les N premières séances, peu importe le futur
tronqué — même méthode que #191/#193/#195). Sortie :
`results/nonml_drawdown_duration_overlay_result.md`.
