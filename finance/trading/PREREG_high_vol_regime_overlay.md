# Pré-enregistrement — Overlay levé sur régime de vol ÉLEVÉE

**Committé AVANT tout calcul.** Cycle #31 du backlog non-ML. Variante
inverse du cycle #9 (overlay sur vol CALME, FAIL 2/5) : ici on teste le
régime de vol ÉLEVÉE, motivé par le clustering de volatilité déjà
documenté à l'Étape A (effet ARCH massif, ν≈4,8) — la vol élevée
persiste statistiquement, contrairement au niveau de prix (déjà testé et
FAIL aux cycles #13/#22/#24). Hypothèse distincte : on teste la
persistance de la VOLATILITÉ, pas un rebond de PRIX.

## Hypothèse

Le clustering de volatilité (une vol élevée aujourd'hui prédit une vol
élevée demain, effet ARCH validé à l'Étape A) pourrait s'accompagner
d'une prime de risque positive (rendement attendu plus élevé en période
de vol élevée, littérature du "volatility risk premium") suffisante pour
compenser le risque additionnel du levier — à distinguer explicitement
du #13/#22/#24 qui testaient un REBOND DE PRIX après un choc, pas la
persistance de la vol elle-même.

## Définition (fixée ici, avant tout résultat)

- Vol roulante 20j (écart-type des rendements log quotidiens), même
  fenêtre que le #9, calcul strictement causal (vol connue à la clôture
  de t-1, utilisée pour décider la position de t).
- Régime "vol élevée" = vol roulante au jour t-1 dans le **tercile
  supérieur** de la distribution causale (expansive, calculée
  uniquement sur l'historique disponible jusqu'à t-1) — même
  construction causale que le #9, tercile inversé (supérieur au lieu
  d'inférieur).
- Warmup = 252 séances avant tout calcul (même que #9).
- Position = **1.0x en permanence**, SAUF les jours en régime de vol
  élevée où position = **CAP = 2.0x**.
- **Coûts** : 5 bps par unité de changement de position à chaque
  transition.
- **Référence** : Buy & Hold classique.

## Univers et période

Les 5 échantillons déjà figés du projet (`data/*.txt`).

## Critère de succès RENFORCÉ (pré-enregistré)

L'overlay doit battre Buy & Hold **simultanément** en Sharpe annualisé
net de coûts ET en rendement total net de coûts, sur **au moins 4 des 5
marchés**. n_trials=1 (CAP=2.0x cohérent avec tous les cycles
précédents, tercile fixé a priori comme au #9).

## Anti-cheat

Ce fichier committé avant `nonml_high_vol_regime_overlay_backtest.py`,
vérification via `nonml_anti_cheat_check.py high_vol_regime_overlay`.
