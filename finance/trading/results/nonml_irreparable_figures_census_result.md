# **Combien des défauts restants sont irréparables ?** (pré-enregistré)

Le **#482** a découvert une catégorie que le #479 n'avait pas prévue :

> **Une grandeur historique dont l'univers n'est plus reconstructible
> n'est pas réparable — seulement signalable.**

**Aucun des 17 n'avait été classé.** Ce cycle les classe tous.

## La population

- dénombrés au **#479** : **18**
- **rétracté au #482** *(`nonml_reproducibility_sample_lot3_audit` : citation de diff, pas
  tableau)* : **−1**
- **attendus ici** : **17** — **re-dérivés : 17** (**+0**)

## Le proxy mécanique — et son inutilité, mesurée

Le pré-enregistrement le déclarait **faible d'avance**. Il l'est plus
encore que prévu :

- scripts où le proxy répond « la matière première peut exister » : **17 / 17**

> **Il répond « oui » à tous.** Un proxy qui ne discrimine jamais n'a
> **aucun pouvoir de séparation** : il aurait donné le même résultat
> sur n'importe quelle population. **Sa valeur informative est nulle,**
> et c'est mesuré, pas supposé.

La cause est banale : `for … in`, `len(…)`, `sorted(…)` sont présents
dans **tout** script qui rédige un rapport. **J'avais choisi un motif
qui teste « ce script est écrit en Python », pas « il dispose de la
grandeur ».**

## Les verdicts, un par un

**Écrits à la main après lecture de chaque ligne et du code qui
l'entoure.** Aucune règle ne les produit.

### `nonml_battery_backfill_lot_audit.py` — **IRRÉPARABLE**

```python
131:L.append("son overlay **0,00 %** du temps : son P&L est *identique* à celui de Buy & Hold")
```

**Corrigé au #511** : la seule source du script est `read_battery()`, qui relit des rapports `.md` — aucune occurrence de `np.load(` ni `.npz`. Le « 0,00 % » exigerait d'ouvrir une source que le script n'ouvre pas ; ce n'est pas une interpolation, c'est un cycle distinct.

### `nonml_coverage_wording_fix_audit.py` — **IRRÉPARABLE**

```python
133:L.append("examine réellement les **284** scripts `nonml_*_backtest.py` du dépôt, 0 illisible,")
```

**Corrigé au #518** : aucun appel `.glob(` nulle part dans le fichier. « 284 » est un littéral brut dans une chaîne simple, absent aussi du seul fichier que ce script lit. Le cas jugé « le plus trivialement réparable » ne calcule en réalité rien du tout.

### `nonml_marker_emitted_by_scripts_backtest.py` — **IRRÉPARABLE**

```python
103:L.append("| rapport **portant** l'encart, script ne l'émettant pas | **1** |")
104:L.append("| rapport dont le script **l'émet déjà** (rien à faire) | **1** |")
105:L.append("| rapport qui **cite** l'encart sans le porter | **1** |")
... et 2 autres
```

**C'est le #451**, dont le #473 a établi que le script n'énumère **jamais** `results/` : il ne travaille que sur **5 cibles codées en dur**. Les comptes décrivent une classification du dépôt entier **qu'il n'a jamais faite**.

### `nonml_pnl_duplicate_sweep_audit.py` — **IRRÉPARABLE**

```python
207:L.append("**Correction retenue : 1 essai surnuméraire**, soit 372 → **371**.")
```

« **Correction retenue : 1 essai surnuméraire**, soit 372 → **371** » : le **372** est le décompte d'essais du backlog entier, que cet audit ne construit pas et qu'aucun module n'expose. Le recalculer demanderait de reconstituer la comptabilité `n_trials` — **la question précisément en attente d'arbitrage depuis le #421.**

### `nonml_pnl_persistence_exposed_pass_audit.py` — **IRRÉPARABLE**

```python
147:L.append("| candidats mesurés | 33 | **42** |")
148:L.append("| détectés non mesurés | 29 | **20** |")
149:L.append("| dont portant un PASS | 10 | **0** |")
```

**Établi au #482** : les comptes portent sur l'univers du balayage **#415**, que le script n'importe pas et qu'aucun module n'expose. Substituer un décompte moderne mesurerait **autre chose**.

### `nonml_protocol_inventory_audit.py` — **IRRÉPARABLE**

```python
59:L.append("Le compte brut était **19**. Le pré-enregistrement annonçait qu'il ne se conclurait")
124:L.append("| B — résultat sans PREREG | 5 | **0** (variantes résolues) |")
125:L.append("| C — PASS sans batterie | 33 | **6** strictement postérieurs à la Règle 9 |")
... et 4 autres
```

La colonne publiée est **« Après inspection »** — le produit d'une lecture manuelle, pas d'un calcul. Aucun code ne peut produire « 33 → **6** strictement postérieurs à la Règle 9 » : c'est un jugement de date rendu à l'œil sur des entrées de backlog.

### `nonml_report_idempotence_backtest.py` — **IRRÉPARABLE**

```python
124:L.append("soit **5,7 %** — ceux des entrées #443-#460, même univers figé que les #461")
```

**Corrigé au #518** : aucun appel `.glob(` nulle part dans le fichier. « 314 » (le total du dépôt) est un littéral brut à l'intérieur d'une f-string qui n'interpole que le numérateur — le script ne lit jamais le dépôt pour obtenir son dénominateur.

### `nonml_reproducibility_campaign_v2_audit.py` — **IRRÉPARABLE**

```python
52:L.append("- - fichiers `nonml_*_pnl.npz` trouvés : **173**")
56:L.append("Le rapport annonçait **173** fichiers `.npz` ; il y en a **208** aujourd'hui.")
```

**Corrigé au #518** : le seul `.glob(` du fichier porte sur `nonml_*_backtest.py` pour une fonction sans rapport avec le compte cité ; « 208 » est un littéral brut, jamais issu d'un glob sur `*_pnl.npz` que ce script n'exécute nulle part.

### `nonml_content_defined_magnitudes_audit.py` — réparable

```python
93:L.append("Le rapport n'accuse pas le #449 parce que **2** des importateurs sont")
```

« **2** des importateurs » — l'audit énumère les importateurs pour les examiner ; le compte est à portée d'un `len()`.

### `nonml_content_defined_magnitudes_backtest.py` — réparable

```python
154:L.append("Vérifié plutôt que supposé : au commit du #451, **8** fichiers")
155:L.append("contiennent la phrase, et ma règle en classe **8** comme porteurs.")
165:L.append("**majorant** : il vaut probablement **7** porteurs et **1** citeur,")
```

« au commit du #451, **8** fichiers contiennent la phrase » est une mesure sur objets git, que le script **lit déjà**. *(La troisième ligne — « il vaut probablement **7** porteurs et **1** citeur » — est une **estimation en prose**, pas une mesure : il n'y a rien à recalculer, seulement un avis à assumer.)*

### `nonml_dsr_corrected_trials_backtest.py` — réparable

```python
221:L.append("Le balayage du #445 trouvait **3** groupes de doublons exacts ; ce cycle en")
222:L.append("fusionne **2**. La différence n'est pas une contradiction : le troisième")
```

« ce cycle en fusionne **2** » est le résultat de la fusion que le script opère. *(« Le #445 trouvait **3** groupes » est une citation, légitime.)*

### `nonml_duplicate_sweep_coverage_audit.py` — réparable

```python
120:L.append("Écart toléré, fixé avant calcul : **0**.")
155:L.append("> « **76** candidats non-ML n'ont aucun `.npz`… Ils portent un FAIL pour la")
160:L.append("1. Le **76** venait de la soustraction `284 − 208`. Les deux ensembles ne se")
... et 1 autres
```

La ventilation « **90** FAIL, **2** PASS, **6** indéterminés, **1** sans rapport » porte sur l'ensemble que l'audit **construit déjà** — il interpole `n_missing` dans la phrase précédente. Les parts se calculent du même ensemble que le total.

### `nonml_idempotence_famille_capable_backtest.py` — réparable

```python
207:L.append("était d'environ **10 %**, soit **0,3** défaut attendu. **Ce résultat")
```

« environ **10 %**, soit **0,3** défaut attendu » se dérive de la vérité terrain du #463 — que ce script **importe** (`v1.FAUTIFS_463`, `v1.SAINS_463`). Le taux est à portée d'une division.

### `nonml_idempotence_lot2_backtest.py` — réparable

```python
106:L.append("signalements, **0** était réellement défectueux. Ce qui reste est coûteux")
220:L.append("tirer que le dépôt est sain.** Dix scripts sur **296** non éprouvés,")
221:L.append("c'est **3,4 %** du reste : ne rien trouver dans un si petit lot est")
```

« Dix scripts sur **296** non éprouvés, c'est **3,4 %** » : le script construit `tous` et `DEJA`, donc `len(tous) - len(DEJA)` et le ratio.

### `nonml_marker_emitter_crossing_backtest.py` — réparable

```python
245:L.append("**Aucun citeur établi.** Le compte mécanique en donnait **1** ; "
```

« Le compte mécanique en donnait **1** » est **le compte que ce script calcule** (`douteux`) — il l'écrit en dur juste après l'avoir obtenu.

### `nonml_orphans_interrupted_or_lost_backtest.py` — réparable

```python
169:L.append("Le **#464** avait compté **10** entrées sans aucun fichier et **24**")
424:L.append("travail.** Sur 33 objets examinés, **1** correspond à du travail annoncé")
```

**Mon cycle #474.** « Sur 33 objets examinés, **1** correspond à du travail annoncé et introuvable » : le script calcule `len(ent) + len(orp)` et le reste après contrôle post-hoc. **Mon propre défaut est réparable, et je n'ai pas d'excuse.**

### `nonml_reproducibility_campaign_v3_lot2_audit.py` — réparable

```python
159:L.append("24 tirages de plus feraient passer la borne de **6,2 %** à **~4,1 %** — de ~17 à")
```

**Corrigé au #493** : le script définit `def bound(n)` au niveau module et publie déjà `{100*bound(cum):.1f} %` à trois endroits. Le « 6,2 % » écrit en dur est exactement cette valeur, et le « ~4,1 % » est `100*bound(cum + 24)` — dérivable d'une fonction que le script possède, pas une projection sans univers.

## Le compte

- **IRRÉPARABLES** : **8 / 17** (**47,1 %**)
- **réparables** : **9**

| Irréparable | Pourquoi, en un mot |
|---|---|
| `nonml_protocol_inventory_audit.py` | colonne « après inspection » = lecture manuelle |
| `nonml_marker_emitted_by_scripts_backtest.py` | classification jamais effectuée par le script |
| `nonml_battery_backfill_lot_audit.py` | corrigé #511 : lit des .md, jamais de .npz |
| `nonml_coverage_wording_fix_audit.py` | corrigé #518 : aucun `.glob(`, littéral en dur |
| `nonml_pnl_duplicate_sweep_audit.py` | compte `n_trials` du backlog entier, non exposé |
| `nonml_pnl_persistence_exposed_pass_audit.py` | univers du balayage #415, disparu |
| `nonml_report_idempotence_backtest.py` | corrigé #518 : dénominateur jamais lu par le script |
| `nonml_reproducibility_campaign_v2_audit.py` | corrigé #518 : `.glob(` sans rapport avec le chiffre |

> **La dette du #479 est actionnable à 52,9 %.** Les **9** réparables le sont par une simple interpolation ; les
**8** autres ne peuvent qu'être **signalés dans le rapport**,
jamais recalculés.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 5 irréparables | ≥ 5 | 8 | **vérifiée** |
| ≥ 8 réparables | ≥ 8 | 9 | **vérifiée** |
| accord du proxy < 80 % | < 80 % | 52,9 % | **vérifiée** |

**L'accord du proxy est de 52,9 %**, mais ce chiffre flatte :
le proxy répond « oui » partout, donc il « s'accorde » exactement avec
le nombre de réparables, **par construction**. **Ce n'est pas un
accord, c'est une coïncidence arithmétique.**

## Ce que ce cycle établit

- la catégorie du #482 est **réelle et minoritaire** : **8** cas
  sur 17, chacun avec sa raison publiée ;
- **une des 8 renvoie à une question en attente d'arbitrage** — le
  décompte `n_trials` du #421 ;
- **mon propre défaut du #474 est réparable**, et rien ne l'excuse ;
- **rien n'est réparé ici** : le #482 a montré qu'une réparation peut
  être nuisible, et chacun des 9 demande sa propre vérification.

## Critères de succès

1. Population re-dérivée (**17**), écart (**+0**),
   rétractation du #482 prise en compte — **OUI**.
2. **17/17** examinés à la main avec ligne,
   verdict et raison — **OUI**.
3. Proxy publié à côté, accord chiffré (**52,9 %**) — **OUI**.
4. Aucun « irréparable » sans sa raison — **OUI**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).