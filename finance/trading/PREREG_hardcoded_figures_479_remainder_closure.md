# Pré-enregistrement — clôture du lot `hardcoded_figures_remainder` (#479) : les 22 candidats restants, un par un

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de VÉRIFICATION, réparation si confirmée**,
première piste de la file ouverte au #527.

## Pourquoi clore le lot en un cycle plutôt qu'un par un

Les #523-#527 ont traité 10 des 32 candidats du #522 un par un, avec
des profondeurs variables (désaccord d'axe évident, ou recoupement
demandant plusieurs vérifications). **Deux leçons se dégagent, et sont
déclarées ici avant de les appliquer aux 22 restants** :

1. Quand le verdict `V` du #479 est **« defaut »** ou **« partiel »**
   et que le cycle citant discute la **même figure** en la trouvant
   **elle aussi problématique** (réparable, résidu non tracé, calcul
   propre en dur…), **les deux verdicts sont compatibles** — « defaut »
   ne dit que « ce chiffre n'est pas dérivé aujourd'hui », pas
   « personne n'a jamais montré qu'il pourrait l'être ». Ce n'est **pas**
   une contradiction (cas #504/#518/#485 pour `content_defined_
   magnitudes_*`, `report_idempotence_backtest`,
   `reproducibility_campaign_v3_lot2_audit`, `orphans_interrupted_or_
   lost_backtest`, `idempotence_famille_capable_backtest`,
   `dsr_corrected_trials_backtest`, `idempotence_lot2_backtest`,
   `reproducibility_campaign_v2_audit`, `pnl_persistence_exposed_pass_
   audit` — le #482 a même confirmé ce dernier « défaut réel »).
2. Quand le verdict `V` du #479 est **« legitime »** et que le cycle
   citant porte sur un **axe de classification différent** (MASQUANT/
   ANODIN d'une garde au #481, idempotence/écart temporel au #509,
   classe d'exécution A/C au #494, procédural/substantiel au #516),
   **c'est un faux positif du screen du #522** — même mécanisme
   qu'aux #523/#524/#525.

**Un seul mécanisme a produit une vraie contradiction jusqu'ici** :
une **rétractation explicite jamais appliquée** (#527) ou une
**citation dont le contenu n'est pas retrouvable dans sa source
prétendue** (#526). Ce cycle applique ces deux tests, mécaniquement,
aux 22 candidats restants, plutôt que de suivre l'intuition ligne par
ligne.

## Le protocole — deux tests mécaniques, appliqués aux 22

1. **Test de rétractation** : la section source contient-elle, à
   proximité (± 300 caractères) du nom du script, l'un des marqueurs
   `rétracté`, `n'est pas un défaut`, `verdict... est faux` — **sans**
   qu'il s'agisse d'une collision de sous-chaîne avec un AUTRE nom de
   script déjà traité (vérifié explicitement) ?
2. **Test d'axe** : le verdict `V` actuel (`defaut`/`partiel`/`legitime`)
   est-il **compatible** avec le sujet du cycle citant, selon les deux
   règles énoncées ci-dessus, appliquées cas par cas et publiées ?

## Critère de succès — chiffré, il porte sur le procédé

1. Les **22** candidats listés, chacun avec le verdict `V` actuel cité.
2. Pour chacun, le résultat du test de rétractation publié.
3. Pour chacun, le verdict de compatibilité d'axe publié avec une
   phrase de justification citée du cycle source.
4. Tout candidat pour lequel les deux tests **ne concluent pas** à la
   compatibilité est nommé comme **candidat à un cycle dédié** — pas
   résolu ici sans preuve suffisante.
5. Toute correction confirmée (rétractation trouvée, non appliquée) est
   appliquée avec un diff borné à l'entrée concernée.

> **PASS** = les cinq points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **Au plus 1** nouvelle rétractation non appliquée est trouvée parmi
   les 22 (le gisement le plus probable, `reproducibility_sample_lot3`,
   étant déjà traité au #527).
2. **Au moins 18** des 22 sont classés compatibles par le test d'axe
   sans nécessiter de correction.
3. **Au plus 3** candidats restent insuffisamment tranchés et sont
   reportés à un cycle dédié.

## Ce que ce cycle ne fait pas

- Il ne **répare** aucune entrée sans preuve mécanique suffisante
  (rétractation retrouvée, ou incompatibilité d'axe démontrée).
- Il ne **revérifie pas** les 2 cas déjà tranchés (#526, #527).
- Il n'**exécute** aucun script de marché.
- Il ne **tranche** ni `n_trials` (#421) ni la batterie au schéma panier
  (#432).

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification/réparation de dépôt, aucune
position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris si plus de candidats que prévu
   restent non tranchés.
2. Population et protocole **inchangés** après mesure.
3. **Chaque verdict adossé à une ligne de code ou de texte citée.**
4. **Relecture intégrale du rapport produit avant commit** (engagement
   #414).
