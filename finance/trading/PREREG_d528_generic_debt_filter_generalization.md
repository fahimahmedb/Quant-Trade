# Pré-enregistrement — généralisation du filtre dette-générique de D528

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de RÉPARATION**, première piste de la file
ouverte au #530 (« le filtre dette générique de D528, à généraliser »).

## La faille trouvée au #530, non corrigée sur place par déclaration

Le #530 a montré que le filtre d'exclusion codé pour la seule phrase
exacte « rétractés sur mesure » ne couvre pas la narration propre d'un
cycle décrivant sa **propre** découverte d'une collision — au #528 :
« collision avec la phrase générique de la « Dette restante » listant
des numéros de cycle rétractés — **pas une discussion du script**. »
Cette phrase contient le mot « rétracté » à proximité de
`battery_backfill_lot_audit.py` sans être la phrase générique visée
par le filtre actuel. Le #530 a **délibérément refusé** de corriger
sur la base de son propre résultat (portée déclarée à l'avance) —
cette dette attendait un cycle de réparation séparé.

## Où le filtre est dupliqué (4 sites de production)

`grep -rl "rétractés sur mesure" finance/trading/scripts/*.py` (hors
le script de mesure du #530 lui-même, qui n'est pas un site de
production et reste inchangé) trouve **4** fichiers :

1. `nonml_hardcoded_figures_479_remainder_closure_backtest.py` (#528)
2. `nonml_hardcoded_figures_479_remainder_closure_audit.py` (#528)
3. `nonml_verdict_dicts_origin_staleness_screen_backtest.py` (#529)
4. `nonml_verdict_dicts_origin_staleness_screen_audit.py` (#529)

## Le risque actuel, mesuré avant toute modification

Les 4 scripts, ré-exécutés **aujourd'hui** sur le backlog déjà étendu
aux #528/#529/#530, restent **tous PASS inchangés** (baseline capturée
avant modification, ci-dessous) — la faille du #530 est **latente**,
pas encore active dans ces 4 sites précis (fenêtres/candidats
légèrement différents de celle du #530). La réparation est donc
**préventive** : elle doit préserver ces 4 verdicts identiques, pas
les changer.

| Script | Sortie baseline (avant modification) |
|---|---|
| #528 backtest | `PASS — nouvelles_retractations=0, non_tranches=0` |
| #528 audit | `PASS — n_marqueurs_reels=0, v_absent=True` |
| #529 backtest | `PASS — entrées=10, contradictions=0` |
| #529 audit | `PASS — candidats_confirmes=8, accord_backtest=True, dicos_touches=False` |

## Le protocole

1. **Ajouter un second marqueur d'exclusion**, `"pas une discussion du
   script"`, à côté de `"rétractés sur mesure"` dans les 4 sites — un
   littéral choisi parce qu'il apparaît **exactement 2 fois** dans tout
   le backlog (`grep -c`), toutes deux dans une narration méta décrivant
   une collision déjà exclue (#528 original, #530 qui le cite) — **aucun
   risque connu de sur-exclusion d'un cas substantiel**, vérifié avant
   modification.
2. **Ré-exécuter les 4 scripts** après la modification, confirmer que
   les 4 sorties sont **identiques** à la baseline ci-dessus (aucune
   régression).
3. **Script de régression dédié**, réutilisant l'occurrence exacte
   trouvée au #530 (`battery_backfill_lot_audit.py`, section #528,
   marqueur « rétracté », distance 151) : prouver que le filtre
   **avant** la modification ne l'excluait pas, et qu'**après**, il
   l'exclut — la preuve directe que la réparation comble la faille
   identifiée, pas seulement qu'elle ne casse rien.
4. **Diff borné** : seule la ligne d'exclusion (`if "rétractés sur
   mesure" in ... :` → `if any(m in ... for m in (...)):`) est modifiée
   dans chacun des 4 fichiers, rien d'autre.

## Critère de succès — chiffré

1. Les **4** sites de production identifiés et listés.
2. Baseline des 4 sorties capturée **avant** toute modification.
3. Les **4** sorties **identiques** après modification (0 régression).
4. Le script de régression dédié prouve l'écart avant/après sur
   l'occurrence exacte du #530.
5. Diff borné à la ligne d'exclusion dans chacun des 4 fichiers.

> **PASS** = les cinq points. **FAIL** = un seul manque — en
> particulier, toute régression sur les 4 sorties existantes serait un
> **FAIL immédiat**, quelle que soit la validité du point 4.

## Prédictions — falsifiables

1. Les 4 sorties restent **identiques** avant/après (0 régression).
2. Le script de régression dédié montre l'écart avant (non exclu) /
   après (exclu) sur l'occurrence du #530.
3. Le diff total des 4 fichiers de production est de **4 lignes
   modifiées, 0 ligne ajoutée/retirée ailleurs**.

## Ce que ce cycle ne fait pas

- Il ne **réexamine** aucun verdict `V`/`VERDICTS` des 6 dictionnaires
  déjà clos (#522-#529).
- Il ne **corrige** pas le lift < 3 du #530 (limite de fond du filtre
  de proximité, déjà documentée, pas un bug).
- Il n'**exécute** aucun script de marché.

## Simulation 300 € et robustesse

**Sans objet** : cycle de réparation de dépôt, aucune position, aucun
paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si une régression apparaît
   (auquel cas la modification serait retirée, pas maintenue).
2. **Chaque étape adossée à une sortie de commande citée.**
3. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
