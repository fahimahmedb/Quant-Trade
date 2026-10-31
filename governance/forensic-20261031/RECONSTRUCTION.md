# Quant-Trade — reconstruction factuelle, lot 1

État : **INCOMPLET — ce document n'est pas la reconstruction exhaustive demandée.**

Périmètre observé le 31 octobre 2026 : `fahimahmedb/Quant-Trade`, branche par défaut `blue/master-v2-2026-09-20@b76bb13f4200784185bc2034e3763df78a72f9ab`. Les exports, index, lectures et vérifications sont comptés séparément. Aucun avis sur les causes de la dispersion n'est formulé.

## Couverture de collecte et d'indexation

| Ensemble | Résultat |
|---|---:|
| Branches API et miroir, comparées nom/SHA | 275 / 275, égalité exacte |
| Têtes de branche distinctes | 266 |
| Références Git, incluant notes et PR | 320 |
| Commits accessibles indexés | 6 393 |
| Blobs de fichiers distincts indexés | 17 221 |
| Couples blob/chemin indexés | 41 422 |
| Blobs documentaires distincts | 6 465 |
| Couples blob/chemin documentaires | 12 936 |
| Issues et PR | 46 : 35 PR, 11 autres issues |
| Commentaires de conversation collectés | 326 |
| Commentaires de code collectés | 62 |
| Soumissions de revue collectées | 35 |
| Threads de revue renvoyés par le connecteur | 48 |
| Événements de timeline collectés | 1 775 |
| Exécutions Actions collectées / identifiants distincts | 4 806 / 4 806 |

La catégorie documentaire est définie par les extensions `.md`, `.mdx`, `.rst`, `.txt`, `.adoc`, `.pdf`, `.org`, `.html`, `.htm`. Les preuves JSON/YAML, scripts et autres fichiers sont dans le catalogue de tous les fichiers ; ils ne sont pas inclus dans le seul dénominateur documentaire. Les noms Git échappés restent conservés comme tels. Les identifiants de la timeline ne sont pas additionnables aux commentaires et revues : plusieurs représentations peuvent désigner le même événement.

Les tableaux CSV contiennent des statuts de lecture. Leurs lignes ne certifient pas une lecture sémantique. `branches.csv` contient les 275 branches ; son statut `PRESERVE_PENDING_RECONCILIATION` est une attente de traitement, pas une décision finale de conservation. `carryover-bytes.csv` contient 1 531 comparaisons de fichiers ciblés ; l'égalité des octets ne prouve pas l'utilisation effective ni l'équivalence du comportement d'ensemble.

## Traces chronologiques vérifiées

La création GitHub est horodatée `2026-07-13T01:29:49Z`. Le plus ancien commit produit accessible est `d49290b2a335ba47d83c8ae056f1c66ae253ff9c`, daté auteur et committer du 13 juillet, intitulé « Étapes A et C : diagnostics NASDAQ + moteur de volatilité walk-forward ». Le graphe contient aussi une racine d'audit et une racine de notes. Les 6 393 commits se répartissent par mois committer en juillet : 702, septembre : 1 421, octobre : 4 270. Aucun commit d'août n'est présent dans ce périmètre accessible ; cela n'établit pas l'absence de travail hors de ce graphe.

Les PR #3–#5 datent du 12–13 septembre et portent sur l'alignement, l'évaluation économique et Alpha Factory. Les PR #6–#15 portent sur la reconstruction autonome, la recherche persistante, Quant System V1 et la data plane. Ces intitulés et descriptions sont des traces de demandes/constructions ; ils ne certifient pas leur achèvement. Les PR #16 et #18 ont des dates de fusion GitHub respectivement le 18 et le 19 septembre. Les PR #24–#28 conservent la chaîne F1/F2/EURUSD ; leur lecture scientifique exhaustive n'est pas terminée. PR #29 conserve la proposition de renderer Live Lab 3D.

CP12, sur `audit/forensic-checkpoint-20261019@67543ff286ff7a81a6705a197b7e557442d62ac2`, distingue Oracle V1, V2 Core, Live Lab et les corpus historiques. Ses affirmations sur les capacités non absorbées décrivent son périmètre V2 Core au moment de l'audit. Elles ne permettent pas d'affirmer leur absence dans toutes les constructions postérieures.

Le 21 octobre, les PR #30, #31 et #33 ont été fusionnées dans Wave2. Leur métadonnée `merged_at` et leur commit de fusion sont collectés. Les trois commits sont effectivement ancêtres de `ebc72b9fd14f91420c37e0b7607f9bfb584a289a` : #30 `0722dc4d3a69e70b67b15962b9bfe1858f963408`, #31 `7f043122fa18437f6e7ffbed6e199099cea2811d`, #33 `b8110b39d611c7813b937cacb5727247149a516e`. PR #32 a été fusionnée sur la source Multi-Source, une destination distincte.

Le manifeste Wave2 référence explicitement des ports B, D0, C0 et Mega E, ainsi que Multi-Source. Sa déclaration de PASS est une déclaration documentaire jusqu'à confrontation au sujet exact et aux journaux correspondants. La tête Wave2 observée date du 23 octobre malgré le suffixe `20261021` de son nom.

Les branches horizontales et verticales ont leurs propres bases et conditions de Phase B. Le manifeste horizontal Convergence #1 ne qualifie pas la Wave2 finale. Le manifeste vertical contient un arrêt Owner à CP046 et garde des limites de profondeur non prouvées. Les lectures ne permettent pas encore d'attester le devenir de chacune de leurs corrections dans les descendants.

La lignée one-shot → réparation du comptage C0 → réparation de la membrane de référence est visible dans l'historique. Le commit one-shot `d19b1237…` est parent de la séquence aboutissant au C0 `13721384…`. Les revues Pass B classent le défaut one-shot comme défaut de représentation/comptage et distinguent le défaut de référence ultérieur ; cela reste une conclusion de revue à suivre jusqu'aux tests et au code, et non une évaluation scientifique globale de cet audit.

Les PR #39, #41 et #46 conservent ensuite des travaux WP2, de revue et d'orchestration GPT-OSS/Codex. Elles sont ouvertes dans la photographie collectée. Leur présence ne constitue pas une preuve de promotion ni d'installation VM.

## Vérifications CI au sujet exact

1. `40437918834` : workflow C0, head `13721384fe5b94b0136fb4548192e05d5e34e605`, completed/success. Le job `121970986243` et son journal sont collectés. Les extraits examinés montrent la qualification et le contrôle final de worktree sur cette tête, ainsi que la publication de l'artifact `12705480219`. Le routeur qui laissait les seuls contrôles finaux hébergés inconnus est donc dépassé sur ce point précis. Le contenu ZIP de l'artifact n'a pas été examiné et aucune promotion ni santé VM n'est déduite.
2. `39882531103` : workflow cumulatif Wave2 sur `ebc72b9…`, completed/success. Le journal du job `120183033203` déclare `FINAL_CUMULATIVE_QUALIFICATION_CANDIDATE=PASS` et `WAVE2_INTEGRATED_SHA_EMITTED=FALSE`. Le succès ne vaut donc pas émission du sceau final.
3. `39882531036` : Mega E sur le même `ebc72b9…`, failure. Le journal du job `120183033112` contient trois erreurs d'import `ModuleNotFoundError: No module named 'pytest'`, dans les modules Mega B ; 458 tests annoncés, `FAILED (errors=3)`. Les étapes V1 E2E, clean-tree et émission du reçu sont skipped. Ce résultat ne démontre pas une régression fonctionnelle du runtime ; il démontre l'échec de ce gate dans cet environnement.

Les 4 806 métadonnées de runs indiquent 3 116 success, 1 551 failure, 117 cancelled, 17 skipped, 4 action_required et un résultat nul lors de la collecte. Ces chiffres ne constituent pas un taux de qualification produit. Les logs complets de toutes les exécutions, toutes les tentatives et tous les artifacts ne sont pas collectés.

## Sauvegarde, limites et suite de traitement

`git fsck --full` n'a pas signalé d'erreur. Le bundle autonome de 657 942 355 octets a passé `git bundle verify`, qui annonce un historique complet pour les références sauvegardées. Cela n'inclut pas les objets jamais poussés, devenus inaccessibles ou supprimés avant la photographie. LFS, sous-modules et wiki nécessitent encore une vérification de tout l'historique ; une absence dans le seul arbre courant ne suffit pas.

Les endpoints deployments, tags et workflows ont été refusés par le connecteur utilisé. Les tags Git sont conservés par le miroir s'ils sont annoncés ; le refus API n'est pas une preuve d'absence de tags, workflows ou déploiements. Le wiki, les pièces jointes et la pagination interne éventuelle des threads restent à vérifier. Les déclarations scientifiques protégées ne sont pas une autorisation d'ouvrir des outcomes ou de relancer des expériences.

La lecture exhaustive des 6 465 versions documentaires et des 423 objets de discussion n'est pas achevée. La causalité détaillée, le devenir sémantique de toutes les branches, la sélection finale d'une lignée produit, la carte complète des capacités et le patch d'intégration restent à produire. Aucune branche n'est déclarée supprimable, aucun tronc n'est promu et aucun runtime n'est modifié par ce lot.

Reprise : les CSV et SQLite définissent les objets restants. Commencer par vérifier les archives et les références de la photographie, puis lire les objets `read=false` et enregistrer les preuves assertion par assertion. Les rapprochements d'ascendance et d'octets déjà calculés sont à réutiliser ; ils ne remplacent pas l'examen sémantique.
