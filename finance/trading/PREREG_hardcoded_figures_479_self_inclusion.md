# Pré-enregistrement — la citation « 16 et 2 » du #479 est-elle traçable au #463 ?

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de VÉRIFICATION**, première piste de la file
ouverte au #525 (« 24 candidats restants du #522, tous dans
`hardcoded_figures_remainder` »).

## Le lot le plus dense, traité un cas à la fois

`hardcoded_figures_remainder` (#479) porte **24** des 32 candidats
signalés au #522 — trop pour un seul cycle si chacun exige la même
profondeur que les #523/#524/#525. Ce cycle en traite **un**,
sélectionné parce qu'un examen préliminaire montre une **tension
réelle** (pas un désaccord d'axe évident comme aux #523/#524/#525) :
`nonml_self_inclusion_detector_backtest.py`.

## La tension, déclarée avant mesure

Le #479 classe ce script **« legitime »**, justifiant : *« "Le #463 a
trouvé 2 scripts non idempotents en en rejouant 18", "2 fautifs, 16
sains" — citations du #463, dont le script déclare par ailleurs les
listes nominatives »*.

Le **#504**, dans la série dédiée à confronter les emprunts à leur
source (#500-#504), classe **ce même script** parmi **« les 5
résidus »** — les *« seuls emprunts que cinq cycles n'ont pas su
rattacher à une source publiée »*, citant explicitement *« (#463, 16 et
2) »*.

**Ces deux verdicts ne peuvent pas être simultanément corrects au sens
fort** : soit la citation du #463 est traçable (#479 a raison), soit
elle ne l'est pas (#504 a raison). Un examen préliminaire (autorisé,
même précédent que les cycles antérieurs) du texte publié au #463
montre que son propre récit **ne nomme, par leur nom de script,
qu'un seul des 18** (`verdict_rule_propagation`) — pas les 16 « sains ».
**Ce cycle vérifie mécaniquement**, sans se fier à cette lecture.

## Le protocole

1. **Extraire par script** les deux listes hardcodées dans
   `nonml_self_inclusion_detector_backtest.py` (`FAUTIFS_463`,
   `SAINS_463`) — effectifs et noms.
2. **Parcourir mécaniquement** la section `## Backlog #463` du backlog
   (délimitation par en-tête, pas par citation manuelle) et compter :
   combien des 18 noms de script (2+16) y apparaissent **littéralement**,
   sous quelque forme (avec ou sans préfixe `nonml_`/suffixe `.py`) ?
3. **Comparer** au nombre attendu par une citation réelle (18/18) contre
   ce qui est effectivement trouvé.
4. **Si moins de 18/18** : la classification « legitime » du #479 est
   **fausse** au sens strict — ce n'est pas une citation vérifiable,
   c'est une reconstruction non publiée. Reclassement proposé :
   **« partiel »** (le script DÉCLARE ses listes, contrairement à un
   littéral nu, mais leur contenu n'est pas traçable au #463 tel que
   publié) — pas « defaut », car le #479 lui-même réserve « defaut » aux
   cas sans aucune déclaration nominative.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **18** noms (2 `FAUTIFS_463` + 16 `SAINS_463`) extraits par
   script et publiés.
2. Le compte de noms retrouvés littéralement dans la section `## Backlog
   #463` publié, sur les 18.
3. Le verdict du #479 confronté à ce compte, sans être rejugé à l'œil.
4. Si contradiction confirmée : la ligne `V` du #479 corrigée, diff
   borné à cette seule entrée, avec citation du #504.
5. Aucun script de marché exécuté.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Au plus 2 des 18** noms (les 2 `FAUTIFS_463`, explicitement
   discutés au #463) sont retrouvés littéralement dans la section
   `## Backlog #463` — les 16 `SAINS_463` n'y figurent **pas**.
2. Le verdict « legitime » du #479 est donc **contredit** : reclassé
   « partiel ».
3. La correction n'affecte **aucune** autre entrée du dictionnaire `V`
   du #479 (diff borné à 1 ligne).

## Ce que ce cycle ne fait pas

- Il ne **vérifie** aucun des 23 autres candidats de
  `hardcoded_figures_remainder` — file distincte, cycles séparés.
- Il ne **rejuge pas** le verdict du #504 lui-même (déjà établi,
  cinq cycles).
- Il n'**exécute** aucun script de marché.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification/réparation de dépôt, aucune
position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si les 18 noms se retrouvent
   tous (prédiction réfutée, pas de correction).
2. Population et protocole **inchangés** après mesure.
3. **Chaque verdict adossé à une ligne de code ou de texte citée.**
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
