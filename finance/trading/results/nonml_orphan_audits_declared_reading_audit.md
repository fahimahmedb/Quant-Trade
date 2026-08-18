# Audit adversarial — la règle de lecture déclarée (#483)

**Recalcul par une route différente** : population établie par
`os.scandir` et un ensemble de noms, et auto-déclaration cherchée sur les
**vingt** premières lignes au lieu des douze pré-enregistrées.

| Grandeur | Audit | Rapport | Verdict |
|---|---|---|---|
| population | **126** | 126 | **concordant** |
| SANS RÉSULTAT ATTENDU | **9** | 9 | **concordant** |
| RÉSULTAT ATTENDU | **4** | 4 | **concordant** |
| NON DÉCLARÉ | **113** | 113 | **concordant** |

## La fenêtre de douze lignes écarte-t-elle des déclarations ?

Le pré-enregistrement a figé **douze** lignes. Une fenêtre trop courte
gonflerait artificiellement les « NON DÉCLARÉS ».

- déclarations trouvées entre la ligne **13** et la ligne **20** : **0**

> **Aucune.** Élargir la fenêtre ne récupère rien : la convention
> d'auto-déclaration, quand elle existe, tient dans l'en-tête. **Le
> chiffre de 113 non déclarés n'est pas un
> artefact de fenêtre**, c'est la réalité du dépôt.

## Le contrôle central — l'engagement le plus difficile a-t-il tenu ?

Ce cycle rejouait une question **dont il connaissait déjà la réponse**.
La tentation était d'inscrire « 3/3 vérifié » au crédit du cycle.

| Contrôle | Résultat |
|---|---|
| le PREREG déclare l'aveu avant mesure | **OUI** |
| le PREREG interdit toute prédiction sur les trois | **OUI** |
| le rapport qualifie le résultat de non informatif | **OUI** |
| aucune des 3 prédictions ne porte sur les trois | **OUI** |
| le rapport publie l'échec de sa propre règle | **OUI** |
| la liste de mots n'est pas élargie après mesure | **OUI** |
| la liste de mots du script est identique à celle du PREREG | **OUI** |

> **L'engagement a tenu.** Le cycle ratifie sans se créditer, et
> publie que sa propre règle s'est trompée sur **la totalité** de son
> échantillon d'examen.

## Les trois du #480, recomptés

- `n_trials_dependence_correction` → **SANS RÉSULTAT ATTENDU** (« correction statistique »)
- `pnl_duplicate_sweep_v2` → **SANS RÉSULTAT ATTENDU** (« diagnostic »)
- `pnl_persistence_exposed_pass` → **SANS RÉSULTAT ATTENDU** (« infrastructure et de mesure »)

> **La ratification est confirmée par la route indépendante.**
> Elle **n'apprend rien de neuf** — c'est le propre d'une ratification,
> et le rapport le dit lui-même.

## Effets de bord du backtest

- écritures : **1** (`OUT` seul)
- `subprocess` / `checkout` / suppression : **0**

**Aucun effet de bord — le script ne fait que lire le disque.**

## Verdict

**CONCORDANT** — **4/4** grandeurs se retrouvent, et
**7/7** contrôles de
protocole sont tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des fichiers à la date
> de son exécution (cycles #436-#438).