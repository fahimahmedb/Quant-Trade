# Audit indépendant — confrontation des emprunts (#501)

Le backtest découpe le registre **ligne à ligne**. Cet audit le recoupe
par **`re.split` sur les en-têtes** et reclasse tout.

## Le reclassement

| Grandeur | Rapport | Audit | Accord |
|---|---|---|---|
| chaînes | **31** | **31** | **oui** |
| nombres | **39** | **39** | **oui** |
| confirmé | **22** | **22** | **oui** |
| retrouvé ailleurs | **17** | **17** | **oui** |
| non retrouvé | **0** | **0** | **oui** |
| non vérifiable | **0** | **0** | **oui** |
| confirmations fortes | **3** | **3** | **oui** |
| confirmations faibles | **19** | **19** | **oui** |

- grandeurs en désaccord : **0**

## Trois propriétés que le backtest n'énonce pas

- les quatre classes forment une **partition** : **OUI**
- **confirmé ⊂ retrouvé quelque part** — une classe ne peut être plus
  stricte que celle qui la contient : **OUI**
- la coupure forte/faible ne dépend que du **nombre de chiffres** : **OUI**

> L'inclusion n'est pas une évidence de code : « confirmé » regarde
> **une** section, « retrouvé ailleurs » regarde **tout**. Qu'aucun
> confirmé n'échappe au second est ce qui rend les classes lisibles
> comme des cercles emboîtés plutôt que comme des étiquettes.

## Ce que l'accord des deux routes **ne** prouve **pas**

Les deux mécaniques partagent la **même règle de confrontation** — elles
ne diffèrent que par le **découpage** du registre. Leur accord valide le
découpage, **pas la règle** : si chercher un nombre en gras dans une
section est un mauvais test de justesse, les deux routes se trompent
ensemble. **Le rapport le dit déjà, et cet audit ne le contredit pas.**

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **23** ; dont **tapés en dur** : **0**

## Verdict

1. les deux découpages donnent les mêmes huit grandeurs — **OUI**.
2. les quatre classes forment une partition — **OUI**.
3. confirmé est inclus dans retrouvé quelque part — **OUI**.
4. la coupure forte/faible est reproductible — **OUI**.
5. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (5/5)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
Son équivalent ici est **l'inertie**, vérifiée ci-dessus.
