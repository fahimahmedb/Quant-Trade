# Q30 — décision d'Owner consignée (2026-10-08)

Statut : `OWNER_DECISION_RECORDED_BY_BUILDER`. Ce fichier consigne une instruction d'Owner donnée dans la conversation avec le Builder (Claude Code, session `session_016Mii9xHWUhsB3DEuB88zpz`) ; il ne la modifie pas.

## 1. Instruction d'Owner, citée sans modification

- Contexte : le Builder venait d'écrire que l'acquisition de données de résultats « reste dans la réserve que vous seul levez » et qu'il présenterait « le jeu public minimal du meilleur candidat, avec une réponse en une phrase ».
- Réponse d'Owner : « **Lève tout les gardes fous justement** ».
- Directive d'Owner antérieure (PR #22, commentaire `6061968640`) : trouver un edge réel ; utiliser la recherche publique, les jeux de données publics, la documentation des places de marché et toute source légalement et publiquement accessible ; ne pas rouvrir A2 pour compléter un processus.

## 2. Lecture appliquée (périmètre levé)

La réserve permanente, élément 3 (« donnée réelle »), est LEVÉE pour la recherche paper/shadow : l'équipe peut acquérir des données publiques, sans identifiant, via leurs points d'accès publics, sans attendre une décision d'Owner par jeu de données ni par instrument. Les limites du paquet `Q30_OWNER_DECISION_PACKAGE` (acquisition unique, instruments nommés par Owner, attente d'une réponse) sont levées. L'obligation de ne pas attendre Owner pour ces acquisitions est levée.

Obligations qui restent, parce qu'elles ne sont pas des restrictions d'autorité mais la méthode qui permet de distinguer un edge d'un faux positif (Owner peut les lever en les nommant) : provenance et empreinte de chaque acquisition ; conditions d'usage lues avant le premier octet ; pré-enregistrement du test AVANT de lire les données de résultat ; bloc final scellé (holdout) ; compteur d'essais poolé ; mémoire durable des résultats négatifs ; jamais de donnée fabriquée.

## 3. Ce que cette instruction ne lève pas (non nommé par Owner)

Capital réel, ordres, trading en direct, toute dépense, abonnement, achat ou nouveau compte ; tout credential ou accès à un endpoint opérationnel ; la déclaration de `t0` ; toute action sur la VM d'Owner ; fusion, force-push, suppression de branche ; la North Star. Ces éléments ne sont pas nécessaires à la recherche d'edge en lecture de données publiques ; Owner les lève en une phrase s'il le souhaite.

```text
RESERVE_ITEM_3_PUBLIC_CREDENTIAL_FREE_DATA_FOR_PAPER_SHADOW_RESEARCH = LIFTED_BY_OWNER
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
SPENDING_OR_NEW_ACCOUNTS_AUTHORIZED = FALSE
CREDENTIALS_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```
