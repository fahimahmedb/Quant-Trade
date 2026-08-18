# Pré-enregistrement — la **règle de lecture déclarée**, et son application élargie

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #482.

## Un aveu préalable, qui commande tout le reste

Le #480 devait classer trois cycles. Sa règle mécanique a répondu **A/C/?**.
Puis, hors protocole, **je les ai lus à la main et j'ai publié que les trois
relevaient de C** — sans retenir cette version, faute d'examen déclaré.

> **Je connais donc déjà la réponse sur ces trois-là.** Rejouer la question et
> annoncer « prédiction vérifiée : 3/3 en C » serait **prédire ce que j'ai déjà
> vu**. Ce serait la forme la plus creuse de confirmation, et le protocole
> anti-snooping l'interdit.

**Conséquence, fixée ici :** sur les trois, ce cycle **ratifie**, il ne teste
rien. Le résultat sera publié comme **non informatif**, et **aucune prédiction
n'est formulée à son sujet**.

Ce qui est réellement ouvert, c'est autre chose : **la même règle, appliquée à
une population plus large où je n'ai rien lu.**

## La population élargie

Tout `PREREG_<nom>.md` du dépôt **dont aucun `results/nonml_<nom>_result.md`
n'existe**. Les trois du #480 en font partie ; les autres n'ont **jamais été
examinés**, et c'est sur eux que porte le contenu de ce cycle.

## La règle de lecture — déclarée ici, mot pour mot

Sur les **douze premières lignes** de chaque `PREREG_`, extraire la
**auto-déclaration** de la forme `Cycle de **X**` / `Cycle d'**X**`.

Le cycle est classé **SANS RÉSULTAT ATTENDU** si `X` contient l'un de ces mots,
et **RÉSULTAT ATTENDU** sinon :

```
audit, correction, diagnostic, infrastructure, inventaire,
vérification, verification, modification, réparation, arbitrage
```

Un `PREREG_` **sans auto-déclaration** dans ses douze premières lignes est
classé **NON DÉCLARÉ** — compté à part, **jamais présenté comme fautif**.

**Cette liste est figée.** L'élargir après avoir vu les résultats serait le
retuning exact que le #480 a refusé de commettre.

## L'examen à la main — DÉCLARÉ, et son échantillon fixé

**Jusqu'à 5 cycles classés RÉSULTAT ATTENDU** — donc les seuls candidats à être
de vrais cycles inachevés — pris **dans l'ordre alphabétique du `<nom>`**, sont
lus un par un. Chacun reçoit un verdict écrit à la main :

- **INACHEVÉ** — le pré-enregistrement annonce bien un résultat propre au cycle,
  et il n'existe pas ;
- **MAL CLASSÉ** — la lecture montre que ma règle s'est trompée (déclaration
  formulée autrement, mention d'un `_result.md` qui désigne **un autre** cycle —
  le faux positif exact du #480).

## Critère de succès — chiffré, il porte sur le procédé

1. Population énumérée, effectif publié, les **3** du #480 **identifiés comme
   ratifiés et non testés**.
2. **100 %** classés, la liste de mots **citée verbatim** dans le rapport.
3. Les **NON DÉCLARÉS** comptés à part et exclus de tout total de dette.
4. **Jusqu'à 5 examinés à la main**, chacun avec son verdict.
5. Le caractère **non informatif** du résultat sur les trois **écrit à
   l'endroit du chiffre**, pas en note.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables, et **aucune ne porte sur les trois**

1. Sur la population élargie, **≥ 60 %** des `PREREG_` sans résultat se
   déclarent **SANS RÉSULTAT ATTENDU**. *(Fondement : un cycle qui ne publie pas
   de `_result.md` est le plus souvent un cycle d'audit ou de correction.)*
2. **≥ 1** cycle est classé **RÉSULTAT ATTENDU** — sans quoi l'examen à la main
   n'aurait aucun objet.
3. Sur les cycles examinés, **≥ 1** est **MAL CLASSÉ** — ma règle littérale a un
   angle mort, comme en ont eu celles des #469, #478, #480 et #481.

Si la prédiction 3 est réfutée — **aucun mal classé** — alors la règle déclarée
tient sur toute la population, et je devrai le noter **sans en tirer qu'elle est
juste** : cinq lectures ne valident pas une règle, elles échouent seulement à la
prendre en défaut.

## Ce que ce cycle ne fait pas

- Il ne **produit** aucun `_result.md` manquant.
- Il n'**exécute** aucun script du dépôt : lecture du disque, **aucun effet de
  bord**.
- Il ne **réécrit** ni le #480 ni son entrée — la ratification s'ajoute, elle
  n'efface pas.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il prend ma règle en défaut.
2. Liste de mots, population et taille d'échantillon **inchangées** après mesure.
3. **Le résultat sur les trois est présenté comme une ratification non
   informative**, jamais comme une prédiction vérifiée.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
