# L'incohérence émetteur/rapport de `six_reports_regeneration` (pré-enregistré)

Le **#469** a croisé script émetteur et rapport produit, et une seule
paire a échoué. **Il l'a lue comme une perte** — « ces rapports **ont
perdu** un encart que leur script émet » — **sans le vérifier**.

## 1. La ligne d'émission, verbatim, et sa cible

La règle du #469, telle qu'il l'a écrite :

```python
EMISSION = re.compile(r"(append|write|print)\s*\(.*Rapport dépendant du dépôt")
```

Lignes qu'elle capture dans le script : **1**

```python
240:        L.append("> **Rapport dépendant du dépôt** — *ce document décrit l'état du dépôt à la")
```

**Ce qui la garde** — les blocs englobants, du plus externe au plus
interne :

- ligne 231 — `if perdus:`

**La cible de l'écriture.**

- la liste `L` est écrite dans `OUT`, c'est-à-dire **son propre
  rapport** : **OUI**
- autres chemins de `results/` écrits littéralement : **0**

## 2. Le rapport a-t-il **jamais** porté la marque ?

Une **perte** suppose une **possession antérieure**. La commande, pour
qu'un lecteur la refasse :

```
for s in $(git log --all --format=%H -- finance/trading/results/nonml_six_reports_regeneration_result.md); do
  git show "$s:finance/trading/results/nonml_six_reports_regeneration_result.md" | grep -q "Rapport dépendant du dépôt" && echo "$s"
done
```

- commits touchant ce rapport : **2**
- commits où il **porte** la marque : **1**
  - bbe5165 #450 regeneration des six rapports : PASS — la derive domine, 18 groupes contre 5
- le porte-t-il **aujourd'hui** : **non**

## 3. Les rapports que ce script régénère

- déclarés dans sa constante `SIX` : **6**
- **portant la marque aujourd'hui** : **4**

| Rapport régénéré | Porte la marque |
|---|---|
| `nonml_capitulation_gate_floor_sweep_result.md` | **oui** |
| `nonml_empty_pass_basket_extension_result.md` | **oui** |
| `nonml_empty_pass_requalification_result.md` | **oui** |
| `nonml_pnl_persistence_lot4_audit.md` | non |
| `nonml_protocol_inventory_result.md` | **oui** |
| `nonml_sameday_timestamp_resolution_result.md` | non |

## La lecture retenue

Le pré-enregistrement en proposait **trois**.

| Lecture | Verdict |
|---|---|
| **A** — encart perdu, le #469 avait raison | **retenue** |
| **B** — faux positif : l'écriture vise d'autres fichiers | **écartée** |
| **C** — indéterminable sans exécuter | **écartée** |

**Le #469 avait raison** : le rapport a porté la marque puis l'a
perdue. La dette est réelle et reste inscrite.

## Où la marque se trouvait-elle ? — constat post-mesure

*Ajouté après mesure, et signalé comme tel. **Le verdict ci-dessus
n'est pas modifié.***

Dans le rapport historique, la marque se trouve sous :

> ## Un effet de bord découvert — les marqueurs du #439 sont effacés

C'est **la section produite par la ligne 240**, sous la garde
`if perdus:`. Le rapport ne se marquait donc pas lui-même : il
**citait** l'encart pour expliquer que **quatre autres rapports**
venaient de le perdre.

La « perte » constatée par le #469 se lit alors ainsi : la garde
`if perdus:` **n'a plus produit sa section** lors d'une exécution
ultérieure — les encarts ayant été rétablis au #451, il n'y avait
plus rien à signaler.

**Quand la marque a-t-elle disparu ?** Le pickaxe (`git log -S`)
donne les deux seuls commits où la chaîne apparaît ou disparaît :

- 1a0c51d #468 : les deux scripts auto-inclusifs sont REPARES et idempotents
- bbe5165 #450 regeneration des six rapports : PASS — la derive domine, 18 groupes contre 5

Le retrait a donc eu lieu au **#468**, en réparant l'auto-inclusion
de ce script — **un cycle avant que le #469 ne le signale**. Les
quatre encarts ayant été rétablis au #451, la garde `if perdus:`
n'avait plus rien à produire.

> **Cela ne renverse pas le verdict.** Le #469 a signalé un fait
> textuel exact — un script dont la règle capte une écriture, un
> rapport qui ne la contient pas — et **mon hypothèse était fausse**.
> Ce constat en précise la mécanique, il ne l'annule pas.

## Ce que devient l'incohérence du #469

**Elle est confirmée**, et reste inscrite telle quelle : le rapport
a porté la marque au commit `bbe5165ace4e` et ne la porte plus.

La dette « **1 incohérence émetteur/rapport** », portée depuis le
#469 et répétée dans six entrées de backlog, **n'est pas levée par
ce cycle**. Elle est seulement mieux comprise.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| lecture B retenue | B | A | **réfutée** |
| le rapport n'a jamais porté la marque | jamais | 1 commit(s) | **réfutée** |
| ≥ 6 rapports régénérés portent la marque | ≥ 6 | 4 | **réfutée** |

**Mes trois prédictions sont réfutées.** Le cycle avait été ouvert
sur le soupçon qu'un cycle antérieur s'était trompé ; **la mesure
donne raison au #469 sur les trois points.**

> Le pré-enregistrement disait : *« ce cycle est ouvert parce que je
> soupçonne un cycle antérieur d'avoir eu tort — c'est exactement la
> position où l'on trouve ce qu'on cherche »*, et il exigeait que la
> lecture A reste atteignable. **Elle l'était, et c'est elle qui
> sort.** Le garde-fou a servi.

La prédiction 3 mérite un mot : j'annonçais **≥ 6** rapports
régénérés portant la marque, il y en a **4** — parce que
la liste `SIX` contient un `_audit.md` et un rapport que le #439
n'avait jamais marqués. **J'avais supposé une population homogène
sans la regarder.**

## Critères de succès

1. Ligne d'émission citée verbatim avec sa cible — **OUI**.
2. Historique du rapport balayé, commande publiée — **OUI**.
3. Rapports régénérés énumérés nominativement — **OUI**.
4. Une lecture explicitement nommée — **OUI**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de
> l'historique à la date de son exécution (cycles #436-#438).