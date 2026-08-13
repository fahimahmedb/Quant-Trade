# Audit — requalification des PASS obtenus par inactivité

Le balayage n'a requalifié **aucun** candidat. Deux lectures opposées sont
possibles : il n'y avait rien à requalifier, ou la règle ne sait pas détecter.
Cet audit tranche.

## 1. Contrôle positif — la règle reconnaît-elle l'inactivité ?

`weakness_breadth_vol_targeting_overlay` a un P&L établi comme identique à Buy & Hold (#416).

- séances testées : **1385**
- séances où le P&L diffère (hors coût d'entrée) : **0**
- reconnu identique par la règle : **OUI**

**CONFORME — le zéro requalification est informatif.**

## 2. Contrôle négatif — une porte rare n'est pas une porte neutralisée

`santa_vol_targeting_overlay` n'active sa porte que 1,70 % du temps mais **agit** quand elle
s'ouvre (#416). La règle ne doit **pas** le requalifier.

- séances où le P&L diffère de Buy & Hold : **203**
- requalifié à tort : **NON**

**CONFORME — le critère d identité ne confond pas rareté et inactivité.**

## 3. La tâche demandée était-elle déjà faite ?

Le backlog du #416 inscrivait comme tâche : « requalifier
`weakness_breadth_vol_targeting_overlay` — le PASS doit porter l'étiquette non informatif comme sa version
point-in-time ». L'audit vérifie l'historique du fichier plutôt que de croire
l'énoncé de la tâche.

- le rapport porte l'étiquette « NON INFORMATIF » : **OUI**
- cette étiquette a-t-elle été ajoutée par le présent cycle : **NON**

**La tâche était déjà faite — et depuis son cycle d'origine.** Le rapport du
#89 portait déjà, dans son propre texte, un avertissement en toutes lettres :
« PASS NON INFORMATIF […] l'overlay ne s'active essentiellement jamais […]
ne constitue PAS une validation économique ». L'étiquette n'a jamais manqué.

**L'erreur est la mienne, et elle est datée** : en rédigeant la file du #416
j'ai inscrit cette requalification sans rouvrir le rapport concerné. C'est
exactement la règle du #400 — vérifier l'historique avant d'agir — appliquée
scrupuleusement aux candidats de stratégie et oubliée pour une tâche de
maintenance.

Ce que le cycle a produit de réel n'est donc pas la requalification annoncée,
mais le **balayage systématique** qui l'accompagnait.

## 4. Portée non couverte

- `.npz` inexploitables par la règle : **15**
- dont portant un PASS : **8**

- `amihud_illiquidity_tilt`
- `january_effect_lowprice_overlay_pit_universe`
- `leaders_index52w_high_overlay`
- `leaders_vol_targeting_20_overlay`
- `momentum_12_1_pit_universe`
- `momentum_turnover_doublesort`
- `sma200_leaders_overlay`
- `winners_trend_vol_targeting_overlay`

Ces candidats ont une jambe de référence qui n'est **pas** Buy & Hold mais un
portefeuille (schémas « panier » et « deux jambes »). Le critère d'identité ne
s'y transpose pas tel quel : un overlay de panier peut être inactif sans que son
P&L égale celui d'un indice. Étendre la règle à ces schémas demanderait de
comparer chaque candidat à **sa propre** référence — travail distinct, non
entrepris ici et déclaré comme tel.

## Verdict de l'audit

**MÉTHODE VALIDE.** Contrôles positif et négatif conformes : le zéro
requalification signifie bien qu'il n'y avait rien à requalifier parmi les
**158** candidats mesurables, et non que la règle est aveugle.

Sur ces 158, **72** portent un PASS dont
l'overlay agit réellement. **Le PASS obtenu par inactivité est un cas isolé**,
déjà documenté à son cycle d'origine — pas un travers répandu du backlog.
