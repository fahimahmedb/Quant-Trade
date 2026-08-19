# Pré-enregistrement — bilan des témoins de la série #500-#515, et le témoin faible est-il utilisé seul quelque part ?

**Écrit et committé AVANT toute mesure.** `n_trials` continue le compte
global. **Cycle de VÉRIFICATION**, première piste de la file ouverte au
#518.

## Ce que la file demande

Depuis le #515 : *« Bilan complet des témoins appliqués à la série
#500-#514 — les 4 couches de détection ont désormais un témoin publié
(#514 contextuel, #515 D500/D501/D497). Un cycle de synthèse pourrait
consolider ce qui tient et ce qui ne tient qu'en combinaison. »*

## Partie 1 — la consolidation, purement descriptive

Les quatre témoins ont déjà été mesurés et publiés ; ce cycle ne les
recalcule pas, il les rassemble dans une seule table, avec leur cycle
d'origine cité :

| Couche | Cycle d'origine | Témoin | Résultat |
|---|---|---|---|
| Extraction (D500) | #500, témoin #515 | lift | **6,4** — discrimine |
| Confirmation brute (D501, `en_gras_dans`) | #501, témoin #515 | rapport decoy | **1,5** — ne discrimine pas seul |
| Contextuelle (#502) | #502, témoin #514 | spécificité | **35,9 %**, mais **64 %** de faux positifs |
| Primitive d'exécution (D497-P10) | #497, témoin #515 | lift | **12,1** — discrimine |

**Aucun nombre ci-dessus n'est recalculé** — republiés tels que déjà
committés, avec citation du cycle source.

## Partie 2 — la question jamais posée : D501 est-il utilisé seul ailleurs ?

Le #502 a été construit **précisément parce que** la confirmation brute
du #501 était trop large — 14 des 22 « confirmés » sont tombés une fois
le contexte ajouté. Le #515 l'a confirmé quantitativement (lift 1,5).
**Mais personne n'a vérifié si un autre script du dépôt, écrit après le
#502, réutilise la fonction faible (`en_gras_dans` du module du #501)
sans passer par la couche contextuelle qui la corrige.**

Un examen préliminaire de son propre code (autorisé avant le PREREG,
même précédent que les cycles antérieurs) montre que la fonction
`en_gras_dans` du module `nonml_borrowed_figures_confrontation_backtest.py`
n'apparaît, par recherche textuelle brute sur tout le dossier
`scripts/`, que dans deux fichiers. **Ce cycle vérifie mécaniquement,
sans se fier à cette lecture**, laquelle.

## Le protocole — mécanique, par script

1. **Recenser**, par `grep` sur `scripts/*.py`, tout fichier contenant
   la sous-chaîne `en_gras_dans` (l'appel à la fonction, pas sa
   définition).
2. **Pour chacun**, à l'exclusion du fichier qui la **définit**
   (`nonml_borrowed_figures_confrontation_backtest.py`), déterminer par
   lecture du fichier s'il s'agit :
   - du script du **#502** lui-même (où `en_gras_dans` sert de brique à
     une règle plus stricte, **compensée** — cas attendu, pas une
     lacune) ;
   - du script du **#515** (où `en_gras_dans` est le **sujet testé**,
     pas une source de vérité utilisée pour un verdict — cas attendu,
     pas une lacune) ;
   - d'un **troisième cas** : un script qui utilise `en_gras_dans` pour
     produire un verdict substantiel **sans** compensation contextuelle
     — ce serait la lacune méthodologique réelle.
3. **Séparément**, recenser tout fichier import ant le module du #501
   (`nonml_borrowed_figures_confrontation_backtest`) mais **pas** celui
   du #502 (`nonml_contextual_confrontation_backtest`), et publier
   **l'attribut précis** qu'il consomme du module du #501 (via AST,
   attributs `c501.<nom>` observés) — pour distinguer une réutilisation
   d'utilitaire générique (ex. `sections_backlog()`, `git()`) d'une
   réutilisation du jugement faible lui-même.

## Critère de succès — chiffré, il porte sur le procédé

1. La table des 4 témoins publiée, chaque nombre cité avec son cycle
   source, **aucun recalculé**.
2. Tous les fichiers contenant `en_gras_dans` recensés et classés dans
   l'une des trois catégories ci-dessus.
3. Pour chaque script import ant le module du #501 sans celui du #502,
   l'attribut consommé publié explicitement.
4. **Si un « troisième cas » existe** : nommé, et la conclusion qu'il
   porte signalée comme reposant sur un témoin **invalidé**.
5. **Si aucun « troisième cas » n'existe** : publié comme tel, sans
   minimiser que ce n'était pas garanti d'avance.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. `en_gras_dans` n'apparaît, par appel, que dans **exactement 2**
   fichiers (le #502 et le #515), en excluant sa propre définition.
2. **0** « troisième cas » — aucun script ne s'appuie sur la confirmation
   brute seule pour un verdict substantiel.
3. Tout script important le module du #501 sans celui du #502
   consomme **exclusivement** des utilitaires génériques
   (`sections_backlog`, `git`, `recensement_500`), **jamais**
   `en_gras_dans` ni `chiffres_seuls` employé comme verdict final.

Si la prédiction 2 est réfutée, le script et la conclusion concernée
seront **nommés explicitement** comme reposant sur un témoin invalidé,
sans atténuation.

## Ce que ce cycle ne fait pas

- Il ne **recalcule** aucun des 4 témoins déjà publiés.
- Il ne **modifie** aucun script existant, même si un « troisième cas »
  est trouvé — un éventuel correctif serait un cycle distinct.
- Il n'**exécute** aucun script de marché : lecture du disque et du code
  source uniquement, **aucun effet de bord**.
- Il ne **tranche pas** `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de synthèse bibliographique/code, aucune position,
aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si un « troisième cas » existe.
2. Population, protocole et forme des verdicts **inchangés** après
   mesure.
3. **Chaque verdict adossé à une ligne de code citée**, jamais à une
   impression.
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
