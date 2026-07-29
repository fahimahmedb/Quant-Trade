# Pré-enregistrement — Overlay de vol-targeting gaté par le calendrier

**Committé AVANT tout calcul.** Cycle #54 du backlog non-ML. Variante du
mécanisme hiérarchique déjà validé au #47 (tendance + vol-targeting,
PASS 4/5) : remplace le signal de GATING (quand moduler l'exposition par
la vol) par la fenêtre calendaire union ToM∪Halloween déjà validée au
#21 (PASS 4/5), au lieu du signal de tendance 52w-high.

## Hypothèse

Le #47 a montré que gater le vol-targeting par un signal de RÉGIME DE
MARCHÉ (tendance) fonctionne bien. Ce cycle teste si le principe de
gating hiérarchique se généralise à un signal de nature complètement
différente (calendaire, sans lien avec le prix) : moduler l'exposition
par la vol réalisée UNIQUEMENT pendant les fenêtres calendaires déjà
identifiées comme statistiquement favorables (#21), plutôt qu'un CAP
fixe uniforme comme au #21 lui-même.

## Définition (fixée ici, avant tout résultat)

- Fenêtre calendaire = union ToM (4 derniers j. de bourse du mois + 3
  premiers j. du mois suivant) ∪ Halloween (novembre à avril inclus),
  définitions identiques aux cycles #2/#8/#17/#21.
- Vol réalisée = écart-type des rendements log quotidiens sur 20
  séances, annualisée, calcul causal identique au #43/#46/#47.
- Vol cible = **20% annualisé**, identique au #46/#47/#48/#51/#53.
- Position(t) :
  - si fenêtre calendaire active : **clip(vol_cible /
    vol_réalisée(t-1), 1.0, CAP=2.0)** (jamais en-dessous de 1.0x,
    identique à la logique du #47).
  - sinon : **1.0x**.
- Échantillon testable = à partir de la 21e séance.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (vol cible 20%, fenêtre 20j et CAP=2.0x
identiques au #46/#47, fenêtre calendaire identique au #21, aucune
grille testée avant ce résultat).

## Anti-cheat

Ce fichier committé avant
`nonml_calendar_vol_targeting_overlay_backtest.py`, vérification via
`nonml_anti_cheat_check.py calendar_vol_targeting_overlay`.
