# Pré-enregistrement — la règle complète du détecteur de verdict

**Écrit et committé AVANT toute modification et toute mesure.** `n_trials = 1`.

**Cycle de MODIFICATION**, quatrième après les #445, #446 et #447.

## Ce que le #447 a laissé, chiffré

Le #447 a remplacé `"**PASS" in t` par une lecture **en début de ligne**. Bilan
publié, **mixte** :

- **3 faux positifs corrigés** — des rapports d'inventaire sans aucun verdict,
  comptés PASS parce qu'ils *parlaient* d'un PASS ;
- **2 faux négatifs introduits** — le #444 (`## Verdict : **FAIL**`) et le #446
  (`### **FAIL**`) **portent** un FAIL et sont déclarés *indéterminés* ;
- **1 défaut résiduel isolé** — le littéral `"PASS (niveau 1)"`, laissé intact
  par la règle « un seul changement à la fois », reste comparé **en
  sous-chaîne**. Il classe le rapport du #447 en PASS alors que son verdict est
  FAIL, **parce que ce rapport parle du détecteur**.

Le #447 s'interdisait de corriger tout cela après avoir vu les comptes. Ce cycle
le déclare **avant**.

## La règle complète — écrite avant toute mesure

Un rapport **porte** un verdict si une ligne, **débarrassée de sa décoration
Markdown**, commence par le marqueur.

```python
def _nu(ln):                      # retire la decoration, pas le sens
    s = ln.strip()
    s = re.sub(r"^#{1,6}\s*", "", s)                     # titre
    s = re.sub(r"^>\s*", "", s)                          # citation
    s = re.sub(r"^[-*]\s+", "", s)                       # puce
    s = re.sub(r"^(\*\*)?Verdict(\s+final)?(\*\*)?\s*[:：—-]\s*", "", s, flags=re.I)
    return s

def porte_verdict(t, m):
    return any(_nu(ln).startswith(f"**{m}") or
               (m == "PASS" and _nu(ln).startswith("PASS (niveau 1)"))
               for ln in t.splitlines())
```

Deux changements, tous deux déclarés ici :

1. la décoration Markdown (titre, citation, puce, étiquette « Verdict : ») est
   retirée avant lecture — un verdict énoncé en titre est un verdict ;
2. le littéral `"PASS (niveau 1)"` devient **positionnel** comme le reste : il
   ne compte plus s'il apparaît en cours de phrase.

La **précédence reste inchangée** (PASS l'emporte sur FAIL). Le #447 avait
raison de ne changer qu'une chose ; il a isolé le défaut résiduel, et c'est
pourquoi ce cycle peut désormais viser les deux causes ensemble en les nommant
séparément.

## Régime de modification — différent du #447, et pourquoi

Le #447 s'interdisait toute ligne hors des deux occurrences, ce qui l'a forcé à
**dupliquer** la règle en clair aux deux endroits. La règle complète est trop
longue pour être écrite deux fois sans risque de divergence entre les copies.

**Régime déclaré ici — deux régions, pas une** :
(a) une fonction `_nu` + `porte_verdict` insérée **immédiatement avant
`def main()`** ; (b) les **deux occurrences** remplacées par un appel.

Toute ligne touchée **hors de ces deux régions** vaut échec du cycle. Le régime
est plus large qu'au #447, il est déclaré comme tel **avant** d'écrire le code,
et non élargi après avoir buté dessus.

## Critère de succès — chiffré, et il peut échouer

1. `git diff` **confiné aux deux régions annoncées**.
2. **Chaque rapport reclassé est publié** avec la ligne qui décide.
3. **Relecture de contrôle** : tous les reclassés si **≤ 15**, sinon **15** tirés
   de façon déterministe. **FAIL si une seule relecture contredit.**
4. **Les deux faux négatifs du #447 sont récupérés** : `third_npz_schema_handling`
   et `sweep_pass_prose_fix` doivent être classés **FAIL**. C'est la raison
   d'être du cycle ; s'ils ne le sont pas, il a échoué.
5. **Le défaut résiduel a disparu** : le rapport de ce cycle doit être classé
   selon **son propre verdict**, et non selon les littéraux qu'il cite. Vérifié
   après écriture.

> **PASS** = les cinq points tenus. **FAIL** = un seul manque.

**L'idempotence n'est pas reprise comme critère.** Le #447 a établi qu'un
rapport qui compte les rapports ne peut pas être idempotent, puisqu'il en est
un. Reconduire ce critère serait exiger l'impossible et le savoir.

## Prédiction — falsifiable

- **Les 2 faux négatifs sont récupérés** : c'est ce que la règle vise, et si
  elle échoue là, elle échoue tout court.
- Le passage du littéral en positionnel **peut reclasser d'autres rapports**, en
  nombre que **je n'ai pas mesuré**. Je m'attends à ce qu'il en fasse basculer
  au moins un vers *indéterminé* ou *FAIL* — sans quoi le littéral n'aurait
  jamais rien changé et le #447 se serait alarmé pour rien.
- Je **n'exclus pas** que la règle nouvelle produise ses propres faux positifs :
  retirer les puces fait remonter des lignes de variantes. Le critère 3 est là
  pour l'attraper, et je publierai le cas échéant.

## Engagements

1. Résultat rapporté tel quel, y compris un **FAIL**.
2. Aucune ligne hors des deux régions annoncées.
3. Aucun reclassement sans la ligne qui le décide.
4. **Aucun ajustement de la règle après avoir vu les comptes.**
5. **Relecture intégrale des rapports produits avant commit** (engagement #414).
