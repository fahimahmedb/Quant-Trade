# Évaluer ce travail avec une autre IA

Lire RESUME.md, coverage-summary.json, puis les trois rapports de ce dossier. Évaluer l'audit réalisé, pas l'ensemble de Quant. Le travail est explicitement incomplet.

Contrôles prioritaires et falsifiables :

1. Les archives se réassemblent-elles avec les deux SHA-256 du README ? Les tips de snapshot-refs.txt restent-ils accessibles par les parents d'archive ? Attention : sauvegarde n'est pas intégration produit.
2. Le périmètre initial donne-t-il 275 branches / 266 têtes / 6 393 commits, même après les publications d'audit ? Employer raw/remote-refs-initial.tsv et les scripts courants ; éviter de remplacer le dénominateur par git log --all.
3. Les 52 blobs de reads-overlay.json sont-ils uniques et présents ? Le CSV de discussion contient-il exactement 7 read=True ? Ne pas traiter tous les objets exportés comme lus.
4. Vérifier quelques conclusions jusqu'aux sources : noyau D0 blob a56b042a… ; tests W1 Data blobs df4bfbd1… et 8b8b39b6… aux nouveaux chemins ; façades quant.factory vers les modules canoniques ; commits de fusion #30/#31/#33 dans Wave2.
5. Vérifier les nuances CI dans les JSON/jobs/logs exportés : final C0 au SHA 13721384… ; cumulatif Wave2 réussi mais WAVE2_INTEGRATED_SHA_EMITTED=FALSE ; trois erreurs d'import pytest dans le job Mega E. Ne pas convertir ces faits en qualification globale ou déploiement.
6. Vérifier la chaîne des corrections CP5→CP6, CP7–CP9→CP10, CP11→CP12, CP14/CP15→CP16 et le retrait des modules du one-shot. Les assertions des anciens audits restent REPORTED tant que leurs sources ne sont pas contrôlées.

Livrable de revue : erreurs établies avec objet/SHA/chemin précis, conclusions supportées et portée, limites non résolues, puis modifications minimales du point de reprise si nécessaire. Aucun pourcentage de complétude inféré du volume exporté. Ne rien supprimer, fusionner, promouvoir, déployer ou relancer scientifiquement. Ne pas recommencer la collecte intégrale sans une corruption ou lacune démontrée.

Consigne courte à copier : « Évalue les résultats et la fiabilité de reprise de l'audit au checkpoint lié, en suivant REVIEW_THIS_WORK.md. Vérifie les compteurs et plusieurs conclusions jusqu'aux objets bruts. Distingue données collectées, lectures et assertions vérifiées. Rends une revue factuelle avec preuves et limites ; n'exécute aucune action produit et ne poursuis pas l'audit suspendu. »
