# Audit adversarial — détecteur d'auto-inclusion (#466)

Le backtest conclut **lui-même** que son détecteur est inutilisable
(rappel 1/2). L'audit ne cherche donc pas à le confirmer : il vérifie que
**l'aveu est exact** et que rien d'autre n'est surestimé.

## A. Les trois comptes, recomptés

| | Rapport | Audit |
|---|---|---|
| hors périmètre | 296 | 296 |
| protégés | 3 | 3 |
| signalés | 20 | 20 |

**CONCORDANT.**

## B. Le cas manqué — le diagnostic tient-il ?

Le rapport affirme que ce script énumère par `git status`, forme que la
règle déclarée ne couvre pas. **Si c'était faux, l'excuse serait pire que
l'erreur.**

- appelle `git status` : **oui**
- énumère par un glob de `results/` : **non**

**CONCORDANT** — le diagnostic tient.

## C. Les faux positifs sont-ils vraiment faux ?

Un script « sain au #463 » mais signalé n'est pas forcément un faux
positif : il peut être **réellement exposé** et n'avoir simplement pas
rencontré son propre fichier lors des deux passages du #463.

Contrôle : ces scripts écrivent-ils leur rapport **dans le dossier qu'ils
énumèrent** ?

- faux positifs examinés : **10**
- qui écrivent bel et bien dans `results/` **et** l'énumèrent : **10**

> **Ce ne sont pas des faux positifs au sens strict.** Ces scripts sont
> **structurellement exposés** ; le #463 ne les a pas vus dériver, ce
> qui est une observation, pas une garantie. La calibration du rapport
> les compte comme des erreurs du détecteur : **elle est donc
> pessimiste**, et le rapport ne le dit pas.

C'est un écart **en faveur** du détecteur — et il se publie au même
titre qu'un écart défavorable.

## D. Idempotence de mon propre rapport

Ce rapport **énumère `results/`** et **y écrit** : il est exactement le
genre de script qu'il signale. À vérifier, pas à supposer.

- avant : `4fa99971659c2b9d`
- après : `4fa99971659c2b9d`

**CONCORDANT.**

## Ce que cet audit ne couvre pas

- Il ne **répare** pas le détecteur : la règle a été déclarée avant
  mesure, l'élargir ici la taillerait sur le cas qu'elle vient de rater.
- Il n'**exécute** aucun des scripts signalés : leur défaut reste
  **supposé**, pas prouvé.

## Verdict — **CONCORDANT** (3/3)

L'aveu du backtest est exact et son diagnostic tient.