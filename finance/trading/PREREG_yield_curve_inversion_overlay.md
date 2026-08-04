# Pré-enregistrement — Inversion de la courbe des taux (DGS10-DGS3MO < 0), overlay défensif

**Committé AVANT tout calcul.** Cycle #187 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

L'inversion de la courbe des taux (taux long < taux court) est l'un des
prédicteurs de récession les plus documentés en macro-finance (chaque
récession américaine depuis 1970 a été précédée d'une inversion
2Y/10Y ou 3M/10Y). Distinct de la PENTE CONTINUE déjà utilisée comme
facteur de DIMENSIONNEMENT dans les mécanismes vol-targeting
(#44/#134/#149, où la pente module une exposition déjà active) : ici,
l'inversion est testée comme signal BINAIRE discret (ON/OFF), jamais
sous cette forme dans ce backlog. Distinct aussi des #175/#186 (régime
de NIVEAU/DIRECTION d'un seul taux, tous deux FAIL avec le même
mécanisme contre-productif) : l'inversion est un signal RELATIF entre
deux taux, pas le niveau ou la direction d'un seul.

## 2. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 3. Mécanisme (figé, design PUREMENT DÉFENSIF — jamais de levier, contrairement aux #175/#186)

- Signal : `spread(t) = DGS10(t-1) - DGS3MO(t-1)`, alignement causal
  `ffill+shift(1)` identique aux #175/#186 pour les deux séries.
- `position(t) = 0,5x` si `spread(t) < 0` (courbe inversée), `1,0x`
  sinon. **CUT=0,5x réutilisé à l'identique** des #175/#176/#186 (aucun
  nouveau paramètre). **Design intentionnellement défensif pur** :
  jamais de levier (contrairement aux #175/#186 qui levaient aussi en
  régime de baisse) — cohérent avec la nature du signal (l'inversion
  prédit un risque accru, pas une opportunité de rendement). Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que les #175/#186)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal binaire relatif entre deux taux déjà en
local, un plancher réutilisé, un critère multi-marché, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. L'inversion de courbe précède historiquement les récessions par un
   délai variable (souvent 12-24 mois) — la période d'inversion
   elle-même peut encore être une phase de marché haussier (le marché
   continue souvent de monter APRÈS l'inversion, avant la récession
   effective) : couper l'exposition dès l'inversion pourrait donc
   arriver trop tôt et coûter du rendement, même si le signal de risque
   est économiquement valide à plus long terme.
2. Comme aux #175/#186, un design purement défensif sans levier
   compensatoire limite structurellement le rendement total, ce qui a
   déjà fait échouer plusieurs mécanismes défensifs de ce backlog par
   sous-dimensionnement (#43, #58).
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
