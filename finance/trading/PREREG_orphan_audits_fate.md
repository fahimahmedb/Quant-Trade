# Pré-enregistrement — le sort des **3 audits orphelins**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #479.

## La dette à lever

Le **#477** a trouvé, parmi les cycles sans entrée de backlog, **trois** dont
seul un `_audit.md` existe, sans `_result.md` :

- `n_trials_dependence_correction`
- `pnl_duplicate_sweep_v2`
- `pnl_persistence_exposed_pass`

Il les a nommés « **audits orphelins** » et a posé la question sans y répondre :
**cycle interrompu après l'audit, ou résultat publié sous un autre nom ?**

Le #477 avait déjà reconnu que son étiquette précédente — « cycle complet » —
était trop généreuse. **Rien ne garantit que « audit orphelin » soit plus
juste**, et ce cycle doit pouvoir l'infirmer.

## Le protocole — quatre faits par cycle, aucun jugement

Lecture d'objets git et du disque. **Aucun script du dépôt n'est exécuté.**

Pour chacun des trois :

1. **Le script producteur du résultat existe-t-il ?**
   `scripts/nonml_<nom>_backtest.py` — présent ou absent.
2. **Un `_result.md` a-t-il jamais existé ?** balayage de tout l'historique :
   `git log --all --diff-filter=A -- 'finance/trading/results/nonml_<nom>_result.md'`.
3. **L'audit désigne-t-il le rapport qu'il audite ?** lecture de son
   `_audit.md` : cite-t-il nominativement un `nonml_*.md`, et ce fichier
   existe-t-il ?
4. **Le pré-enregistrement annonçait-il un résultat ?** lecture de
   `PREREG_<nom>.md` : promet-il un `_result.md`, ou se déclare-t-il cycle
   d'**audit / de correction** portant sur un autre cycle ?

## Les trois lectures — toutes publiables

- **A. Cycle interrompu après l'audit** — pas de script producteur, aucun
  `_result.md` dans l'historique, et le pré-enregistrement en annonçait un.
- **B. Résultat publié sous un autre nom** — l'audit désigne un rapport qui
  **existe** sous un `<nom>` différent.
- **C. Aucun résultat attendu par conception** — le pré-enregistrement déclare
  un cycle d'audit ou de correction portant sur **un autre** cycle ; il n'y a
  donc jamais eu de `_result.md` à produire.

**Si la lecture C l'emporte, « audit orphelin » est un mauvais nom**, et c'est
moi qui l'ai écrit au #477. Je devrai le dire aussi nettement que le #477 a dit
que « cycle complet » était trop généreux.

## Critère de succès — chiffré, il porte sur le procédé

1. Les **3** nommés, avec les **quatre faits** publiés pour chacun.
2. L'historique balayé, **la commande publiée** pour qu'un lecteur la refasse.
3. **Une** des trois lectures explicitement nommée **pour chacun** — ou l'aveu
   qu'aucune ne s'applique.
4. Si la lecture C domine, l'étiquette « audit orphelin » **rétractée
   explicitement**, sans que le #477 soit réécrit.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **≥ 2 sur 3** relèvent de la lecture **C** — aucun résultat n'était attendu.
   *(Fondement : leurs noms — « correction », « v2 », « exposed_pass » — sont
   ceux de cycles qui portent sur un travail antérieur, pas sur une stratégie
   neuve.)*
2. **Aucun** des trois n'a jamais eu de `_result.md` dans tout l'historique.
   *(Réfutable : un seul ajout suffit.)*
3. Pour **au moins 1**, l'audit **nomme** le rapport qu'il audite et ce fichier
   **existe** aujourd'hui.

Si la prédiction 1 est réfutée et que la lecture **A** domine, alors ce sont de
vrais cycles inachevés, la dette du #477 est réelle, et je devrai l'inscrire
telle quelle plutôt que de la dissoudre — c'est le résultat qui m'arrangerait le
moins, et il doit rester atteignable.

## Ce que ce cycle ne fait pas

- Il ne **produit** aucun `_result.md` manquant, ne complète aucun cycle.
- Il n'**exécute** aucun script : lecture seule, **aucun effet de bord**.
- Il ne **réécrit** ni le #477 ni son entrée — une rétractation s'inscrit, elle
  ne s'efface pas.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que mon étiquette du #477
   était fausse.
2. Protocole et lectures **inchangés** après mesure.
3. **Chacun des trois traité nominativement**, jamais agrégé — leçon des #462,
   #464, #465, #469, #474.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
