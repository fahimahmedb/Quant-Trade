# Pré-enregistrement — Cycle électoral combiné (année 3 levée + année 2 coupée), overlay continu

**Committé AVANT tout calcul.** Cycle #179 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les #30/#176

Le #30 (année 3 pré-électorale, `position=2,0x`) est **PASS (5/5)**. Le
#176 (année 2 mid-term, `position=0,5x`) est **PASS (4/4)**. Ce cycle
teste si les COMBINER en une seule stratégie continue sur les 4 années
du cycle électoral apporte un gain supplémentaire — hypothèse
opérationnelle simple : moins de transitions de position que d'exécuter
les deux séparément en parallèle (impossible de toute façon, un seul
portefeuille), et un profil de risque/rendement lissé sur le cycle
complet plutôt que deux fenêtres isolées.

**Ce n'est PAS un nouvel essai déguisé** : les deux composantes ont déjà
leur verdict PASS individuel, établi indépendamment et pré-enregistré
avant ce cycle. Ici, aucun paramètre n'est retouché (mêmes seuils 2,0x
et 0,5x, mêmes détections calendaires) — seule la combinaison en une
politique continue est testée.

## 2. Marchés testés (figés, intersection des #30/#176)

4 marchés : NDX, Russell 2000, S&P 500, DAX (Composite exclu, comme au
#176 — historique insuffisant pour l'année de mid-term). Même prudence
de non-indépendance que les #30/#176.

## 3. Mécanisme (figé, réutilisation stricte Règle 7)

- `position(t) = 2.0x` si année pré-électorale (`preelection_mask` du
  #30, `(année+1)%4==0`).
- `position(t) = 0.5x` si année de mid-term (`midterm_mask` du #176,
  `année%4==2`).
- `position(t) = 1.0x` les deux autres années (élection et post-élection).
- Aucune valeur retouchée (2,0x et 0,5x copiés à l'identique des #30/#176).
  Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que le #176)

> **PASS si et seulement si ≥3 des 4 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (combinaison de deux mécanismes déjà validés
séparément, aucun paramètre nouveau, un critère multi-marché).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le gain de chaque composante étant déjà positif indépendamment, la
   combinaison DEVRAIT en principe préserver au moins la moyenne des
   deux effets — un FAIL ici serait surprenant et signalerait une
   interaction négative inattendue entre les deux fenêtres (ex. coûts de
   transition supplémentaires aux changements d'année qui n'existaient
   pas en isolant chaque fenêtre sur son propre historique).
2. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
