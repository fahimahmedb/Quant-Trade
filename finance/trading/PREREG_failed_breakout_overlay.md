# Pré-enregistrement — Overlay défensif sur "faux breakout" de Donchian

**Committé AVANT tout calcul.** Cycle #55 du backlog non-ML. Dernier
item de la file actuelle. Variante INVERSE du cycle #40 (breakout
Donchian 20j comme signal de CONTINUATION haussière, FAIL 2/5) :
teste ici le breakout qui ÉCHOUE à se maintenir (retour sous le niveau
cassé dans les 2 séances suivantes) comme signal BAISSIER contrarian,
motivé par la littérature de microstructure (chasse aux stops, pièges
haussiers "bull traps"). Contrairement à tous les overlays précédents
qui AMPLIFIENT l'exposition sur un signal, celui-ci la RÉDUIT (c'est un
signal défensif, pas un signal de levier).

## Hypothèse

Un breakout qui échoue rapidement à se maintenir (le prix retombe sous
le niveau cassé dans les 2 séances qui suivent) signale un manque de
conviction acheteuse ("bull trap") et pourrait précéder une baisse — une
RÉDUCTION temporaire de l'exposition après ce signal pourrait améliorer
le ratio rendement/risque par rapport à une exposition constante.

## Définition (fixée ici, avant tout résultat)

- Canal de Donchian = plus haut glissant des 20 dernières clôtures
  (identique au #40).
- Breakout au jour t = clôture(t) ≥ plus haut glissant 20j au jour t
  (identique au #40). Niveau de breakout = ce plus haut glissant.
- Faux breakout confirmé au jour t' (avec 1 ≤ t'-t ≤ 2) si clôture(t') <
  niveau de breakout (le prix retombe sous le niveau cassé dans les 2
  séances suivant le breakout).
- Dès qu'un faux breakout est confirmé au jour t', position =
  **FLOOR = 0,5x** (réduction défensive, PAS une vente à découvert)
  pendant les **5 séances suivantes** (même longueur de fenêtre que les
  cycles #13/#22/#24), 1.0x sinon. Si un nouveau faux breakout est
  confirmé pendant la fenêtre déjà active, la fenêtre est relancée à 5
  séances (même logique de re-déclenchement que #13/#22/#24). Décision
  prise à la clôture du jour t' (connu à cette date), appliquée au
  rendement t'→t'+1.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (fenêtre Donchian 20j identique au #40, fenêtre de
confirmation 2j, fenêtre défensive 5j et FLOOR=0,5x fixés a priori,
aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_failed_breakout_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py failed_breakout_overlay`.
