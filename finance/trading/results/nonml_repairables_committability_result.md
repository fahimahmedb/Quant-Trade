# Les **13 réparables**, sous le critère de **committabilité** (pré-enregistré)

Le **#499** a tenté la réparation du 13ᵉ. Elle était **parfaite** —
**0 ligne** de diff sur les valeurs — et elle a **échoué** : régénérer le
rapport en réécrivait la **dérive du dépôt**.

> **Un chiffre dérivable n'est pas pour autant réparable par un geste
> borné.** Le compte « 13 réparables » mesure la **dérivabilité** ;
> personne n'avait mesuré la **committabilité**.

## La règle, citée verbatim — statique, sans exécution

> - **NC1** — le script déclenche l'une des primitives **P1, P2, P9, P10** du #497 (règle **importée**, non
>   recopiée) : le régénérer déclencherait une **cascade** ;
> - **NC2** — il appelle `glob`, `iterdir`, `listdir`, `rglob`, `scandir` sur `scripts/` ou
>   `results/`, **ou** invoque `git` : sa sortie **bouge avec le dépôt**.

| Classe | Définition |
|---|---|
| **NC1** | exécute un tiers |
| **NC2** | ne l'exécute pas, mais **lit l'état courant** du dépôt |
| **C** | ni l'un ni l'autre — **candidat** committable |
| **?** | script ou rapport introuvable |

## La population, dérivée par code

- « réparable » lus dans le recensement du #485 : **12**
- requalifiés au #493 (justification fausse) : **1**
- **population** : **13**

## Les quatre classes

| Classe | Nombre | Part |
|---|---|---|
| **NC1** | **2** | **15,4 %** |
| **NC2** | **9** | **69,2 %** |
| **C** | **2** | **15,4 %** |
| **?** | **0** | **0,0 %** |

- **non committables** (NC1 + NC2) : **11** sur **13**

## Le contrôle : la cible du #499

`nonml_reproducibility_campaign_v3_lot2_audit.py` est **connue non committable par l'expérience**. Si la
règle statique la classait **C**, la règle serait fausse.

- classe rendue : **NC2**
- motifs d'état courant : `git`, `glob(…)`

> **Le contrôle passe.** La règle statique retrouve, sans rien
> exécuter, ce que le #499 avait payé une exécution complète pour
> découvrir.

## Le détail, script par script

| Script | Classe | Motif |
|---|---|---|
| `nonml_battery_backfill_lot_audit.py` | **C** | — |
| `nonml_coverage_wording_fix_audit.py` | **C** | — |
| `nonml_content_defined_magnitudes_audit.py` | **NC1** | P1 |
| `nonml_report_idempotence_backtest.py` | **NC1** | P1 |
| `nonml_content_defined_magnitudes_backtest.py` | **NC2** | `git` |
| `nonml_dsr_corrected_trials_backtest.py` | **NC2** | `glob(…)` |
| `nonml_duplicate_sweep_coverage_audit.py` | **NC2** | `glob(…)` |
| `nonml_idempotence_famille_capable_backtest.py` | **NC2** | `git`, `glob(…)` |
| `nonml_idempotence_lot2_backtest.py` | **NC2** | `git`, `glob(…)` |
| `nonml_marker_emitter_crossing_backtest.py` | **NC2** | `glob(…)` |
| `nonml_orphans_interrupted_or_lost_backtest.py` | **NC2** | `git`, `glob(…)` |
| `nonml_reproducibility_campaign_v2_audit.py` | **NC2** | `glob(…)` |
| `nonml_reproducibility_campaign_v3_lot2_audit.py` | **NC2** | `git`, `glob(…)` |

## Les candidats

- effectif : **2**

- `nonml_battery_backfill_lot_audit.py`
- `nonml_coverage_wording_fix_audit.py`

> **« Candidat » n'est pas « committable ».** La règle est une
> **borne supérieure** : un script peut dériver pour une raison
> qu'elle n'énumère pas. Seule l'exécution trancherait, et le #499 a
> montré ce qu'elle coûte. **Le mot était choisi avant la mesure
> pour qu'il ne puisse pas être durci après.**

## Un troisième angle mort — découvert, **non absorbé**

- réparables dépendant de `sys.argv` : **2**
- dont **classés candidats** par ma règle : **1**

- `nonml_coverage_wording_fix_audit.py`

> Un script qui attend des **arguments de ligne de commande** ne se
> régénère pas seul : il lui faut des fichiers « avant » qui
> n'existent peut-être plus. **C'est une troisième cause de
> non-committabilité, que ma règle ne nomme pas.**
>
> **Elle est enregistrée comme angle mort, pas absorbée après coup** —
> la règle a été figée avant mesure, et l'élargir maintenant serait
> la dérive refusée aux #496 et #497. Le compte de candidats reste
> **2** ; le lecteur sait désormais que **1**
> d'entre eux est fragile pour une raison de plus.

## Ce que ce cycle ne contredit pas

**La dérivabilité mesurée par les #485 et #493 reste vraie.** Ces
chiffres peuvent bien être recalculés par le code qui les entoure. Ce
cycle mesure **autre chose** : la possibilité de **déposer** la
correction sans emporter la dérive du dépôt avec elle.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| la cible du #499 est **NC2** | NC2 | NC2 | **vérifiée** |
| ≥ 8 non committables | ≥ 8 | 11 | **vérifiée** |
| ≥ 1 candidat subsiste | ≥ 1 | 2 | **vérifiée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

> **Ce script est lui-même de classe NC2 par sa propre règle** : il
> balaie `scripts/` et appelle `git`. Il ne prétend donc pas être
> committable — il ne répare rien.

## Critères de succès

1. Règle et quatre classes citées verbatim, règle du #497 importée — **OUI**.
2. Population dérivée par code (**13**), écart publié — **OUI**.
3. Quatre classes comptées et **contrôle du #499 passé** (**NC2**) — **OUI**.
4. Candidats nommés individuellement (**2**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la
> date de son exécution.
