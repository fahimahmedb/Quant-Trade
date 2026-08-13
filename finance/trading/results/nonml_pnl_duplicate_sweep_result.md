# Balayage des doublons de P&L du backlog (pré-enregistré)

Diagnostic, pas une stratégie. Reconstruit le P&L net de **tous** les
`results/*_pnl.npz` du dépôt et cherche les paires identiques ou quasi
identiques. Critères fixés avant exécution : égalité exacte
(`np.array_equal`) ou corrélation ≥ 0.9999.

## Couverture

- fichiers `*_pnl.npz` trouvés : **165**
- P&L reconstruits : **165**
- schémas non reconnus ou séries inexploitables : **0**

**Couverture 100 %** — critère 1 du pré-enregistrement atteint.

Répartition par schéma : indiciel (140), deux jambes (13), panier (10), candidat+turnover (1), candidat seul (1).

## Doublons exacts

- paires à P&L **bit-à-bit identique** : **2**
- groupes de doublons : **2**
- entrées surnuméraires (essais comptés en trop) : **2**

- **groupe de 2** : `etape_D_overlay_optimized`, `nonml_etape_d_garch_defensive_overlay`
- **groupe de 2** : `nonml_leaders_trend_union_overlay_pit_universe`, `nonml_sma200_leaders_overlay_pit_universe`

## Quasi-doublons (corrélation ≥ seuil, non identiques)

- paires signalées : **0**

Aucune.

## Effet sur le décompte d'essais

Le backlog compte actuellement **372** essais dans le calcul du DSR.
Les doublons exacts en rendent **2** surnuméraires, soit un
décompte corrigé de **370** avant examen des quasi-doublons.

**Aucune correction n'est appliquée dans ce cycle**, conformément au
pré-enregistrement : rejouer les batteries avec un `n_trials` corrigé après
avoir vu quels candidats en bénéficieraient serait précisément ce que le
protocole interdit. Le décompte corrigé est publié, son usage est un cycle
distinct à déclarer.
