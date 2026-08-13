# Pré-enregistrement — corriger `n_trials` de la non-indépendance mesurée

**Écrit et committé AVANT toute modification.** `n_trials = 1` pour ce cycle.
Cycle de **correction statistique** : aucune stratégie ré-évaluée, aucun
paramètre de stratégie touché.

## La dette, déclarée trois fois et jamais soldée

Le DSR de la batterie Règle 9 utilise `n_trials` = taille du backlog (372
actuellement). Trois cycles ont établi que ce compte surestime le nombre
d'essais **indépendants** :

| Cycle | Constat | Nature |
|---|---|---|
| #403 / #419 | `sma200_leaders_overlay` ≡ `leaders_trend_union_overlay`, P&L **bit-à-bit identiques** sur les deux univers | identité mesurée |
| #414 | `momentum_decile_spread` / `momentum_dispersion` : portes identiques à **93,3 %**, corrélation 0,8679 | voisinage |
| #418 | `momentum_breadth` / `sma200_momentum_breadth_and` : le second est le **ET** du premier, P&L corrélés à 0,99990654 | emboîtement |

Chacun a été déclaré « opération distincte à mener séparément » — et jamais menée.

## Sens de la correction : elle m'arrange, donc elle exige plus de discipline

Réduire `n_trials` **abaisse** le seuil de sélection SR0, donc **augmente** le
DSR : la correction va dans le sens **favorable aux candidats**. C'est la
direction où le risque de complaisance est le plus fort. Deux garde-fous, fixés
ici avant tout calcul.

### Garde-fou 1 — seules les identités **mesurées** sont déduites

> Sont déduits du décompte les seuls candidats dont le P&L est **bit-à-bit
> identique** à celui d'un autre candidat du backlog, établi par mesure.
> **Les paires voisines ou emboîtées ne sont PAS déduites.**

Les cas #414 et #418 sont des stratégies **distinctes** : un ET est plus
restrictif que son opérande, deux agrégats d'une même matrice ne sont pas le même
agrégat. Les déduire relèverait d'un jugement qui, par construction, m'arrange.
Ils restent documentés comme non-indépendance **sans effet sur le compte**.

### Garde-fou 2 — l'ampleur est annoncée avant d'être calculée

Déduction attendue : **2 entrées** (`leaders_trend_union_overlay` et sa version
point-in-time, dont les jumeaux `sma200_leaders_overlay` restent comptés).
`n_trials` passe donc de **372 à 370**, soit **−0,5 %**.

Sur un DSR observé entre 0,12 et 0,18 pour un seuil à 0,95, l'effet attendu est
**négligeable**. Si un verdict basculait, ce serait le résultat principal du
cycle et devrait être rapporté comme tel — mais je n'y compte pas, et je l'écris
avant de mesurer.

## Ce qui n'est pas corrigé, et pourquoi c'est dit ici

`n_trials` est lu par **expression régulière dans la prose du backlog**
(`"X PASS sur Y hypothèses testées"`). Écrire un rapport modifie donc une
statistique. Ce défaut structurel a déjà été signalé et **reste non corrigé** :
le figer dans un fichier de données versionné est un changement de protocole qui
relève de l'arbitrage de l'utilisateur, pas d'une décision d'exécution. Ce cycle
ne le touche pas ; il le redit.

## Implémentation

Une constante explicite dans `nonml_pass_validation_battery.py`, listant les
paires identifiées et la déduction appliquée, avec commentaire renvoyant aux
cycles qui les ont établies. **Aucune autre ligne modifiée.**

## Critère de succès — chiffré

1. `n_trials` publié par la batterie passe de 372 à **370**.
2. Batteries ré-exécutées sur **au moins 3 candidats**, DSR **avant / après**
   publiés côte à côte.
3. Nombre de verdicts modifiés publié — y compris s'il vaut 0, ce qui serait la
   confirmation que la dette était **immatérielle**.

## Engagements

1. Résultat rapporté tel quel, y compris si la correction ne change rien —
   auquel cas le cycle aura mesuré l'inutilité pratique d'une dette portée trois
   fois, ce qui est un résultat.
2. Aucune déduction au-delà des identités mesurées.
3. **Relecture intégrale des rapports avant commit** (engagement #414).
