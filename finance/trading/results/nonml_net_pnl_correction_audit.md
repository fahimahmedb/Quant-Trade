# Audit indépendant — correction de `net_pnl` (#445)

Point 4 du critère pré-enregistré : **recalculer les groupes de doublons sans
réutiliser la fonction corrigée**. Cet audit réimplémente la reconstruction
depuis les `.npz`, avec sa propre règle — *un P&L déjà net se lit tel quel, un
P&L brut se lit net de son turnover* — et **n'importe pas** `net_pnl`.

## Contrôle 1 — le diff est-il confiné aux lignes annoncées ?

- insertions : **0** — suppressions : **3**
- conforme au régime annoncé (0 insertion, 3 suppressions) : **OUI**

## Contrôle 2 — la branche fautive a-t-elle disparu ?

- `"candidat+turnover"` absent du source : **OUI**
- lecture directe `"candidat seul"` présente : **OUI**

## Contrôle 3 — lecture exacte, mesurée indépendamment

Écart entre la reconstruction **de cet audit** et `pnl_candidate` brut pour
`dollar_neutral_composite_pit` : **0.0e+00**.

## Contrôle 4 — les groupes de doublons

Groupes trouvés par la reconstruction **indépendante** : **3**.

- `etape_D_overlay_optimized`, `nonml_etape_d_garch_defensive_overlay`
- `nonml_leaders_trend_union_overlay`, `nonml_sma200_leaders_overlay`
- `nonml_leaders_trend_union_overlay_pit_universe`, `nonml_sma200_leaders_overlay_pit_universe`

Groupes listés par le rapport du balayage : **3**.

**Partitions identiques : OUI** — comparaison des
ensembles de noms, pas seulement des effectifs : deux partitions distinctes
peuvent avoir le même nombre de groupes.

## Verdict de l'audit

**CONFORME** — la correction fait ce qu'elle
annonce, et une reconstruction écrite indépendamment retrouve les mêmes
groupes de doublons.

### Ce que cet audit ne prouve pas

Il partage avec le balayage la **convention** « `pnl_candidate` est déjà net ».
Si cette convention était fausse, les deux se tromperaient ensemble. Elle a été
établie au #444 par **lecture des scripts producteurs**, pas par accord entre
deux reconstructions — et c'est cette lecture, pas cet audit, qui la fonde.
