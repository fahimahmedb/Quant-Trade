# Les **chiffres publiés sans code qui les produise** (pré-enregistré)

Le **#473** a établi que le « **1** » du #451 — que trois cycles avaient
cherché à reproduire — était une **chaîne écrite à la main**. Ce cycle
mesure si le cas est **isolé ou courant**.

## Ce que ce chiffre est, et ce qu'il n'est pas

**Il mesure une prévalence, pas une culpabilité.** Un chiffre littéral
est légitime dans au moins trois cas courants : un **seuil**
pré-enregistré rappelé (« critère : **25 %** »), un **chiffre cité d'un
cycle antérieur** (« le #451 comptait **1** »), une **constante de
protocole** (« **5 bps** aller-retour »).

La faute du #473 est plus étroite : un littéral **présenté comme le
résultat mesuré par ce cycle-là**. **Ma règle mécanique ne sait pas faire
cette différence** — c'est pourquoi aucun total ci-dessous n'est un
compte de fautes, et pourquoi cinq scripts sont examinés à la main.

## La population

- rapports de `results/` : **1070**
- avec script producteur sous la convention : **762**
- **hors convention** *(comptés à part, jamais fautifs — #464)* : **308**

La règle de classement, reprise **sans modification** du #473 :

```python
INTERPOLE = re.compile(r"f[\"\']|\.format\(|%\s*[sd]|\{[^}]*\}|\"\s*\+|\+\s*\"|str\(")
```

## La prévalence

- rapports dont le script porte **au moins un** chiffre littéral : **35 / 762** (**4,6 %**)
- lignes littérales au total : **73**
- **médiane** par rapport affecté : **2,0**
- maximum sur un seul script : **7**

## L'examen individuel — les **5** plus chargés

Échantillon **fixé avant de regarder** : les 5 scripts portant le plus
de littéraux, ex æquo départagés par ordre alphabétique. **Un littéral
non examiné ne sera jamais qualifié de défaut.**

### `nonml_protocol_inventory_audit.py` — **7** littéraux

```python
59:L.append("Le compte brut était **19**. Le pré-enregistrement annonçait qu'il ne se conclurait")
124:L.append("| B — résultat sans PREREG | 5 | **0** (variantes résolues) |")
125:L.append("| C — PASS sans batterie | 33 | **6** strictement postérieurs à la Règle 9 |")
126:L.append("| D — source `data/` absente | 0 | **0** |")
127:L.append("| E — PREREG sans artefact | 19 | **0** (19/19 faux positifs) |")
129:L.append("**Une dette réelle a été trouvée** : les **6** PASS publiés strictement après")
... et 1 autres
```

*Verdict : **DÉFAUT de type #473** — motif ci-dessous.*

### `nonml_marker_emitted_by_scripts_backtest.py` — **5** littéraux

```python
103:L.append("| rapport **portant** l'encart, script ne l'émettant pas | **1** |")
104:L.append("| rapport dont le script **l'émet déjà** (rien à faire) | **1** |")
105:L.append("| rapport qui **cite** l'encart sans le porter | **1** |")
106:L.append("| rapports **effacés au #450**, à rétablir | **4** |")
114:L.append("savoir combien. Il y en a **1** au sens strict.")
```

*Verdict : **DÉFAUT de type #473** — motif ci-dessous.*

### `nonml_repo_magnitudes_recount_backtest.py` — **5** littéraux

```python
197:L.append("Le #457 racontait avoir soumis **29** stratégies à la batterie après")
198:L.append("avoir corrigé un défaut de son pilote (le code de sortie **2** signifie")
231:L.append("Lisez les lignes : « **99** scripts **sans** `.npz` », « **20** `.npz`")
232:L.append("**sans** rapport », « **1** PASS **non évaluable par** la batterie »,")
233:L.append("« les **29** **ont passé** la batterie ». Ce sont des **sous-ensembles**")
```

*Verdict : **légitime** — motif ci-dessous.*

### `nonml_citer_451_definition_backtest.py` — **4** littéraux

```python
53:L.append("trouvé **0**. Le #472 a laissé **deux lectures** ouvertes sans pouvoir les")
182:L.append("| **1** — deux définitions différentes de « citer » | **écartée** |")
183:L.append("| **2** — un angle mort de plus dans ma règle | **écartée** |")
184:L.append("| **3** — un périmètre de fichiers différent | **écartée** |")
```

*Verdict : **légitime** — motif ci-dessous.*

### `nonml_duplicate_sweep_coverage_audit.py` — **4** littéraux

```python
120:L.append("Écart toléré, fixé avant calcul : **0**.")
155:L.append("> « **76** candidats non-ML n'ont aucun `.npz`… Ils portent un FAIL pour la")
160:L.append("1. Le **76** venait de la soustraction `284 − 208`. Les deux ensembles ne se")
177:L.append("#427 lui-même), **6** indéterminés et **1** sans rapport. La correction est portée")
```

*Verdict : **DÉFAUT PARTIEL** — motif ci-dessous.*

## Les verdicts de l'examen

**Rédigés à la main après lecture de chaque ligne**, et non produits par
une règle : c'est précisément ce qu'une règle ne sait pas faire.

### `nonml_protocol_inventory_audit.py` — **DÉFAUT de type #473**

Le tableau de conclusion — `| Contrôle | Compte brut | Après inspection |` — publie **cinq comptes** (1, 5→0, 33→6, 0→0, 19→0) entièrement écrits à la main, **présentés comme les résultats de l'inspection de ce cycle**. C'est la forme exacte du #451. **Nuance à sa décharge, et elle compte** : l'en-tête de colonne « Après inspection » **annonce l'origine manuelle**, comme le #451 annonçait « rétabli par lecture ». Le défaut n'est pas un mensonge, c'est qu'**aucun code ne produit ces nombres**, donc qu'aucun cycle ultérieur ne peut les reproduire — ce que les #469 et #472 ont appris à leurs dépens.

### `nonml_marker_emitted_by_scripts_backtest.py` — **DÉFAUT de type #473**

**C'est le #451 lui-même**, dont le #473 a établi le cas. Sa présence ici n'est pas une découverte : c'est le **contrôle positif** de la méthode. Une règle qui ne l'aurait pas retrouvé serait à jeter.

### `nonml_repo_magnitudes_recount_backtest.py` — **légitime**

Les cinq littéraux sont des **citations de cycles antérieurs** — « le #457 racontait avoir soumis **29** stratégies », « lisez les lignes : « **99** scripts **sans** `.npz` » ». Le cycle *rapporte* des chiffres publiés ailleurs pour les discuter ; les écrire en dur est la seule façon correcte de citer.

### `nonml_citer_451_definition_backtest.py` — **légitime**

Un littéral est une citation du #472 (« trouvé **0** »). Les trois autres — `**1**`, `**2**`, `**3**` — sont les **étiquettes des trois lectures** dans un tableau, pas des mesures. **C'est un faux positif de ma propre règle** : `GRAS` ne distingue pas un nombre-mesure d'un nombre-numéro. Je le publie contre moi.

### `nonml_duplicate_sweep_coverage_audit.py` — **DÉFAUT PARTIEL**

Deux littéraux sont des citations, un troisième est un **seuil fixé avant calcul** (« Écart toléré : **0** ») — tous légitimes. Mais la phrase finale mélange les deux régimes : le total est **calculé** (`{n_missing}` interpolé) tandis que sa **ventilation** — **90** FAIL, **2** PASS, **6** indéterminés, **1** sans rapport — est **écrite en dur** dans la ligne suivante. Le lecteur ne peut pas voir que la somme et ses parts n'ont pas la même origine.

- **défauts établis** (complets ou partiels) : **3 / 5**
- **légitimes** : **2**

> **Ce `3` ne se généralise pas aux 35 rapports affectés.** L'échantillon
> a été choisi pour sa **charge maximale**, c'est-à-dire là où un défaut
> avait le plus de chances de se voir. **Un taux mesuré sur les cas les
> plus chargés ne s'extrapole pas au reste** — le dire est le prix de la
> méthode d'échantillonnage, choisie avant de regarder.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 50 rapports avec au moins un littéral | ≥ 50 | 35 | **réfutée** |
| ≥ 1 défaut de type #473 parmi les 5 | ≥ 1 | 3 | **vérifiée** |
| médiane ≤ 3 par rapport affecté | ≤ 3 | 2,0 | **vérifiée** |

**La prédiction 1 est réfutée, et largement** : j'annonçais ≥ 50
rapports affectés, il y en a **35** sur **762**,
soit **4,6 %**. Je surestimais la prévalence parce que je pensais
aux **rappels de seuils**, qui sont en fait presque toujours écrits
dans le pré-enregistrement plutôt que recopiés dans le rapport.

**La prédiction 2 est vérifiée : le #451 n'était pas isolé.** Mais
l'un des deux défauts pleins **est le #451 lui-même** — il sert de
contrôle positif, pas de découverte. **La découverte nette de ce
cycle est donc de 2, pas de 3**, et c'est
ainsi qu'il faut la lire.

## Critères de succès

1. Population énumérée, hors convention comptés à part — **OUI**.
2. **762/762** rapports classés — **OUI**.
3. **5** scripts examinés individuellement — **OUI**.
4. Aucun total présenté comme un compte de fautes — **OUI**, dit à
   l'endroit du chiffre et non en note.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).