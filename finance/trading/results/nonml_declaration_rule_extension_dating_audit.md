# Audit indépendant — extension de la règle tolérante au #483 (#498)

Le backtest date **fichier par fichier** (`git log --diff-filter=A` par
`PREREG_`). Cet audit reconstruit les dates en **un seul parcours** de
l'historique (`git log --name-status`), puis recompte tout par-dessus.

## La datation, par une autre commande

- `PREREG_` datés par le parcours unique : **473**
- `PREREG_` que ce parcours **ne date pas** : **0**
- population publiée par le rapport : **473**
- accord sur la taille : **OUI**

## Les comptes et les verdicts, recalculés

| Grandeur | Rapport | Audit | Accord |
|---|---|---|---|
| déclarés — littérale | **36** | **36** | **oui** |
| déclarés — tolérante | **78** | **78** | **oui** |
| verdict — littérale | **C** | **C** | **oui** |
| verdict — tolérante | **A** | **A** | **oui** |
| antérieurs au 1ᵉʳ déclaré | **380** | **380** | **oui** |
| dont tolérants | **0** | **0** | **oui** |

- grandeurs en désaccord : **0**

## Une propriété que le backtest n'énonce pas

La tolérante doit être un **sur-ensemble** de la littérale : elle accepte
les deux typographies, la littérale une seule. Un `PREREG_` détecté par
la **littérale seule** signalerait une transcription fautive.

- détectés par la littérale **seule** : **0**

> **Inclusion vérifiée.** L'écart de **+42** annoncé par le
> rapport est donc un **gain net**, jamais un échange.

## Les emprunts sont-ils fidèles ?

Le #497 a montré qu'un chiffre repris d'un cycle antérieur **sans être
relu** est un canal d'erreur. Ici, ce ne sont pas des chiffres qui sont
empruntés mais un **critère** et deux **règles** :

- le critère A/B/C se retrouve mot pour mot dans le #483 : **OUI**
- les deux regex se retrouvent dans le #492 : **OUI**

## Inertie et chiffres calculés

- fichiers de l'arbre git modifiés hors ce cycle : **0**
- nombres en gras : **13** ; dont **tapés en dur** : **0**

## Verdict

1. la datation par un autre parcours donne la même population — **OUI**.
2. comptes et verdicts recalculés concordent — **OUI**.
3. la tolérante inclut bien la littérale — **OUI**.
4. critère et règles retrouvés dans leurs cycles d'origine — **OUI**.
5. aucun chiffre tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (5/5)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
La datation, elle, est **strictement rétrospective** — chaque `PREREG_`
est daté par son **premier** commit d'ajout, jamais par l'état courant.
