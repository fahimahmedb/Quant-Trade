# Pré-enregistrement — Overlay vol-targeting gaté par la breadth de rebond rapide post-creux

**Committé AVANT tout calcul.** Cycle #120 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## Hypothèse

Distinct du #111 (fraction de titres en drawdown PROFOND, seuil absolu
-20% sous le plus haut) et du #100/#112 (dispersion/spread du momentum,
mesures de niveau) : ce cycle mesure la VITESSE de rebond — la fraction
de titres NDX-100 remontant fortement (≥10%) depuis leur PLUS BAS
glissant 20 jours, une fenêtre courte captant la dynamique de reprise
plutôt qu'un niveau de prix. Distinct aussi du #13 (rebond post-drawdown
au niveau INDICE, déjà FAIL net) : ici la mesure est cross-sectionnelle
(fraction de titres), pas un signal univarié sur l'indice. Hypothèse
contrarian/momentum hybride : une fraction élevée de titres rebondissant
fortement signale une reprise large et confirmée (pas un rebond isolé
de quelques titres), régime propice à amplifier l'exposition via le
mécanisme hiérarchique déjà validé.

## Définition (fixée ici, avant tout résultat)

- Univers : titres NDX-100 individuels, `data/pead/prices/*.json`
  (calendrier UNION des tickers, convention identique à #78/#89/#111).
- `RollingLow_20(t)` = minimum glissant du prix de clôture sur 20
  séances (fenêtre PLEINE requise, comme #89/#111 : `has_full`).
- Titre en rebond rapide au jour t si `close(t) >= 1.10 *
  RollingLow_20(t)` (seuil ABSOLU +10% depuis le plus bas 20j récent).
- `Breadth_Rebound(t)` = fraction des titres COTÉS ce jour-là (prix du
  jour fini, dénominateur = tous les titres listés, même convention que
  #89/#111) en rebond rapide.
- Porte active si `Breadth_Rebound(t) ≥` sa médiane glissante 252j (même
  convention que #99/#100/#104/#109/#111/#112).
- Position : `clip(20%/vol_réalisée_20j(t-1), 1.0, 2.0x)` si porte
  active, sinon 1.0x (mécanisme hiérarchique identique à toute la
  famille).
- **Coûts** : 5 bps par unité de turnover.
- **Référence** : Buy & Hold sur NDX (`nasdaq100_daily.txt`).
- Échantillon restreint à la période où le signal titre-par-titre est
  disponible (leçon #77/#89), comme tous les membres de cette famille.

## Critère de succès RENFORCÉ (pré-enregistré, niveau 1)

Sharpe annualisé net de coûts ET rendement total net de coûts
simultanément > Buy&Hold. n_trials=1 pour ce backtest individuel.

## Batterie de validation renforcée (Règle 9, SI PASS niveau 1)

`scripts/nonml_pass_validation_battery.py rebound_speed_breadth_vol_
targeting_overlay`, n_trials=taille totale du backlog (jamais 1).

## Robustesse prévue (SI PASS niveau 1)

Grille de perturbation non-tunable : CAP ∈ {1.5x, 2.0x, 2.5x, 3.0x} et
fenêtre de vol ∈ {15j, 20j, 25j, 30j} — le seuil de rebond +10% et la
fenêtre 20j ne sont PAS retunés (paramètres de définition de
l'hypothèse).

## Anti-cheat

Ce fichier committé avant
`nonml_rebound_speed_breadth_vol_targeting_overlay_backtest.py`,
vérification via
`nonml_anti_cheat_check.py rebound_speed_breadth_vol_targeting_overlay`.
