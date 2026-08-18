# Audit indépendant — résidus et sources non publiées (#505)

Cet audit ne refait pas la même mesure : il **relâche la contrainte**.
Il cherche le nombre **nu, sans aucune exigence de sujet**, dans tout le
dépôt suivi par git. Un « introuvable partout » qui reste introuvable
**même sans contrainte de contexte** est un constat bien plus fort ;
s'il apparaît, **c'est la contrainte qui le masquait**.

## Le corpus élargi

- fichiers suivis lus (`.py`, `.md`, `.txt`) : **3203**
- messages de commit : **2340**
- « introuvables partout » relus dans le rapport : **2**
- effectif publié par le rapport : **2**
- accord : **OUI**

## Chaque introuvable, sans contrainte de contexte

| Script | Cite | Nombre | Fichiers portant le nombre nu | Dans un commit |
|---|---|---|---|---|
| `nonml_content_defined_magnitudes_audit.py` | `#449` | **2** | **1335** | **oui** |
| `nonml_report_idempotence_backtest.py` | `#443` | **5,7** | **9** | **oui** |

- introuvables **même sans contrainte de sujet** : **0** sur **2**

> **Tous apparaissent ailleurs dès qu'on retire la contrainte de
> sujet.** Ce n'est donc pas leur existence qui manquait, mais leur
> **voisinage thématique** : la règle du #502 les a écartés parce
> qu'ils n'étaient pas entourés des bons mots, non parce qu'ils
> étaient absents. **Le mot « introuvable » du rapport est trop
> fort**, et cet audit le corrige.

## Les résidus sont-ils bien extraits de leur script ?

- « introuvables » dont l'emprunt est **retrouvé par l'AST** du script
  qui les publie : **2** sur **2**

> Ils ne sont donc pas un artefact d'extraction de la chaîne
> #500-#504 : chacun correspond bien à une chaîne publiée par son
> script, citant le cycle annoncé.

## Le sourçage circulaire, recompté

- trouvailles circulaires publiées : **2**
- trouvailles en `PREREG_` tiers : **1**

> La distinction que le rapport s'impose — un chiffre trouvé dans le
> `PREREG_` **du script qui le publie** ne le source pas — est la seule
> qui empêche cette série de se valider elle-même. Sans elle, le cycle
> aurait annoncé **3** résidus sourcés au
> lieu de **1**.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **51** ; dont **tapés en dur** : **0**

## Verdict

1. l'effectif des introuvables concorde avec le rapport — **OUI**.
2. chaque introuvable est re-cherché sans contrainte de contexte — **OUI**.
3. les introuvables ne sont pas un artefact d'extraction — **OUI**.
4. le sourçage circulaire est distingué du sourçage tiers — **OUI**.
5. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (5/5)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
Son équivalent ici est **l'inertie**, vérifiée ci-dessus.
