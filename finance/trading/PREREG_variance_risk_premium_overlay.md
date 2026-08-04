# Pré-enregistrement — Prime de risque de variance (VIX − vol réalisée), overlay défensif

**Committé AVANT tout calcul.** Cycle #191 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

Le VIX (volatilité implicite du S&P 500, CBOE) surestime en moyenne et
de façon systématique la volatilité future réalisée — écart connu sous
le nom de "prime de risque de variance" (variance risk premium, VRP),
documenté notamment par Bekaert & Hoerova (2014) et Carr & Wu (2009).
Une prime COMPRESSÉE ou INVERSÉE (vol réalisée qui rattrape ou dépasse
la vol implicite) signale historiquement un régime d'aversion au risque
élevée plutôt que la complaisance habituelle. Distinct du #130 (niveau
VIX SEUL comme porte d'un mécanisme hiérarchique vol-targeting,
FAIL — Sharpe +0,51→+0,50) : ici le signal est l'ÉCART entre volatilité
implicite et volatilité réalisée, jamais testé sous cette forme dans ce
backlog. Design PUREMENT DÉFENSIF (jamais de levier), cohérent avec les
#175/#178/#186/#187 (rate-signal family) plutôt qu'avec le mécanisme
hiérarchique à deux sens du #130.

## 2. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX). Le VIX est un
indicateur de peur GLOBAL largement utilisé au-delà du seul S&P 500
(risk-off international corrélé) — appliqué aux 5 marchés comme les
autres signaux macro de ce backlog (#175/#178/#186/#187), pas seulement
au marché d'origine du VIX.

## 3. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Vol réalisée : `RV_ann(t) = std(rendements log quotidiens, fenêtre
  glissante VOL_WINDOW=20j) × sqrt(252) × 100`, **VOL_WINDOW=20 réutilisé
  à l'identique** de la famille vol-targeting (#9/#31/#46/#47/#58…),
  Règle 7 — aucun nouveau paramètre de fenêtre. `RV_lag(t) = RV_ann(t-1)`
  (même convention `vol_lagged` que ces cycles).
- VIX : alignement causal `ffill+shift(1)` identique aux #130/#175/#178/
  #186/#187 pour la série FRED (`data/vixcls_daily.csv`), Règle 7.
- `VRP(t) = VIX_lag(t) − RV_lag(t)` (les deux termes déjà décalés d'un
  jour, donc `VRP(t)` est connu à la clôture du jour t-1).
- Seuil : **tercile EXPANDING** de `VRP(t)` (technique établie aux
  #169/#177/#183, aucune fenêtre fixe à choisir) calculé uniquement sur
  l'historique disponible à chaque date.
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique** des
  #175/#176/#178/#186/#187, aucun nouveau paramètre) si `VRP(t)` est
  dans son tercile expanding le PLUS BAS (prime compressée/inversée,
  aversion au risque élevée), `1,0x` sinon. **Jamais de levier** —
  design intentionnellement défensif pur, cohérent avec la leçon des
  #175/#186 (le levier bidirectionnel sur un signal macro est
  contre-productif). Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que les #175/#178/#186/#187)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, une fenêtre de vol
réutilisée, un critère multi-marché figé, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le VIX étant une mesure PROSPECTIVE de 30 jours, il intègre déjà
   souvent une anticipation de hausse de la vol réalisée — la
   compression de la prime pourrait donc arriver APRÈS le pic de stress
   plutôt qu'avant, comme observé pour l'inversion de courbe des taux au
   #187 (signal économiquement valide mais arrivant trop tard pour un
   mécanisme statique sans délai).
2. Comme aux #175/#178/#186/#187, un design purement défensif sans
   levier compensatoire limite structurellement le rendement total.
3. Le VOL_WINDOW=20j (vol réalisée) et le VIX (horizon implicite 30j)
   ne sont pas exactement sur le même horizon — un décalage structurel
   pourrait ajouter du bruit au signal VRP sans que cela constitue un
   bug (limite reconnue à l'avance, pas une correction post-hoc).
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
