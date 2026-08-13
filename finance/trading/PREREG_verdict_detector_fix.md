# Pré-enregistrement — le détecteur de verdict : distinguer « porter » de « mentionner »

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, troisième après les #445 et #446, même discipline :
région annoncée, effet déclaré, critère qui peut échouer.

## Le défaut, établi au #446

Le balayage classe le verdict d'un rapport ainsi :

```python
if "**PASS" in t or "PASS (niveau 1)" in t:   # n'importe OU dans le texte
```

Le #446 a montré que cette règle **confond « porter un PASS » et « parler d'un
PASS »** : le rapport du #446, qui mentionne « stratégie portant un **PASS** » à
propos d'un *autre* candidat, est lui-même compté comme candidat PASS.

Tous les comptes de verdicts publiés par le balayage (FAIL 91, PASS 4,
indéterminé 18) reposent sur cette règle. Ils sont donc **suspects**, sans qu'on
sache encore de combien.

## Portée réelle, plus large que prévu — mesurée avant d'écrire

Le motif `"**PASS" in` apparaît dans **9 scripts** du dépôt, pas seulement le
balayage. Le défaut est **systémique**.

**Ce cycle n'en corrige qu'un** : le balayage (2 occurrences, lignes 156 et 206).
Les **8 autres** sont inventoriés et **explicitement non corrigés** — les
reprendre tous d'un coup serait une modification massive et non déclarable ligne
à ligne. Ils sont inscrits à la file.

C'est une limite assumée, pas un oubli.

## La règle nouvelle — déclarée avant toute mesure

> **Le verdict d'un rapport se lit sur une ligne dont le texte, une fois les
> espaces retirés, COMMENCE par le marqueur.**

```python
lignes = [ln.strip() for ln in t.splitlines()]
a_pass = any(ln.startswith("**PASS") for ln in lignes) or "PASS (niveau 1)" in t
a_fail = any(ln.startswith("**FAIL") for ln in lignes)
```

Une mention en cours de phrase (« portant un **PASS**, sans `.npz` ») ne
commence pas une ligne : elle cesse d'être comptée.

**Un seul changement à la fois** : la *précédence* reste identique (PASS
l'emporte sur FAIL, comme aujourd'hui), et le littéral `"PASS (niveau 1)"` est
**laissé tel quel**. Modifier l'un ou l'autre brouillerait l'attribution de
l'effet. S'ils posent problème, ce sera un autre cycle.

## Ce que la règle nouvelle risque de casser — dit d'avance

Un rapport qui énonce son verdict **en milieu de ligne** (« Verdict : **PASS** »)
ou **dans un titre** (`### **FAIL**`) cessera d'être détecté et deviendra
*indéterminé*. Ce n'est pas un bug de la règle mais sa contrepartie : elle est
plus stricte, donc elle rate ce qui n'est pas énoncé en tête de ligne.

**Cette contrepartie doit être mesurée, pas supposée.** D'où le critère 3.

## Critère de succès — chiffré, et il peut échouer

1. `git diff` **confiné aux deux occurrences annoncées** du balayage. Toute
   ligne touchée ailleurs vaut échec.
2. **Chaque rapport reclassé est listé**, avec son verdict avant, son verdict
   après, et **la ligne qui décide**. Aucun reclassement sans sa preuve.
3. **Lecture manuelle de contrôle.** Si les reclassés sont **≤ 15**, ils sont
   **tous** relus ; sinon **15** sont tirés de façon déterministe (liste triée,
   un sur *k*). **FAIL si une seule relecture contredit** le classement
   nouveau — c'est-à-dire si le rapport porte bien le verdict que la règle
   nouvelle lui refuse, ou l'inverse.
4. **Idempotence avec auto-inclusion** (leçon du #446) : le rapport de ce cycle
   est **supprimé avant mesure**, puis la mesure est refaite **après** son
   écriture. Les comptes doivent être identiques.

> **PASS** = les quatre points tenus.
> **FAIL** = diff hors région, ou un reclassement sans preuve, ou une relecture
> qui contredit, ou des comptes non idempotents.

## Prédiction — falsifiable

Je n'ai **pas** mesuré combien de rapports changent de classe.

Déductivement : la règle nouvelle étant **strictement plus stricte**, le compte
de PASS ne peut que **baisser ou rester égal**, et celui d'*indéterminé* ne peut
que **monter ou rester égal**. Si l'un des deux bougeait dans l'autre sens, ce
serait un défaut de ma mise en œuvre — et je le publierais comme tel.

J'attends que **les PASS baissent**. Je n'ai aucune idée de l'ampleur, et je
m'interdis d'ajuster la règle en fonction de ce que la mesure montrera.

## Engagements

1. Résultat rapporté tel quel, y compris un **FAIL** de ma propre correction.
2. Aucune ligne touchée hors des deux occurrences annoncées.
3. Aucun reclassement publié sans la ligne qui le décide.
4. **Aucun ajustement de la règle après avoir vu les comptes** — si elle
   reclasse mal, cela se publie, cela ne se retouche pas dans le même cycle.
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).
