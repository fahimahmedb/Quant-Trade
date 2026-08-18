# La **direction temporelle** des emprunts « B tiers » (pré-enregistré)

Le **#508** a laissé **21** emprunts sourcés **au sujet mais ailleurs**
que dans le cycle cité, hors sourçages circulaires. Le **#503** avait
établi qu'une source **postérieure ne prouve rien** — ce registre reprend
ses chiffres **vers l'avant**. Le test n'avait jamais été appliqué ici.

## La règle de datation, citée verbatim

```
git log --diff-filter=A --reverse --format=%ct -- <chemin>
```

> - **date du cycle cité** : celle de son `PREREG_<nom>.md`, `<nom>`
>   extrait de sa section par la règle du **#504** ;
> - **date de la source** : celle du **fichier** où le contexte a été
>   trouvé, ou du `PREREG_` du cycle si la source est une section.

Ce sont des **premiers commits d'ajout**, jamais l'état courant.

## Les trois classes

- emprunts « B tiers » repris du #508 : **21**

| Classe | Nombre | Part | Ce qu'elle permet de conclure |
|---|---|---|---|
| **postérieure** | **19** | **90,5 %** | **rien** — reprise vers l'avant (leçon du #503) |
| **antérieure** | **1** | **4,8 %** | **candidat** d'erreur de citation |
| **indatable** | **1** | **4,8 %** | **rien**, et il faut le compter |

## Ce que « postérieure » vaut — rappelé et chiffré

**19** des **21** « B tiers » ont une
source **postérieure** au cycle qu'ils citent. **Elles ne prouvent
rien** : un cycle ultérieur qui reprend un chiffre est le fonctionnement
normal de ce registre, et un détecteur aveugle au temps prend cette
reprise pour une erreur d'attribution — **c'est exactement l'erreur que
le #503 a commise puis publiée.**

- après retrait des postérieures et des indatables, il reste : **1** emprunt(s)

## Les antérieures — les seuls candidats

- effectif : **1**

| Script | Cite | Nombre | Source | Date source | Date cycle cité | Écart |
|---|---|---|---|---|---|---|
| `nonml_guards_witness_remainder_backtest.py` | `#481` | **766** | `nonml_conditional_sections_sweep_audit.md` | 18/08/2026 | 18/08/2026 | **56** min |

> **1** de ces antériorités sont **inférieures à un
> jour**. Ce dépôt produit plusieurs cycles par heure : une
> antériorité de quelques minutes n'établit **rien** sur l'ordre
> logique des travaux — elle reflète l'ordre d'écriture des
> fichiers, pas celui des idées.
>
> **La règle figée les compte comme antérieures, et je ne la
> change pas** ; mais le lecteur doit savoir que leur poids
> probant est **quasi nul**. Le publier vaut mieux que présenter
> un résidu plus solide qu'il n'est.


> **Aucune antériorité ne dépasse le jour.** Il n'y a donc ici
> **aucun candidat** d'erreur de citation dont l'écart soit
> interprétable — et le mot « candidat », choisi avant la mesure,
> ne peut pas être appliqué à un écart de quelques minutes.

## Les indatables — ma prédiction 3 les annonçait à zéro

- `nonml_reproducibility_sample_backtest.py` cite `#416` pour **44**, source
  `#434` — **le cycle cité** n'a pas de date d'ajout.

> La règle de datation ne couvre pas tout : un fichier peut avoir été
> ajouté hors du chemin balayé, ou un cycle n'avoir pas de
> `PREREG_` nommable. **Compté, pas dissimulé.**

## Ce que la classe B du #508 vaut après ce filtre

Le #508 concluait que **la majorité des emprunts ne se justifient pas
par le cycle qu'ils citent**. Ce cycle en donne la lecture datée :

| Étape | Effectif |
|---|---|
| classe **B** du #508 | **26** |
| moins les **circulaires** (#508) | **21** |
| moins les **postérieures** et **indatables** | **1** |

> Il reste **1** emprunt(s) que ni la circularité ni la
> reprise vers l'avant n'expliquent.
>
> **Dont antériorité d'au moins un jour : 0.** Le
> résidu de neuf cycles d'enquête se réduit donc à **0** cas au poids probant réel.
>
> **Autrement dit : rien.** Neuf cycles n'ont produit aucun
> candidat d'erreur qui résiste à la mesure de son propre écart
> temporel. Le canal soupçonné au #497 est **réel** — 39 nombres
> retapés au lieu d'être relus — et **n'a produit aucune faute
> repérable**.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| ≥ 15 postérieures | ≥ 15 | 19 | **vérifiée** |
| ≥ 1 antérieure | ≥ 1 | 1 | **vérifiée** |
| 0 indatable | 0 | 1 | **réfutée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Population, mots-clés, fenêtres et correspondance cycle → rapport sont
**importés** des backtests des #500 à #508.

## Critères de succès

1. Règle de datation et commande citées verbatim — **OUI**.
2. Les **21** « B tiers » classés, **3** classes publiées — **OUI**.
3. Antérieures nommées avec leurs deux dates (**1**) — **OUI**.
4. « Postérieure ne prouve rien » rappelé et chiffré — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts et de
> l'historique à la date de son exécution.
