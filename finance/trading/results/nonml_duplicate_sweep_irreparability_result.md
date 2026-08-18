# Trancher la **réserve du #485** (pré-enregistré)

Le **#485** a classé `pnl_duplicate_sweep_audit` **IRRÉPARABLE**. Son
audit n'a **pas pu le confirmer** — le script énumère `results/` sans
liste codée en dur — et **le doute a été inscrit**. Le voici levé.

## 1. La ligne fautive, verbatim

```python
207:    L.append("**Correction retenue : 1 essai surnuméraire**, soit 372 → **371**.")
```

## 2. Ce que le script énumère **réellement**

- `results/` (fichiers)
- **le backlog** (texte)
- un dossier passé en argument

> **Il lit bien le backlog** — et ma prédiction 2 annonçait le
> contraire. Le #485 avait écrit que cet audit « ne construit pas » le
> décompte d'essais ; **c'était trop vite dit**.

### Ce qu'il en tire, verbatim

```python
128:    backlog_txt = BACKLOG.read_text(encoding="utf-8")
129:    n_entries = sum(1 for line in backlog_txt.splitlines()
130:                    if line.startswith("| ") and line[2:].split(" |")[0].strip().isdigit())
131:
132:    L.append("## 3. Portée réelle — que voit le balayage ?")
```

| Grandeur | Valeur |
|---|---|
| `n_entries` **publié** dans son rapport | **404** |
| `n_entries` **recalculé aujourd'hui** | **449** |
| le chiffre écrit en dur dans la ligne fautive | **372** |

## 3. Le **372** est-il une grandeur calculée ?

- lignes publiant une grandeur **interpolée** : **2**
- parmi elles, portant `372` : **0**
- occurrences de `372` dans tout le script : **1** — **toutes littérales**

> **Le script calcule bien un décompte de backlog — mais c'est
> 404, pas 372.** Les deux nombres ne mesurent pas la même
> chose : `n_entries` compte les **lignes de tableau numérotées**,
> tandis que le 372 vient de la comptabilité `n_trials` du
> projet, qui compte les **essais** — une notion que ce script
> n'implémente nulle part.

Et l'écart n'est pas un décalage temporel : recalculé aujourd'hui,
`n_entries` vaut **449** — il s'éloigne encore du 372.

## La lecture retenue

| Lecture | Verdict |
|---|---|
| **A** — irréparable confirmé | **retenue** |
| **B** — réparable, le #485 s'est trompé | **écartée** |
| **C** — indéterminable sans la comptabilité `n_trials` | **écartée** |

> ### **L'irréparabilité est confirmée — mais pas pour la raison que
> le #485 avait écrite.**

Le #485 disait que l'audit « **ne construit pas** » le décompte du
backlog. **C'est faux** : il en construit un. Ce qui est vrai, et que
le #485 n'avait pas vu, c'est que **le décompte qu'il construit n'est
pas celui-là** — 404 lignes de tableau contre 372 essais.

**La conclusion tient, la justification était fausse.** C'est
exactement le reproche que le #475 s'était fait à lui-même : *« il
avait raison, mais pas pour la raison qu'il croyait »*.

## La réserve de l'audit du #485

Elle était : *« le script énumère `results/` sans liste codée en dur, sa
route ne confirme pas l'irréparabilité »*.

> **Elle est levée — et elle avait raison de se méfier.** La route AST
> ne pouvait pas confirmer, parce que le script **construit bel et
> bien** un décompte de backlog. Elle a correctement refusé de
> valider un raisonnement faux, **même si sa conclusion était juste**.

**C'est le meilleur usage qu'un audit puisse avoir** : ne pas
confirmer ce qu'il ne peut pas établir, plutôt que de suivre le
verdict qu'on attend de lui.

## Ce que ce cycle ne tranche pas

Le **372** vient de la comptabilité `n_trials` du projet.
**Cette comptabilité elle-même est en attente d'arbitrage de
l'utilisateur depuis le #421**, et ce cycle ne la tranche pas : il
établit seulement qu'elle **n'est pas reconstructible depuis ce
script-là**.

> **Une dette technique dépend donc d'une décision qui n'appartient pas
> à ces cycles.** Le #485 l'avait déjà signalé ; le #488 le confirme sur
> pièce.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| lecture A retenue | A | A | **vérifiée** |
| il énumère `results/`, **pas** le backlog | pas le backlog | **il lit le backlog** | **réfutée** |
| `372` n'est nulle part une grandeur calculée | 0 | 0 | **vérifiée** |

**La prédiction 2 est réfutée, et c'est elle qui apprend quelque
chose.** J'avais repris sans la vérifier la justification du #485 —
« cet audit ne construit pas le décompte » — et elle est fausse. **Le
verdict survit, la raison change**, et c'est la mesure qui l'a imposé.

## Critères de succès

1. Code cité verbatim, corpus énumérés publiés — **OUI**.
2. Recherche du `372` comme grandeur calculée publiée — **OUI** (**0** trouvée(s)).
3. Une lecture nommée — **OUI** (**A**).
4. Réserve du #485 explicitement levée ou maintenue — **OUI**.

**PASS** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).