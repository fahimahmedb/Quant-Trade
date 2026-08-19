# Pré-enregistrement — témoin (permutation + négatif/positif) du détecteur D528

**Écrit et committé AVANT toute mesure.** `n_trials` continue le compte
global. **Cycle de VÉRIFICATION**, deuxième piste de la file ouverte au
#529 (« appliquer la même discipline de témoin — négatif/positif, lift,
permutation — aux détecteurs plus récents non encore éprouvés »).

## Le détecteur ciblé : D528

Le filtre « radical le plus proche du marqueur, parmi TOUS les radicaux
connus, doit être celui du script examiné » — introduit au #528 pour
écarter les collisions de sous-chaîne, réutilisé tel quel au #529 sur
un second dictionnaire. Jamais soumis à un témoin de vraisemblance
(lift), contrairement à D500/D501/D497 (#515) et à la couche
contextuelle du #502 (#514) : les #528/#529 n'ont validé le filtre que
sur un **univers restreint** de radicaux (32 puis 10 candidats
curés + une poignée de radicaux « autres connus » cités à la main),
jamais sur l'**univers complet** des scripts du dépôt.

## Ce que ce cycle teste, et ce qu'il ne teste pas

Il teste si la **proximité seule** (marqueur à moins de 400 caractères
d'un radical connu) discrimine un signal réel d'une simple densité de
texte, une fois l'univers de radicaux élargi de ~12 (portée du #528/#529)
à la **totalité** des scripts `finance/trading/scripts/nonml_*.py`
(1037 au dénombrement de ce cycle). Il ne réexamine **aucun** verdict
des dictionnaires `V`/`VERDICTS` déjà tranchés (#522-#529) — le filtre
de distance combiné aux témoins ci-dessous suffit à répondre.

## La population

- **Radicaux connus** : `radical(nom)` pour chaque fichier
  `finance/trading/scripts/nonml_*.py` (glob complet au moment du run,
  dénombré et publié).
- **Marqueurs réels** : chaque occurrence des 5 motifs déjà en usage
  depuis le #522 (`rétracté`, `FAUSSE`, `n'est pas un défaut`,
  `contredit`, `réfuté`) dans le texte intégral de
  `NONML_STRATEGY_BACKLOG.md`, découpé en sections `## Backlog #NNN`
  (350 sections au dénombrement de ce cycle). **164** occurrences
  totales mesurées en amont (35+3+1+22+103), chiffre reproduit par le
  script et confronté.

## Le protocole

1. **Taux réel** : pour chacune des occurrences de marqueur réelles,
   vérifier si au moins un radical connu apparaît dans une fenêtre de
   ±400 caractères (même fenêtre qu'au #528/#529) **à l'intérieur de sa
   section**. `A_réel` = proportion d'occurrences avec au moins un
   candidat.
2. **Test de permutation** : pour chaque section contenant au moins une
   occurrence de marqueur, tirer, à la place de chaque marqueur réel,
   une position aléatoire dans les bornes de la même section (racine
   aléatoire fixée `random.seed(529)`, déclarée avant tout calcul,
   **un seul tirage complet répété 20 fois**, `n_trials=1` — le nombre
   de répétitions du tirage n'est pas un paramètre ajusté après lecture
   du résultat). Mesurer le même taux `A_nul` sur chaque répétition,
   moyenne sur les 20.
3. **Lift** : `lift = A_réel / moyenne(A_nul)`. **Seuil fixé à 3 avant
   tout calcul**, même convention que le #515.
4. **Témoins négatifs** (2, déjà documentés, réutilisés tels quels) :
   - `nonml_battery_backfill_lot_audit.py` / phrase générique
     « rétractés sur mesure » (#528) — doit rester écarté par le filtre
     dette générique.
   - `nonml_reproducibility_sample_backtest.py` (collision de
     sous-chaîne avec `reproducibility_sample_lot3_audit` / `_lot2`,
     bug d'audit du #528) — le radical le plus proche du marqueur
     voisin doit être le radical le plus long/le plus spécifique, pas
     le préfixe court.
   Les deux doivent être **correctement écartés** même sur l'univers
   élargi à 1037 radicaux (où le risque de collision est mécaniquement
   plus élevé qu'aux #528/#529).
5. **Témoin positif** (1, déjà documenté) : `nonml_reproducibility_
   sample_lot3_audit.py`, retraction confirmée au #482 et appliquée au
   #527 — doit rester **retenu** (radical le plus proche = lui-même)
   sur l'univers élargi.

## Critères de succès — chiffré

1. Population dénombrée et publiée (nombre de radicaux, de sections, de
   marqueurs).
2. `A_réel`, `A_nul` (moyenne sur 20 tirages) et le lift publiés, avec
   la formule et le seuil (3) déclarés ci-dessus.
3. Les **2** témoins négatifs correctement écartés.
4. Le **1** témoin positif correctement retenu.
5. Résultat honnête publié quel que soit le sens du lift (même si < 3).
6. Aucun script de marché exécuté.

> **PASS** = les six points. **FAIL** = un seul manque — un lift < 3
> **n'est pas un FAIL du critère 5**, c'est un résultat publié tel quel.

## Prédictions — falsifiables

1. **Lift < 3** : sur un univers élargi à plus de 1000 radicaux, la
   plupart courts ou composés de fragments de mots usuels du dépôt
   (`sweep`, `sample`, `backtest`…), je m'attends à ce qu'un radical
   connu se trouve **quasi systématiquement** dans n'importe quelle
   fenêtre de 800 caractères de prose — la proximité seule ne
   discriminerait alors presque rien, et c'est précisément la raison
   déjà donnée au #529 pour ajouter un jugement de compatibilité
   (`RESOLUTIONS`) **en plus** du filtre de distance.
2. Les **2** témoins négatifs restent correctement écartés (le filtre
   « le plus proche » continue de fonctionner localement, même si le
   lift global est faible).
3. Le témoin positif reste correctement retenu.

## Ce que ce cycle ne fait pas

- Il ne **réexamine** aucun verdict `V`/`VERDICTS` déjà tranché
  (#522-#529).
- Il ne **modifie** aucun script existant (D528 est mesuré tel quel,
  pas corrigé — un lift faible documenterait une limite déjà compensée
  par le jugement `RESOLUTIONS`, pas un bug à corriger).
- Il n'**exécute** aucun script de marché.

## Simulation 300 € et robustesse

**Sans objet** : cycle de mesure de dépôt, aucune position, aucun
paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris un lift < 3.
2. Population et protocole **inchangés** après mesure.
3. **Chaque témoin adossé à une ligne de code ou de texte citée.**
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
