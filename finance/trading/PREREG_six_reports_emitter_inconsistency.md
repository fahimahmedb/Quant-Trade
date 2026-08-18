# Pré-enregistrement — l'incohérence émetteur/rapport de `six_reports_regeneration`

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, première piste de la file ouverte au #474 — dette
inscrite depuis le #469 et jamais levée.

## L'incohérence à expliquer

Le **#469** croisait script émetteur et rapport produit, sur la règle :

> Si un script **émet** la marque « Rapport dépendant du dépôt », son rapport
> doit la **contenir**. L'inverse signalerait une **régénération perdue**,
> comme au #450.

Une seule paire a échoué au contrôle :

| Script émetteur | Rapport sans la marque |
|---|---|
| `nonml_six_reports_regeneration_backtest.py` | `nonml_six_reports_regeneration_result.md` |

Le #469 l'a lue comme une **perte** : « ces rapports **ont perdu** un encart que
leur script émet ». **Il ne l'a pas vérifié** — c'est une interprétation, pas
une mesure.

## L'hypothèse concurrente, énoncée avant de regarder

`six_reports_regeneration` est, par construction, un script qui **réécrit les
rapports des autres** : le #469 lui-même note qu'il « écrit **7** rapports qui
ne sont pas le sien » et qu'il « n'énumère pas `results/` par un glob : il
exécute » d'autres scripts.

Si sa ligne d'émission sert à écrire la marque **dans les rapports qu'il
régénère**, alors son propre rapport n'a **jamais eu** à la porter, et
l'incohérence du #469 est un **faux positif de sa règle de croisement** — la
règle « un script émet ⇒ *son* rapport contient » ne vaut pas pour un script
dont la sortie est **ailleurs**.

## Le protocole

Lecture d'objets git et du disque. **Aucun script du dépôt n'est exécuté** — en
particulier pas `six_reports_regeneration`, qui réécrirait des rapports.

1. **La ligne d'émission, verbatim**, et sa **cible** : le fichier écrit est-il
   le `OUT` du script (son propre rapport) ou un autre chemin ?
2. **L'historique du rapport** : `nonml_six_reports_regeneration_result.md`
   a-t-il **jamais** contenu la marque, à un commit quelconque ? Une perte
   suppose une possession antérieure.
3. **Les rapports que ce script écrit** : lesquels, et combien portent la marque
   aujourd'hui ?

## Les trois lectures — toutes publiables

- **A. Encart perdu** — le script écrit la marque dans *son* rapport, et le
  rapport l'a portée puis perdue → **le #469 avait raison**, et la dette est
  réelle.
- **B. Faux positif du #469** — le script écrit la marque **ailleurs**, et son
  rapport ne l'a jamais portée → la règle de croisement du #469 est **trop
  large**, et la dette n'existe pas.
- **C. Indéterminable** — la cible de l'écriture ne se lit pas sans exécuter.

## Critère de succès — chiffré, il porte sur le procédé

1. La **ligne d'émission citée verbatim**, avec sa cible identifiée ou l'échec
   à l'identifier **déclaré**.
2. L'historique du rapport **balayé sur tous les commits**, et le fait qu'il ait
   ou non porté la marque **publié avec la commande**.
3. Les rapports écrits par ce script **énumérés nominativement**, et leur port
   de la marque compté.
4. **Une** des trois lectures explicitement nommée.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. **La lecture B est retenue** : l'écriture vise d'autres fichiers que son
   propre rapport.
2. `nonml_six_reports_regeneration_result.md` **n'a jamais** contenu la marque,
   à aucun commit — donc rien n'a été « perdu ».
3. **≥ 6** des rapports que ce script écrit portent la marque aujourd'hui.

Si la prédiction 1 est réfutée et que la lecture **A** l'emporte, alors le #469
avait raison, la dette est confirmée, et je devrai l'écrire sans chercher à
sauver l'hypothèse qui m'a fait ouvrir ce cycle.

## Le risque que je me fais à moi-même, dit d'avance

Ce cycle est ouvert **parce que je soupçonne un cycle antérieur d'avoir eu
tort**. C'est exactement la position où l'on trouve ce qu'on cherche. Deux
garde-fous, fixés ici :

- la lecture **A** doit rester atteignable — les prédictions 1 et 2 sont
  formulées de sorte qu'un seul fait contraire (la marque présente à un commit
  ancien) les réfute toutes deux ;
- **je ne reformule pas** la règle du #469 pour la rendre fausse : elle est
  citée telle qu'il l'a écrite, en tête de ce document.

## Ce que ce cycle ne fait pas

- Il ne **répare** rien : ni encart réajouté, ni rapport régénéré, ni règle du
  #469 réécrite dans son rapport.
- Il n'**exécute** aucun script du dépôt.
- Il ne conclut rien sur les **autres** résultats du #469, dont le verdict
  central (0 citeur établi) n'est pas en cause ici.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification, aucune position, aucun paramètre
numérique à perturber.

## Engagements

1. Résultat rapporté tel quel, y compris s'il confirme le #469 contre mon
   hypothèse.
2. Protocole et lectures **inchangés** après mesure.
3. Rapports écrits par le script **nommés**, jamais seulement comptés — leçon
   des #462, #464, #465, #469, #474.
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
