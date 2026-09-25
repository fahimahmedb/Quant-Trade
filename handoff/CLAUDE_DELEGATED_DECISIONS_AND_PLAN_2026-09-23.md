# Décisions déléguées et plan d'exécution — 2026-09-23

> Le propriétaire a délégué ces décisions au Builder (Claude Code) le 2026-09-23 : « prends autant de décisions que possible, aligné ».
> Base factuelle : `handoff/CLAUDE_PROJECT_REVIEW_AUDIT_2026-09-23.md`.
> Ces décisions prennent effet comme direction de travail. Blue doit les ratifier avant de les inscrire dans `CURRENT_GOVERNANCE_STATE`.
> **Aucune ne touche le capital réel, l'hôte cible, ni les branches d'autrui.**

```text
ECONOMIC_PROGRESS  = passer de « zéro évidence » à une décision GO/NO-GO chiffrée, nette de frictions, en ~10 semaines
REMAINING_BLOCKER  = défauts P0 bloquants ; verdict économique non contraignant ; géométrie gelée non puissante
EXIT_CONDITION     = V4.1 scellé et Gate-B exécuté ; vertical réparé et reçu ; lecture unique du holdout de la voie rapide
```

## D0 — Invariants inchangés

- `REAL_CAPITAL_AUTHORIZED = FALSE`.
- Paper/shadow uniquement.
- Aucune mutation de l'hôte depuis une session Builder.
- Aucun merge vers master, suppression de branche ou force-push sans le propriétaire.
- Le run `gate-b-31f4fa2e…` tentative 1 reste l'unique réservation : **ne pas en réserver d'autre**.

## D1 — Rail A : pas de scellement sur V4 en l'état

- **Candidat P0 V4.1** = V4 `4d06bdb` plus trois correctifs, et rien d'autre :
  1. **P0-B1** — réconciliation bornée. Un jour qui a des filings manquantes n'est plus redemandé en boucle : backoff exponentiel borné, puis état terminal « réconcilié avec gap ouvert ». Les gaps sont idempotents, un par jour. Les accessions manquantes sont mises en file si la machinerie de tâches le permet proprement.
  2. **P0-B2** — calendrier EDGAR 2027 :
     - Il est lié avec une provenance explicite : page officielle SEC si 2027 y est publié ; sinon règle fédérale 5 U.S.C. 6103, marquée `DERIVED_PENDING_SEC_PUBLICATION`.
     - Une année non liée ne bloque plus que la réconciliation, jamais la découverte.
     - Alerte DEGRADED 45 jours avant une année non liée.
  3. **H3** — `sec-serve` n'amorce plus le Desk ni la recherche. L'empreinte d'acquisition devient la **fermeture d'imports du point d'entrée SEC** au lieu de tout `src/`. Une fusion de code produit ne réinitialisera plus l'identité P0.
- Ensuite :
  - Blue lie les digests V4.1 et Route-1 dans l'enveloppe, puis régénère le relais.
  - Le propriétaire fait la session root (fenêtre de 4 h).
  - Suivent Gate-B, t0, puis Gate C (≈ 6–8 jours).
- Prévérifications opérateur ajoutées au relais :
  - aucun `nftables.service`, firewalld ni ufw susceptible de vider le ruleset ;
  - aucun reboot pendant la campagne ;
  - accès à l'hôte par un chemin autre que 443 confirmé avant l'installation du blocage tcp/443.
- Reportés après Gate-B (backlog P0) : alerting `OnFailure=` et dead-man externe, indexation du stockage (coût quadratique), sandbox systemd, borne de décompression, outil de quarantaine de journal, cause de reboot pré-autorisée.

## D2 — Rail B : R1 et réparation bornée, puis re-vérification ciblée

- **R1** : `economics/{consistency,journal,sizing}.py` sont reclassés ADAPT avec leurs nouveaux blobs, et l'attestation est corrigée.
- Correctifs obligatoires :
  - **V-B1** : pas d'ordre sur le Book capital sans admission économique éligible liée à la stratégie (sinon NO_TRADE motivé). Le chemin inline passe par les contrôles de cohérence de coûts.
  - **V-B2** : la frontière d'admission refuse ce qui suit :
    - un artefact synthétique ;
    - des labels incohérents ;
    - un D19 incomplet ;
    - une FORWARD_CONFIRMATION sans reçu valide ni qualification non synthétique.
    - Elle lie aussi `spec` à `protocol_hash` et `allocation_constructor_id`.
  - **V-H1** : ordre = cible − sleeve courant, jambes à zéro incluses.
  - **V-H2** : admission reconstruite depuis le journal, avec contrôle du cycle de vie.
  - Gardes NaN/inf sur l'ADV et la marge.
  - Les sorties de pure réduction de risque sont exemptées du halt de drawdown et du blocage ADV.
- Re-vérification indépendante **limitée** à ces points et à l'identité d'import, avec sondes exécutables obligatoires.

## D3 — Une seule ligne de code

- Une fois D1 et D2 reçus, créer une branche d'intégration unique : code V4.1 et vertical portés (pas de fusion d'historiques : tronc et V4 n'ont aucun ancêtre commun).
- Grâce à H3, l'identité P0 = digest de la fermeture SEC. Le produit peut donc évoluer sans réinitialiser t0.

## D4 — Science : lignée gelée suspendue, pas abandonnée

- Le constat G ≈ 1 est reçu comme **nouvelle contradiction reproduite** (aucun rendement consulté).
- L'activation de la cohorte 1 de `FORM4_FIRST_VERTICAL_MULTI_COHORT_V1` est **suspendue**. Elle n'a jamais démarré et aucun rendement n'a été lu.
- Après la décision de la voie rapide, elle est remplacée par une **lignée prospective de confirmation du ou des finalistes** :
  - portefeuille en temps calendaire ;
  - bootstrap par blocs de 80 séances ;
  - regards séquentiels O'Brien–Fleming à 6, 12, 18 et 24 mois.
- Enregistrement avant toute activation.

## D5 — Voie rapide `QUANT_FASTLANE_HPIT_V1` autorisée

| Paramètre | Valeur figée à pré-enregistrer |
|---|---|
| Événements | SEC *Insider Transactions Data Sets* (trimestriels, depuis 2006T1, gratuits, tels que déposés). Form 4 originaux seulement (4/A exclus), code transaction P. |
| Entrée | Ouverture de la première séance strictement postérieure à la date de dépôt. Le calendrier de séances est celui du fournisseur de prix (pas de calendrier inventé). |
| Découpage | Découverte 2006-01-01 → 2018-12-31 ; walk-forward 2019-01-01 → 2021-06-30 ; **holdout scellé 2021-07-01 → 2026-06-30, une seule lecture**. |
| Inférence | Rendement net quotidien, en excès de SPY, d'un portefeuille en temps calendaire. Bootstrap par blocs de 80 séances. FF5+UMD en robustesse. |
| Multiplicité | M ≤ 48 variantes déclarées d'avance. Deflated Sharpe et Romano-Wolf/SPA en découverte. ≤ 3 finalistes. Holm, α famille = 0,05 sur le holdout. |
| Frictions | Spread Abdi–Ranaldo avec plancher, plus commission. Participation ≤ 0,1 % ADV20. Délisting manquant = −30 % (−100 % en stress). Capacité à 1×, 10× et 100× C0. |
| **Critère GO** | Alpha net annualisé vs SPY ≥ 3 %/an **et** p ajusté Holm < 0,05 **et** positif à 1× C0 après frictions **et** DSR > 0,95. Sinon NO-GO, enregistré comme résultat. |
| Prix | Fournisseur **incluant les délistés** : Sharadar (Nasdaq Data Link : SEP, ACTIONS, TICKERS avec CIK) en principal, EODHD en repli. **L'achat est une action du propriétaire.** Sans lui, seul le travail aveugle aux rendements est autorisé. |
| Pare-feu | Espace `var/fastlane/`, ledgers propres, aucune écriture vers la lignée gelée. Le hash de pré-enregistrement est commité avant tout accès aux rendements. |

## D6 — Nouvelle classe d'évidence `HISTORICAL_PIT_VALIDATION`

- Reçus exigés :
  - pré-enregistrement scellé antérieur à l'ouverture du holdout ;
  - consommation du ledger d'usage ;
  - registre de multiplicité ;
  - attestations point-in-time et survivant.
- Autorité conférée : `SHADOW_PROVISIONAL` **paper**, plafonnée :
  - lignée ≤ 20 % de la NAV paper ;
  - ligne ≤ 2 % de la NAV ;
  - participation ≤ 0,1 % ADV20.
- Rétrogradation automatique si l'un de ces cas survient :
  - écart d'exécution > modèle + 25 bp sur au moins 50 fills ;
  - drawdown de la lignée > 15 % ;
  - rupture de provenance.
- Ne confère **jamais** FORWARD_CONFIRMATION ni de capital réel.

## D7 — Process

- Un seul fichier d'état vivant. Les routeurs ne contiennent que l'ordre de lecture.
- Un fichier vivant par sujet, amendé sur place.
- Une revue n'est recevable que si elle est bornée par invariant et accompagnée de sondes exécutables.
- Suppression du lot de branches prêtes : **action du propriétaire**.

## Ordre d'exécution

| # | Travail | Propriétaire | Statut 2026-09-23 |
|---|---|---|---|
| 1 | Revue et audit | Builder | FAIT (`edfbb0a`) |
| 2 | Ces décisions | Builder, sous délégation | FAIT (ce fichier) |
| 3 | V4.1 (D1) | Builder | **En attente d'autorisation** : branche de livraison |
| 4 | Réparation du vertical (D2) | Builder | **En attente d'autorisation** : branche de livraison |
| 5 | Voie rapide, semaines 0–2 : pare-feu, ingestion EDGAR, recensement aveugle, interface prix | Builder | **FAIT, puis protocole SCELLÉ** (`9c8350d`, voir ci-dessous) |
| 6 | Achat du fournisseur de prix | **Propriétaire** | Reporté par le propriétaire le 2026-09-23 |
| 7 | Scellement Gate-B, puis consommation | Blue, puis **propriétaire root** | Après 3 |
| 8 | Voie rapide, semaines 3–10, lecture unique du holdout | Builder, puis revue indépendante | Après 5 et 6 |
| 9 | Ratification D4/D6 et fichier d'état unique | Blue ou propriétaire | Ouvert |

## État au 2026-09-24 — voie rapide scellée

```text
FASTLANE_PREREG = SEALED
PROTOCOL_SHA256 = sha256:78b3a501e609e135def64783f53f0f02ecbc8df2ea3d86e99c4d00fa206a6999
SEAL_COMMIT     = 9c8350d  (branche claude/project-review-audit-q5kfb9, poussée)
SEALED_AT_UTC   = 2026-09-24T23:32:08Z
OUTCOME_ACCESS  = NONE (aucun prix ni rendement lu)
```

**Ce qui est fait :**
- Données SEC : 82 trimestres (2006T1–2026T2, 922 Mo), avec les liens lus sur la page d'index SEC. Le contact du User-Agent vient de l'environnement et n'est enregistré nulle part.
- Table d'événements primaire commitée : `research/fastlane/data/events_primary_v1.jsonl.gz` (13,8 Mo, 360 115 lignes).
- Événements après filtres (titre action ordinaire, notes de bas de page de transaction, doublons, antidatés) :

| Split | Jours émetteur | Par an |
|---|---|---|
| Découverte | 182 071 | 14 006 |
| Walk-forward | 27 173 | 10 869 |
| Holdout | 51 274 | 10 255 |

- Filtre gelé (proxy) : environ 1 550–2 300/an. C'est 3 à 7 fois plus que l'hypothèse de l'audit.
- Quadrillage **M = 22**. Il inclut la cellule gelée littérale `FROZEN_FV_10S_V0_H20`. Six cellules sont écartées par la règle d'adéquation, qui ne regarde que les comptes.
- Puissance recalculée avec 8 % de tracking error : l'effet minimal détectable sur le portefeuille est **≈ 11 %/an à K = 100** (13 % au premier pas de Holm).
  - Conséquence : un edge réel de 3–8 %/an sortira probablement **INCONCLUSIVE**, pas GO.
  - C'est une limite honnête du holdout de 5 ans, pas un défaut.
- Revue adversariale indépendante en 3 tours :
  - tour 1 : 9 bloquants, dont la falsification d'autorisation et l'annulation de la lecture unique ;
  - tour 2 : 4 bloquants (comptage des essais, clone superficiel, faux « publié », force-push) ;
  - tour 3 : **SEAL_READY**.
- Tests : 485 OK. Demo 35/35. Schémas OK.

**Actions du propriétaire pour sécuriser le sceau** (risques résiduels acceptés, qui ne se couvrent pas en code) :
1. Protéger la branche `claude/project-review-audit-q5kfb9` sur GitHub : pas de force-push, pas de suppression.
2. Consigner hors du dépôt (note datée, e-mail à soi-même…) : `SEAL_COMMIT = 9c8350d`, `PROTOCOL_SHA256 = sha256:78b3a501…`, puis plus tard le commit de `HOLDOUT_REQUEST.json`.

**Prochaines étapes :**
- **Sans achat, sans lire de rendement :** le constructeur de portefeuille et le moteur d'évaluation (période de découverte seulement) sont codés et testés sur fixtures.
- **Dès que le fournisseur de prix est acheté** (clé Sharadar, secret `NASDAQ_DATA_LINK_API_KEY`) :
  - manifestes vendeur et carte des délistings dérivée de la documentation, commités ;
  - puis `git fetch --unshallow` ;
  - criblage des 22 variantes sur la découverte et le walk-forward ;
  - au plus 3 finalistes ;
  - requête holdout commitée ;
  - **lecture unique** → GO / INCONCLUSIVE / NO_GO.

## État au 2026-09-25 — moteur d'évaluation prêt à être épinglé

```text
EVALUATION_ENGINE = PIN_READY (revue indépendante, 290d8c7)
TESTS             = 525 OK ; demo 35/35 ; schémas OK
OUTCOME_ACCESS    = NONE
```

**Livré :**
- `evaluation.py` : portefeuille en temps calendaire, ADV20 point-in-time, slots, frictions, sorties, délistings, purges.
- `inference.py` : bootstrap par blocs studentisé, HAC fixed-b, DSR avec plancher de variance, Holm, Romano–Wolf/SPA.
- `screen.py` : les 22 variantes, essais sûrs en cas de crash, au plus 3 finalistes.
- `verdict.py` : GO / INCONCLUSIVE / NO_GO, capacité, stress, robustesse aux seeds.
- La lecture unique **recalcule** le criblage. Rapport, spec et requête sont commités ensemble.
- 25 clarifications déposées avant tout rendement : `research/fastlane/PROTOCOL_CLARIFICATIONS_PRE_OUTCOME.md`.
- C16 : valeur critique fixed-b = la plus conservatrice entre la simulation et Kiefer–Vogelsang, soit 1,8663.

**Lot « avant criblage »** (à faire quand la clé fournisseur existera, **avant** le premier `screen`) :
1. Brancher l'adaptateur Sharadar :
   - SEP, ACTIONS converties en SPLIT/CASH_DIVIDEND ;
   - TICKERS pour le mapping CIK → titre point-in-time ;
   - SPY total return ;
   - carte des délistings dérivée de la documentation.
   Puis une **revue indépendante** de cet adaptateur, qui fait partie de l'empreinte de code.
2. La grant holdout appelle elle-même `screen.recompute_and_verify` (au lieu d'accepter un reçu en processus).
3. Des checkpoints append-only du ledger d'accès sont commités dans `research/fastlane/`. Chaque checkpoint prolonge le précédent, ce qui survit au conteneur éphémère.
4. `git fetch --unshallow`, puis le criblage (découverte et walk-forward), puis la requête holdout commitée, puis **une seule lecture**.
