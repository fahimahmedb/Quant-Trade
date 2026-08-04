# Pré-enregistrement — Régime DISCRET de volatilité PRÉVUE GJR-t (tercile calme), overlay binaire

**Committé AVANT tout calcul.** Cycle #169 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Tous les mécanismes testés jusqu'ici avec la vol PRÉVUE GJR-t (#165, #166,
#168) utilisent une formule CONTINUE (`clip(cible/vol_prévue, ..., CAP)`) :
l'exposition varie en proportion inverse du niveau de vol. Ce cycle teste
un mécanisme structurellement différent : un **régime binaire discret**
— levier fixe **si et seulement si** la vol prévue est dans son TERCILE
historique le plus BAS (régime calme anticipé), 1.0x sinon. C'est
l'inverse conceptuel de deux cycles déjà FAIL avec la vol RÉALISÉE : le
#9 (overlay levé en régime de vol réalisée CALME, FAIL 2/5) et le #31
(overlay levé en régime de vol réalisée ÉLEVÉE, FAIL 0/5) — jamais testé
avec la vol PRÉVUE, qui capte le clustering AVANT qu'il ne se matérialise
(contrairement au proxy réalisé, toujours en retard).

## 2. Marchés testés (figés, même exclusion qu'au #166/#168)

4 marchés : NDX, S&P 500, Russell 2000, DAX (Composite exclu, SPA GJR-t
non validé dessus à l'Étape C, `CLAUDE.md`).

## 3. Mécanisme (figé, aucun paramètre libre après ce document)

- Prévision : `walk_forward_vol_forecast` de `finance/src/overlay.py`
  (T0=750, REFIT_EVERY=21, GJR-t), IDENTIQUE au #165/#166/#168.
- Seuil du tercile : **percentile EXPANDING** (pas de fenêtre glissante à
  choisir — zéro paramètre de fenêtre supplémentaire, Règle 2) calculé sur
  tout l'historique de prévisions déjà connu au jour de la décision :
  `seuil(t) = percentile_33,33(vol_fcst[T0 : t+1])`. Comme `vol_fcst[t]`
  est lui-même construit avec l'information disponible en t-1 (documenté
  et vérifié au #165), inclure `vol_fcst[t]` dans le calcul du seuil ne
  crée AUCUNE fuite : toutes les prévisions utilisées pour estimer le
  seuil sont déjà connues au moment de la décision pour la période t.
- **BURN_IN = 252 observations supplémentaires** après T0 avant de
  commencer à trader (fenêtre testable : `t ≥ T0 + 252`), pour que
  l'estimation du tercile ne soit pas basée sur une poignée de points —
  valeur choisie par cohérence avec les fenêtres de 252j déjà utilisées
  ailleurs dans le backlog (#4, #37), pas ajustée après résultat.
- Formule : `position(t) = 2.0x si vol_fcst(t) ≤ seuil(t), 1.0x sinon`.
  CAP=2.0x réutilisé tel quel (valeur standard de toute la famille
  vol-targeting du backlog, #43/#46/#47/#165/#166/#168), aucun retuning.
- Coûts 5 bps.

## 4. Critère de succès (figé, même seuil qu'au #166/#168)

> **PASS si et seulement si ≥3 des 4 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (une architecture, un seuil de tercile expanding sans
paramètre libre, un critère multi-marché).

## 5. Engagement Règle 10 (déclaré à l'avance)

Si PASS sur un marché : décomposition Règle 10 (financement DGS3MO réel
des deux côtés) avant toute communication comme edge authentique — la
position peut dépasser 1.0x (jusqu'à 2.0x en régime calme), donc une
fraction est empruntée une partie du temps, exactement le mécanisme qui a
fait échouer le #166 sur Russell 2000/S&P 500.

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le régime calme anticipé par GJR-t pourrait ne pas coïncider avec un
   bon ratio rendement/risque prospectif — la littérature Moreira & Muir
   suggère que c'est le cas pour l'exposition CONTINUE, mais un seuil
   discret pourrait introduire un effet de bord (juste sous/au-dessus du
   tercile) qui dilue le signal.
2. Comme au #166/#168, même un PASS pourrait ne pas survivre au
   financement réaliste (Règle 10) hors NDX.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
