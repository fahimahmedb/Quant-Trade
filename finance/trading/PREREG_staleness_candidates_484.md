# Pré-enregistrement — vérification (et réparation si confirmée) des 3 candidats du #484

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de VÉRIFICATION, réparation si confirmée**,
première piste de la file ouverte au #524 (« 27 candidats restants »).

## La cible

L'écran du #522 a signalé **3** candidats dans le dictionnaire `V` de
`nonml_guards_witness_remainder_backtest.py` (#484, 10 entrées) :

| Clé `V` | Verdict `V` | Ligne | Mentionné en |
|---|---|---|---|
| `nonml_six_reports_regeneration_backtest.py` | MASQUANT | 232 | #494 |
| `nonml_sweep_pass_prose_fix_backtest.py` | MASQUANT | 134 | #494 |
| `nonml_self_inclusion_detector_backtest.py` | ANODIN | 106 | #504 |

## Une lecture préliminaire, déclarée avant mesure (même précédent que les #511/#517/#523/#524)

Un examen du code des deux cibles MASQUANT montre que chacune a
**déjà, dans son état actuel**, une ligne `L.append(` publiant sa
variable **avant** la garde citée — `perdus` (l.231, garde l.233) et
`strategies` (l.133, garde l.135). La justification du #484 affirmait
littéralement l'inverse : *« `perdus` n'apparaît nulle part hors de sa
garde »* et *« aucun compte de `strategies` n'est publié hors garde »*.

**Le cas `six_reports_regeneration` / `perdus` est le « contrôle
positif » explicitement désigné par le #484** — *« le cas exact du
#475 »*, cité comme référence dans plusieurs cycles ultérieurs
(#485 : *« Contrôle positif… une règle qui ne le classerait pas
masquant serait à jeter »*). **Si ce cas tombe, c'est le plus
significatif des 32 candidats du #522 identifiés à ce jour.**

Le #494 (« 4 témoins non publiés ») discute ces deux mêmes scripts
pour une raison compatible : un témoin existe **dans le code**, sans
que le rapport régénéré n'ait pu être committé (diff non borné). Ceci
**pourrait expliquer** la présence du témoin aujourd'hui sans trancher
s'il était déjà là au moment du #484 — question **hors du périmètre**
de ce cycle, qui vérifie l'état **actuel**, pas l'historique.

`self_inclusion_detector`, en revanche, est mentionné au #504 pour un
axe totalement différent (emprunts non rattachés à une source
publiée) — **hypothèse de faux positif**, même mécanisme qu'aux
#523/#524.

## Le protocole — mécanique, avant tout verdict définitif

Pour les 2 MASQUANT : même protocole qu'au #524 — extraire par AST le
noeud `If` de la garde (recherché par **nom de variable**, pas par
numéro de ligne exact, au cas où le fichier aurait dérivé), lister
toute référence de la variable dans un `L.append(`, vérifier si l'une
d'elles tombe hors de la plage du noeud `If`.

Pour `self_inclusion_detector` : comparer l'axe du #504 (chiffres
empruntés à une source) à celui du #484 (MASQUANT/ANODIN d'une
section), par citation de phrase caractéristique.

## Le geste, si confirmé — minimal et borné, même forme que les #520/#521/#524

Si un verdict tombe : modifier **uniquement** la ligne `V` concernée,
avec un commentaire citant la ligne de code qui la contredit. **Ne pas
régénérer le rapport du #484** si cela capture une dérive de
population plus large que les verdicts corrigés (vérifié avant de
committer quoi que ce soit sur le rapport, même garde-fou qu'au #524).

## Critère de succès — chiffré, il porte sur le procédé

1. Les **3** candidats vérifiés, chacun avec verdict et ligne de code
   à l'appui.
2. Pour les 2 MASQUANT : présence/absence de référence inconditionnelle
   établie par AST.
3. Pour `self_inclusion_detector` : axe du #504 comparé à celui du #484.
4. Tout verdict renversé publié avec diff borné à cette seule entrée.
5. Si régénérer le rapport du #484 déborderait du périmètre déclaré,
   la régénération est **refusée et documentée**, pas committée.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Les 2** candidats MASQUANT ont chacun **au moins une** référence
   inconditionnelle — verdict à reclasser ANODIN.
2. `self_inclusion_detector` est un **faux positif** (axe distinct).
3. Régénérer le rapport du #484 capturerait une dérive de population
   plus large que les 3 verdicts — **la régénération sera refusée**,
   comme au #524.

## Ce que ce cycle ne fait pas

- Il ne **vérifie** aucun des 24 autres candidats du #522 (tous dans
  `hardcoded_figures_remainder`, #479) — file distincte.
- Il ne **rejuge** aucune autre entrée de `V` du #484 hors les 3
  candidats.
- Il ne **détermine pas quand** le témoin manquant a été ajouté au
  code — seulement s'il y est **aujourd'hui**.
- Il n'**exécute** aucun script de marché.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification/réparation de dépôt, aucune
position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si le contrôle positif du
   #475/#484 tombe.
2. Population et protocole **inchangés** après mesure.
3. **Chaque verdict adossé à une ligne de code citée.**
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
