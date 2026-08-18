# Audit indépendant — référence ou valeur (#503)

Le backtest balaie **toutes les sections** et cherche le nombre dans
chacune. Cet audit prend le **chemin inverse** : il localise le nombre
dans le fichier entier, puis rattache chaque occurrence à sa section
**par position**. Même règle, parcours opposé.

## Le reclassement par le chemin inverse

| Grandeur | Rapport | Audit | Accord |
|---|---|---|---|
| suspects | **29** | **29** | **oui** |
| référence probable ailleurs | **15** | **15** | **oui** |
| valeur suspecte | **13** | **13** | **oui** |
| indéterminé | **1** | **1** | **oui** |
| candidates uniques | **12** | **12** | **oui** |
| candidates toutes postérieures | **14** | **14** | **oui** |

- grandeurs en désaccord : **0**

## Quatre propriétés que le backtest n'énonce pas

- les trois classes forment une **partition** : **OUI**
- l'effectif égale **14** + **15** du #502 : **OUI**
- « valeur suspecte » et « indéterminé » ont **0** candidate : **OUI**
- la direction des candidates, recalculée : **14** sur
  **15** n'ont que des candidates **postérieures**

> La correction que le rapport s'inflige — « ma classe s'appelle
> mal » — est **confirmée par ce chemin indépendant**. Elle n'est pas
> une concession rhétorique : le registre **reprend ses chiffres vers
> l'avant**, et un détecteur qui ignore le temps prend cette reprise
> pour une erreur d'attribution.

## Ce que cet audit ne prouve pas

Les deux parcours appliquent la **même règle contextuelle**. Leur accord
valide le **parcours**, pas la règle. Et **aucun des deux** ne lit le
sens : « repris plus tard » reste une inférence tirée de **numéros de
cycle**, pas de la lecture des phrases.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **74** ; dont **tapés en dur** : **0**

## Verdict

1. les deux parcours donnent les mêmes six grandeurs — **OUI**.
2. les trois classes forment une partition — **OUI**.
3. l'effectif des suspects égale celui du #502 — **OUI**.
4. les classes sans candidate en ont bien zéro — **OUI**.
5. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (5/5)

Anti-lookahead **sans objet au sens temporel** pour les prix ; en
revanche ce cycle **introduit une notion de temps** — l'ordre des
cycles — et c'est elle qui a corrigé sa propre conclusion.
