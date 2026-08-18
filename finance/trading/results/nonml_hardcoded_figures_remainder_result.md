# Les rapports **non examinés** du #476 (pré-enregistré)

Le **#476** avait trouvé **35** rapports portant un chiffre littéral et
n'en avait examiné que **5** — les plus chargés — en écrivant lui-même
que son taux **ne se généralisait pas**. **Ce cycle lit les restants**,
et rend le premier compte **complet** de la série.

## La population, re-dérivée

| | #476 | Ici | Écart |
|---|---|---|---|
| rapports affectés | 35 | **37** | **+2** |
| déjà examinés au #476 | 5 | **5** | — |
| **restants, examinés ici** | — | **32** | — |

> **L'effectif a monté.** Les cycles **#477** et **#478** ont été
> écrits depuis, et leurs propres scripts portent des littéraux — ils
> entrent donc dans la population qu'ils contribuent à mesurer. **Un
> compte de dépôt est daté** (#436-#438), et le chiffre publié ici est
> celui d'aujourd'hui.

Je m'exclus de ma propre population (`hardcoded_figures_remainder`) — règle des **#447/#463**,
appliquée avant mesure.

## Le verdict, un par un

**Écrits à la main après lecture de chaque ligne.** Aucune règle ne les
produit : c'est exactement ce qu'une règle ne sait pas faire.

### `nonml_battery_backfill_lot_audit.py` — **DÉFAUT**

```python
131:L.append("son overlay **0,00 %** du temps : son P&L est *identique* à celui de Buy & Hold")
168:L.append("reste **1** candidat hors de portée de l'outil (schéma panier), listé et non")
```

« son overlay **0,00 %** du temps » et « reste **1** candidat hors de portée » sont **deux résultats de ce cycle-là**, écrits en dur.

### `nonml_citer_451_resolution_backtest.py` — légitime

```python
204:L.append("est reproduit par une méthode indépendante, et le **0** du #469")
```

« le **0** du #469 » — citation d'un cycle antérieur.

### `nonml_conditional_sections_sweep_backtest.py` — légitime

```python
263:L.append("> avant la section gardée.** Le lecteur voit « divergents : **0** »,")
```

« le lecteur voit « divergents : **0** » » — un **exemple illustratif** en prose, pas une mesure.

### `nonml_content_defined_magnitudes_audit.py` — **DÉFAUT**

```python
93:L.append("Le rapport n'accuse pas le #449 parce que **2** des importateurs sont")
```

« **2** des importateurs sont… » — compte établi par cet audit, en dur.

### `nonml_content_defined_magnitudes_backtest.py` — **DÉFAUT**

```python
154:L.append("Vérifié plutôt que supposé : au commit du #451, **8** fichiers")
155:L.append("contiennent la phrase, et ma règle en classe **8** comme porteurs.")
165:L.append("**majorant** : il vaut probablement **7** porteurs et **1** citeur,")
```

« au commit du #451, **8** fichiers contiennent la phrase, et ma règle en classe **8** comme porteurs », puis « il vaut probablement **7** porteurs et **1** citeur ». **Trois mesures et une estimation**, toutes en dur — et le cycle dit pourtant « vérifié plutôt que supposé ».

### `nonml_coverage_wording_fix_audit.py` — **DÉFAUT**

```python
133:L.append("examine réellement les **284** scripts `nonml_*_backtest.py` du dépôt, 0 illisible,")
```

« examine réellement les **284** scripts […] 0 illisible » — vérification de cet audit, écrite en dur.

### `nonml_dsr_corrected_trials_backtest.py` — **PARTIEL**

```python
221:L.append("Le balayage du #445 trouvait **3** groupes de doublons exacts ; ce cycle en")
222:L.append("fusionne **2**. La différence n'est pas une contradiction : le troisième")
```

« Le balayage du #445 trouvait **3** groupes » est une citation ; « ce cycle en fusionne **2** » est **son propre résultat**, en dur. Les deux dans la même phrase, sans que rien ne les distingue.

### `nonml_hardcoded_figures_sweep_backtest.py` — légitime

```python
134:L.append("Le **#473** a établi que le « **1** » du #451 — que trois cycles avaient")
143:L.append("pré-enregistré rappelé (« critère : **25 %** »), un **chiffre cité d'un")
144:L.append("cycle antérieur** (« le #451 comptait **1** »), une **constante de")
145:L.append("protocole** (« **5 bps** aller-retour »).")
```

Les quatre littéraux sont la citation du #473 et les **exemples** de littéraux légitimes que le cycle donne lui-même (« critère : **25 %** », « **5 bps** aller-retour »). **Ma règle compte comme littéraux les exemples de littéraux** — ironie signalée, pas défaut.

### `nonml_idempotence_famille_capable_backtest.py` — **DÉFAUT**

```python
207:L.append("était d'environ **10 %**, soit **0,3** défaut attendu. **Ce résultat")
```

« le taux observé était d'environ **10 %**, soit **0,3** défaut attendu » — un calcul fait de tête et publié comme tel.

### `nonml_idempotence_lot2_backtest.py` — **PARTIEL**

```python
106:L.append("signalements, **0** était réellement défectueux. Ce qui reste est coûteux")
220:L.append("tirer que le dépôt est sain.** Dix scripts sur **296** non éprouvés,")
221:L.append("c'est **3,4 %** du reste : ne rien trouver dans un si petit lot est")
```

« **0** était réellement défectueux » cite le #467 (légitime) ; « dix scripts sur **296** non éprouvés, c'est **3,4 %** » est une statistique de ce cycle, en dur.

### `nonml_marker_emitter_crossing_backtest.py` — **DÉFAUT**

```python
245:L.append("**Aucun citeur établi.** Le compte mécanique en donnait **1** ; "
```

« Le compte mécanique en donnait **1** » — **le #469 écrit en dur son propre compte**, celui-là même dont les #472 et #473 ont ensuite cherché l'origine dans le code.

### `nonml_net_pnl_correction_robustness.py` — légitime

```python
57:L.append("**Étape 7a. Ce n'est pas un retuning.** Le seuil du balayage reste **0,9999**,")
```

« Le seuil du balayage reste **0,9999** » — constante de protocole.

### `nonml_orphan_npz_inspection_backtest.py` — légitime

```python
66:L.append("- annoncé par le #442, jamais revérifié depuis : **20**")
```

« annoncé par le #442 […] : **20** » — citation explicite.

### `nonml_orphans_interrupted_or_lost_backtest.py` — **PARTIEL**

```python
169:L.append("Le **#464** avait compté **10** entrées sans aucun fichier et **24**")
424:L.append("travail.** Sur 33 objets examinés, **1** correspond à du travail annoncé")
```

« Le #464 avait compté **10** […] et **24** » est une citation. Mais « Sur 33 objets examinés, **1** correspond à du travail annoncé et introuvable » est **mon propre résultat au #474, écrit en dur**. **Je commets le défaut que je mesure**, deux cycles après l'avoir nommé.

### `nonml_pnl_duplicate_sweep_audit.py` — **DÉFAUT**

```python
207:L.append("**Correction retenue : 1 essai surnuméraire**, soit 372 → **371**.")
```

« Correction retenue : 1 essai surnuméraire, soit 372 → **371** » — conclusion chiffrée de cet audit, en dur.

### `nonml_pnl_duplicate_sweep_v2_audit.py` — légitime

```python
156:L.append("Le #414 mesurait **93,3 %** de décisions de porte identiques et une corrélation")
157:L.append("de portes de **0,8679** pour la paire point-in-time. La corrélation des P&L est")
```

« Le #414 mesurait **93,3 %** […] et une corrélation de **0,8679** » — deux citations attribuées.

### `nonml_pnl_persistence_exposed_pass_audit.py` — **DÉFAUT**

```python
147:L.append("| candidats mesurés | 33 | **42** |")
148:L.append("| détectés non mesurés | 29 | **20** |")
149:L.append("| dont portant un PASS | 10 | **0** |")
```

Un tableau entier — « candidats mesurés | 33 | **42** », « détectés non mesurés | 29 | **20** », « dont portant un PASS | 10 | **0** » — écrit à la main. **Même forme que `protocol_inventory_audit` au #476.**

### `nonml_pnl_persistence_lot5_audit.py` — légitime

```python
109:L.append("déjà. Écart toléré, fixé avant calcul : **0**.")
```

« Écart toléré, fixé avant calcul : **0** » — seuil pré-enregistré.

### `nonml_report_idempotence_audit.py` — légitime

```python
160:L.append("Le backtest constate **8** rapports réécrits sans dire par qui. On")
226:L.append("- Il n'attribue pas les **8** écritures hors périmètre à tous leurs")
228:L.append("- Il ne teste que **3** passages : une dérive à période plus longue lui")
230:L.append("- Il ne dit rien des **296** scripts hors de l'univers.")
```

Les quatre littéraux — **8** rapports, **8** écritures, **3** passages, **296** scripts — citent les grandeurs du backtest audité et son protocole, dans une section de **limites**.

### `nonml_report_idempotence_backtest.py` — **DÉFAUT**

```python
124:L.append("soit **5,7 %** — ceux des entrées #443-#460, même univers figé que les #461")
```

« soit **5,7 %** » — pourcentage calculé par ce cycle, publié en dur.

### `nonml_reproducibility_campaign_v2_audit.py` — **PARTIEL**

```python
52:L.append("- - fichiers `nonml_*_pnl.npz` trouvés : **173**")
56:L.append("Le rapport annonçait **173** fichiers `.npz` ; il y en a **208** aujourd'hui.")
```

« Le rapport annonçait **173** fichiers » est une citation ; « il y en a **208** aujourd'hui » est **la mesure de cet audit**, en dur — et c'est précisément le chiffre qui fonde son verdict.

### `nonml_reproducibility_campaign_v3_lot2_audit.py` — **DÉFAUT**

```python
159:L.append("24 tirages de plus feraient passer la borne de **6,2 %** à **~4,1 %** — de ~17 à")
```

« 24 tirages de plus feraient passer la borne de **6,2 %** à **~4,1 %** » — une projection calculée à la main.

### `nonml_reproducibility_sample_backtest.py` — légitime

```python
56:L.append("propre code ? Les lots #416-#427 ont vérifié **44** rapports, mais seulement ceux")
```

« Les lots #416-#427 ont vérifié **44** rapports » — citation.

### `nonml_reproducibility_sample_lot2_backtest.py` — légitime

```python
169:L.append("La borne annoncée **avant** de mesurer était de **8,0 %** (8,2 % en version")
```

« La borne annoncée **avant** de mesurer était de **8,0 %** » — valeur pré-enregistrée, rappelée.

### `nonml_reproducibility_sample_lot3_audit.py` — **DÉFAUT**

```python
60:L.append("- | scripts de backtest non-ML du dépôt | **284** |")
62:L.append("- | **couverture non-ML** | **73.2 %** |")
```

Un tableau de résultats en dur — « scripts de backtest non-ML | **284** », « couverture non-ML | **73.2 %** ». **Détail supplémentaire** : `73.2` emploie le point décimal, contre la virgule partout ailleurs — signe que la ligne a été tapée, non produite.

### `nonml_self_inclusion_detector_backtest.py` — légitime

```python
81:L.append("Le #463 a trouvé **2** scripts non idempotents en en rejouant **18**. Le")
88:L.append("Le #463 fournit une **vérité terrain** : **2** fautifs, **16** sains.")
```

« Le #463 a trouvé **2** scripts non idempotents en en rejouant **18** », « **2** fautifs, **16** sains » — citations du #463, dont le script déclare par ailleurs les listes nominatives.

### `nonml_self_inclusion_detector_v2_audit.py` — légitime

```python
167:L.append("- Il éprouve **6** scripts sur les 320 : la fermeture de la piste repose")
169:L.append("- Il ne teste que **3** passages : une dérive de période plus longue lui")
```

« Il éprouve **6** scripts sur les 320 », « **3** passages » — grandeurs de protocole, dans une section de limites.

### `nonml_self_inclusion_repair_audit.py` — légitime

```python
139:L.append("Le cycle promet de restaurer les **7** rapports que")
```

« restaurer les **7** rapports » — périmètre déclaré du cycle audité.

### `nonml_sessions_column_backfill_audit.py` — légitime

```python
121:L.append("Écart toléré, fixé avant calcul : **0**. C'est le contrôle qui donne son sens au")
198:L.append("Recalculé ici sur les **16** candidats du lot 5, en appliquant la règle du #427 :")
```

« Écart toléré […] : **0** » est un seuil ; « les **16** candidats du lot 5 » est un **périmètre d'entrée**, pas un résultat.

### `nonml_sweep_basket_schema_support_audit.py` — légitime

```python
100:L.append("Le pré-enregistrement annonçait **3** candidats panier parmi les 7 non mesurés,")
```

« Le pré-enregistrement annonçait **3** candidats panier » — citation.

### `nonml_sweep_pass_prose_fix_backtest.py` — légitime

```python
164:L.append("> **4** PASS sont **les deux** candidats écartés au #427 avec leur raison publiée")
```

« > **4** PASS sont **les deux** candidats… » — à l'intérieur d'un bloc de citation.

### `nonml_tom_decomposition_npz_robustness.py` — légitime

```python
61:L.append("apparierait. Le seuil du dépôt reste **0,9999** et n'est pas touché : ce")
```

« Le seuil du dépôt reste **0,9999** » — constante de protocole.

## Le compte

- **DÉFAUTS pleins** : **11**
- **PARTIELS** *(citation et résultat propre mêlés)* : **4**
- **légitimes** : **17**

### Consolidé sur toute la population

| Origine | Défauts (pleins + partiels) | Examinés |
|---|---|---|
| #476 *(les 5 plus chargés)* | 3 | 5 |
| **#479** *(le reste)* | **15** | **32** |
| **total** | **18** | **37** |

> **Ce total n'est plus un taux d'échantillon : c'est un dénombrement.**
> Toute la population a été lue. C'est le premier chiffre de cette série
> qui ne demande aucune extrapolation.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 3 défauts parmi les restants | ≥ 3 | 15 | **vérifiée** |
| ≥ 20 légitimes *(sur 30 annoncés, 32 réels)* | ≥ 20 | 17 | **réfutée** |
| total consolidé ≤ 8 défauts | ≤ 8 | 18 | **réfutée** |

**Les prédictions 2 et 3 sont réfutées, et dans le mauvais sens.**
J'annonçais au plus **8** défauts au total ; il y en a **18**.
Le défaut du #451, que trois cycles avaient traité comme une
singularité, est en réalité **un usage répandu** dans ce dépôt.

> **Et j'en fais partie.** `orphans_interrupted_or_lost` — **mon propre
> cycle #474** — écrit en dur « Sur 33 objets examinés, **1** correspond
> à du travail annoncé et introuvable ». **Je commets le défaut que je
> mesure, deux cycles après l'avoir nommé.** Aucune circonstance
> atténuante : le #473 l'avait déjà décrit, et je l'ai reproduit.

## Ce que cela change à la lecture du #451

Le #473 concluait : *« la leçon utile est sur ce que coûte un nombre
publié sans le code qui le produit »*. Ce cycle en donne la mesure :
**18 occurrences** sur toute la population, dont deux tableaux
entiers de résultats tapés à la main.

**Le #451 n'était pas fautif — il était ordinaire.** Ce qui l'a rendu
coûteux n'est pas d'avoir écrit un nombre à la main, c'est que **trois
cycles ont ensuite cherché dans le code un calcul qui n'existait pas**.

## Critères de succès

1. Population re-dérivée, écart signalé (**+2**), les 5 du #476
   déclarés et exclus — **OUI**.
2. **32/32** examinés avec
   ligne verbatim et verdict — **OUI**.
3. Total consolidé publié, part du #476 distinguée — **OUI**.
4. Aucun défaut compté sans sa ligne publiée — **OUI**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).