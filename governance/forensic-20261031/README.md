# Archives de reconstruction — 31 octobre 2026

STATUT : audit incomplet. Lire PROGRESS.md puis coverage-summary.json. La collecte, l'indexation et la lecture sont distinctes.

L'arbre reste celui de l'audit ; les parents supplémentaires des commits d'archive rendent les objets sources accessibles durablement. Ce sont des attaches de sauvegarde, pas des intégrations produit. Le snapshot initial contient 320 références / 6 393 commits ; snapshot-refs.txt inclut également un complément Oracle V2 observé pendant la collecte.

Les données API et changements Git sont compressés en vingt parties binaires :
raw-export.tar.gz SHA-256 a676c40debe397999d40f5f19a32088258e48d3375b3e4b1cffed7133816c38e (5 053 283 octets).
L'index et les scripts sont compressés en treize parties :
analysis-export.tar.gz SHA-256 5ca98410b1e78427d9d2e8a433c9f4d2c282ca8042b2703359cfd35c03257ffe (3 183 558 octets).

Depuis un clone complet de la branche d'audit, dans un répertoire de restauration vide :
```sh
cat /chemin/clone/governance/forensic-20261031/raw-export.tar.gz.part-* > raw-export.tar.gz
cat /chemin/clone/governance/forensic-20261031/analysis-export.tar.gz.part-* > analysis-export.tar.gz
sha256sum raw-export.tar.gz analysis-export.tar.gz
tar -xzf raw-export.tar.gz
tar -xzf analysis-export.tar.gz
```

Comparer les empreintes avant extraction. Conserver les dates, IDs et statuts dans les exports. Le Git natif peut être restauré depuis les parents archivés et les références exactes du manifeste. Le bundle local de 657 942 355 octets a été vérifié ; ses octets ne sont pas dupliqués dans ces exports. Aucun LFS n'est référencé par git lfs ls-files --all ; aucun historique .gitmodules/.gitattributes n'a été renvoyé. La lecture de la wiki distante a renvoyé Repository not found ; ne pas conclure à son absence historique. Les limites de collecte sont détaillées dans RECONSTRUCTION.md.

Les scripts reconstruisent l'index et les rapprochements mécaniques ; ils ne lisent pas sémantiquement les documents. Préserver le registre reads SQLite et les CSV de lecture avant de régénérer : build_ledgers.py initialise les statuts de discussion à false. La lecture complète n'est consignée que pour neuf blobs documentaires ; aucune clôture exhaustive n'est revendiquée.
