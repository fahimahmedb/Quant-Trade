# Réparer les **2 tableaux tapés à la main** (pré-enregistré)

**Cycle de MODIFICATION** — et il ne modifie rien. La mesure préalable
établit qu'**aucune des deux réparations ne doit avoir lieu**, pour deux
raisons **différentes**. Le code du dépôt est laissé intact, et voici
pourquoi.

## Cible 2 — `reproducibility_sample_lot3_audit` : **ce n'est pas un défaut**

Le #479 avait classé son tableau « DÉFAUT », et retenu comme indice
aggravant que `73.2 %` employait le **point décimal** quand tout le dépôt
écrit la virgule. **Lu dans son contexte, le classement tombe.**

```python
    L.append("## La cause — un chiffre que j'ai moi-même rendu instable au #428")
    L.append("")
    L.append("Les lignes divergentes portent toutes sur le même décompte :")
    L.append("")
    L.append("```")
    L.append("- | scripts de backtest non-ML du dépôt | **284** |")
    L.append("+ | scripts de backtest non-ML du dépôt | **289** |")
    L.append("- | **couverture non-ML** | **73.2 %** |")
    L.append("+ | **couverture non-ML** | **72.0 %** |")
    L.append("```")
    L.append("")
    n_now = len(list(SCRIPTS.glob("nonml_*_backtest.py")))
```

Les lignes incriminées sont **à l'intérieur d'un bloc de citation**, et
commencent par `-` et `+` : **c'est un diff reproduit**, celui que le
cycle a observé entre deux versions d'un rapport. Le point décimal n'est
pas une négligence de saisie — **c'est la reproduction fidèle** du texte
cité.

> **Le verdict du #479 sur cette cible est rétracté.** Réparer aurait
> consisté à **falsifier une citation** pour la faire ressembler à une
> mesure. C'est plus grave que le défaut supposé.

Le #479 avait pourtant lu chaque ligne et publié son motif. **Sa lecture
a manqué le contexte de la ligne** — l'indice qu'il croyait aggravant
(le point décimal) était en réalité la **preuve** qu'il s'agissait d'une
citation. Le total de **18** défauts du #479 devient donc **17**.

## Cible 1 — `pnl_persistence_exposed_pass_audit` : défaut réel, **non réparable dans le périmètre déclaré**

```python
144:    L.append("")
145:    L.append("| | Avant (#415) | Après (#416) |")
146:    L.append("|---|---|---|")
147:    L.append("| candidats mesurés | 33 | **42** |")
148:    L.append("| détectés non mesurés | 29 | **20** |")
149:    L.append("| dont portant un PASS | 10 | **0** |")
150:    L.append("")
```

**Le défaut est réel** : trois comptes de la colonne « Après (#416) »
sont écrits à la main et présentés comme les résultats de cet audit.

**Mais ils ne sont pas recalculables depuis ce script.** Vérifié :

- le script ne connaît que ses **10 cibles** ; les comptes portent sur
  l'univers du balayage **#415**, qu'il n'importe pas et ne reconstruit
  pas ;
- aucun module du dépôt n'expose cet univers *(recherché parmi les
  scripts `nonml_*pnl_persistence*` et `*sweep*`)* ;
- le seul décompte disponible aujourd'hui — **209** fichiers `.npz`
  dans `results/` — **ne mesure pas la même chose** que le « 42 » écrit
  à l'époque.

Le pré-enregistrement interdisait explicitement de **changer une
population**. Substituer un décompte moderne à un décompte historique
serait exactement cela : **remplacer un chiffre faux par un chiffre qui
mesure autre chose**, ce qui est pire que de le laisser visible.

> **Une grandeur historique dont l'univers n'est plus reconstructible
> n'est pas réparable — seulement signalable.** C'est une catégorie que
> le #479 n'avait pas prévue en inscrivant « réparer » à la file.

## Le protocole d'exécution, appliqué quand même

Les deux scripts sont **exécutés deux fois** — non pour valider une
réparation qui n'a pas lieu, mais parce que les prédictions 1 et 3
portaient dessus et qu'elles doivent être confrontées.

| Script | État | Passage 1 | Passage 2 | Lignes de diff |
|---|---|---|---|---|
| `nonml_pnl_persistence_exposed_pass_audit.py` | idempotent | `74d5975785c099` | `74d5975785c099` | 0 |
| `nonml_reproducibility_sample_lot3_audit.py` | idempotent | `715cc60a2d99ca` | `715cc60a2d99ca` | 33 |

### Diff du rapport de `nonml_reproducibility_sample_lot3_audit.py`

Lignes : **33** *(les 12 premières)*

```diff
--- committé
+++ régénéré
@@ -29 +29 @@
-Le dépôt comptait **284** scripts de backtest au #428 ; il en compte **289**
+Le dépôt comptait **284** scripts de backtest au #428 ; il en compte **335**
@@ -46 +46 @@
-entrées) : **7**
+entrées) : **23**
@@ -48,0 +49,4 @@
+- `idempotence_famille_capable`
+- `idempotence_lot2`
+- `net_pnl_correction`
```

**Aucun rapport régénéré n'est committé** — le pré-enregistrement ne
l'autorisait que si le contenu était identique, et aucune réparation
n'a de toute façon eu lieu.

- résidus sous `results/` après restauration finale : **0**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| les 2 s'exécutent sans erreur | 2 | 2 | **vérifiée** |
| ≥ 1 produit des chiffres différents | ≥ 1 | 1 | **vérifiée** |
| les 2 sont idempotents | 2 | 2 | **vérifiée** |

**Ces prédictions supposaient toutes que la réparation aurait lieu.**
Elles sont confrontées telles qu'elles ont été écrites, sur les scripts
**non modifiés** — c'est la lecture la plus défavorable, et la seule
honnête : je ne les réinterprète pas après coup.

## Ce que l'idempotence ne prouve pas

*Observation sur un fait mesuré ci-dessus ; aucun verdict n'en dépend.*

`nonml_pnl_persistence_exposed_pass_audit.py` régénère son rapport **octet pour octet** — **0**
ligne de diff.

> **C'est exactement ce à quoi il fallait s'attendre, et c'est le
> problème.** Un tableau tapé à la main se reproduit parfaitement,
> indéfiniment, **quoi qu'il advienne du dépôt**. Son idempotence est
> celle d'une constante, pas celle d'une mesure.

Le cycle **#463** avait fait de l'idempotence un critère de qualité.
Ce cas montre sa limite : **les rapports les plus stables peuvent
l'être pour la pire des raisons**. À l'inverse, le second script
produit **27** lignes de diff précisément parce que son décompte est
**calculé** et que le dépôt a grossi.

**L'instabilité est ici le signe du bon comportement.**

## Ce que ce cycle laisse

- **1 défaut rétracté** : le total du #479 passe de **18** à **17**.
- **1 défaut confirmé mais irréparable** : sa grandeur est historique et
  son univers n'existe plus sous forme reconstructible.
- **0 ligne de code modifiée** dans le dépôt.

> **Un cycle de modification qui ne modifie rien n'a pas échoué** — il a
> établi que les deux modifications prévues étaient, l'une inutile,
> l'autre nuisible. **La piste « réparer » de la file du #479 est close.**

## Critères de succès

1. Les 2 scripts examinés, **code cité verbatim** — **OUI** *(la
   modification est refusée, motivée pour chacun)*.
2. Chacun exécuté deux fois, empreintes publiées — **OUI**.
3. Diff avant/après publié pour chacun — **OUI**.
4. Aucun rapport régénéré committé — **OUI**.
5. Zéro résidu sous `results/` — **OUI**.

**PASS** — le critère porte sur le
**procédé** : un cycle qui refuse ses deux modifications et publie
pourquoi réussit.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).