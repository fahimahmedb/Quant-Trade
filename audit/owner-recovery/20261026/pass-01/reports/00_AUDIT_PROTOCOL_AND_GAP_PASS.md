# Protocole, couverture et lacunes restantes

**AUDIT_COMPLETENESS=INCOMPLETE.** Les 25 livrables forment une photographie de reconstruction; ils ne certifient pas la clôture de toute l'histoire. La synthèse Owner est en français et les dossiers techniques en anglais.

## Mission appliquée

La mission courante est une récupération forensique. Le premier prompt reste le contexte d'une recherche externe ultérieure sur l'architecture manquante. Pendant cette passe : aucune recherche de littérature nouvelle, modification du produit, correction de défaut, exécution de test produit, nouvelle capacité, activation, publication ou message à un tiers.

Les écritures se trouvent dans `/workspace/quant-trade-owner-recovery`, hors du dépôt produit. Le miroir bare et les extractions sont des supports de lecture. Les CSV sont des projections d'audit figées, pas une nouvelle base opérationnelle.

```
AUDIT_STARTED_AT=2026-10-26 00:52:12 UTC
AUDIT_AS_OF_TIME=2026-10-26 00:52:12 UTC
AUDIT_AS_OF_SHA=ebc72b9fd14f91420c37e0b7607f9bfb584a289a
AUDIT_AS_OF_SHA_SCOPE=W2_COMPARISON_CANDIDATE_NOT_OWNER_PROMOTION
AUDIT_REF_VECTOR_SHA256=6cd5df10580c5b51f57b8203a19194127e60e7c008422b7725288d4975314a88
```

Toutes les branches annoncées sont conservées comme potentiellement pertinentes tant que leur portée n’est pas établie ; le chiffre 261 ne signifie pas 261 campagnes matérielles indépendantes.

La vérité multi-rails repose sur le vecteur des 261 refs. Un seul SHA ne peut pas représenter des branches divergentes. Les observations ultérieures de CI ont été interrogées par SHA exact. Le miroir n'a pas été actualisé sous les analyses.

## Travail réellement effectué

1. Métadonnées GitHub, default et refs figés; miroir du graphe accessible :5 509 commits,261 branches,252 HEAD distincts.
2. Catalogue des 162 087 entrées d'arbres de HEAD et9 267 paths distincts. Extraction de 4 483 blobs de texte,4 669 couples path/blob, dont des artefacts historiques. Les objets binaires/gros et les chemins sensibles ne sont pas injectés dans le contexte; le miroir conserve les objets Git accessibles.
3. Export de 12 snapshots matériels; lectures d'implémentations, contrats, tâches, reçus et résultats. Les README et prompts ne sont pas considérés comme preuve d'exécution.
4. Ledger des261 branches avec merge-base/ahead/behind; index de 704 records CP/mentions. Git ne conserve pas directement la création d'une branche : CREATED_FROM reste UNKNOWN si rien ne la prouve.
5. CI exacte W2/F/Q/V3/A/B/C0/D0/E/Form144/V2-forward; jobs/logs des points critiques. Comparaison du contenu des ports. Vérification83/83 hashes source V,334/334 hashes de preuve V et 21 logs Q compressés/décompressés.
6. Census des 72 tasks et 15 hypothèses du runtime figé;49 frontier tasks; motifs des 38 blocages; descendants réels sur branches séparées et deux continuations documentaires automatiques.
7. Extension historique :15 result paths Edge Lab,20 legacy records,33 seeds Weather,6 versions du Fast ledger, anciens résultats positifs originaux;146 lignes récupérées avec chevauchements explicites.
8. Registres des autorités, représentations concurrentes, orphelins, blocs, North Star, H/V/L et dette qualifiée non intégrée. Récupération supplémentaire du rail Builder CP080–099 après sélection de la base CP079.

## Classes de preuve

FACT_PROVEN : objet, identité, contenu ou activité datée observés; pas vérité économique implicite. STRONG_INFERENCE : meilleure interprétation bornée des objets, par exemple une exécution attendue absente des corpus recherchés. WEAK_INFERENCE : indice insuffisant. CONTRADICTORY_EVIDENCE : représentations concurrentes conservées. UNKNOWN : preuve insuffisante. NOT_FOUND : recherche décrite sans objet retrouvé, pas preuve absolue d'inexistence.

`AUDIT_REVIEW_STATUS` distingue l'indexation d'un examen fonctionnel scoped. Les 120 records CP classifiés sont 100 dispositions actuelles de labels V et 20 du rail Builder V2-forward. Cela ne signifie ni 120 réparations, ni 704 CP compris. Les 53 labels V rejetés sont classifiés comme tels, pas validés comme progrès.

## Métriques

```json
{
  "RELEVANT_BRANCHES_DISCOVERED": 261,
  "RELEVANT_BRANCHES_CLASSIFIED": 38,
  "BRANCHES_PARTIALLY_CLASSIFIED": 1,
  "CP_RECORDS_DISCOVERED": 704,
  "CP_RECORDS_CLASSIFIED": 120,
  "CP_RECORD_COUNT_SCOPE": "517 artifact versions +187 unbound subject-label records, not704 completed CPs; classified120=100 current V label dispositions +20 current Builder V2-forward label dispositions",
  "POSITIVE_RESEARCH_ITEMS_DISCOVERED": 15,
  "POSITIVE_RESEARCH_ITEMS_TRACED_TO_TERMINUS": 10,
  "POSITIVE_RESEARCH_SCOPE": "Recovered unique positive leads; global completeness unknown",
  "QUALIFIED_HEADS_DISCOVERED": "UNKNOWN_GLOBAL;8 exact-head component/cumulative CI qualification scopes plus3 locally bound H/V source scopes documented",
  "QUALIFIED_HEADS_ACCOUNTED_FOR": "11_SCOPED; other historical qualification claims pending",
  "ARCHITECTURE_CAPABILITIES_DISCOVERED": 63,
  "ARCHITECTURE_CAPABILITIES_CLASSIFIED": 63,
  "ARCHITECTURE_SCOPE": "Requested/recovered functional surfaces, not every historical module semantically closed",
  "UNRESOLVED_CONTRADICTIONS": 8,
  "UNTRACED_POSITIVE_HANDOFFS": 5,
  "UNTRACED_POSITIVE_HANDOFFS_SCOPE": "1 suspected UST missing execution +4 historical positives with unknown descendant; not5 proven orphans",
  "UNKNOWN_CRITICAL_ITEMS": 12,
  "AUDIT_COMPLETENESS": "INCOMPLETE"
}
```

## EXACTLY_WHAT_REMAINS_UNAUDITED

- [GAP_BRANCHES.csv](GAP_BRANCHES.csv) :223 rails non clos, dont222 census Git seulement et 1 partiel. Ils ont chacun un HEAD fixé, pas une qualification fonctionnelle inventée. Familles restantes : P0, GateA/B, Weather Owner/Astra/Lots1–3, anciens labs/fast/F1/F2, variantes Live Lab, economic-readiness sub-builders, anciens rails Claude et host/ops.
- [GAP_CP_RECORDS.csv](GAP_CP_RECORDS.csv) :584 records non clos, dont 187 mentions de CP dans les subjects encore non liées à leur portée exacte. Des versions d'un artefact ne sont pas des CP indépendants. Un trou numérique ne prouve pas qu'un CP aurait dû exister; aucun checkpoint manquant n'est inventé.
- [GAP_POSITIVE_LINEAGES.csv](GAP_POSITIVE_LINEAGES.csv) : UST après freeze; LAB24 futures/trend/carry; LAB25 HL-CEX funding, FOMC et pensions. Les fichiers des résultats anciens existent et ont été lus; descendants finaux et comptabilité des expositions/variantes restent à réconcilier.
- Hors des 72 tasks Oracle : reçus/outbox/Book/Learning historiques ne sont pas intégralement corrélés. Les claims de qualification et missions anciens ne sont pas tous liés à leurs SHAs exécutables.
- Tous les raw data, binaires, gros logs et artefacts Actions non committés n'ont pas été audités intégralement. Aucun rejeu du produit n'a été effectué.
- Les 764 cas en échec dans le vieux rejeu Q ne sont pas triés en causes racines indépendantes et applicables. Aucun H/V/L final ne peut être certifié pour une convergence comprenant les correctifs tardifs C0/V2, F et V3.
- GIGA C : aucun artefact nommé retrouvé dans les refs/texte extraits. Les conversations privées ou builds non poussés restent UNKNOWN; ce n'est pas une preuve d'inexistence.

## Douze inconnues critiques

| ID | Inconnue restante |
|---|---|
|K01 |Promotion canonique Owner et politique exacte de seal |
|K02 |État frais du processus, release installée et site distant |
|K03 |Exécution/résultat UST et reçu de validation manquant |
|K04 |Owner et wire natif/partagé Economic Identity |
|K05 |Dénominateur historique root/variant/trial/look dédupliqué |
|K06 |Exposition privée humaine/modèle aux outcomes |
|K07 |Terminus des quatre positifs des anciens labs |
|K08 |Examen fonctionnel complet des223branches restantes |
|K09 |Interprétation scoped des584 records CP restants |
|K10 |Causes applicables des échecs hostiles Q |
|K11 |Autorités et preuves hôte historiques Weather/P0/Gates |
|K12 |Provenance primaire non récupérée de claims MLB/Soccer/BoxOffice |

## Résultat du GAP PASS

Il reste des branches non classifiées fonctionnellement, des CP non interprétés, des qualifications anciennes non liées,5 positifs non tracés jusqu'au terminus, des artefacts runtime non corrélés et un owner de seam inconnu. Les composants North Star portent tous un statut, mais plusieurs sont PARTIAL ou UNKNOWN. La mission n'est donc pas close.

La prochaine passe doit reprendre ces listes et ce miroir, conserver les acquis et fermer les trous. La question d'architecture du premier prompt reste en attente de cette base factuelle; elle n'est pas remplacée par une intuition tirée des lacunes de l'audit.


## Moving-head check after the anchor

At 2026-10-26T01:49:57.832184+00:00, a separate remote-ref check found the following changes. The frozen mirror, census and as-of claims above were not updated. These later commits are not silently included or qualified by this audit.

| Branch | Frozen audit HEAD | Later advertised HEAD |
|---|---|---|
|builder/oracle-v2-core-20261020|`16eafd0b3c8d9e0c633ef01dd191cbd32ae50b42`|`ce3ceb9746e0f65551b69bfc0df406e8f9836100`|
|claude/data-feeds-6vr22g|`262102f049a887b9a1037f3cc490b666bc76cc0d`|`9325ee62a40e90d7d0325b3b0198b26139ad9549`|

Evidence: `../evidence/moving_head_check.json` and `remote_refs_end.tsv`.
