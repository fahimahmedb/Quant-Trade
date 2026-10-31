# Reprise — Quant-Trade, reconstruction du 31 octobre 2026

## État faisant foi pour cette mission

**PAUSE DEMANDÉE PAR L'OWNER. AUDIT EXHAUSTIF NON TERMINÉ.**

L'Owner demande d'arrêter après sauvegarde pour faire évaluer le travail par une autre IA. Ne pas relancer l'audit, modifier le produit ou exécuter une expérience sur la seule base de ce fichier. Une reprise ultérieure continue les objets restants ; elle ne recommence pas la collecte initiale.

Mandat : reconstruire factuellement ce qui s'est passé, quand, ce qui a été construit/testé/intégré/retiré, et ce qui se réutilise afin de simplifier GitHub. Pas d'opinion sur les causes de la dispersion. La simplification finale et le patch d'intégration restent à produire.

## Ordre de lecture sans historique du chat

1. `AGENTS.md` et `QUANT_NORTH_STAR.md` de la branche par défaut, puis son routeur `governance/CURRENT_PROJECT_STATE_2026-10-20.md`.
2. Ce fichier sur la branche `audit/forensic-checkpoint-20261019`, dossier `governance/forensic-20261031/`.
3. `resume.json`, `coverage-summary.json`, `PROGRESS.md`.
4. `CHRONOLOGIE_REUTILISATION.md` et `W1_MEGA_A_REUTILISATION.md` pour les résultats nouveaux ; `RECONSTRUCTION.md` décrit le premier lot et reste daté.
5. `reads-overlay.json` et `discussion-coverage.csv` pour savoir exactement ce qui est lu. Les archives initiales conservent des compteurs plus anciens : ne pas les remettre à la place des fichiers courants.
6. `REVIEW_THIS_WORK.md` pour évaluer ce lot, ou la prochaine action bornée ci-dessous si l'Owner autorise la reprise.

Un SHA contenant ce fichier se résout via Git ; aucun auto-hash n'est inventé dans son propre contenu. Le routeur par défaut doit pointer vers le commit immuable de ce checkpoint après publication.

## Périmètre initial figé et couverture

Photographie initiale : défaut `blue/master-v2-2026-09-20@b76bb13f4200784185bc2034e3763df78a72f9ab`, ancien audit `67543ff286ff7a81a6705a197b7e557442d62ac2`.

| Ensemble | Collecte/indexation | Lecture / analyse achevée |
|---|---:|---:|
| Branches | 275, 266 têtes distinctes | 0 réconciliations sémantiques complètes de branche ; comparaisons ciblées conservées |
| Références et commits | 320 références ; 6 393 commits accessibles | chronologies et graphes indexés ; pas 6 393 modifications lues intégralement |
| Blobs de fichiers | 17 221 uniques | pas de lecture globale revendiquée |
| Blobs documentaires | 6 465 uniques ; 12 936 couples blob/chemin | **52 lus**, identifiés dans l'overlay |
| Issues/PR | 46 dont 35 PR | objets bruts conservés ; pas tous analysés |
| Discussion | 326 commentaires + 62 inline + 35 soumissions = 423 objets | **7 lus** ; les extraits ne sont pas comptés comme lecture complète |
| Timelines | 1 775 événements | plusieurs représentent aussi des commentaires/revues ; ne pas additionner comme objets distincts |
| Actions | 4 806 IDs distincts | 14 listes de jobs, 3 logs collectés, 3 examens d'extraits ; aucun log entier déclaré lu |
| Artifacts | 1 export ZIP via connecteur | contenu ZIP non examiné |

Les extensions définissant le dénominateur documentaire sont dans RECONSTRUCTION.md. Les preuves JSON/YAML restent dans le catalogue global. Indexé n'est pas lu ; lu n'est pas vérifié dans toutes ses assertions ; des octets identiques ne prouvent pas l'activation ou l'équivalence du système.

## Travail déjà fait à ne pas répéter

- Miroir et bundle initiaux complets pour les références accessibles ; fsck et bundle verify réussis.
- API paginée : branches, issues/PR, commentaires, revues, timelines, 49 pages Actions. API branches et miroir égaux pour les 275 noms/SHA ; 4 806 IDs de runs distincts.
- Base SQLite locale, CSV des versions/ref/commits/discussions/branches/runs ; registre chronologique UTC + Europe/Paris avec DST ; vue quotidienne mécanique.
- Archives brutes et d'analyse publiées dans GitHub en parties binaires, avec empreintes SHA-256 et instructions de restauration.
- Restauration depuis GitHub dans un autre répertoire : deux archives vérifiées, 289 têtes sauvegardées récupérables, compteurs et curseur relus par un nouveau processus.
- CP2–CP16 lus, datés et reliés à leurs corrections ; racine CP1 README/RESUME lue. Les anciennes versions de chacun restent un travail distinct.
- Sept checkpoints de ports Wave2 lus ; suivis B/D0/E/C0 sur cinq destinations (70 lignes) ; noyau D0 identique à son source qualifié ; merges #30/#31/#33 vérifiés dans Wave2.
- W1/Mega A : manifestes lus, ports retrouvés ; comparaison de cinq deltas vers trois descendants. Façades Factory inspectées ; deux tests Data déplacés retrouvés octet pour octet.
- One-shot : retrait CP03/CP04/CP06 relié au commit `68f16c0f…`, verdict historique NOT_QUALIFIED conservé ; réparations C0 et membrane séparées et datées.
- CI exactes : final C0 `13721384…` run `40437918834` réussi ; Wave2 `ebc72b9…` cumulatif réussi mais sceau non émis dans le log ; Mega E échoue sur trois imports pytest absents. Aucune promotion ou VM actuelle déduite.
- Index Builder : 99 documents Markdown, 98 numéros de CP ; CP050 est retrouvé comme commit de fusion `93a2a5af…`, ne pas le déclarer perdu du seul fait de l'absence d'un Markdown nommé CP050.
- Scripts corrigés et testés sur une SQLite neuve : dénominateurs initiaux inchangés après archivage et lectures conservées. Le test a vérifié 45 lectures documentaires/7 discussions ; les sept lectures documentaires suivantes sont dans l'overlay, portant le total courant à 52.

## Prochaine action bornée, uniquement lors d'une reprise autorisée

1. Lire les objets réellement restants dans `builder-checkpoints.csv`, sans répéter les CP déjà lus. Commencer par le raccordement Evidence Store CP055 et l'archéologie CP062 : chemin exact `research/research_os/architecture/work_receipts/BUILDER_CP_055_HISTORICAL_EVIDENCE_STORE_CONNECTED_20261020.md`. Le précédent essai a utilisé un nom inexistant ; le bon nom a été trouvé mais son contenu n'a pas encore été lu. CP055 a déjà été localisé au commit `103af122…` ; ne pas reconsidérer l'Evidence Store globalement absent.
2. Pour les CP001–CP099, relier demande/décision → code → tests exécutés → ports/remplacements/limites. Traiter ensuite explicitement CP080–CP099 et les corrections horizontales/verticales : ce qui est conservé par les quatre gardes CP02 ne prouve pas la reprise de toute la profondeur.
3. Poursuivre les discussions non lues et la mémoire scientifique juillet–octobre, notamment PR #1, Edge, Legacy, Weather et décisions Owner. Réutiliser les objets bruts ; ne pas relancer les expériences ni ouvrir des outcomes protégés.
4. Compléter les preuves CI nécessaires et les limites de collecte. Puis seulement proposer une lignée produit, les destinations exactes, le devenir sémantique des 275 branches, un patch d'intégration isolé et un backlog fini.

Conserver les dates Git auteur/committer, les événements GitHub et les dates d'installation distincts. Ne pas choisir le tronc par date, nom, défaut GitHub, ancienneté ou seule ascendance.

## Stockage et pièges de reprise

Les scripts et CSV courants sont accessibles directement dans ce dossier. Les gros catalogues, registres et objets bruts sont dans les archives décrites par README.md. Les scripts courants remplacent les versions anciennes contenues dans l'archive initiale. Copier `reads-overlay.json` dans `index/` et le CSV de discussion courant dans `index/` avant de reconstruire l'index.

Si le workspace initial n'est plus disponible : cloner un miroir complet du dépôt public dans un répertoire neuf, nommé `repository.git`. Extraire le dossier `governance/forensic-20261031/` du commit immuable indiqué par le routeur. Réassembler et vérifier les deux archives, puis extraire raw d'abord et analysis ensuite. **Recopier ensuite les scripts et fichiers courants du checkpoint par-dessus les versions initiales extraites** ; placer l'overlay et le CSV de discussion courants dans `index/`. `python index_git.py` puis `python build_ledgers.py` reconstruisent les catalogues sans exécuter les scripts de Quant. Contrôler les dénominateurs et les lectures avant toute analyse supplémentaire. Si un objet source manque, enregistrer l'erreur et récupérer le SHA depuis l'archive Git ; ne pas inventer son contenu et ne pas réinitialiser le suivi des lectures.

**Les commits d'archive attachent les anciens tips comme parents pour préserver leurs objets. Ils n'intègrent pas ces capacités dans le produit.** Toute analyse d'ascendance produit doit utiliser les branches/SHA produit, pas la branche d'audit. Un `git log --all` après archivage inclut les nouveaux commits d'audit ; l'indexeur corrigé utilise `raw/remote-refs-initial.tsv` pour conserver le périmètre initial.

Complément déjà sauvegardé : Oracle V2 est passé de `be5baeb6…` à `6731e672…` pendant la collecte. Le delta reste séparé ; l'autonomie du writer exige une photographie datée, pas une illusion de dépôt immobile. Les publications documentaires de cet audit et la nouvelle entrée du routeur sont aussi des compléments hors photographie initiale.

Limites restantes : endpoints deployments/tags/workflows refusés par le connecteur ; wiki distante « Repository not found » ; pagination interne des threads à vérifier ; collecte logs/artifacts/pièces jointes incomplète. Aucun LFS listé par `git lfs ls-files --all`, aucun historique `.gitmodules/.gitattributes` renvoyé dans les références examinées. Une limite d'accès n'est pas une preuve d'absence historique.

## Contre-vérification et limites de clôture

Contre-exemples traités : différence de graphe ≠ capacité absente ; fichier déplacé ≠ test perdu ; candidat C0 ≠ attestation finale ; run head ≠ forcément commit de merge testé ; PASS cumulatif ≠ sceau émis ; erreur de dépendance CI ≠ régression runtime démontrée ; ancien constat CP5/CP7/CP9 ≠ défaut encore actuel après CP6/CP10 ; mémoire d'archive ≠ intégration produit.

Le pipeline a été révisé pour le dernier contre-exemple (parents d'archive) et pour préserver les lectures. Aucun travail produit, déploiement, suppression de branche, fusion de PR ou autorité économique n'a été exécuté. La clôture exhaustive n'est pas atteinte. Ne pas annoncer 100 %, ni poursuivre après la pause Owner sans nouvelle instruction.
