# Pré-enregistrement — Année 4 électorale (force modérée selon Hirsch), overlay levé modérément

**Committé AVANT tout calcul.** Cycle #181 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et lien avec les cycles existants — leçon du #180 appliquée ici

Dernière fenêtre du cycle de Hirsch (1986) jamais testée dans ce
backlog : l'année de l'élection présidentielle elle-même (`année%4==0`),
caractérisée comme de force **modérée** — ni la plus forte (année 3,
#30, `CAP=2,0x`) ni la plus faible (année 2 mid-term, #176,
`CUT=0,5x`).

**Leçon explicitement appliquée du #180** : réutiliser un calibrage
EXTRÊME déjà établi (2,0x ou 0,5x) pour une fenêtre qualifiée de
"modérée" reproduirait exactement l'erreur de calibrage qui a fait
échouer le #180 (plancher 0,5x trop agressif pour une fenêtre "2e plus
faible", pas "la plus faible"). Décision prise ICI, **avant tout
calcul** : utiliser **CAP_MODÉRÉ = 1,5x**, la moyenne arithmétique exacte
entre le neutre (1,0x) et le CAP fort déjà établi (2,0x) — un choix
PRINCIPIEL (point médian entre deux ancres déjà existantes dans ce
backlog), pas un nouveau paramètre ajusté après résultat, et surtout pas
choisi pour maximiser les chances de succès (le point médian est le
choix le plus neutre possible étant donné la qualification "modérée").

## 2. Marchés testés (figés, identiques aux #176/#179/#180)

4 marchés : NDX, Russell 2000, S&P 500, DAX (Composite exclu). Même
prudence de non-indépendance que les #30/#176/#179/#180.

## 3. Mécanisme (figé)

- Détection 100% data-driven : `election_mask(t) = (année(t) % 4) == 0`
  (année de l'élection présidentielle elle-même).
- `position(t) = 1.5x` pendant l'année électorale, `1.0x` sinon. Coûts
  5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que les #176/#179/#180)

> **PASS si et seulement si ≥3 des 4 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (une fenêtre calendaire fixée avant calcul, un CAP
modéré choisi par principe AVANT tout calcul — pas un balayage, un
critère multi-marché).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Même avec un calibrage "moyen" plutôt qu'extrême, l'année électorale
   pourrait ne porter aucun edge net de coûts détectable — Hirsch la
   qualifie de modérée, pas nécessairement d'exploitable au sens du
   critère renforcé de ce backlog (rendement net de coûts).
2. L'incertitude électorale elle-même (issue du scrutin inconnue jusqu'à
   novembre) pourrait dominer toute tendance saisonnière moyenne,
   rendant le signal plus bruyant que les années 2/3 déjà testées.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
