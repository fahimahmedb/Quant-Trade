# Avancement durable — reconstruction Quant-Trade

STATUT : NON TERMINÉ. Collecte et indexation initiales réalisées ; lecture exhaustive et simplification produit restantes.

Photographie : 275 branches / 266 têtes, 320 références Git, 6 393 commits accessibles. Catalogue : 17 221 blobs de fichiers dont 6 465 blobs documentaires selon les extensions déclarées. Ne pas assimiler COLLECTÉ ou INDEXÉ à LU.

Lecture complète consignée : 9 blobs documentaires / 6 465. Objets de discussion : 423 collectés/indexés ; lecture complète non consignée. Réconciliation sémantique complète des branches : 0 / 275. Métadonnées CI : 4 806 / 4 806 ; listes de jobs : 14 runs ; logs : 3 collectés, extraits examinés, aucune lecture complète revendiquée. Les archives ZIP des artifacts ne sont pas analysées.

Travail accompli : miroir complet, fsck et bundle verify ; collecte issues/PR/commentaires/revues/timelines ; pagination ; compteurs exacts ; catalogue SQLite et CSV ; registre événementiel UTC/Paris ; comparaison d'ascendance et de présence exacte des octets ; 3 vérifications CI ciblées ; rapport RECONSTRUCTION.md.

Contre-vérifications : inventaire API 275 branches égal au miroir nom/SHA ; 4 806 IDs de runs distincts ; merges #30/#31/#33 retrouvés dans le graphe Wave2 ; candidat et attestation C0 distingués ; succès cumulatif Wave2 distingué de l'échec Mega E et du sceau non émis ; échec Mega E identifié comme imports pytest absents, pas comme régression produit établie. Aucune expérience historique rejouée.

Complément : branche Oracle V2 déplacée de be5baeb6861732543e59ef56c3b9cddb8d37ebb2 à 6731e672780398ed2ea47e02110105cc2ca180cf entre les deux observations. Le périmètre initial ne change pas ; conserver le delta à part.

Prochaine action bornée : reprendre les lignes read=false du catalogue documentaire et discussion, traiter chaque assertion avec ses preuves sources ; vérifier les sources/corrections CP, horizontal/vertical/Mega/one-shot et descendants sans inférer les ports sémantiques de la seule ascendance. Terminer les collectes CI/artefacts/pièces jointes/threads et les limites d'accès déclarées. Ensuite seulement choisir la lignée, dresser les destinations et produire un patch d'intégration borné. Aucun nouveau tronc sélectionné ; aucune suppression/promotion/runtime autorisée par cet avancement.

Le rapport ne satisfait pas encore les critères de clôture. Les archives et scripts permettent la reprise sans refaire les objets collectés. Les commits d'archive préservent les parents Git uniquement ; ils n'intègrent pas leurs produits dans l'arbre de la branche d'audit.
