# Audit indépendant — taux de rectification (#512)

Cet audit ne refait pas la même mesure : il monte un **témoin négatif**.
Il rejoue **exactement la même règle** avec des marqueurs **neutres** —
des mots fréquents du registre étrangers à toute rectification. Si le
taux obtenu avec des mots neutres approche le taux publié, **le
détecteur ne mesure pas la rectification mais la cooccurrence**.

## Le témoin négatif

> mots neutres employés : `cycle`, `rapport`, `mesure`, `script`, `publie`, `critère`, `verdict`, `audit`, `population`, `chiffre`, `règle`, `dépôt`

| Liste de marqueurs | Cycles « rectifiés » | Taux |
|---|---|---|
| **réels** (#512) | **183** | **59,4 %** |
| **neutres** (témoin) | **275** | **89,3 %** |

- écart : **-29,9** points

> **Le témoin négatif fait MIEUX que les marqueurs réels.** Des mots
> quelconques du registre — `cycle`, `rapport`, `mesure` — désignent
> **plus** de cycles « rectifiés » (89,3 %) que les marqueurs de
> rectification (59,4 %).
>
> **Le détecteur ne discrimine rien.** Il réagit à la présence d'une
> référence `#NNN` dans un texte dense, pas au fait qu'une
> rectification soit écrite. **Le taux publié par le #512 ne mesure
> pas ce qu'il annonce**, et sa « borne supérieure » comme sa
> « lecture stricte » héritent du même défaut.

## Trois propriétés que le backtest n'énonce pas

- **auto-rectifications** captées (un cycle se citant lui-même avec un
  marqueur) : **132** — elles sont **exclues** par la règle ;
- **références rétrospectives** (un cycle citant un successeur) : **32** — exclues elles aussi ;
- **paires symétriques** (A rectifie B **et** B rectifie A) : **0** *(doit valoir 0 : seul un successeur rectifie)*

## Le recalcul des grandeurs publiées

| Grandeur | Rapport | Audit | Accord |
|---|---|---|---|
| cycles rectifiés | **183** | **183** | **oui** |
| taux global | **59,4** | **59,4** | **oui** |
| délai médian | **1** | **1** | **oui** |

- grandeurs en désaccord : **0**

## Ce que cet audit ne prouve pas

Le témoin négatif teste la **spécificité** du détecteur, pas la
**justesse** de chaque appariement. Et il partage la fenêtre de
**±200 caractères** : si cette fenêtre est trop large, les deux
listes en souffrent également — c'est justement ce que l'écart mesure.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras : **77** ; dont **tapés en dur** : **0**

## Verdict

1. le témoin négatif est monté et publié — **OUI**.
2. le détecteur discrimine mieux que des mots neutres — **NON**.
3. aucune paire symétrique — **OUI**.
4. les grandeurs publiées sont recalculées à l'identique — **OUI**.
5. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT — RÉSERVE** (4/5)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
