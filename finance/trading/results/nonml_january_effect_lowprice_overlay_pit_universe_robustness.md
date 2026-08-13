# Robustesse — effet janvier (proxy prix bas), univers POINT-IN-TIME

Grille **identique** à celle du cycle d'origine, donc fixée avant exécution.
**Pas un retuning** : le tercile (1/3), le rebalancement (21j) et la
définition du signal (mois de janvier) restent figés.

CAP pré-enregistré = 2.0x.

| CAP | Sharpe>réf | Rendement>réf | PASS | Sharpe | Rendement total | MDD |
|---|---|---|---|---|---|---|
| 1.5x | OUI | OUI | OUI | +0.76 | +568.2% | -32.6% |
| 2.0x ← CAP pré-enregistré | OUI | OUI | OUI | +0.77 | +660.3% | -32.8% |
| 2.5x | OUI | OUI | OUI | +0.77 | +757.6% | -35.4% |
| 3.0x | OUI | OUI | OUI | +0.76 | +859.2% | -38.0% |

**4/4 cellules PASS.** Rapporté tel quel, sans réajustement.

Pour mémoire, le cycle d'origine (univers biaisé par le survivant) obtenait
**3/4** sur cette même grille, la cellule CAP=3,0x échouant sur le Sharpe.
