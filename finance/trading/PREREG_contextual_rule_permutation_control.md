# Pré-enregistrement — la règle contextuelle du #502 devant un **témoin de permutation**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #513.

## Pourquoi ce test est dû

Les #512 et #513 ont établi qu'un détecteur peut produire un chiffre entier
sans rien mesurer : leurs témoins neutres faisaient **mieux** que les
marqueurs réels. **Aucun détecteur des #500-#511 n'a subi ce test.**

Or l'un d'eux n'est pas un détecteur parmi d'autres : la **règle contextuelle
du #502** — *« ≥ 2 mots-clés de l'emprunt dans ±200 caractères »* — est le
**socle partagé** des cycles **#502, #503, #504, #505, #508 et #509**. Si elle
ne discrimine pas, **six cycles de conclusions tombent ensemble**.

## Le témoin — une **permutation**, pas des mots neutres

Un témoin de mots neutres ne convient pas ici : la règle ne cherche pas des
mots choisis, elle cherche **les mots-clés de l'emprunt lui-même**. Le témoin
correct est donc une **permutation** :

> Pour chaque emprunt, on rejoue **exactement la même règle** en remplaçant
> ses mots-clés par ceux de **l'emprunt suivant** dans la population triée par
> `(script, cycle cité, valeur)` — le dernier reprenant ceux du premier.

**C'est une dérangement déterministe** : aucun tirage, aucun aléa, reproductible
à l'identique. Un emprunt confirmé avec les mots-clés **d'un autre** l'est par
**coïncidence de vocabulaire**, pas par identité de sujet.

## Ce qui est mesuré

1. Le taux d'emprunts **« au sujet quelque part »** (registre, rapports,
   `PREREG_`) avec leurs **vrais** mots-clés.
2. Le même taux avec les mots-clés **permutés**.
3. L'**écart**, et le verdict au seuil de **20 points** — **le seuil du #513,
   repris verbatim**.
4. Les emprunts confirmés **sous permutation**, nommés : ce sont les faux
   positifs que la règle produit par construction.

## Ce qui est en jeu — dit d'avance

| Résultat | Conséquence |
|---|---|
| écart **≥ 20 points** | la règle du #502 **discrimine** ; les conclusions des #502-#509 tiennent |
| écart **< 20 points** | la règle **ne discrimine pas** ; **six cycles** reposent sur un détecteur qui mesure la densité du texte, et il faudra l'écrire |

> **Je ne peux pas gagner à tous les coups ici, et c'est le but.** Ce cycle
> peut invalider six de mes propres cycles ; le pré-enregistrement fixe la
> conséquence **avant** de connaître le chiffre.

## Critère de succès — chiffré

1. La règle de permutation et le seuil de **20 points** cités verbatim.
2. Les **deux taux** publiés, avec leurs effectifs.
3. L'**écart** publié et le verdict rendu au seuil.
4. Les emprunts confirmés sous permutation **nommés individuellement**.
5. **Aucun script exécuté**, arbre vérifié propre.

> **PASS** = les cinq points. **FAIL** = un seul manque.
> **Le PASS ne dépend pas du succès de la règle** — il dépend de la
> publication honnête du verdict, quel qu'il soit.

## Prédictions — falsifiables

1. L'écart est **≥ 20 points** : la règle du #502 survit.
2. Le taux sous permutation est **> 0** — des coïncidences existent.
3. Les emprunts confirmés sous permutation sont **< 10**.

Si la prédiction 1 est réfutée, **les #502, #503, #504, #505, #508 et #509
sont tous atteints**, et le backlog devra le porter. Ce serait le plus large
retrait de la série.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script, ne **réécrit** aucun rapport antérieur.
- Il ne teste **que** la règle contextuelle : les autres détecteurs des
  #500-#511 (appariement AST, primitives d'exécution) relèvent d'un cycle
  distinct, et **restent non testés** — je le rappellerai dans le rapport
  plutôt que de laisser croire à un examen complet.
- Il ne **se compte pas lui-même** — auto-exclusion (règle #447).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, **y compris s'il invalide six cycles**.
2. Règle de permutation, seuil et population **inchangés** après mesure.
3. Les deux taux publiés côte à côte, jamais le seul favorable.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
