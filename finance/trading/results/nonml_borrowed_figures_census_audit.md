# Audit indépendant — chiffres empruntés sans relecture (#500)

Le backtest **reconstruit** le texte d'une f-string en concaténant ses
`Constant`. Cet audit part du **segment de source brut** du même nœud et
retire les champs `{…}` à la main. **Même définition, mécanique
différente** — c'est là qu'un faux positif porteur/citeur se cacherait.

## Le recomptage

| Grandeur | Rapport | Audit | Accord |
|---|---|---|---|
| porteurs | **24** | **24** | **oui** |
| emprunts | **31** | **31** | **oui** |
| relecteurs | **133** | **133** | **oui** |
| porteurs qui lisent aussi | **19** | **19** | **oui** |
| porteurs qui ne lisent pas | **5** | **5** | **oui** |

- grandeurs en désaccord : **0**

## Trois contrôles que le backtest n'énonce pas

- chaînes détectées **absentes verbatim** de leur fichier : **0**
- docstrings comptées comme chaînes publiées : **0** *(exclues par
  construction : cet audit les identifie explicitement et les écarte)*
- l'arithmétique du croisement ferme (**19** + **5** = **24**) : **OUI**

> Les deux mécaniques **concordent sur les cinq grandeurs**. La
> distinction porteur / citeur tient donc aussi bien depuis le texte
> reconstruit que depuis la source brute — ce qui n'allait pas de soi :
> les #496 et #497 ont tous deux vu une route se tromper.

## Ce que cet audit ne vérifie pas non plus

**Aucun emprunt n'est confronté à sa source.** Le rapport le disait ; je
le redis, parce qu'un audit qui concorde sur cinq comptes peut donner
l'illusion d'avoir validé les **valeurs**. Il n'a validé que le
**dénombrement**.

## Inertie et chiffres calculés

- fichiers de l'arbre modifiés hors ce cycle : **0**
- nombres en gras dans le rapport : **41** ; dont **tapés en dur** : **0**

## Verdict

1. les deux mécaniques donnent les mêmes cinq comptes — **OUI**.
2. chaque chaîne détectée existe verbatim dans son fichier — **OUI**.
3. l'arithmétique du croisement ferme — **OUI**.
4. aucun chiffre du rapport tapé en dur, arbre propre — **OUI**.

**AUDIT OK** (4/4)

Anti-lookahead **sans objet au sens temporel** : aucune série de prix.
Son équivalent ici est **l'inertie**, vérifiée ci-dessus.
