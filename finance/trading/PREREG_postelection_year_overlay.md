# Pré-enregistrement — Année 1 post-électorale (2e plus faible selon Hirsch), overlay coupé

**Committé AVANT tout calcul.** Cycle #180 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants

Complète la théorie de Hirsch (1986) sur les 4 années du cycle
présidentiel : année 3 pré-électorale (la plus forte, #30 PASS 5/5),
année 2 mid-term (la plus faible, #176 PASS 4/4), et maintenant **année 1
post-électorale** (l'année suivant l'élection présidentielle,
généralement identifiée dans la littérature comme la **2e plus faible**
— nouvelle administration, mesures d'austérité/ajustement post-électoral
fréquentes). Teste si cette 2e fenêtre faible ajoute encore de la valeur
à la combinaison déjà validée #30+#176 (#179).

## 2. Marchés testés (figés, identiques aux #176/#179)

4 marchés : NDX, Russell 2000, S&P 500, DAX (Composite exclu, historique
insuffisant). Même prudence de non-indépendance que les #30/#176/#179.

## 3. Mécanisme (figé)

- Détection 100% data-driven : `postelection_mask(t) = (année(t) % 4) == 1`
  (élection présidentielle en années divisibles par 4 ; l'année suivante
  a pour reste 1).
- `position(t) = 0.5x` pendant l'année post-électorale, `1.0x` sinon.
  **CUT=0.5x réutilisé À L'IDENTIQUE** des #175/#176/#178 (pas une
  nouvelle valeur inventée pour refléter une faiblesse "moindre" que le
  mid-term — cela introduirait un paramètre non justifié ; le test porte
  sur l'EXISTENCE d'un edge à ce degré de coupure déjà établi, pas sur
  son calibrage optimal). Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que le #176)

> **PASS si et seulement si ≥3 des 4 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (une fenêtre calendaire fixée avant calcul, un plancher
réutilisé du #175/#176, un critère multi-marché, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Si l'année post-électorale est réellement "2e plus faible" (moins
   faible que le mid-term), couper à 0,5x pourrait être une réduction
   trop agressive par rapport à la faiblesse réelle — un FAIL ici
   n'invaliderait pas nécessairement l'existence d'un edge plus faible,
   seulement l'ampleur de coupure testée (déclaré à l'avance, pas un
   prétexte pour retester avec un autre plancher dans ce même cycle).
2. Comme aux #30/#176, un petit nombre de cycles (9-10) limite la
   puissance statistique.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
