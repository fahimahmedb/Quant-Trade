# Audit adversarial — re-mesure des grandeurs du dépôt (#462)

Recomptage par une **autre route** : le backtest liste l'arbre puis filtre
en Python avec `re.match` ; l'audit filtre la même liste avec `fnmatch`,
un mécanisme de motif distinct. Un bug de regex ne peut pas se cacher dans
les deux.

## A. Les 108 cellules, recomptées par pathspec

- cellules recomptées : **108**
- lignes du rapport relues : **18**
- **écarts** : **0**

**CONCORDANT.**

## B. Le saut `batteries` — vaut-il +29, et est-il unique ?

- variations détectées sur la série : **1**
- #456 → #457 : 92 → **121** (**+29**)

C'est le point sur lequel repose la seule affirmation positive du cycle.
Un saut **unique**, **au bon commit**, de **+29** exactement — sinon la
confirmation du #457 ne tient pas.

**CONCORDANT.**

## C. Les fichiers ajoutés entre #456 et #457 sont-ils des batteries ?

Le contrôle B compte un solde entre les deux commits épinglés. Il resterait
compatible avec 30 ajouts et 1 suppression. On regarde donc les fichiers
**réellement ajoutés** sur le même intervalle.

- fichiers ajoutés sous `results/` : **31**
- dont rapports de batterie : **29**
- dont **autre chose** : **2**

  - `nonml_battery_coverage_anti_cheat.md`
  - `nonml_battery_coverage_result.md`

**CONCORDANT.**

## D. Idempotence

- avant : `83e991256ef202d6`
- après : `83e991256ef202d6`

**CONCORDANT.**

## Ce que cet audit ne couvre pas

Il vérifie que le **recomptage** est juste. Il ne sauve pas l'appariement
de prose, que le rapport publie comme un **échec** : comparer un
sous-ensemble (« 99 scripts *sans* `.npz` ») à un total n'a pas de sens,
et aucun des 9 « écarts » n'est une erreur du backlog.

## Verdict — **CONCORDANT** (4/4)

Aucun bug détecté par recomptage indépendant.