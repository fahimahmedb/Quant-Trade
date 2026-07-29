# Pré-enregistrement — Overlay levé sur "faux breakdown" de Donchian (capitulation/récupération)

**Committé AVANT tout calcul.** Cycle #62 du backlog non-ML. Miroir du
#55 (faux breakout Donchian, signal baissier défensif, FAIL) mais sur le
canal BAS : ici un "faux breakdown" (le prix casse le plus bas glissant
20j PUIS récupère au-dessus dans les 2 séances suivantes) est traité
comme un signal HAUSSIER (amplification, pas réduction), motivé par la
littérature distincte de la capitulation/selling climax (Kirkpatrick &
Dahlquist) plutôt que par la microstructure des pièges haussiers utilisée
au #55.

## Hypothèse

Une cassure du plus bas récent suivie d'une récupération rapide
au-dessus de ce niveau dans les 2 séances suivantes signale un
épuisement des vendeurs (capitulation, "selling climax") plutôt qu'une
poursuite baissière — contrairement au #55 où l'échec d'un breakout
signalait un manque de conviction ACHETEUSE (piège haussier). Les deux
patterns ne sont PAS symétriques en théorie de marché : la capitulation
suivie d'une récupération rapide est un signal de retournement HAUSSIER
bien documenté (contrairement au #55, qui a échoué). Un overlay qui reste
investi 1,0x en permanence mais AMPLIFIE l'exposition après ce signal
pourrait battre Buy&Hold.

## Définition (fixée ici, avant tout résultat)

- Canal de Donchian = plus bas glissant des 20 dernières clôtures
  (`DONCHIAN_WINDOW=20`, symétrique du #55/#40 mais sur le plus bas).
- Breakdown au jour t = clôture(t) ≤ plus bas glissant 20j au jour t.
  Niveau de breakdown = ce plus bas glissant.
- Faux breakdown confirmé au jour t' (avec 1 ≤ t'-t ≤ `CONFIRM_WINDOW=2`)
  si clôture(t') > niveau de breakdown (le prix récupère au-dessus du
  niveau cassé dans les 2 séances suivant le breakdown).
- Dès qu'un faux breakdown est confirmé au jour t', position = **CAP =
  2,0x** (amplification, PAS une réduction — inverse du #55) pendant les
  **`DEFENSE_LEN=5` séances suivantes** (même longueur que #13/#22/#24/
  #55), 1,0x sinon. Si un nouveau faux breakdown est confirmé pendant la
  fenêtre déjà active, la fenêtre est relancée à 5 séances (même logique
  de re-déclenchement que #55).
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (fenêtre Donchian 20j, fenêtre de confirmation 2j,
fenêtre d'amplification 5j et CAP=2,0x fixés a priori par symétrie
directe avec le #55/#40, aucune grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant `nonml_failed_breakdown_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py failed_breakdown_overlay`.
