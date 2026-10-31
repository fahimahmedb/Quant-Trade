# W1 et Mega A — devenirs vérifiés, lot 3

Statut : reconstruction partielle. Les heures sont celles des commits, en UTC. Une intégration Git ou des octets identiques ne prouvent ni activation ni état actuel de la VM.

## Séquence d'intégration du 21 octobre

| Heure UTC | Commit | Source et destination |
|---|---|---|
| 13:04:33 | `5c101f48…` | Port Scientific Memory vers le socle CP079. Modules `scientific_memory.py`, `archaeology.py`, `memory_archaeology_bridge.py`, schéma, catalogue de provenance et tests. `legacy.py` est adapté en préservant les lois de revue de sources plus récentes. |
| 13:09:54 | `6e99ce39…` | Port Data/Evidence/PIT : `schemas/dataset_record.schema.json`, `src/quant/dataplane/{adapters,identity,ingest,registry}.py`, tests et gate. |
| 13:22:38 | `1467336c…` | Intégration des primitives W1 Factory et des façades historiques. Le raccordement Validator/readiness est complété ensuite ; ce commit seul ne qualifie pas toute la chaîne. |
| 13:57:40 | `8340dd9a…` | Intégration du portefeuille structurel W1 Economic. |
| 14:16:14 | `f4be6953…` | Intégration de Mega A Research Intelligence. |

Ces commits sont retrouvés dans l'histoire de Wave2. Les checkpoints Convergence CP079 CP001–CP003 et les manifestes W1/Mega A sont lus. Ils déclarent des ports sélectifs et des adaptations, avec exclusion des anciens états globaux `STATE.md`, plutôt que des fusions aveugles de rails complets.

## Ce qui se réutilise déjà dans la lignée intégrée

**Factory historique.** Les quatre anciens modules `src/quant/factory/{experiments,geometry,power,outcome_firewall}.py` sont, dans Wave2, des re-exports vers les propriétaires canoniques `research/research_os/expansion/experiment_{registry,geometry,power,outcome_firewall}.py`. Leur code a été inspecté. L'absence d'égalité avec les anciennes implémentations ne signifie donc pas une capacité perdue. Le manifeste W1 précise les décisions : registre immuable et hypothèses geometry/power adaptés ; géométrie sur rendements réalisés remplacée dans le périmètre pre-outcome ; ancienne ouverture d'outcomes laissée fermée. Ne pas recopier les anciennes implémentations au-dessus de ces propriétaires sans un besoin démontré.

**Data et tests déplacés.** Deux tests W1 absents à leur ancien chemin `tests/` existent octet pour octet sous `research/research_os/tests/`. Les blobs `df4bfbd1…` et `8b8b39b6…` ont été comparés directement. Le checkpoint explique le déplacement pour préserver l'inventaire V1 et exécuter les tests par une étape CI explicite. Ils ne sont pas perdus.

**Scientific Memory.** W1 introduit la représentation canonique des états NEGATIVE/BLOCKED/UNEXECUTED/POSITIVE_BUT_INSUFFICIENT/INVALIDATED_PROTOCOL, distincts de la provenance et de l'autorité. Il réutilise le ledger append-only existant. Le manifeste garde des lacunes de preuves historiques F1/Box Office/replications/EURUSD/V1 ; ces lacunes sont celles des sources épinglées examinées dans cette mission, pas la preuve d'une disparition partout dans GitHub. Les archives opaques signalées par CP1 restent à réconcilier.

**W1 Economic.** Les empreintes structurelles à douze dimensions, états connus/inconnus/conflits et blocages d'overlap sont intégrés. Cela ne produit pas de corrélation empirique ni de contribution marginale estimée. `final_shape.py` est modifié dans l'intégration ; conserver l'implémentation intégrée et vérifier les changements plutôt que restaurer l'ancien fichier globalement.

**Mega A.** Research Intelligence consomme mémoire/archéologie/frontière/capacités pour recommander une prochaine action. Le manifeste distingue épuisement opérationnel de file et épuisement scientifique démontré. Il ne crée pas un second scheduler. Le run `39594809701` est retrouvé en succès au SHA code `75c3351b…` dans la collecte Actions ; ses détails ne constituent pas encore une qualification du descendant actuel.

## Comparaison bornée, sans échantillonnage dans ces deltas

`w1-mega-a-lineages.csv` examine les fichiers Python/JSON/YAML/MJS modifiés par cinq deltas déclarés, vers Wave2, C0 final et WP2. Il ne compare pas tout le dépôt à partir de noms de branches. Dans Wave2 :

- W1 Memory : 10 fichiers identiques, 1 fichier adapté (`legacy.py`), 1 manifeste documentaire absent à son ancien chemin.
- W1 Data : 4 fichiers identiques au même chemin, 2 tests déplacés identiques, 1 fichier adapté (`adapters.py`).
- W1 Factory : 15 fichiers identiques, 4 surfaces modifiées à examiner dans leur historique (workflow, readiness, Validator, tests de validation).
- W1 Economic : 5 fichiers identiques, `final_shape.py` modifié.
- Mega A : 21 fichiers identiques, workflow et `legacy.py` modifiés.

Les destinations de blobs déplacés sont conservées dans le CSV. Les en-têtes « FINAL » et les bornes des sources sont conservés séparément des têtes actuelles. Les runs Factory `39578983345` au SHA `6a2fba61…`, et CP079 `39596056413`/`39596056454` au SHA `dc00f295…`, sont retrouvés en succès ; ce sont des métadonnées au sujet exact, pas une certification des arbres suivants.

## CP et rails actuels

CP049 consigne l'élargissement Owner à la convergence de tout Quant. CP079 consigne la réparation de l'attribution freeze/source/candidat avant challenge natif, avec une limite de qualification source. Cela explique pourquoi les ports W1 sont réévalués sur CP079 et ne doivent pas annuler les corrections CP070–CP079.

Pour WP2, des commentaires du 30 octobre distinguent correction de projection, push local bloqué, revue d'un parent exact et identité head/merge-ref dans les preuves hébergées. Les objets correspondants ont été lus lorsqu'ils sont marqués comme tels ; ils ne sont pas convertis en PASS indépendant. La branche PR #46, fondée sur la branche par défaut, est un autre chantier d'orchestration. L'absence de modules W1 dans son arbre ne suffit pas à en faire un remplacement du produit intégré.

## Reprise vérifiée

L'indexeur a été ajusté pour utiliser les références de la photographie initiale, même après les commits d'archive : les parents de sauvegarde ne deviennent pas des intégrations produit et ne changent pas le dénominateur initial. Un processus avec une base SQLite neuve retrouve 320 refs, 275 branches, 266 têtes, 6 393 commits, 6 465 blobs documentaires et les 45 lectures enregistrées. Les scripts préservent aussi les statuts de discussion existants.

Restent à traiter : CP001–CP099 hors points lus, historique scientifique, discussions complètes, changements aux interfaces partagées et qualification finale des capacités. Aucun tronc définitif ni retrait de branche n'est déclaré dans ce lot.
