# Pré-enregistrement — sauvegarde du P&L des 10 PASS restés invérifiables

**Écrit et committé AVANT toute modification de script.** `n_trials = 1`.
Cycle d'**infrastructure et de mesure** : aucune stratégie n'est évaluée, aucun
paramètre de stratégie n'est touché.

## Pourquoi, et pourquoi maintenant

Deux cycles consécutifs ont buté sur la même lacune :

- le **#406** a mesuré que le balayage de doublons ne voit que **41 %** du
  backlog, faute de `.npz` sauvegardés — et a manqué de ce fait le seul doublon
  connu d'avance ;
- le **#415** a chiffré le coût exact : **10 candidats portant un PASS** ont la
  structure à risque identifiée au #410 et **restent invérifiables**.

Ce n'est plus une gêne théorique : ce sont dix verdicts positifs qu'aucune mesure
ne peut confirmer ni infirmer.

## Portée — délibérément étroite

Le dépôt compte **114** scripts dont la sauvegarde `.npz` est conditionnée au
verdict et **130** qui n'en font aucune. Les modifier tous serait un geste de
masse — exactement ce qui a produit les défauts des **#392** et **#404**, où une
correction appliquée par motif plutôt que par lecture a cassé des scripts et
publié des chiffres faux.

Ce cycle traite donc **les 10 candidats du #415 et eux seuls** :

`dispersion_trend_vol_targeting_overlay`, `momentum_breadth_vol_targeting_overlay`,
`momentum_dispersion_trend_and_overlay`, `multimarket_breadth_vol_targeting_overlay`,
`net_breadth_vol_targeting_overlay`, `santa_vol_targeting_overlay`,
`sma200_breadth_vol_targeting_overlay`, `sma200_momentum_breadth_and_overlay`,
`weakness_breadth_vol_targeting_overlay`, `winners_trend_vol_targeting_overlay`.

Vérification faite : aucun des dix n'appelle `np.savez`, et aucun ne dépend d'une
source externe — ils sont donc tous ré-exécutables hors ligne. Le reste du dépôt
est laissé en l'état et compté comme dette déclarée.

## Modification — une seule, lue script par script

Ajout d'un appel `np.savez` **inconditionnel** écrivant le schéma déjà utilisé
par le dépôt (`pos`, `r_asset`, `dates`, `cost_bps` pour les candidats indiciels ;
`pnl_gross_ov`, `pnl_gross_bh`, `turn_ov`, `turn_bh`, `dates`, `cost_bps` pour
les paniers).

**Aucune ligne de calcul n'est modifiée.** Chaque script est lu avant édition
pour déterminer son schéma ; aucune substitution automatique n'est appliquée à
l'ensemble.

## Contrôle de non-régression — le garde-fou central

Pour chacun des dix : le fichier `results/nonml_<nom>_result.md` est comparé
**octet à octet** avant et après ré-exécution.

- **Toute différence est un échec du cycle**, à investiguer avant tout commit :
  elle signifierait que la ré-exécution ne reproduit pas le résultat publié, donc
  que quelque chose d'autre a changé depuis (données, dépendances, ou une
  correction intermédiaire jamais rejouée).
- Le nombre de fichiers identiques et différents est publié **quel qu'il soit**.

C'est ce contrôle, et non l'ajout du `savez`, qui est le vrai contenu du cycle :
il teste dix résultats publiés contre leur propre code.

## Mesure — le paiement de la dette du #415

Après ré-exécution, le balayage `nonml_capitulation_gate_floor_sweep_backtest.py`
est relancé **sans modification**. Sont publiés :

1. la nouvelle couverture du volet B (mesurés / détectés) ;
2. pour chacun des dix, l'activation mesurée ;
3. le nombre de nouveaux candidats **structurellement inactifs** au sens du seuil
   de 2 % — seuil **repris tel quel** du #410, non rediscuté.

## Critère de succès — chiffré

1. **10/10** scripts modifiés, ré-exécutés, `.npz` produit.
2. **0 différence** sur les dix fichiers de résultat. Toute différence est
   rapportée et bloque la conclusion tant qu'elle n'est pas expliquée.
3. Couverture du volet B du #415 recalculée et publiée.

**Aucune requalification de PASS n'est appliquée dans ce cycle**, même si un
candidat se révèle inactif : cela reste une opération distincte, à déclarer.
Ce cycle **mesure**, il ne juge pas.

## Prédiction — non tranchée

Aucune. Je ne sais pas combien des dix, s'il y en a, se révéleront inactifs.

## Engagements

1. Résultats rapportés **tels quels**, y compris si le contrôle de
   non-régression échoue — ce qui serait le résultat le plus important du cycle.
2. Aucun paramètre de stratégie modifié.
3. Dette restante (114 + 130 scripts) explicitement chiffrée au backlog.
4. **Relecture intégrale des rapports produits avant commit** (engagement #414).
