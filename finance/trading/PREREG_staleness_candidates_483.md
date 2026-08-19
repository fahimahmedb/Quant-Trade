# Pré-enregistrement — vérification des 2 candidats de staleness du #483

**Écrit et committé AVANT toute mesure.** `n_trials` continue le compte
global. **Cycle de VÉRIFICATION**, première piste de la file ouverte au
#522 (« 32 candidats à vérifier manuellement »).

## La cible — le plus petit lot, entièrement vérifiable en un cycle

L'écran du #522 a signalé **2** candidats dans
`nonml_orphan_audits_declared_reading_backtest.py` (#483, dictionnaire
`V` de 4 entrées) :

| Clé `V` du #483 | Verdict `V` | Mentionné en | Marqueurs |
|---|---|---|---|
| `coverage_wording_fix` | MAL CLASSÉ | #518 | FAUSSE, réfuté |
| `duplicate_sweep_coverage` | MAL CLASSÉ | #518 | FAUSSE, réfuté |

Sur les 4 dictionnaires du #522, celui-ci est **le seul entièrement
vérifiable en un cycle** (4 entrées, 2 candidats) — les 3 autres
(**hardcoded_figures_remainder** 24/32, **guards_witness_remainder**
3/10, **guards_without_witness** 3/5) restent en file pour des cycles
dédiés séparés, comme prévu au #522.

## Une hypothèse déjà lisible, déclarée avant mesure

Un examen préliminaire (autorisé, même précédent que les #511/#517)
montre que la population du #483 porte sur des `PREREG_<nom>.md`
**sans suffixe** (`PREREG_coverage_wording_fix.md`,
`PREREG_duplicate_sweep_coverage.md`), tandis que le #518 discutait des
scripts `nonml_coverage_wording_fix_audit.py` et
`nonml_duplicate_sweep_coverage_audit.py` — **avec le suffixe
`_audit`**. L'écran du #522 réduisait les deux à la même clé courte
(« coverage_wording_fix ») en retirant les suffixes `_backtest.py`/
`_audit.py`, ce qui **pourrait avoir confondu deux objets distincts**
plutôt qu'avoir trouvé une vraie contradiction. **Ce cycle vérifie
mécaniquement**, sans se fier à cette lecture.

## Le protocole

Pour chacun des 2 candidats :

1. **Le verdict `MAL CLASSÉ` porte-t-il toujours** au vu du texte actuel
   de `PREREG_<nom>.md` (l'auto-déclaration contient-elle encore un mot
   absent de la liste `MOTS` du #483) ?
2. **La population du #483 tient-elle toujours** : `PREREG_<nom>.md`
   existe, et `nonml_<nom>_result.md` (sans suffixe) **n'existe
   toujours pas** — sinon l'item ne serait plus un « orphelin » et le
   #483 devrait être révisé pour une raison différente ?
3. **Le sujet du #518 est-il le même objet** que la clé du #483, ou un
   script de nom voisin (`_audit.py` vs sans suffixe) ? Réponse binaire,
   par comparaison littérale des chemins de fichiers.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **2** candidats vérifiés, chacun avec verdict et ligne de code
   ou de fichier à l'appui.
2. Le statut « objet identique ou distinct » du #518 publié pour
   chacun.
3. Si les 2 sont des **faux positifs** (objet distinct) : publié comme
   tel, avec la cause précise (collision de nom courte dans le screen
   du #522) — **pas minimisé**.
4. Si au moins un est un **vrai candidat** (objet identique,
   contradiction réelle) : le verdict `V` du #483 corrigé, avec diff
   borné à cette seule entrée, même discipline que les #520/#521.
5. Aucun script de marché exécuté.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Les 2** candidats se révèlent être des **objets distincts** de
   ceux discutés au #518 (faux positifs par collision de nom).
2. **La population du #483 tient toujours** pour les 2 : aucun
   `nonml_<nom>_result.md` sans suffixe n'existe.
3. Le verdict `MAL CLASSÉ` du #483 **reste exact** pour les 2 une fois
   relu contre le texte actuel du `PREREG_`.

Si la prédiction 1 est réfutée pour au moins un candidat, la
correction sera appliquée au dictionnaire `V` du #483, avec diff
mesuré et publié, comme au #520.

## Ce que ce cycle ne fait pas

- Il ne **vérifie** aucun des 30 autres candidats du #522 — file
  distincte, cycles séparés.
- Il ne **rejuge** aucune autre entrée de `V` du #483 hors les 2
  candidats.
- Il n'**exécute** aucun script de marché.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification bibliographique/code, aucune
position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si un vrai candidat est trouvé.
2. Population et protocole **inchangés** après mesure.
3. **Chaque verdict adossé à une ligne de code ou de fichier citée.**
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
