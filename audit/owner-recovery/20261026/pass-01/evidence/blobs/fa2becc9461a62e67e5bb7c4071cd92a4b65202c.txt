# Revue complète du projet Quant — état, chemin critique, audit, voie rapide

> **Statut : NON-AUTORITAIRE.** Revue indépendante du Builder (Claude Code), 2026-09-23.
> Elle n'amende ni la gouvernance Blue, ni la spec gelée, ni les octets V4.
> Elle apporte des constats reproduits que Blue peut recevoir ou rejeter.
> Méthode : lecture de la gouvernance courante, puis 5 audits parallèles et indépendants (état, vertical économique, runtime P0/Gate-B, process, voie rapide).
> Les constats critiques ont été re-vérifiés dans le code par l'agent principal.
> Sondes reproductibles : scratchpad de session (`audit_vertical/`, `audit_runtime/`, `fastlane/geom_power.py`).

```text
ECONOMIC_PROGRESS  = aucune évidence économique sur l'edge à ce jour (ni historique, ni prospective)
REMAINING_BLOCKER  = (A) seal Gate-B ; (B) réception finale du vertical ; (science) lignée gelée quasi-certaine d'échouer
EXIT_CONDITION     = décision go/no-go chiffrée sur l'edge Form 4 en mois, pas en années
```

---

## 0. En bref

1. **Le constat le plus important est scientifique, pas logiciel.**
   - La lignée prospective gelée `FORM4_FIRST_VERTICAL_MULTI_COHORT_V1` (3,6–5,0 ans) va **presque certainement se terminer en `INSUFFICIENT_CLUSTER_INFORMATION`**.
   - La cause : la règle de composantes gelée relie deux événements dès que leurs fenêtres d'influence se chevauchent (|Δentrée| ≤ 79 séances, tous émetteurs confondus). Chaque cohorte s'effondre alors en ~1 composante, et le garde-fou G ≥ 10 devient inatteignable (§3.1).
   - Ce raisonnement n'utilise aucun rendement : Blue peut le recevoir **maintenant** sans contaminer le one-look.
2. **Rail A (Gate-B) avance mais le binaire P0 V4 a 2 défauts bloquants.** Il est gelé et c'est lui qui sera qualifié. Il faut les corriger **avant** de consommer le run réservé :
   - boucle infinie de requêtes au daily index SEC dès la première filing manquante ;
   - crash certain le **2027-01-01**, car le calendrier EDGAR 2027 n'est pas lié.
3. **Rail B (vertical économique).**
   - Le seul bloquant Astra est réel mais cosmétique : 3 fichiers REUSE_AS_IS modifiés.
   - L'audit trouve 2 vrais bloquants économiques qu'Astra a manqués :
     - **le Desk trade le Book capital même quand le verdict économique est KILL** ;
     - **l'admission accepte un artefact synthétique sans reçu ni qualification**.
   - Aujourd'hui, **le verdict économique ne contrôle pas le capital**.
4. **Le process coûte plus qu'il ne produit.**
   - Il y a 2,6 lignes de prose de gouvernance par ligne de code, 88 branches et des routeurs périmés.
   - Deux réceptions Blue ne sont pas sur master.
   - Le code est réparti sur **deux historiques Git sans ancêtre commun**.
5. **Phase 3 : une voie rapide est faisable.**
   - Elle prend la forme d'une validation historique point-in-time, avec un holdout scellé regardé une seule fois, plus un shadow loop d'exécution.
   - Délai : environ **10 semaines** vers une décision go/no-go chiffrée.
   - Côté Form 4, les données EDGAR sont gratuites et accessibles depuis ce conteneur. Côté prix, il faut une source payante qui inclut les titres délistés.
   - Tant qu'une décision propriétaire n'a pas créé une nouvelle classe d'évidence, cette voie ne peut produire que du DEVELOPMENT.

---

## 1. Où en est-on (vérifié le 2026-09-23)

Aucun push sur aucune branche depuis le 2026-09-21 22:05Z. **Master a un cran de retard sur chaque rail.**

### Rail A — Gate-B / hôte cible

| Élément | État réel |
|---|---|
| Candidat production | V4 `4d06bdb` gelé (Gate A v4 PASS). 423 tests OK. |
| Pack Route-1 | **Livré** : `builder/gate-b-route1-concrete-mutation-pack@929cba2`, CI verte. Il contient nft tcp/443 drop, l'unité egress-guard et le montage synthétique `/var/lib/quant-p0`. `ALLOW_REAL_SEC_NETWORK=false`. Six vérifications restent TARGET_HOST_ONLY. |
| Réception Blue du pack | **Faite mais hors routeur** : `blue/gate-b-route1-seal-integration@738c4a5`, verdict `PASS_TO_FINAL_SEAL_INTEGRATION`, CI verte. Elle n'est ni sur master ni dans GITHUB_BRANCH_HYGIENE. |
| Enveloppe d'activation | Elle contient encore le placeholder `route1_deny_mechanism_reference`. Il faut y lier les digests du pack et régénérer le relais de scellement. |
| Run Gate-B | `gate-b-31f4fa2e…`, tentative 1 : réservé, **non scellé, non consommé**. `GATE_B = NOT_STARTED`, `t0 = NOT_DECLARED`. |

### Rail B — premier vertical économique (Form 4 → SIZE → RISK → FILLS → BOOK → Learning)

| Élément | État réel |
|---|---|
| Builder | `5c8b5b7`, M1–M4 verts, 478 tests OK, demo 35/35. |
| Revue Astra | **BLOCKED** (`astra/first-vertical-independent-review@264f31a`). Bloquant unique A.1 : `economics/{consistency,journal,sizing}.py` ne sont pas identiques au manifeste alors que l'attestation les dit identiques. Les domaines B–J sont jugés « CLEAN ». Remèdes : R1 (reclasser en ADAPT) ou R2 (déplacer vers `desk/`). |
| Ce que fait le vertical aujourd'hui | La chaîne Form 4 n'existe que comme **bibliothèque exécutée par des tests sur fixtures ou objets construits à la main**. Aucune donnée Form 4 réelle ne circule, `assess_and_admit` n'est appelé nulle part en production, et la qualification de méthode est toujours `synthetic_only=True`, donc pas de FORWARD_CONFIRMATION possible. |

### Contradictions de routage (risque de redémarrage)

1. L'ordre de lecture de `CLAUDE.md` pointe vers des fichiers périmés :
   - `BLUE_MASTER_V2_STATE` décrit encore Rail B = cohort geometry et `TARGET_HOST_READY=FALSE` ;
   - `BLUE_CONTEXT_REACQUISITION` dit encore « v4 Builder ACTIVE, P14D STILL_FROZEN ».
   - La vraie surface de reprise est `handoff/BLUE_PROJECT_REACQUISITION_2026-09-21.md` avec `NEXT_BUILD_MISSION.md`.
2. `CLAUDE_CURRENT_MISSION.md` contient un snapshot figé (« Gate A v4 audit dispatched », « P14D STILL_FROZEN »), ce que son propre texte interdit.
3. `BLUE_MASTER_V2_STATE` se contredit sur P14D : HISTORICAL/SUPERSEDED à la ligne 79, STILL_FROZEN à la ligne 247.
4. `CURRENT_GOVERNANCE_STATE_2026-09-20.md` a pour en-tête « 2026-09-21 », et son contenu (bloqueur à 6e4f37d, « next = Astra review ») est déjà dépassé.
5. `GITHUB_BRANCH_HYGIENE` oublie `blue/gate-b-route1-seal-integration` et `astra/first-vertical-independent-review`.

---

## 2. Ce qui reste à faire, dans l'ordre (aligné gouvernance)

Principe de la gouvernance : un bloqueur → un propriétaire borné → une condition de sortie.
Les rails A et B sont **indépendants jusqu'à la sortie P0**. La voie rapide (§4) est indépendante des deux.

### Étape 0 — Hygiène de routage (Blue, dépôt seul, quelques heures)

- Fusionner dans master les réceptions `738c4a5` (pack Route-1) et `264f31a` (Astra).
- Mettre à jour `CURRENT_GOVERNANCE_STATE`, `NEXT_BUILD_MISSION` et `GITHUB_BRANCH_HYGIENE`.
- Réduire `CLAUDE_CURRENT_MISSION.md` à l'ordre de lecture seul.
- Corriger l'ordre de lecture de `CLAUDE.md`.
- *Sortie :* master = état réel, et un seul fichier d'état.

### Rail A

| # | Étape | Qui | Précondition → sortie |
|---|---|---|---|
| A0 | **Nouveau (recommandé) : corriger P0-B1 et P0-B2** (§3.3) dans un candidat V4.1 minimal, en un seul Builder borné, avec re-vérification ciblée. | Builder, puis Astra (périmètre restreint) | Il faut le faire **avant** A1. Sinon on qualifie un binaire qui saturera l'index SEC dès Gate C et plantera au 01/01/2027, puis tout sera à requalifier (t0 compris). *Sortie :* V4.1 vert, digests re-liés. |
| A1 | Lier les digests du pack (et de V4.1) dans l'enveloppe d'activation, puis régénérer le relais. | Blue | *Sortie :* `READY_FOR_OWNER_HOST_SEAL_RELAY`, CI verte. |
| A2 | Relais de scellement sur l'hôte. Pré-vérifications : host-id, **boot-id `919bed…`**, NTP, MainPID=0, tête du registre. | **Humain propriétaire, root** | Si l'hôte a redémarré, il faut d'abord un nouveau rebind en lecture seule. Or la dernière tentative a échoué (`BLOCKED_NO_TARGET_HOST_ACCESS`). |
| A3 | Dans la **fenêtre de 4 h** : vérifications TARGET_HOST_ONLY, consommation unique, phases 1–7 du runbook. | Humain/Opérateur | Le premier échec obligatoire est terminal : il faut alors un nouveau run et une nouvelle activation. |
| A4 | Réception de l'évidence Gate-B → `PASS | BLOCKED`. | Blue | — |
| A5 | Sceller le précommit t0 (événements Gate C planifiés), puis faire un lancement qualifiant → **t0**. | Blue, puis humain | — |
| A6 | Gate C : 5 événements réels (E1 nuit, E2 cycle, E3 week-end ven. 22:00 → lun. 06:00 ET, E4 post-week-end, E5 réconciliation après +30 h). | Surveillance seule | ≈ **6–8 jours calendaires** (inférence : aucun document ne le chiffre). |
| A7 | Gate D → sortie P0 → `PRODUCT_INTEGRATION` réactivée. | Blue | — |

### Rail B (en parallèle du Rail A)

| # | Étape | Qui | Sortie |
|---|---|---|---|
| B1 | Choisir R1 (reclasser les 3 fichiers en ADAPT et corriger l'attestation, sans changement de code). | Blue | Décision. |
| B2 | **Nouveau (recommandé) : réparation bornée des bloquants économiques** V-B1, V-B2, V-H1, V-H2 (§3.2), avec tests adversariaux. | Builder unique | Le verdict économique contrôle réellement le capital, et le Risk approuve le portefeuille réellement simulé. |
| B3 | Re-vérification ciblée (identité d'import, attestation, et les 4 correctifs). | Astra, périmètre restreint | — |
| B4 | Réception finale → `ACCEPTED`. L'intégration produit (Forward → Clock, `assess_and_admit` automatique, `run_lane_entry`) attend A7. | Blue | — |

### Science (décision à prendre avant tout regard sur les rendements)

- **S1.** Transmettre à Blue le constat G ≈ 1 (§3.1). Ce raisonnement n'utilise aucun rendement, et c'est une « nouvelle contradiction reproduite », donc autorisée à rouvrir la géométrie malgré la do-not-reopen list.
- Décider ensuite entre deux voies :
  - (a) re-geler la géométrie **avant** l'activation de la cohorte 1, par exemple avec des clusters par émetteur et un bootstrap par blocs de temps sur un portefeuille en temps calendaire ;
  - (b) conserver la lignée comme simple témoin prospectif.
- **S2.** Aucun document ne fixe l'instant d'activation de la cohorte 1 ni s'il doit attendre Gate D. C'est pourtant l'horloge dominante : décision Blue ou propriétaire.

---

## 3. Audit — points faibles, par sévérité

### 3.1 Scientifique / stratégique

| Sév. | Constat | Preuve | Correctif |
|---|---|---|---|
| **BLOQUANT** | **Le garde-fou G ≥ 10 est inatteignable avec la règle gelée.** Le lien temporel porte sur tous les émetteurs, avec une fenêtre [e−40, e+39]. Deux composantes ne restent donc séparées que si **80 séances ou plus passent sans aucun événement**. En simulation à K=4 : G moyen = 4,8 à 2 événements/an, 2,8 à 25/an et **1,0 à partir de 100/an** ; P(G ≥ 10) = 0,005 à 2/an et **0** partout ailleurs. L'estimation « ~3,6 ans » supposait implicitement ≤ 4 composantes par cohorte séparées par des trous vides. | `wt/vertical/src/quant/science/effect.py:790-829` ; prestage L436-439 et L605-615 ; spec gelée §1 ; `fastlane/geom_power.py` (reproduit par l'agent principal) | Re-geler l'inférence avant la cohorte 1 : portefeuille en temps calendaire et bootstrap par blocs de 80 séances. Sinon, accepter une issue quasi certaine `INSUFFICIENT_CLUSTER_INFORMATION` après ~5 ans. |
| HAUTE | **Zéro évidence économique à ce jour.** Route B (D05/D09) n'a jamais été exécutée (« D05-A empirical pass: NOT YET EXECUTED », « outcome access: NOT AUTHORIZED »). Le projet ne sait pas encore si l'edge Form 4 existe après frictions. | `BLUE_D05_D09_ROUTE_B_CHECKPOINT_2026-09-17.md:296,300` | Voie rapide (§4). |
| HAUTE | **Concentration.** Une seule famille de stratégies (achats d'initiés Form 4), une seule source (EDGAR), un seul hôte, un seul opérateur humain avec accès root, et une seule revue (Astra) qui fait passer tout le reste. | Audit process | Dans la voie rapide, 2–3 familles candidates filtrées large/pas cher, puis étroit/profond (North Star §5). |
| MOYENNE | **Frictions trop légères pour des small caps** : 1 bp de demi-spread, 0,5 bp de commission, impact de 10 bp à 5 % de l'ADV, pas de coût d'emprunt alors que le Desk exécute du long/short. | `wt/vertical/src/quant/desk/execution.py:42-45` | Spread par instrument ou par tranche d'ADV (Abdi–Ranaldo avec plancher) et accrual d'emprunt. |
| MOYENNE | **Données du tronc faibles en provenance.** `nasdaq_composite_daily.txt` est un export opérateur en locale FR, sans URL, sans date de récupération, à volume nul, arrêté au 2026-07-10. L'`adj_close` de Yahoo n'est pas point-in-time. Aucune donnée de délisting (un titre délisté comme SIVB renvoie 404, d'où un biais du survivant). | `data/`, `adapters.py:26` | Métadonnées vendeur et fournisseur incluant les délistés. |

### 3.2 Code — vertical économique (`5c8b5b7`)

| Sév. | Constat | Preuve | Correctif |
|---|---|---|---|
| **BLOQUANT V-B1** | **Le Desk ignore un verdict KILL, DEVELOPMENT_SIGNAL_ONLY ou ADMISSION_REFUSED.** Si l'admission n'est pas éligible, le Desk retombe sur un dimensionnement fraction-de-NAV et trade quand même le Book capital (134 fills dans la sonde). Le test l'affirme comme comportement attendu. Le chemin d'entrée inline saute aussi les deux contrôles de cohérence des coûts. | `desk/desk.py:235-249` (vérifié) ; `tests/test_m3_size_risk_fills_book.py:604` | Admission présente mais non éligible → NO_TRADE. L'entrée passe par `run_lane_entry`. |
| **BLOQUANT V-B2** | **L'admission accepte un artefact synthétique sans reçu forward ni qualification.** Elle ne vérifie ni `synthetic`, ni `evidence_label`, ni `d19_complete`, ni `forward_receipt.valid_for`. Une stratégie `spec={}` est admise sur l'évidence Form 4, ce qui viole « l'évidence décrit la stratégie exécutée ». | `integration/econ_bridge.py:119-172` | Exiger à la frontière non-synthétique, labels cohérents, reçu et qualification, et lier `spec` à `protocol_hash` / `allocation_constructor_id`. |
| HAUTE V-H1 | **`run_lane_entry` ordonne la cible complète au lieu de l'écart cible − position.** Une position déjà détenue double (2 500 → 5 000), et les jambes ramenées à zéro sont ignorées. Le Risk approuve donc un portefeuille qui n'est pas celui simulé. | `desk/economic_size.py:317,337,345` (vérifié) | Ordonner cible − sleeve courant, comme `desk._execute`. |
| HAUTE V-H2 | **M2 → M3 est relié « à la main ».** `run_lane_entry` accepte n'importe quelle admission : un id inventé « A » est BOOKED. Le chemin positif de l'e2e fabrique à la main un artefact `synthetic=False` + FORWARD_CONFIRMATION sans passer par `assemble_form4_effect`. | `tests/test_vertical_e2e.py:57-71,127-132` | Construire l'admission via `journal.get(assessment_id)` et vérifier le cycle de vie. |
| MOYENNE | Un halt de drawdown bloque une **sortie** qui réduit le risque (5 000 titres restent détenus à −30 %). | `desk/risk.py:60` | Exempter les ordres de pure réduction de risque. |
| MOYENNE | Un ADV NaN ou inf marqué AVAILABLE passe la vérification. Une marge NaN dimensionne à `max_fraction`. | `economics/consistency.py:194,237` ; `economics/sizing.py:58-63` | Exiger des valeurs finies strictement positives. |
| MOYENNE | Un crash au milieu des fills dans `run_lane_entry` bloque la lane : le replay recalcule l'échelle sur une NAV post-coûts → FillConflict. Il n'y a pas de journal d'intention. | Sonde P6 | Persister le plan approuvé avant le premier fill. |
| MOYENNE | **Enum présenté comme capacité.** Aucun code de production n'écrit `SHADOW_EXECUTION_FACT` ni `REJECTION_COUNTERFACTUAL`, BOOKED ne contient pas de champs attendu vs réalisé, et il n'y a pas de Learning durable en production. | `economic_size.py:203-208` | Implémenter, ou retirer la prétention. |
| BASSE | Un même Learning peut recevoir deux issues terminales (RISK_VETO et BOOKED). Les évaluations n'expirent jamais. | `economic_size.py:202` | Id indépendant de l'action et TTL. |

**Ce qui est sain :** sleeves et attribution par stratégie sur un instrument partagé, replay exact du Book, Learning durable après redémarrage, timing causal (entrée à la séance strictement postérieure au dépôt EDGAR, signal à la clôture, fill à l'ouverture suivante).

### 3.3 Code — service de capture P0 (V4 `4d06bdb`) et pack Gate-B

| Sév. | Constat | Preuve | Correctif |
|---|---|---|---|
| **BLOQUANT P0-B1** | **Boucle de réconciliation infinie.** Une filing manquante ouvre un gap, mais le jour n'est jamais marqué réconcilié, il n'y a pas de backoff et pas de backfill. `reconciliation_due()` renvoie donc le même jour indéfiniment. Sonde : 30 requêtes identiques en 14,5 s. En production, cela fait ≈ 2 req/s (≈ 170 k/jour) sur le même fichier SEC, avec un état qui croît de ~365 KiB tous les 1 000 cycles. Déclenchement quasi certain, car l'index du jour de démarrage liste des filings antérieures au lancement. Gate-B (réseau SEC coupé) ne le verra pas ; Gate C, si. | `collector.py:1645-1670`, `:860-882` (vérifié) | Mettre les accessions manquantes en file de tâches, et garder le jour « en backfill » avec backoff. |
| **BLOQUANT P0-B2** | **Crash certain le 2027-01-01 à 00:00 ET.** Le calendrier ne contient que 2026 : `EdgarCalendarUnbound` est levé et relancé en mode qualifiant, ce qui tue aussi la découverte (trous irrécupérables). | `calendar.py:33-47,50-56` (vérifié) ; `clock.py:442-443` | Lier 2027 maintenant. Une année non liée ne doit bloquer que la réconciliation. |
| HAUTE | **Un hôte, un processus, aucune alerte.** Après 5 redémarrages en 600 s (superviseur) et `StartLimitBurst=5`, l'unité reste en échec. Il n'y a ni `OnFailure=`, ni `WatchdogSec=`, ni heartbeat hors hôte, ni réplication de `var/sec`. Une panne de nuit devient un trou permanent. | `quant_sec_supervisor.py:36-38` | Notifier `OnFailure=`, ajouter un dead-man externe et répliquer. |
| HAUTE | **Travail de stockage quadratique dans le temps.** Relecture complète du journal à chaque poll, scan linéaire des locators, re-hash de tous les objets à chaque démarrage. | `collector.py:419`, `store.py:378,385-407` | Index SQLite ou index par identité. |
| HAUTE | **P0 couplé à tout le code.** L'empreinte d'acquisition hache tout `src/quant` et `src/autonomous_research`, et `sec-serve` exécute le `boot()` complet du Desk et de la recherche. **Toute fusion de code Desk ou recherche réinitialise donc t0**, et une panne côté recherche arrête la capture. | `fingerprint.py:214-235`, `clock.py:146-171` | Point d'entrée SEC séparé, avec une fermeture d'imports étroite. **À faire dans V4.1** pour ne pas bloquer l'intégration du Rail B. |
| HAUTE | **Garde d'egress Route-1 fragile.** La table nft n'est pas persistante et n'est vérifiée qu'une fois : un `flush ruleset` ou un reboot l'efface pendant que l'unité reste « active ». Un reboot non prévu pendant la bascule démarre sur le réservoir **synthétique**. | Pack route1, unité mount L36-43 | Assertion périodique qui arrête le collecteur si la table manque, et garde au boot. |
| HAUTE | **Pas de verrou d'écrivain unique sur le runtime du tronc** (hors `sec-*`). Avec deux écrivains `Ledger`, un fill sur deux est perdu. | `scripts/quant.py:172-186` | Verrou exclusif global pour run/serve/tick/boot. |
| HAUTE | **Deux historiques Git sans ancêtre commun** : racine du tronc `29d6f49`, racine de V4 `d49290b`. Le `src` du tronc est identique à route1, qui porte donc le collecteur **pré-V4** : ses 460 tests n'exercent pas V4. Le vertical (+11,8 k lignes) ne contient pas V4 non plus. | `git merge-base` vide | Une seule branche d'intégration basée sur V4, où l'on porte le code (pas de fusion d'historiques). |
| MOYENNE | Le pack coupe **tout** le TCP/443 sortant : risque de verrouiller l'opérateur s'il accède à l'hôte en HTTPS (SSM, Tailscale). | `quant-gate-b-egress.nft:22` | Confirmer un accès non-443 avant l'installation, ou cibler uniquement la SEC. |
| MOYENNE | Service en root sans sandbox. Décompression gzip non bornée. | `transport.py:186` | `User=`, `ProtectSystem=strict`, plafond sur la taille décompressée. |
| MOYENNE | Une queue de journal déchirée bloque le service (`ValueError` non capturée), sans outil de quarantaine. Tout reboot est classé `MANUAL_START` et réinitialise la qualification. | `state.py:138`, `store.py:312`, superviseur L177-195 | Commande de quarantaine et cause de reboot pré-autorisée. |
| MOYENNE | Le Book du tronc est un snapshot JSON réécrit à chaque fill (l'idempotence des opérations est correcte), sans journal append-only pour reconstruire. | `ledger.py:155-206` | Faire d'un journal de fills append-only la source de vérité. |

**Ce qui est sain :** 2 req/s, une connexion, User-Agent avec contact et backoff sur 403/404/429, conformes au fair-access SEC. Gestion DST correcte. Idempotence des fills par identifiant d'opération. Tests : V4 423, route1 460, tronc 371, vertical 478, tous OK. Demo 35/35. Schémas OK.

### 3.4 Process / gouvernance

| Sév. | Constat | Chiffres | Recommandation |
|---|---|---|---|
| HAUTE | La prose dépasse le code. | 193 fichiers et ~44 k lignes (1,7 Mo) de gouvernance/handoff, contre 16,8 k lignes de code sur le tronc, soit **2,6 : 1**. Sur 14 jours, les chemins de docs sont touchés 862 fois contre 640 pour src/tests. 30 fichiers « Gate A », 27 amendements D05A/D09 pour un seul sous-sujet. | Un fichier vivant par sujet, amendé sur place (Git garde l'historique). Un doc de gate n'est recevable que s'il cite le delta de code ou de tests qu'il conditionne. |
| HAUTE | Le cycle mission → Builder → réception → Astra → réception finale est lent et incomplet. | Astra a jugé « CLEAN » des domaines contenant V-B1 et V-B2 : elle a testé `assemble_form4_effect`, pas les frontières en aval. La revue n'était pas adversariale sur les invariants économiques. | Revues bornées **par invariant du CLAUDE.md**, chacune avec une sonde exécutable obligatoire. |
| HAUTE | Routeurs périmés et contradictoires (§1). | 5 contradictions. | Un seul fichier d'état, date = nom de fichier, vérifiée par CI. Le routeur ne contient que l'ordre de lecture. |
| MOYENNE | Prolifération de branches. | 88 branches (blue 26, builder 25, astra 14, parallel 11…). Le lot de 35 suppressions « prêt » n'a jamais été exécuté. | Exécuter le lot (action admin humaine). |
| MOYENNE | Dépendance humaine sur le chemin critique. | Seul le propriétaire a l'accès root, avec une fenêtre de 4 h ; la dernière tentative a échoué faute d'accès. | Planifier une session hôte dédiée, et prévoir à l'avance le rebind si l'hôte a redémarré. |
| BASSE | Les skills `.claude/` sont légers (78 lignes au total). | — | Rien à changer. |

---

## 4. Phase 3 — voie rapide « quelques mois, pas 4–5 ans »

### 4.1 Pourquoi 3,6–5 ans aujourd'hui

1. **L'historique est exclu par construction** : « no historical dataset can ever serve as forward confirmation » (`dataplane/admissibility.py:5-8`), et la recherche historique reste du DEVELOPMENT (`economics/decision.py:40`).
2. **L'information dépend du calendrier, pas du nombre d'événements.** Il faut K×252 + (K−1)×80 séances, soit 916 à 1 248, avec une seule lecture et aucun arrêt anticipé.
3. **Et d'après §3.1, même au bout de ces 5 ans, la lignée n'atteindra probablement pas le garde-fou.**

La lenteur ne vient ni des données ni de la puissance statistique : elle vient d'un choix de provenance et d'adaptivité. Ce choix est légitime pour la *confirmation*, mais pas nécessaire pour une *décision d'investissement de recherche*.

### 4.2 Design proposé : lignée `QUANT_FASTLANE_HPIT_V1`

Branche proposée : `parallel/claude-fastlane-historical-pit-2026-09-23`.

- **Pare-feu.** Ledger d'usage, ledger d'essais et espace de registre propres. **Aucune écriture** dans `FORM4_FIRST_VERTICAL_MULTI_COHORT_V1`. Le hash d'enregistrement de la spec gelée est scellé **avant** toute ouverture d'un rendement de la voie rapide.
- **Données.**
  - EDGAR full-index et XML Form 4 (codes P) depuis 2004, gratuits et accessibles depuis ce conteneur (200 OK). Environ 1–2 jours de collecte à ≤ 10 req/s.
  - Entrée à l'ouverture suivant `DATE_FILED` : c'est point-in-time sûr (Reg S-T 13(a)(4)) et identique à la règle gelée S06.
  - Seules les filings originales créent des événements ; un 4/A ne crée ni ne modifie d'événement.
  - Prix : **fournisseur payant incluant les délistés** (CRSP, Norgate, Sharadar ou EODHD), plus un ledger d'actions corporatives et un mapping CIK → titre point-in-time.
- **Découpage temporel.**
  - Découverte : 2006–2018.
  - Walk-forward : 2019–2021S1.
  - **Holdout scellé : 2021-07 → 2026-06.** Il est stocké en quarantaine, le hash de pré-enregistrement est commité avant ouverture, et on ne le regarde qu'une fois.
- **Unité d'inférence.** Rendement net quotidien, en excès de SPY, d'un portefeuille en temps calendaire. L'alpha FF5+UMD sert de contrôle de robustesse. Bootstrap par blocs de 80 séances : cela garde la portée de dépendance gelée **sans exiger de trous vides**, et donne environ 15 blocs sur le holdout et 63 sur 20 ans.
- **Multiplicité.** Au plus 48 variantes déclarées d'avance (filtres CEO/CFO, tranches de taille, horizons 5/20/60 j), classées sur la période de découverte par Deflated Sharpe puis testées avec Romano-Wolf ou Hansen SPA. **Au plus 3 finalistes** vont au holdout, avec correction de Holm à α famille = 0,05.
- **Frictions dans les mêmes objets stratégie que le shadow loop.**
  - Positions : 20 slots, chacun plafonné à 0,1 % de l'ADV20.
  - Coûts : spread Abdi–Ranaldo avec plancher, plus commissions.
  - Délistings : rendement de délisting manquant fixé à −30 % ou −100 %.
  - Capacité : courbes à 1×, 10× et 100× C0.
- **Shadow loop en parallèle**, lancé au pré-enregistrement : environ 125 entrées en 3 mois. Il sert de **contrôle d'exécution** (écart d'implémentation détectable ≈ 13 bp), **pas** d'estimation d'effet (erreur-type ≈ 125 bp).

**Puissance** (σ du rendement à 20 j = 14 %, α unilatéral 0,05, puissance 80 %, effet de design 1,5) :

| Événements/an | Effet net minimal détectable, holdout 5 ans |
|---|---|
| 300 | 110 bp |
| 500 | 85 bp |
| 1 000 | 60 bp |
| 2 000 | 43 bp |

Le taux d'événements réel est inconnu (hypothèse 300–800/an pour le filtre gelé). Un recensement **aveugle aux rendements** en semaine 1 le fixera.

### 4.3 Plan en semaines

| Sem. | Livrable | Sortie |
|---|---|---|
| 0 | Amendement de gouvernance, pare-feu, scellement du hash de la lignée gelée | Pare-feu testé |
| 1–2 | Manifeste EDGAR et XML codes P, recensement aveugle, ingestion des prix avec délistés, table titres point-in-time | Taux d'événements connu |
| 3–4 | Constructeur d'événements point-in-time, ledger d'actions corporatives, modèle de frictions (mêmes objets que le Desk) | Tests adversariaux de look-ahead |
| 5 | **Pré-enregistrement scellé**, holdout en quarantaine | Hash commité |
| 5–7 | Criblage large puis étroit sur la découverte et le walk-forward | ≤ 3 finalistes |
| 8 | **Lecture unique du holdout** | GO / NO-GO chiffré, net de frictions |
| 3–20 | Shadow loop d'exécution | Écart d'implémentation mesuré |
| 9–10 | Revue économique et runtime indépendante, puis réception Blue | Décision |

### 4.4 Ce que chaque sortie peut et ne peut pas prétendre

| Sortie | Classe actuelle | Ce qu'elle permet | Interdit |
|---|---|---|---|
| Holdout historique | VALIDATION / DEVELOPMENT | DEVELOPMENT_SIGNAL_ONLY (`decision.py:201-202` exige FORWARD_CONFIRMED) | FORWARD_CONFIRMATION, dimensionnement paper |
| Shadow 3 mois | Évidence d'exécution | Calibrer FILLS et coûts | Estimer l'effet |

**Pour qu'un résultat positif autorise un dimensionnement paper**, il faut une décision propriétaire : créer une classe `HISTORICAL_PIT_VALIDATION`. Ses reçus :

- pré-enregistrement scellé ;
- consommation du ledger d'usage ;
- registre de multiplicité ;
- attestations point-in-time et survivant.

Cette classe donnerait une autorité `SHADOW_PROVISIONAL` plafonnée, avec des déclencheurs de rétrogradation déclarés d'avance (écart d'exécution > modèle + 25 bp, limite de drawdown). Si l'on veut quand même une confirmation forward, elle se fait dans une lignée prospective séparée, avec des regards séquentiels de groupe (O'Brien–Fleming).

### 4.5 Risques principaux

- Biais du survivant.
- Remapping CIK → ticker avec les identités d'aujourd'hui.
- Look-ahead via les 4/A et les restatements du fournisseur (prendre une empreinte des snapshots).
- Sur-ajustement : priors publiés et décroissance post-publication. Le holdout 2021–26 inclut le régime des meme stocks.
- Licence du fournisseur. Les conditions de Yahoo sont limitées à un usage personnel.
- Contamination du one-look gelé si la voie rapide trade des événements de la population gelée : exclure ou sceller ces événements.

---

## 5. Décisions réservées au propriétaire

1. **Rail A** : corriger P0-B1, P0-B2 et le découplage d'empreinte (V4.1) **avant** de sceller et consommer le run Gate-B (recommandé), ou qualifier V4 en l'état.
2. **Lignée gelée** : transmettre le constat G ≈ 1 à Blue pour re-gel **avant** la cohorte 1 (recommandé), ou la conserver comme témoin.
3. **Voie rapide** : l'autoriser, choisir et payer une source de prix incluant les délistés, fixer les dates du holdout et le budget de multiplicité (M, finalistes, α), le seuil économique net et le C0 paper.
4. **Gouvernance** : adopter ou non `HISTORICAL_PIT_VALIDATION`, qui mène à `SHADOW_PROVISIONAL` plafonné.
5. **Hygiène** : exécuter le lot de suppression de branches, et dédier une session hôte root pour A2 et A3.

## 6. Actions immédiates recommandées (sans attendre ces décisions)

1. Étape 0 (routage) ; décision R1 sur le Rail B.
2. Un Builder borné pour V-B1, V-B2, V-H1 et V-H2 (vertical) ; un Builder borné pour P0-B1 et P0-B2 (V4.1).
3. Transmettre §3.1 à Blue (aucun rendement impliqué).
4. Démarrer les semaines 0–2 de la voie rapide : pare-feu, recensement EDGAR aveugle, choix du fournisseur. Ces étapes n'engagent aucune lecture de rendement.
