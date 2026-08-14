# Trancher le sort du **citeur du #451** (pré-enregistré)

Le **#451** comptait, dans son propre tableau, **« 1 rapport qui cite
l'encart sans le porter »**. Le **#469**, au dépôt d'**aujourd'hui**, n'a
trouvé **0 citeur établi** — et a refusé de trancher, faute d'avoir
déclaré remonter à ce commit. **Ce cycle le déclare et le fait.**

## Le commit épinglé : `1d7649637137`

## Le classement à ce commit

- rapports **contenant** la marque : **8**
- **PORTEURS** : **7**
- **candidats CITEURS** : **1**
- **INDÉTERMINÉS** : **0**

## L'examen individuel — avant tout décompte

L'engagement 3 l'exige. Le **#469** a montré qu'un script écrivant la
marque **par variable** est invisible à la règle littérale : il avait
produit un faux citeur qu'un examen avait dû retirer.

| Rapport | Script producteur | Écriture par variable ? | Retenu |
|---|---|---|---|
| `nonml_selfref_reports_marking_result.md` | `nonml_selfref_reports_marking_backtest.py` | **oui** | **retiré** |

- **citeurs établis** : **0**

## Le #451 nomme-t-il le rapport qu'il comptait ?

Le pré-enregistrement énonçait **trois issues**, toutes publiables.

Son entrée **ne cite nominativement aucun rapport** `.md`.

> **Issue : **il ne le nomme pas** → la comparaison est **partielle**, et je le dis.**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| exactement 1 citeur établi | 1 | 0 | **réfutée** |
| le #451 ne nomme pas son citeur | ne nomme pas | ne nomme pas | **vérifiée** |
| le citeur n'en est plus un aujourd'hui | — | *le #469 en trouvait 0* | *sans objet* |

> **Zéro citeur établi, déjà à l'époque.** L'explication commode —
> « il a disparu du dépôt depuis » — **tombe**. Le pré-enregistrement
> avait fixé la conséquence : **c'est ma méthode qui est en cause**,
> pas l'histoire du dépôt.

Ma règle ne retrouve pas, au commit même où il a été compté, le
citeur que le #451 comptait. Deux lectures restent ouvertes, et je
n'ai pas de quoi les départager ici :

1. le #451 employait une définition de « citer » que je n'ai pas
   reconstituée ;
2. ma règle littérale a un angle mort de plus que celui du #469.

**Dans les deux cas, le croisement rapport ↔ script émetteur ne suffit
pas à reproduire ce compte** — et c'est le résultat de ce cycle.

### Un fait qui départage partiellement

Le candidat trouvé ici est **le même rapport** qu'au #469 —
`nonml_selfref_reports_marking_result.md` — et il est retiré pour
**la même raison** : son script écrit la marque par variable.

> **Le désaccord avec le #451 est donc stable, pas accidentel.**
> Ma règle donne le même candidat à deux commits séparés par vingt
> cycles, et l'écarte deux fois. Cela **oriente vers la lecture 1**
> — une définition différente de « citer » — plutôt que vers un
> angle mort qui varierait au hasard.

Ce n'est **pas une preuve** : une définition et un angle mort
peuvent produire la même stabilité. Mais un défaut erratique
aurait, lui, donné des candidats différents.

## Critères de succès

1. Commit du #451 retrouvé et publié — **OUI** (`1d7649637137`).
2. **8/8** rapports classés — **OUI**.
3. Chaque citeur examiné avant décompte — **OUI**.
4. Rapport du #451 relu et issue nommée — **OUI**.

**PASS** — le critère porte sur le **procédé** :
un cycle qui échoue à reproduire un compte, et le montre proprement,
réussit.


> **Rapport épinglé** — tout est lu au commit `1d7649637137`. Réexécuté dans dix cycles, il doit rendre les mêmes
> chiffres.