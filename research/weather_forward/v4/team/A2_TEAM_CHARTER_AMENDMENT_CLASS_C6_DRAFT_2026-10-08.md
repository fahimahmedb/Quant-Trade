# Amendement à la charte A2 : élément 6 de la classe C délégué sous conditions — PROJET

```text
DOCUMENT_STATUS = DRAFT_PENDING_EXPLICIT_OWNER_RATIFICATION
AMENDS = charte A2 §5 bis, point 2, élément 6 de la classe C
EFFECT_BEFORE_RATIFICATION = NONE
```

Date : 2026-10-08. Demande d'Owner (conversation) : retirer l'élément 6 de la classe C, aux conditions proposées par le Builder. Seul cet élément est visé. Ce texte n'a d'effet qu'une fois ratifié par Owner à son commit et son blob exacts.

## 1. Élément retiré de la classe C

Élément 6, tel que nommé au §5 bis, point 2 : « Autorité d'exécution E, activation de la root, opération A2 ». Les huit autres éléments restent réservés à Owner, y compris le 5 (actions sur la VM d'Owner).

## 2. Conditions cumulatives (toutes, sinon l'élément redevient réservé)

1. **Revue indépendante :** le lot 3 est mené par une Astra neuve et conclut `PASS_FOR_OWNER_LOT4_CONSIDERATION`, cité par commit et blob exacts.
2. **Conditions propres d'E :** chaque condition du point B.5 d'E est prouvée selon son autorité propre. La présente délégation n'en remplace aucune, notamment la qualification de la VM (L2-A), qui reste une action sur la VM donc réservée (élément 5).
3. **Périmètre :** route D2 uniquement, `READ_INPUT` seul. Aucune libération de sortie (`RELEASE_OUTPUT`), aucune levée de quarantaine, aucune déclaration de `t0`.
4. **Aucune ressource réelle :** ni donnée réelle, ni endpoint ou credential opérationnel, ni dépense, ni capital (éléments 1 à 4 inchangés).
5. **Auteur et ratificateur différents,** justification économique et critère falsifiable écrits (§5 bis, point 3), consignation avec commit et blob exacts, mention `RATIFIE_PAR_DELEGATION`.
6. **Révocabilité :** un commentaire `STOP` d'Owner sur la PR suspend l'élément ; l'arrêt automatique du §5 bis, point 4, s'applique.

## 3. Limites

Aucune activation n'est autorisée par ce texte seul. Il ne crée aucune autorité économique, de capital réel, de trading réel ou de fusion.

```text
CLASS_C_ELEMENT_6_DELEGATED_UNDER_CONDITIONS = TRUE_ONLY_IF_RATIFIED
CLASS_C_ELEMENTS_1_2_3_4_5_7_8_9_RESERVED_TO_OWNER = TRUE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```
