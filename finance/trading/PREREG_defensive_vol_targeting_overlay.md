# Pré-enregistrement — Overlay de vol-targeting DÉFENSIF uniquement

**Committé AVANT tout calcul.** Cycle #44 du backlog non-ML. Variante du
cycle #43 (vol-targeting continu avec levier possible jusqu'à 2.0x,
FAIL 3/5 mais MDD réduit massivement sur tous les marchés). Ce cycle
teste si LIMITER le mécanisme à la seule réduction d'exposition (jamais
de levier au-dessus de 1.0x) rapproche mieux du compromis
rendement/drawdown recherché explicitement à l'Étape D du projet
(capter l'essentiel du rendement Buy&Hold tout en réduisant le MDD).

## Hypothèse

Le #43 a montré que le mécanisme de vol-targeting réduit le MDD sur
TOUS les marchés mais échoue à battre le rendement Buy&Hold sur 2/5
(car la position moyenne descend souvent sous 1.0x). En retirant la
composante "amplification" (jamais de levier > 1.0x, seulement une
réduction en période de vol élevée), l'exposition moyenne devrait être
plus proche de 1.0x en période normale, ce qui pourrait rapprocher le
rendement de Buy&Hold tout en conservant le bénéfice de MDD en période
de stress.

## Définition (fixée ici, avant tout résultat)

- Vol réalisée = écart-type des rendements log quotidiens sur une
  fenêtre roulante de **20 séances**, annualisée (× √252), calcul
  causal identique au #43 (vol connue à t-1, position décidée pour t).
- Vol cible = **15% annualisé**, identique au #43 (paramètre inchangé,
  pour isoler l'effet du SEUL changement de plafond).
- Position(t) = **clip(vol_cible / vol_réalisée(t-1), 0.0, 1.0)** —
  PAS de levier au-dessus de 1.0x (différence unique avec le #43, dont
  le CAP était 2.0x). Pas de vente à découvert (plancher à 0.0).
- Échantillon testable = à partir de la 21e séance.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique (position 1.0x fixe).

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (vol cible 15%, fenêtre 20j identiques au #43,
seul le plafond de position change : 1.0x au lieu de 2.0x — ceci n'est
PAS un retuning du #43 mais une hypothèse mécaniquement distincte,
explicitement pré-enregistrée avant tout calcul).

## Anti-cheat

Ce fichier committé avant
`nonml_defensive_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py defensive_vol_targeting_overlay`.
