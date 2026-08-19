# Pré-enregistrement — correction du statut stale d'E3 (fetches terminés)

**Écrit et committé AVANT toute modification.** `n_trials` continue le
compte global. **Cycle de RÉPARATION**, première piste de la file
ouverte au #533 (« E3 pourrait afficher un statut stale »).

## La dette signalée au #533, non corrigée sur place par déclaration

Le #533 a corrigé la revendication fausse sur E1 mais a explicitement
laissé de côté, hors de son diff borné à 2 passages, un second défaut
trouvé dans le même fichier : la ligne E3 du tableau « Statut » de
`ECONOMIC_MULTIASSET_BACKLOG.md` affiche « **à faire dès que les 3
fetches sont terminés** » alors que la section « L'univers d'actifs »
**du même fichier** affirme déjà que TLT/GLD/UUP sont **récupérés et
vérifiés**. Ce cycle vérifie cette affirmation sur le disque, pas
seulement dans la prose, avant de corriger.

## Le protocole

1. **Vérifier sur le disque**, indépendamment de la prose du fichier,
   que les 3 fichiers (`data/tlt_daily.txt`, `data/gld_daily.txt`,
   `data/uup_daily.txt`) existent, chargent sans erreur via
   `load_ohlc` et passent `quality_report()` sans anomalie.
2. **Comparer** le nombre de séances et les dates extrêmes mesurées à
   celles déjà publiées dans la section « L'univers d'actifs » du
   fichier (6051/2512/4898 séances, dates jusqu'à 17-18/08/2026) —
   confirmer l'accord ou publier l'écart tel quel.
3. **Si confirmé** : corriger la seule ligne E3 du tableau « Statut »
   pour refléter l'état réel (fetches terminés, prêt à être exécuté
   dans un cycle futur dédié — ce cycle ne lance PAS le backtest E3
   lui-même, discipline « une idée par cycle »).
4. **Diff borné** à cette seule ligne.

## Critère de succès — chiffré

1. Les **3** fichiers vérifiés sur le disque (existence, chargement,
   `quality_report`).
2. Accord ou écart avec la prose déjà publiée, publié tel quel.
3. **Si accord** : la ligne E3 corrigée, diff borné à cette ligne
   seule.
4. **Si désaccord** (au moins un fichier absent/invalide) : **aucune**
   correction appliquée, le désaccord publié comme trouvaille
   principale du cycle à la place.
5. Aucun script de marché exécuté (le backtest E3 lui-même n'est pas
   ce cycle).

> **PASS** = les cinq points, quel que soit le sens du résultat (accord
> ou désaccord). **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Les 3 fichiers existent, chargent et passent `quality_report()`
   sans anomalie.
2. Les comptes et dates mesurés sont identiques à ceux déjà publiés
   (6051/2512/4898 séances).
3. La correction est donc appliquée (pas un désaccord qui l'empêche).

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun backtest E3 (momentum cross-actifs) — seule
  la disponibilité des données est vérifiée ici, l'exécution reste un
  cycle futur distinct, motivé séparément.
- Il ne **touche** ni E1 ni la question d'arbitrage du #432 (déjà
  traitée, séparément, au #533).
- Il ne **réexamine** aucun verdict de stratégie déjà tranché.

## Simulation 300 € et robustesse

**Sans objet** : cycle de vérification de données et de correction
documentaire, aucune position, aucun paramètre numérique de stratégie.

## Engagements

1. Résultat rapporté tel quel, y compris en cas de désaccord.
2. **Chaque affirmation adossée à une mesure directe sur le disque.**
3. **Relecture intégrale du fichier corrigé avant commit** (engagement
   #414).
