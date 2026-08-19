# Pré-enregistrement — les 11 justifications RÉPARABLE du #485 jamais relues

**Écrit et committé AVANT toute mesure.** `n_trials` continue le compte
global (aucune remise à 1). **Cycle de VÉRIFICATION**, première piste de
la file ouverte au #517.

## Ce que le #517 a établi

Le tableau des **5** justifications IRRÉPARABLE du #485 est entièrement
couvert depuis le #493 (0 non vérifiée). Mais le #485 classait aussi
**12** figures RÉPARABLE, chacune avec sa propre justification écrite à
la main (`V` dans `nonml_irreparable_figures_census_backtest.py`,
lignes 61-115). **Une seule** — `nonml_battery_backfill_lot_audit.py` —
a été relue depuis (#511), et sa justification s'est révélée **fausse**
(reclassée IRRÉPARABLE). **Les 11 autres n'ont jamais été relues de la
même façon.**

## La population — les 11, nommées et citées verbatim

Extraite du dictionnaire `V` du script du #485 (ligne de code, pas de
mémoire) :

| Script | Justification du #485, à éprouver |
|---|---|
| `nonml_duplicate_sweep_coverage_audit.py` | « `n_missing` interpolé, la ventilation porte sur l'ensemble déjà construit » |
| `nonml_content_defined_magnitudes_audit.py` | « l'audit énumère les importateurs pour les examiner » |
| `nonml_content_defined_magnitudes_backtest.py` | « mesure sur objets git que le script lit déjà » *(+ 1 ligne signalée par le #485 lui-même comme une estimation en prose, non réparable)* |
| `nonml_coverage_wording_fix_audit.py` | « un `glob` — le cas le plus trivialement réparable » |
| `nonml_dsr_corrected_trials_backtest.py` | « le résultat de la fusion que le script opère » |
| `nonml_idempotence_famille_capable_backtest.py` | « se dérive de `v1.FAUTIFS_463`/`v1.SAINS_463`, importés » |
| `nonml_idempotence_lot2_backtest.py` | « le script construit `tous` et `DEJA` » |
| `nonml_marker_emitter_crossing_backtest.py` | « le compte que ce script calcule (`douteux`) » |
| `nonml_orphans_interrupted_or_lost_backtest.py` | « le script calcule `len(ent) + len(orp)` » |
| `nonml_report_idempotence_backtest.py` | « rapport de l'univers figé #443-#460 au total, lu par `glob` » |
| `nonml_reproducibility_campaign_v2_audit.py` | « un `glob` sur `results/*.npz` » |

`nonml_battery_backfill_lot_audit.py` (12ᵉ, déjà relue et tombée au
#511) est **explicitement exclue** — elle n'est pas rejugée ici.

## Le protocole — mécanique d'abord, lecture ensuite, même forme qu'au #493

Pour chacun des 11, **avant tout verdict** :

1. **la preuve littérale citée par la justification** (nom de variable,
   appel `glob`/`len`/import) est cherchée **dans le code source réel**
   du script cible — pas dans le souvenir de sa lecture au #485.
2. **verdict** :
   - **JUSTIFICATION EXACTE** — la preuve existe littéralement, telle
     que décrite ;
   - **JUSTIFICATION FAUSSE, VERDICT SURVIVANT** — la preuve citée est
     absente ou différente, mais le script reste réparable pour une
     autre raison, **qui doit être énoncée avec sa propre ligne de
     code** ;
   - **JUSTIFICATION FAUSSE, VERDICT À REVOIR** — ni la preuve citée ni
     aucune autre ne rend la figure réparable : le compte des 12
     réparables **baisse**.
3. Le cas particulier de `content_defined_magnitudes_backtest.py` est
   examiné **en deux parties**, comme le #485 l'avait lui-même annoncé :
   la mesure sur objets git (réparable ou non) et la ligne d'estimation
   en prose (déjà signalée non réparable par le #485 — **non rejugée
   ici**, seulement rappelée).

**Aucun verdict ne sera écrit sans la ligne de code qui le fonde.**

## Critère de succès — chiffré, il porte sur le procédé

1. Les **11** nommés, avec la justification citée verbatim pour chacun.
2. **11/11** examinés à la main, verdict **et** ligne de code à l'appui.
3. Tout verdict renversé (« VERDICT À REVOIR ») publié comme tel, et le
   compte des réparables du #485 **corrigé à la baisse** dans le rapport
   si applicable.
4. Le cas `content_defined_magnitudes_backtest.py` traité en deux
   parties distinctes, sans rejuger la partie déjà tranchée par le #485.
5. `nonml_battery_backfill_lot_audit.py` **exclu explicitement** — non
   rejugée.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 1** des 11 a une justification **fausse** (comme au #493, au
   #511, et comme trouvé pour la 12ᵉ figure historique du même
   tableau).
2. **Au plus 2** verdicts réparables tombent (basculent en « VERDICT À
   REVOIR ») — la majorité résiste, comme au #493 (1 sur 4 tombé).
3. `nonml_coverage_wording_fix_audit.py` — désigné par le #485 lui-même
   comme *« le cas le plus trivialement réparable de la liste »* — reçoit
   le verdict **JUSTIFICATION EXACTE**.

Si la prédiction 2 est réfutée et que plus de 2 tombent, **je publierai
le compte réel des réparables comme dégradé**, sans amortir la mesure
dans un langage plus favorable après coup.

## Ce que ce cycle ne fait pas

- Il ne **répare** rien, ne modifie aucun script de stratégie.
- Il n'**exécute** aucun script de marché : lecture du disque et du code
  source des 11 cibles uniquement, **aucun effet de bord**.
- Il ne **rejuge pas** `nonml_battery_backfill_lot_audit.py` (#511) ni
  les 5 justifications IRRÉPARABLE (#488, #493).
- Il ne **tranche pas** `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification bibliographique/code, aucune
position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si plusieurs verdicts tombent.
2. Population, protocole et forme des verdicts **inchangés** après
   mesure.
3. **Chaque verdict adossé à une ligne de code citée**, jamais à une
   impression.
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
