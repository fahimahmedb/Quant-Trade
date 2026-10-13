# Amendement à la charte A2 : ratification déléguée et co-gérance — PROJET

```text
DOCUMENT_STATUS = DRAFT_PENDING_EXPLICIT_OWNER_RATIFICATION
AMENDS = charte A2 (§5, §7) ; ajoute les §5 bis (délégation) et §5 ter (co-gérance)
EFFECT_BEFORE_RATIFICATION = NONE
```

Date : 2026-10-08. Instruction d'Owner : ne plus avoir à ratifier, tant et seulement tant que le projet va dans le sens de la rentabilité et du rendement. Modifier la charte est réservé à Owner (§5.5) : ce texte n'a d'effet qu'une fois ratifié à son commit et son blob exacts.

## §5 bis. Ratification déléguée

**Principe.** Les agents peuvent ratifier à la place d'Owner les actes de la classe A ou B ci-dessous, tant que chaque acte satisfait les conditions du point 3. La rentabilité n'est pas une impression d'agent : c'est un critère falsifiable, jugé par un autre agent que l'auteur. La délégation s'arrête d'elle-même dès qu'une condition n'est plus remplie.

### 1. Classes d'actes

| Classe | Actes | Régime |
|---|---|---|
| A, préparation | gels de contenu, consignations, calculs d'identités, outillage, mise à jour de la file de travail, projets de décisions, relectures | ratification déléguée si les conditions 3.1 et 3.3 à 3.5 sont remplies |
| B, choix de recherche et de conception en paper/shadow | choix d'un candidat de recherche, d'un plan de validation, d'un ordre de priorité entre pistes, arrêt d'une piste négative | ratification déléguée si les conditions 3.1 à 3.5 sont toutes remplies |
| C, réservée | voir le point 2 | Owner seul, quelle que soit la rentabilité annoncée |

### 2. Classe C : jamais déléguée, même si le rendement attendu est élevé

1. Capital réel, trading réel, tout ordre ou toute exposition financière.
2. Toute dépense, abonnement, achat, nouveau compte ou service.
3. Tout credential, clé, accès à un endpoint opérationnel, toute donnée réelle ou métadonnée opérationnelle.
4. Le démarrage d'une capture ou d'une expérience (déclaration de `t0`).
5. Toute action sur la VM d'Owner.
6. Autorité d'exécution E, activation de la root, opération A2.
7. Fusion, force-push, suppression de branche, déplacement d'une référence figée.
8. Modification de la North Star, des invariants du projet, de la présente délégation ou de la charte.
9. Les règles d'indépendance d'Astra et toute revue d'Astra.

Pour élargir cette liste de réserves, Owner nomme chaque élément concerné. Une formule générale ne suffit pas.

### 3. Conditions d'une ratification déléguée

1. **Justification économique écrite dans l'acte :** valeur économique nette attendue après frictions réalistes, lien avec la North Star (edge réel, pas résultat de backtest favorable), et ce qui prouverait que l'hypothèse est fausse.
2. **Critère falsifiable, fixé avant le résultat :** seuil de décision et plan de validation enregistrés avant toute observation. Un résultat négatif est consigné et arrête la piste.
3. **Auteur différent du ratificateur :** l'agent qui a rédigé l'acte n'est pas celui qui le ratifie. Le ratificateur écrit son contrôle (références vérifiées, objections). Pour les actes de risque 2 et plus du §6 bis, ce contrôle émane d'un agent indépendant de l'auteur.
4. **Consignation :** fichier daté, avec commit et blob exacts, la mention `RATIFIE_PAR_DELEGATION`, l'auteur, le ratificateur, la classe, et l'application des points 3.1 à 3.3.
5. **Information d'Owner et révocabilité :** chaque ratification déléguée apparaît dans le tableau de bord de la fiche de reprise. Owner peut tout arrêter par un commentaire `STOP` sur la PR ; les actes déjà consignés restent valables jusqu'à leur révocation écrite.

### 4. Fin automatique de la délégation

La délégation est suspendue, et Owner est alerté, dès que l'un des cas suivants se produit : un acte de classe C est requis ; deux ratifications déléguées consécutives sont contestées par Owner ou par Astra ; un résultat contredit la justification économique d'un acte déjà ratifié ; un budget du §6 bis est dépassé ; une condition du point 3 manque.

## §5 ter. Co-gérance Claude Code / Codex

**Principe.** Les deux agents gèrent le projet à parts égales. Aucun n'est supérieur à l'autre, et aucun ne peut seul modifier la charte ni ratifier un acte de classe C.

1. **Pilote alterné.** Chaque lot a un pilote et un contrôleur. Celui qui n'a pas piloté le lot précédent pilote le suivant ; Codex pilote le premier lot après ratification. Le pilote choisit les tâches de la file, écrit le plan du lot (une demi-page au plus) et consigne le résultat. Le contrôleur relit, peut bloquer par une objection écrite, et ratifie ce que le pilote a rédigé (§5 bis, point 3.3). Un désaccord non résolu en deux échanges va à Owner.
2. **Répartition selon la capacité et le coût, pas au nombre de messages.**
   - Codex : réflexion, rédaction, revue, second avis, lecture ; il peut exécuter des scripts dans son environnement, dont les résultats ne valent qu'une fois revérifiés. Il est préféré pour ces tâches quand son quota le permet.
   - Claude Code : toute écriture sur GitHub, les exécutions et tests officiels, les calculs d'identités consignés.
3. **Publication par scribe.** Tant que Codex ne peut pas publier lui-même, il donne le contenu complet de chaque fichier dans un bloc de code de son commentaire, avec le chemin visé et le SHA-256 du contenu. Claude Code le publie octet pour octet après avoir vérifié ce hachage, et indique « rédigé par Codex, publié par Claude Code ». Un fichier ainsi publié ne contient jamais de décision ni de ratification d'Owner.
4. **Équilibre mesuré sur les lots.** Sur quatre lots glissants, chaque agent en pilote deux. Si la part de rédaction et de revue confiée à un agent dépasse 60 % sans cause de quota, le pilote suivant rééquilibre. Si la cause est un quota (§6 quater), l'agent concerné l'indique et Owner est alerté.
5. **Aucune hiérarchie cachée.** Le pilote ne ratifie pas son propre acte ; le contrôleur ne peut pas écrire à la place du pilote sans le dire ; les deux agents appliquent la ligne `QUOTA:` du §6 quater.

```text
NEW_SUBSTANTIVE_AUTHORITY_CREATED = DELEGATION_OF_CLASS_A_AND_B_ONLY_AND_CO_MANAGEMENT_ROLES
CLASS_C_RESERVED_TO_OWNER = TRUE
REAL_CAPITAL_AUTHORIZED = FALSE
LIVE_TRADING_AUTHORIZED = FALSE
MERGE_AUTHORITY = NONE
```
