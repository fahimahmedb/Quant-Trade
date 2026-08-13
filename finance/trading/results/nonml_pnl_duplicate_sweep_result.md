# Balayage des doublons de P&L du backlog (pré-enregistré)

Diagnostic, pas une stratégie. Reconstruit le P&L net de **tous** les
`results/*_pnl.npz` du dépôt et cherche les paires identiques ou quasi
identiques. Critères fixés avant exécution : égalité exacte
(`np.array_equal`) ou corrélation ≥ 0.9999.

## Couverture

- fichiers `*_pnl.npz` trouvés : **200**
- P&L reconstruits : **200**
- schémas non reconnus ou séries inexploitables : **0**

**Couverture 100 %** — critère 1 du pré-enregistrement atteint.

Répartition par schéma : indiciel (168), panier (17), deux jambes (13), candidat+turnover (1), candidat seul (1).

## Doublons exacts

- paires à P&L **bit-à-bit identique** : **3**
- groupes de doublons : **3**
- entrées surnuméraires (essais comptés en trop) : **3**

- **groupe de 2** : `etape_D_overlay_optimized`, `nonml_etape_d_garch_defensive_overlay`
- **groupe de 2** : `nonml_leaders_trend_union_overlay`, `nonml_sma200_leaders_overlay`
- **groupe de 2** : `nonml_leaders_trend_union_overlay_pit_universe`, `nonml_sma200_leaders_overlay_pit_universe`

## Quasi-doublons (corrélation ≥ seuil, non identiques)

- paires signalées : **1**

| Candidat A | Candidat B | Corrélation |
|---|---|---|
| `nonml_momentum_breadth_vol_targeting_overlay` | `nonml_sma200_momentum_breadth_and_overlay` | 0.99990654 |

Ces paires **ne sont pas comptées comme doublons** à ce stade : le critère 2
du pré-enregistrement impose de les confirmer ou de les rejeter par lecture
des deux scripts. Voir l'audit.

## Effet sur le décompte d'essais

Le backlog compte actuellement **372** essais dans le calcul du DSR.
Les doublons exacts en rendent **3** surnuméraires, soit un
décompte corrigé de **369** avant examen des quasi-doublons.

**Aucune correction n'est appliquée dans ce cycle**, conformément au
pré-enregistrement : rejouer les batteries avec un `n_trials` corrigé après
avoir vu quels candidats en bénéficieraient serait précisément ce que le
protocole interdit. Le décompte corrigé est publié, son usage est un cycle
distinct à déclarer.
