# V4 Discovery Lane — Exigences opérationnelles

## A. Objet

Cette voie est le **front-end de recherche** du projet Quant-Trade. Elle doit maximiser le débit d'information économique avant toute validation lourde.

Le moteur `research/edge_lab` existant reste la voie de **validation stricte**. La Discovery Lane ne remplace pas ses protections ; elle décide quelles idées méritent d'y entrer.

---

## B. MUST — exigences non négociables

### R1 — Capital/live

- `REAL_CAPITAL_AUTHORIZED = FALSE`
- `LIVE_TRADING_AUTHORIZED = FALSE`
- Aucun ordre réel, aucune production, aucun achat de données/compte/API payante sans autorisation explicite.

### R2 — Intégrité scientifique minimale

Avant tout calcul, sauvegarder :

- mécanisme ;
- règle testée ;
- proxy ;
- fenêtre ou protocole de sampling ;
- coûts approximatifs ;
- critères `KILL_IF` et `PROMOTE_IF`.

Après exposition au résultat, toute modification substantielle crée **une nouvelle expérience exploratoire** et ne peut pas être présentée comme vierge.

### R3 — Pas de faux edge

Un résultat Discovery porte obligatoirement le label `EXPLORATORY`. Il ne peut jamais conclure `EDGE_VALIDATED`, `LIVE_READY` ou `REAL_CAPITAL_READY`.

### R4 — Timebox

- L1 : maximum **60 minutes** de travail agent cumulé avant décision intermédiaire.
- L2 : maximum **120 minutes** avant décision.
- Toute extension doit expliquer quelle information nouvelle exacte sera obtenue.

### R5 — Deux cycles sans information = PARK

Une piste qui consomme deux cycles consécutifs sans produire l'un des éléments suivants est parkée :

- nouveau résultat ;
- nouveau dataset réellement utilisable ;
- falsification d'une hypothèse ;
- changement de décision ;
- réduction substantielle d'incertitude.

### R6 — Architecture tax

Aucune tâche d'architecture > 1 cycle n'est permise sauf si :

- elle débloque ≥ 2 expériences économiques distinctes, ou
- elle corrige un risque de corruption de résultats.

Sur une fenêtre glissante : **architecture ≤ 10 %** de l'activité du worker.

### R7 — Une expérience = une question

Chaque carte Discovery doit répondre à une seule question discriminante. Interdit de créer un framework général à la place du test.

### R8 — Pas de WAIT bloquant

Les seuls états de Discovery sont :

- `TEST_NOW`
- `RUNNING`
- `KILL`
- `PROMOTE`
- `PROMOTE_HIGH`
- `PARK`
- `PARK_UNTIL`

`PARK` et `PARK_UNTIL` ne bloquent jamais le choix d'une autre piste.

### R9 — Diversification causale

Le worker ne peut pas travailler plus de deux expériences consécutives de la même famille, sauf si la seconde est la validation immédiate d'un résultat déjà obtenu dans le premier cycle.

### R10 — Le test le moins cher d'abord

Si un proxy L1 peut tuer la piste, il doit être préféré à une collecte L3/L4. Une infrastructure lourde avant L1 nécessite une justification explicite.

---

## C. SHOULD — exigences fortes

### R11 — Upper-bound falsification

Quand possible, tester une hypothèse dans des conditions **favorables**. Si même la borne haute économique est mauvaise, `KILL` immédiatement.

### R12 — Coûts pessimistes simples

Au L1, préférer un coût fixe légèrement défavorable plutôt qu'une semaine de reconstruction historique des frais.

### R13 — Réplication avant invention

Au moins 30 % des nouvelles expériences doivent être des réplications/adaptations d'effets documentés publiquement ou observés sur un marché voisin.

### R14 — Prioriser le payeur

Une hypothèse avec `WHO_PAYS = UNKNOWN` est moins prioritaire qu'une hypothèse avec payeur structurel identifiable.

### R15 — Prospective quand mémoire historique dangereuse

Pour annonces politiques, news, événements célèbres ou thèmes largement connus d'un LLM, préférer un test prospectif court ou un protocole chronologique figé avant collecte.

---

## D. KPI et SLO

### KPI principal

`DISCRIMINATING_TESTS_COMPLETED_PER_WEEK`

### Cibles

| Mesure | Cible |
|---|---:|
| Tests discriminants / semaine | >= 10 |
| Familles causalement distinctes / semaine | >= 2 |
| Temps médian idée → verdict L1 | <= 90 min |
| Part architecture | <= 10 % |
| Part recherche économique directe | >= 90 % |
| Cycles sans info avant PARK | <= 2 |
| Tests KILL/PARK | >= 60 % |
| Promotions vers validation | 1–3 / semaine si le signal le justifie |

Aucune obligation artificielle de produire une promotion si les données sont mauvaises.

---

## E. Schéma de carte d'expérience

```yaml
id: string
family: string
status: TEST_NOW|RUNNING|KILL|PROMOTE|PROMOTE_HIGH|PARK|PARK_UNTIL
level: L1|L2
mechanism: string
who_pays: string
why_persist: string
question: string
proxy: string
known_biases: [string]
fixed_rule: string
cost_assumption: string
max_time_minutes: integer
kill_if: string
promote_if: string
exposure_before_run: [string]
result: null|string
decision: null|string
next: string
```

---

## F. Contrat de promotion vers V3

Une carte `PROMOTE` doit transmettre au moteur strict :

1. mécanisme ;
2. payeur ;
3. test Discovery exact ;
4. résultat ;
5. biais connus ;
6. toutes les expositions/variantes ;
7. ce qui manque pour L3 ;
8. proposition de protocole gelé ;
9. raison économique pour laquelle le coût de validation est désormais justifié.

Le V3 ne doit pas refaire l'exploration. Il doit vérifier la capturabilité/robustesse du candidat promu.

---

## G. Contrat d'échec

Un `KILL` ferme **l'expression exacte** testée et conserve le mécanisme parent seulement si une autre expression est causalement distincte.

Un `PARK` conserve la piste sans priorité active. Pour la réactiver, il faut :

- une nouvelle donnée réellement accessible ;
- une nouvelle réduction de coût ;
- une nouvelle hypothèse distincte ;
- ou la disparition vérifiée du blocage.

Simplement « réessayer » n'est pas une raison suffisante.

---

## H. Critères d'acceptation de V4

V4 est considéré correctement appliqué lorsque :

- une tâche `RECOVERY_NEEDED` du moteur strict ne peut plus bloquer la Discovery Lane ;
- la queue Discovery contient au moins 3 expériences immédiatement testables ;
- le worker choisit la prochaine expérience par valeur d'information/coût, pas par ancienneté de WAIT ;
- une expérience peut utiliser un proxy L1 sans satisfaire les 7 gates V3 ;
- aucune architecture nouvelle n'est créée pour un blocage isolé ;
- au moins un premier test Discovery est exécuté et archivé sous cette structure.
