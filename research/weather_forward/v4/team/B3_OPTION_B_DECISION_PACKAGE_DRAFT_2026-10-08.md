# B3 — Projet de dossier de décision « Option B » et contrôle de valeur d'A2 (proposition indépendante du Builder)

```text
DOCUMENT_STATUS = DRAFT_ONLY_NO_EFFECT ; BUILDER_PROPOSAL_NOT_AN_OWNER_DECISION
OPTION_B_AUTHORIZED = FALSE ; T0 = NOT_DECLARED ; CAPTURE_AUTHORIZATION = NONE ; REAL_CAPITAL_AUTHORIZED = FALSE
SOURCES_LUES = dossier A1 `blue/BLUE_V4_A1_DOCUMENTATION_2026-10-04.md` @ 49d3d00, §§10 et 11 (extraits), E, rapport Astra lot 3
```

Proposition rédigée **avant** de lire le résultat de Q21 de Codex, pour que les deux avis soient indépendants (stratégie de co-gérance §1). À contester par Codex.

## 1. Contrôle de valeur : où A2 mène réellement

Chaîne documentée dans le dossier A1 : A1 (documentation, faite) → A2 (intégration documentaire hors ligne, en cours) → **Option B** (« phase-gate » séparé d'Owner : poser des questions *techniques* sur endpoint, authentification, schéma, champs, versions, sans mesurer d'efficacité) → capture avec `t0` → test économique. Le dossier est explicite : « A1, Astra PASS et documentation terminée ne peuvent pas accorder B » ; B n'autorise ni valeur, ni distribution, ni cadence, ni motif révélant l'efficacité.

**Conséquence.** A2 et B sont des étapes de **faisabilité sûre**, sans valeur économique directe. Le test d'edge n'existe qu'après la capture (`t0`, données réelles, identifiants), éléments réservés à Owner. Dans le périmètre actuel de l'équipe, **aucune expérience économique n'est exécutable**. Le travail utile restant est de rendre la décision d'Owner peu coûteuse, ou de le dire si la chaîne ne vaut pas son coût.

## 2. Ce qu'Owner doit décider pour que B existe (liste du dossier §10 et §11, rien d'inventé)

| Bloc | Éléments `UNRESOLVED` / `OWNER_DECISION_REQUIRED` | Forme de décision proposée |
|---|---|---|
| Question technique | question sûre exacte, bornes de requête/réponse sans fuite d'efficacité | Owner rédige ; l'équipe ne propose aucun endpoint, modèle, ville ni station |
| Accès | droits, portée des identifiants, acteurs réels | Owner nomme chaque élément ; l'équipe n'obtient aucun identifiant |
| Entrée sûre | restriction avant toute lecture ; isolation, administration, journaux, erreurs, tableaux de bord | attestation d'Owner ; sinon B indisponible (règle du dossier) |
| Bornes de ressources | durée, calcul, stockage, appels externes, accès humain, accès d'agent, volume de sortie, conservation des journaux, budget monétaire | **11 champs, aucune valeur proposée par l'équipe dans ce projet** : Owner choisit, trois niveaux possibles (minimal / moyen / large) avec le coût d'information de chacun |
| Arrêt | binding de stop et d'incident, preuve des acteurs | extension de la matrice d'incident déjà fixée pour D2 |

Taux d'incomplétude du dossier lui-même : `DECLARED_UNRESOLVED_FIELD_COUNT = 41`, `EXHAUSTIVENESS_CERTIFIED = FALSE`.

## 3. Question de fond pour Owner et Codex (choix stratégique, pas une tâche de remplissage)

Valeur d'information attendue de la chaîne A2 → B → capture contre son coût (Owner : temps de terminal, attestations ; équipe : budget d'agents ; risque : exposition d'information d'efficacité). Trois voies à comparer par Codex et moi dans la prochaine planification :
1. **Continuer** la chaîne telle qu'elle est (A2 jusqu'au lot 4, puis dossier B) ;
2. **Geler** A2 à l'état actuel (préparation complète, E sans effet) et réorienter la capacité vers une piste de recherche d'edge qui n'exige ni `t0` ni identifiants, si Q21 en trouve une ;
3. **Arrêter** l'extension d'A2 (règle du feuille de route P2, point 6 de Codex : « si aucune décision de recherche ou de capital n'est améliorée, arrêter ») et le consigner.

**Recommandation du Builder, révisable après Q21 :** voie 2, parce que tout le travail d'A2 réalisable sans Owner est fait ; ce qui reste dépend du terminal d'Owner et ne produit pas de valeur économique par lui-même.

```text
NEXT_SAFE_ACTION = contre-projet de Codex (Q21 puis comparaison des trois voies) ; aucune démarche vers l'Option B sans décision d'Owner
```
