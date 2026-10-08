# Amendement à la charte A2 : fin de la ratification par Owner — DIRECTIVE D'OWNER CONSIGNÉE

```text
DOCUMENT_STATUS = RATIFIED_BY_OWNER_PR22_COMMENT_6049466067
AMENDS = charte A2 §5, §5 bis, §7
SUPERSEDES = projet team/A2_TEAM_CHARTER_AMENDMENT_CLASS_C6_DRAFT_2026-10-08.md @ f8ec399 (non ratifié)
```

## 1. Directive d'Owner (conversation du 2026-10-08, citée sans modification)

- « Je ne veux plus à avoir à ratifier rien du tout »
- « Modifie la charte c'est moi qui décide »

**Ratification :** Owner a ratifié ce texte par son propre commentaire sur la PR #22, sans l'en-tête `[A2-TEAM] DE:` : « Je ratifie l'amendement d'autonomie d'Owner de la charte A2, tel que je l'ai demandé » (commentaire `6049466067`, 2026-10-08T00:15:19Z). L'agent qui l'a reçue (Claude Code, `session_016Mii9xHWUhsB3DEuB88zpz`) l'applique dans les limites du §3, sans l'étendre. Le commit et le blob exacts de ce fichier sont donnés dans le commentaire de consignation de la PR #22. Owner peut révoquer par `STOP` sur la PR #22.

## 2. Effet

La ratification d'Owner n'est plus requise pour :

1. les actes de classe A et B (§5 bis, déjà délégués) ;
2. l'élément 6 de l'ancienne classe C (autorité d'exécution E, activation de la root, opération A2), sous six conditions cumulatives : verdict `PASS_FOR_OWNER_LOT4_CONSIDERATION` d'une Astra neuve au lot 3 ; conditions B.5 d'E prouvées selon leur autorité propre ; route D2, `READ_INPUT` seul, sans libération de sortie, levée de quarantaine ni `t0` ; aucune ressource réelle ; auteur et ratificateur différents avec justification économique et critère falsifiable écrits ; consignation avec commit et blob exacts et mention `RATIFIE_PAR_DELEGATION` ;
3. les modifications de la charte et de la délégation qui ne touchent pas la réserve permanente du §3 : elles sont ratifiées par l'agent qui n'en est pas l'auteur, consignées à leur commit et blob exacts, et Owner en est informé par la fiche de reprise.

## 3. Réserve permanente (nommée)

Ces éléments viennent des invariants du projet (`CLAUDE.md`, North Star), pas de la charte ; ils ne sont pas levés par la présente directive. Owner peut en lever un en le nommant.

1. Capital réel, trading réel, tout ordre ou exposition financière.
2. Toute dépense, abonnement, achat, nouveau compte ou service.
3. Tout credential, accès à un endpoint opérationnel, donnée réelle ou métadonnée opérationnelle.
4. La déclaration de `t0`.
5. Toute action sur la VM d'Owner (dont la qualification L2-A).
6. Fusion, force-push, suppression de branche, déplacement d'une référence figée.
7. La North Star, les invariants du projet, et la présente réserve.
8. Les règles d'indépendance d'Astra et toute revue d'Astra.

## 4. Information d'Owner

Owner n'est sollicité que pour un élément de la réserve ou une pause de quota. Chaque ratification déléguée figure dans la fiche de reprise. L'arrêt automatique du §5 bis, point 4, et le `STOP` d'Owner continuent de s'appliquer.

```text
OWNER_RATIFICATION_REQUIRED_FOR_A_B_AND_ELEMENT_6_AND_NON_RESERVE_CHARTER_CHANGES = FALSE
PERMANENT_RESERVE_RAISED = FALSE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```
