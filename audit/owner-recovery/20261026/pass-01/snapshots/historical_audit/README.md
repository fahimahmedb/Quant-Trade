# Quant-Trade — checkpoint forensique 001

Audit indépendant en lecture seule commencé le 18 octobre 2026 à 23:51 UTC / 19 octobre à 01:51 Europe/Paris. Ce checkpoint est publié sur instruction explicite de l’Owner du 19 octobre : « Pousse ton premier checkpoint ensuite et reprends ». Seule une nouvelle branche d’audit isolée est publiée. Aucune consolidation, modification de branche active, PR, expérience, acquisition économique ou action opérationnelle n’est autorisée par cette publication.

**État : audit en cours, partiel. Ce document ne constitue pas un feu vert de consolidation.**

## Photographie et conservation initiales

- Dépôt observé : `fahimahmedb/Quant-Trade`, visibilité publique.
- Branche par défaut : `blue/master-v2-2026-09-20`, SHA `09ba64b8bee1419076ec8a30f8d75a916932c2ba`.
- Premier inventaire Git distant capturé le 18/10 entre 23:52:06.418 et 23:52:06.868 UTC, bornes fondées sur création/modification du fichier de capture local. Ce n’est pas une photographie atomique de toutes les surfaces.
- Références accessibles initiales : **259**, soit **221 branches**, **37 références de PR** et **1 référence de notes**; **0 tag**. Les branches pointent vers **212 commits distincts**.
- Miroir non shallow : **3 494 commits accessibles**, **28 939 objets Git packés**. `git fsck --full` terminé sans erreur signalée; bundle `--all` vérifié, historique sans prérequis externes.
- SHA-256 du bundle initial : `1a844022a76d871092405e9eb488af80c610a7de884273f24b8d91929694a923`.
- Miroir, bundle et copie d’analyse indépendants conservés localement sous `/workspace/quant-trade-audit/2026-10-18T2352Z/`. **Le bundle n’est pas publié dans cette branche. La durabilité hors environnement n’est pas démontrée.**
- Le miroir Git ne conserve pas automatiquement les artefacts Actions, pièces jointes, états de Site, bases, VM, credentials ou données externes. Aucun tag ni release exposé dans les collectes initiales. Aucun sous-module ni `.gitattributes` trouvé dans les arbres des pointes inventoriées; cela ne prouve pas une absence historique de LFS.

## Couverture au checkpoint

| Surface | Couverture vérifiée | Limite |
|---|---|---|
| Références | 259/259 inventoriées et fiches structurelles locales | revue sémantique de chacune encore inachevée |
| Branches | 221/221 indexées : SHA, arbre, dates, parents, merge-base, ancêtres, diffs, occurrences | métadonnées et scans ne constituent pas 221 revues complètes |
| Histoire | 3 494 commits indexés; suppressions/renommages indexés | histoire utile analysée par lots, pas intégralement close |
| Pointes | 96 288 occurrences de chemins, 7 974 blobs distincts, 228 arbres distincts | binaires et outcomes scellés exclus des lectures |
| Dépendances textuelles | 3 230 blobs scannés lexicalement; 3 660 mentions de branches | ce sont des occurrences candidates, pas des dépendances sémantiques toutes résolues |
| GitHub | 28 PR, dont 9 ouvertes, 3 fusionnées et 16 fermées non fusionnées; 1 issue hors PR | discussion et portée des décisions en cours de réconciliation |
| Actions | métadonnées de 3 328 runs et 1 067 artefacts catalogués | catalogue ≠ sauvegarde des octets; vert ≠ preuve économique |
| Mémoire scientifique | registres historiques et résultats publiés examinés par lots | familles, alias et expositions encore en cours de réconciliation; aucun taux global annoncé |
| Runtime | tâches/événements/reçus et code de reprise inspectés au SHA fixé | état Git ≠ service vivant; aucune continuité H24 démontrée |

La PR [#22](https://github.com/fahimahmedb/Quant-Trade/pull/22) est un canal de coordination « NE PAS FUSIONNER », et non un candidat ordinaire à fusionner. Sa discussion complète est conservée localement et en cours d’analyse.

## Reprise du 19 octobre à 11:57 Europe/Paris

Plusieurs lecteurs IA ont été interrompus par une limite d’usage. Leurs fichiers de travail ont survécu; aucune activité continue pendant cette interruption n’est prétendue. La reprise repart des SHA et checkpoints conservés.

La nouvelle publicité Git à 09:57 UTC retrouve une branche supplémentaire `ops/oci-one-shot-install-20261019` à `6e8ea155b05086f8e5eabcf830a5f835d3e3d09c`, et le déplacement de `claude/data-feeds-6vr22g` de `55066ed4322f51798a3252a90e976e01d3281276` à `fc243f9a786e13220fe283c5bd0a6d74f7def5b5`. Les autres références initiales sont inchangées et aucune n’a disparu dans cette comparaison. Cette collecte compte 260 références nommées (`refs/*`), avant création de la branche d’audit. Les contenus et conséquences de ces deux changements sont en cours de revue.

L’objet `refs/pull/1/head` à `c60c8ab20b3f08add097e25e7295ba1196b0e4a6`, qui n’est contenu dans aucune pointe de branche actuelle, conserve une génération scientifique supplémentaire. Son backlog de 110 cycles comporte des PASS historiques déclarés, à distinguer des validations effectivement vérifiables. Son examen est ajouté explicitement au travail restant; le nombre de branches n’était donc pas une borne suffisante pour retrouver toute la mémoire.

## Constats étayés, avec leur portée

1. **Routage historique contradictoire.** Au SHA par défaut, `handoff/BLUE_CONTEXT_REACQUISITION_F11_2026-09-21.md` conserve un blocage F11, tandis que `governance/CURRENT_GOVERNANCE_STATE_2026-09-20.md` rapporte sa fermeture et des rails ultérieurs. Ces textes sont des états historiques à relier aux commits/autorités concernés. Aucun des deux n’est appliqué comme instruction pendant l’audit.
2. **Readiness construite et portée distincte.** Le port `d5e6d55ba6084729b585a7bb41cede62d8d0f01b` et l’activation `e980d201d3c84d16d7d91fde0d27a06c9a2c3121` sont des ancêtres du Research OS observé `d0dc70f5dd71f3e6cb8097d2f15807bb99ebc8ec`. Les correspondances de code sont vérifiées séparément de la capacité économique. La première verticale historique `5c8b5b71ef627ac0ec0faa509edc40b7d9d0c4df` n’est pas ancêtre de cette pointe; l’absence de ses chemins n’implique pas à elle seule l’absence d’une capacité équivalente.
3. **Autorité à conserver par objet.** La note Git `e9e163e9553b44873a53a73e825414eeade02560`, attachée à `e980d201…` et conservée sous `refs/notes/economic-readiness`, rapporte une autorisation Owner du 17 octobre pour un premier test borné, puis un blocage faute de paquet économique admissible. La source conversationnelle est rapportée, pas authentifiée indépendamment par ce seul objet. Les flags faux de tâches de découverte et les assertions d’une fixture CI ne révoquent pas rétroactivement cette décision rapportée. Le présent audit n’autorise aucune expérience.
4. **État de file plus récent que le bail du 17.** Les 27 tâches JSON du Research OS à `d0dc70f5…` sont `COMPLETE`; la tâche fondamentale auparavant signalée expirée a une génération 2 et une clôture le 18 octobre. Cela décrit ce snapshot Git, pas une observation actuelle de workers.
5. **Dérive de formats et risque de renouvellement.** À la même pointe, le contrôle borné de JSON contre leurs schémas committés trouve 14/27 tâches, 6/65 événements et 29/37 reçus non conformes. Ce n’est pas une preuve que tous leurs lecteurs échouent. Deux nouvelles tâches stockent cependant leur dérivation hors de `task.derivation`, seul emplacement lu par `_issued_counts` et `_existing_derivation_keys` dans `research/research_os/queue_replenisher.py` lignes 41–56. L’analyse statique de la prochaine sélection prévoit un identifiant déjà présent. Aucune file ni aucun bail n’est modifié.
6. **Dépendance opérationnelle entre branches.** Le workflow [data-feeds.yml](https://github.com/fahimahmedb/Quant-Trade/blob/09ba64b8bee1419076ec8a30f8d75a916932c2ba/.github/workflows/data-feeds.yml#L36) de la branche par défaut charge explicitement `claude/data-feeds-6vr22g` pour les schedules. Les logs d’un run récent montrent le checkout réel puis le commit/push de données. Le SHA du run ne suffit donc pas à identifier tout le code exécuté. L’évaluation H-001 héritée et ses autorisations restent un périmètre distinct du Research OS.
7. **F1 : résultat publié et nuance CI.** Les résultats publiés A/B sont retrouvés et leurs empreintes contrôlées. B rejette l’expression gelée dans son périmètre, sans justifier un rejet universel de tout carry. Le run `38006324356` est globalement en échec mais son étape économique B est réussie; l’échec intervient lors de la publication du delta PR. Le statut global seul aurait masqué cette distinction. Aucun replay n’est effectué.
8. **Mémoire récupérable.** Des rapports et agrégats Box Office et settlement liquidity restent accessibles dans les branches opaques `claude/relaxed-johnson-mqca45` et `claude/hopeful-dirac-4ahy2z`. Les lacunes d’une synthèse secondaire ne prouvent donc pas la disparition de leurs objets. Les résultats ne sont pas recalculés. Des suppressions historiques d’artefacts lookahead/off-by-one sont également retrouvées; les anciens verdicts optimistes ne sont pas réhabilités.
9. **Obstacles de sources ≠ rejet économique.** Form144 a des tentatives d’infrastructure qui n’atteignent pas l’outcome économique; Due Bill reste limité par l’accès aux prix/instruments requis. Les verdicts scientifiques détaillés et leurs conditions de réouverture sont en cours de rapprochement.
10. **Affichage, canary et service distincts.** Les sources Live Lab différencient un canary technique, le transport d’événements et la recherche authentifiée. Une VM déclarée `RUNNING` et une scène affichée ne démontrent ni installation d’un service ni activité économique. L’état courant des services externes n’est pas observé dans ce checkpoint.

## Prochaines lectures et frontières de reprise

1. Achever les familles/hypothèses/alias et les expériences historiques, notamment les variantes invalidées, les fenêtres ETF déjà exposées, les ordres 12/12b et les preuves primaires manquantes.
2. Achever la cartographie de chaque branche au-delà de ses métadonnées, des dépendances codées ou citées et des intégrations partielles. Conserver les rôles distincts des noms au même SHA.
3. Rapprocher les commentaires Owner directs, ratifications rapportées, protocoles, notes Git et scopes de construction/test/exécution/activation. Ne pas déduire une autorité du seul préfixe `owner/`.
4. Vérifier les preuves CI nécessaires aux conclusions (workflow au SHA exact, tentative, étapes, artefacts accessibles) et préserver les artefacts techniques admissibles identifiés. La collecte initiale annonçait une première expiration d’artefact le 19 octobre à 08:07:52 UTC; ce seuil est désormais passé et la disponibilité actuelle reste à revérifier. Une métadonnée conservée ne garantit pas la disponibilité des octets.
5. Écrire les cartes Git/logiciel/science/autorité/opérations/preuves, la matrice active et les lots de consolidation réversibles, puis faire leur revue critique.
6. Effectuer une collecte finale séparée et réconcilier les changements, y compris la nouvelle branche d’audit créée pour ce checkpoint.

Les registres opérationnels existants restent les sources du projet. Cette branche est un index d’audit, sans scheduler, worker, workflow ni code déployable. Aucun secret, donnée brute économique ou outcome scellé n’y est publié. `REAL_CAPITAL_AUTHORIZED = FALSE` et `LIVE_TRADING_AUTHORIZED = FALSE` restent des frontières préservées. Le responsable reprend l’audit après ce checkpoint; aucune poursuite après fermeture de session n’est promise.
