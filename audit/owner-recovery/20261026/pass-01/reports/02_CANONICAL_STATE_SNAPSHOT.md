# État canonique récupéré — photographie figée

```
AUDIT_STARTED_AT=2026-10-26 00:52:12 UTC
AUDIT_AS_OF_TIME=2026-10-26 00:52:12 UTC
AUDIT_AS_OF_SHA=ebc72b9fd14f91420c37e0b7607f9bfb584a289a
AUDIT_AS_OF_SHA_MEANING=W2_COMPARISON_CANDIDATE_NOT_FORMAL_OWNER_PROMOTION
AUDIT_REF_VECTOR_SHA256=6cd5df10580c5b51f57b8203a19194127e60e7c008422b7725288d4975314a88
DEFAULT_BRANCH=blue/master-v2-2026-09-20
DEFAULT_BRANCH_HEAD=9026e4d83d0b3d67637ca8e8437125a372109369
CURRENT_CANONICAL_CANDIDATE=ebc72b9fd14f91420c37e0b7607f9bfb584a289a
CURRENT_CANONICAL_FORMALLY_PROMOTED_SHA=UNKNOWN
CURRENT_WAVE2_CANONICAL_BRANCH=builder/convergence-wave2-canonical-20261021
CURRENT_WAVE2_CANONICAL_HEAD=ebc72b9fd14f91420c37e0b7607f9bfb584a289a
CURRENT_WAVE2_IMMUTABLE_BASE=2b99d8aeb8a342f1ef32544247d366cb8a26037e
CURRENT_V3_BRANCH=builder/multi-source-ideation-intake-v3-20261026
CURRENT_V3_HEAD=0691a4c1c905c8cfa1e68d521b12d66655ec4dd3
CURRENT_OPERATIONAL_STATE_BRANCH=builder/oracle-v2-core-20261020
CURRENT_OPERATIONAL_STATE_HEAD=16eafd0b3c8d9e0c633ef01dd191cbd32ae50b42
LAST_OBSERVED_EXECUTABLE_RELEASE=a67ffec48fff895d5edc42171855e2213e49cf0d
```

**FACT_PROVEN** — ces objets Git existent dans le miroir indépendant. Les261 HEAD complets sont dans [le ledger](05_BRANCH_AND_RAIL_LEDGER.csv) et le vecteur brut dans `../evidence/remote_refs_start.tsv`. Aucun HEAD mouvant n'est utilisé pour les comparaisons. Le temps d'ancrage décrit cette collecte; les dates des artefacts sont des observations antérieures. E01/E08/E09.

**UNKNOWN** — un unique SHA qui serait à la fois le tronc Owner promu, la convergence qualifiée complète et le code actuellement déployé n'est pas établi. Les trois identités ci-dessus restent distinctes. Le manifeste W2 attend un seal externe, et la qualification exacte imprime explicitement `WAVE2_INTEGRATED_SHA_EMITTED=FALSE`. Une CI cumulative réussie existe néanmoins sur le vrai HEAD`ebc72b9fd14f91420c37e0b7607f9bfb584a289a`. E02/E03, contradictionCT01.

## Autres rails actuellement matériels

| Rail | HEAD figé | Réalité prouvée / limite |
|---|---|---|
| F | `79329f15bbf02c25fa61e5d5ef6028e5abfb1493` | Code + CI exacte PASS; feed désactivé; pas dans W2/Q/runtime. |
| Q | `4efadddf694eff0c0df00925b5b4b89194f32f8e` | Réparations et CI exécutées; qualification finale BLOCKED. |
| H pré-W2 | `7aaeea99d51d3ab53c4d7cc2b73b67a7cee2c76f` | Couverture/réparations locales bornées; phaseB non prouvée. |
| H Convergence1 | `6d9dc40b5833442c597f7e7ab8aa631b3d481e83` | Seams/H001-H004/L001 documentés avec probes; pas final W2. |
| V | `5d628db2949144ca6abf94327de3146f3983ecea` | Arrêt Owner CP046;47 entrées substantielles dont061;53 labels rejetés. |
| C0 latest | `6dc84f35e80aec709e67e3d5d3ce0cdcfaee3bcf` | Correctif d'indépendance sémantique absent du noyau préservé W2/Q. |
| V2 forward CP099 | `ded4228de74ce3b6926d9ea3e3c2114ff1be8208` | CI exacte Oracle V2 Core PASS ; contrôles tardifs du chemin composé absents de W2. |
| Source feeds | `262102f049a887b9a1037f3cc490b666bc76cc0d` | Collecte durable récente de données; aucun nouveau test scientifique déduit. |

## Git intégré et contenu porté

**FACT_PROVEN** — F et Q descendent chacun d'ebc par3 commits. V3 ajoute2 commits sur2b99 et n'embarque donc pas les227 commits de convergence ultérieurs. Les HEAD source A/B/C0/D0/E ne sont pas tous ancêtres d'ebc : l'intégration utilise aussi des ports/adapters. L'absence d'ascendance d'un HEAD source ne suffit donc pas à conclure à une absence fonctionnelle.

La comparaison de blobs prouve : Research Intelligence=A identique, oracle_worker=E identique, MultiSource=sourcebbdea identique, noyau D0 identique; Discovery B est adapté; C0 correspond à une version plus ancienne que le latest qualifié. `critical_content_ports.json` et E19. Les counts ahead/behind ne mesurent jamais le pourcentage d'intégration.

## Qualification exacte connue

| Cible | Qualification | Portée |
|---|---|---|
| ebc W2 |39882531103 PASS | Cumulative; pas seal émis. |
| ebc Mega E séparée |39882531036 FAIL | Dépendance pytest absente; ne prouve pas à elle seule un défaut produit. |
| F79329 |40054403097 PASS | Federation/feed bornés, démo et régression. |
| V30691 |40249296902 PASS | Admission V3 + régressions de sa base. |
| Q4efadd |40054895425 FAIL | Ordinary suites PASS; hostile V obligatoire FAIL. |
| B / C0 / D0 / E source | E20/E19 | Qualifications de composants; pas preuve de convergence de tous leurs derniers changements. |

## Autorité à la photographie

**FACT_PROVEN** — le Control Plane opérationnel porte `economic_experiment_authorized=false`, `prospective_observation_authorized=false`, `real_capital_authorized=false`, `live_trading_authorized=false`. **CONTRADICTORY_EVIDENCE** — les reçus de campagne UST conservent une autorisation spécifique d'outcome access après freeze. Aucune résolution de portée ni révocation normalisée n'a été récupérée. L'audit ne change aucune autorité. Voir [17](17_AUTHORITY_MAP.md).

Toutes les preuves sont détaillées dans [EVIDENCE_INDEX](EVIDENCE_INDEX.md). `AUDIT_COMPLETENESS=INCOMPLETE` : ce snapshot est exploitable, pas une certification de toute l'histoire.


## Moving-head check after the anchor

At 2026-10-26T01:49:57.832184+00:00, a separate remote-ref check found the following changes. The frozen mirror, census and as-of claims above were not updated. These later commits are not silently included or qualified by this audit.

| Branch | Frozen audit HEAD | Later advertised HEAD |
|---|---|---|
|builder/oracle-v2-core-20261020|`16eafd0b3c8d9e0c633ef01dd191cbd32ae50b42`|`ce3ceb9746e0f65551b69bfc0df406e8f9836100`|
|claude/data-feeds-6vr22g|`262102f049a887b9a1037f3cc490b666bc76cc0d`|`9325ee62a40e90d7d0325b3b0198b26139ad9549`|

Evidence: `../evidence/moving_head_check.json` and `remote_refs_end.tsv`.
