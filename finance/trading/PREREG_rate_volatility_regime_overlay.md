# Pré-enregistrement — Régime de VOLATILITÉ des taux courts (DGS3MO), overlay coupé/levé

**Committé AVANT tout calcul.** Cycle #178 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Distinct du NIVEAU des taux courts (#175, FAIL net, mécanisme
contre-productif) et de la PENTE de la courbe (#44/#134/#149) déjà
testés : l'incertitude sur la TRAJECTOIRE des taux (mesurée par la
volatilité des variations quotidiennes de DGS3MO) pourrait être un
signal de régime distinct — une incertitude de politique monétaire
élevée est documentée dans la littérature comme associée à une prime de
risque actions plus élevée (aversion au risque accrue), justifiant une
exposition réduite pendant ces phases.

## 2. Marchés testés (figés, identiques au #175)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX), même prudence de
non-indépendance que tout signal basé sur une série macro US unique.

## 3. Mécanisme (figé, réutilisation stricte Règle 7 de la structure du #169)

- Signal : `rate_diff(t) = DGS3MO(t) - DGS3MO(t-1)` (variation
  quotidienne brute), puis `rate_vol(t) = std(rate_diff sur les 63
  dernières séances)` (fenêtre glissante 63j, cohérente avec le choix du
  #175 pour tout signal macro de ce backlog). Alignement causal :
  `rate_vol` est décalé d'un jour (`shift(1)`) avant utilisation dans la
  décision, même convention `ffill+shift(1)` que la Règle 10 des
  #142/#166 et le #175.
- Seuils : **terciles EXPANDING** (33,33 % et 66,67 %) calculés sur tout
  l'historique de `rate_vol` déjà connu au jour de la décision — même
  technique que le #169 (zéro paramètre de fenêtre de percentile à
  choisir).
- **BURN_IN = 252 séances** supplémentaires après la disponibilité du
  premier `rate_vol` avant de commencer à trader (stabilité de
  l'estimation des terciles, même convention que le #169).
- `position(t) = 0.5x` si `rate_vol(t)` dans le tercile SUPÉRIEUR
  (incertitude élevée), `2.0x` si tercile INFÉRIEUR (calme), `1.0x` si
  tercile intermédiaire. CUT=0.5x et CAP=2.0x réutilisés tels quels
  (valeurs déjà établies aux #175/#176/#169). Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que le #175)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (une fenêtre de volatilité fixée par cohérence avec le
#175, des terciles expanding sans paramètre libre, un critère
multi-marché, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme le #175 (niveau), la volatilité des taux pourrait mal
   coïncider avec les régimes de marché pertinents — l'incertitude de
   taux peut culminer PENDANT une crise déjà bien avancée (le plancher
   0,5x arrive alors trop tard) ou PRÉCÉDER un rallye de soulagement
   post-crise (le plancher coupe alors une phase de reprise).
2. La fenêtre glissante 63j peut réagir avec retard à un choc de
   volatilité soudain (contrairement à un signal de niveau plus direct).
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
