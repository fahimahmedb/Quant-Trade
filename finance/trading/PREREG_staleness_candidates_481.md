# Pré-enregistrement — vérification (et réparation si confirmée) des 3 candidats du #481

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de VÉRIFICATION, réparation si confirmée**,
première piste de la file ouverte au #523 (« 30 candidats restants »).

## La cible

L'écran du #522 a signalé **3** candidats dans le dictionnaire `V` de
`nonml_guards_without_witness_backtest.py` (#481, 5 entrées) :

| Clé `V` | Verdict `V` | Ligne | Mentionné en |
|---|---|---|---|
| `nonml_battery_coverage_backtest.py` | MASQUANT | 159 | #489 |
| `nonml_net_pnl_correction_backtest.py` | MASQUANT | 279 | #489 |
| `nonml_marker_emitter_crossing_backtest.py` | ANODIN | 175 | #518 |

## Une lecture préliminaire, déclarée avant mesure (même précédent que les #511/#517/#523)

Un examen du code des cibles montre que **#489 a explicitement ajouté
un témoin** (« Deux témoins ajoutés, patch purement additif ») aux deux
sections **MASQUANT** de `battery_coverage` et `net_pnl_correction` —
précisément les deux du #481. La définition de MASQUANT au #481 est :
*« la variable n'apparaît nulle part hors de la garde »*. Si le témoin
du #489 rend cette variable visible **ailleurs, sans condition**, la
définition même du MASQUANT ne tient plus — indépendamment de la
question distincte que le #489 a posée (son propre critère de
« profondeur » de témoin, qui a d'ailleurs échoué : FAIL au #489).

**Ce constat n'est pas encore vérifié mécaniquement** — seulement lu à
l'œil. `marker_emitter_crossing`, en revanche, est mentionné au #518
pour un axe totalement différent (réparabilité d'un chiffre cité par
le #485), comme au #523 — **hypothèse de faux positif, à vérifier de
la même façon**.

## Le protocole — mécanique, avant tout verdict définitif

Pour `battery_coverage` et `net_pnl_correction` :

1. **Extraire par AST** toutes les lignes où la variable citée
   (`indet`, `incoh`) est référencée dans un `L.append(`.
2. **Pour chaque référence**, déterminer si elle est **à l'intérieur**
   du bloc `if` qui définit la garde citée au #481, ou **en dehors**
   (donc inconditionnelle).
3. **Si au moins une référence inconditionnelle existe** : le MASQUANT
   ne tient plus, reclassé **ANODIN**, avec la ligne exacte citée.
4. **Si aucune** : le MASQUANT tient, aucune correction.

Pour `marker_emitter_crossing` :

5. **Même protocole qu'au #523** : l'objet du #518 est-il le même axe
   d'évaluation, ou un axe distinct (vérifié par citation de la phrase
   caractéristique du #518) ?

## Le geste, si confirmé — minimal et borné, même forme que les #520/#521

Si un verdict tombe : modifier **uniquement** la ligne `V` concernée,
avec un commentaire citant le #489. Régénérer le rapport si applicable.
**Rien d'autre touché.**

## Critère de succès — chiffré, il porte sur le procédé

1. Les **3** candidats vérifiés, chacun avec verdict et ligne de code
   à l'appui.
2. Pour les 2 MASQUANT : présence/absence de référence inconditionnelle
   établie par AST, pas par lecture seule.
3. Pour `marker_emitter_crossing` : axe du #518 comparé à celui du #481.
4. Tout verdict renversé publié avec diff borné à cette seule entrée.
5. Aucun script de marché exécuté.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Les 2** candidats MASQUANT (`battery_coverage`,
   `net_pnl_correction`) ont chacun **au moins une** référence
   inconditionnelle à leur variable — verdict à reclasser ANODIN.
2. `marker_emitter_crossing` est un **faux positif** (axe distinct),
   comme au #523.
3. Le compte final du #481 passe de **2 MASQUANT / 3 ANODIN** à
   **0 MASQUANT / 5 ANODIN**.

## Ce que ce cycle ne fait pas

- Il ne **vérifie** aucun des 27 autres candidats du #522 — files
  distinctes.
- Il ne **rejuge** aucune autre entrée de `V` du #481 hors les 3
  candidats (`citer_451_resolution`, `net_pnl_correction_robustness`
  restent hors périmètre).
- Il n'**exécute** aucun script de marché.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification/réparation de dépôt, aucune
position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si les 2 MASQUANT tiennent
   encore (prédiction 1 réfutée).
2. Population et protocole **inchangés** après mesure.
3. **Chaque verdict adossé à une ligne de code citée.**
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
