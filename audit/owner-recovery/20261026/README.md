# Conservation du dossier Owner Recovery

Cette publication conserve la passe forensique existante sans correction de son contenu.
AUDIT_COMPLETENESS=INCOMPLETE reste la conclusion de la passe 01.

## Accès
- pass-01/reports/01_OWNER_BRIEF.md : synthèse Owner.
- pass-01/QUANT_TRADE_OWNER_RECOVERY_PASS_1.zip : ZIP initial, inchangé.
- pass-01/reports/00_AUDIT_PROTOCOL_AND_GAP_PASS.md : lacunes exactes.
- archives/FULL_ARCHIVE_MANIFEST.json : archive complète et empreintes.
- archives/full-preservation.zip.part001 à part045 : volumes consécutifs du ZIP complet, incluant preuves, scripts, snapshots et miroir Git.
- archives/PRIOR_RESEARCH_WORK_IN_PROGRESS.zip : préparation antérieure de recherche externe, non terminée, sans verdict final.

Le ZIP initial a pour SHA256 :
896cddfa37c2efc2f2281b0795610f4afea84b22de4cfff49d17f649ad35e8c9

Les snapshots consultables réutilisent les arbres Git originaux aux SHAs figés.
Le catalogue SQLite est aussi disponible dans catalog.sqlite.zip; son original est conservé dans l'archive complète.

## Réassembler l'archive complète
Depuis archives, concaténer les volumes dans l'ordre numérique :
`cat full-preservation.zip.part??? > OWNER_RECOVERY_FULL_PRESERVATION.zip`
Vérifier ensuite son SHA256 contre FULL_ARCHIVE_MANIFEST.json, puis décompresser.
Le manifeste fournit également l'empreinte de chaque volume.

## Règle pour toutes les suites
1. Ne jamais réécrire, remplacer ou supprimer une passe publiée, ses preuves ou son ZIP.
2. Ajouter chaque suite dans un nouveau dossier pass-02, pass-03, etc., avec son propre ancrage, son manifeste et son ZIP.
3. Toute correction ultérieure doit être un addendum daté qui cite la version antérieure; conserver l'original.
4. Ne pas réexécuter en place les anciens générateurs: ils peuvent écraser leurs sorties. Adapter une copie pour écrire uniquement dans la nouvelle passe.
5. Vérifier les octets et les empreintes avant publication, puis vérifier le commit distant exact.
6. Conserver les résultats négatifs, inconnues, contradictions, rétractions et lacunes; ne pas réétiqueter une passe incomplète comme complète.
7. Publier les prochaines passes et leurs archives sur GitHub après leur production, conformément à la demande persistante de l'Owner.

Aucun fichier produit à la racine du projet n'est modifié par ce commit; tous les ajouts sont sous audit/owner-recovery/.
