# **Ajouter un témoin** aux 2 sections masquantes (pré-enregistré)

**Cycle de MODIFICATION.** Les #481 et #484 ont établi **4 sections
masquantes** — dont la garde peut être fausse sans qu'aucun compte publié
hors garde ne signale l'absence. **Deux sont réparées ici**, par l'ajout
d'une ligne chacune.

## Le diff, publié en entier

```diff
diff --git a/finance/trading/scripts/nonml_six_reports_regeneration_backtest.py b/finance/trading/scripts/nonml_six_reports_regeneration_backtest.py
index bcc2edc..21eb78b 100644
--- a/finance/trading/scripts/nonml_six_reports_regeneration_backtest.py
+++ b/finance/trading/scripts/nonml_six_reports_regeneration_backtest.py
@@ -228,6 +228,8 @@ def main():
         if "Rapport dépendant du dépôt" in av and "Rapport dépendant du dépôt" not in ap:
             perdus.append(Path(m).name)
 
+    L.append(f"- rapports ayant **perdu** l'encart du #439 en étant régénérés : **{len(perdus)}**")
+
     if perdus:
         L.append("## Un effet de bord découvert — les marqueurs du #439 sont effacés")
         L.append("")
diff --git a/finance/trading/scripts/nonml_sweep_pass_prose_fix_backtest.py b/finance/trading/scripts/nonml_sweep_pass_prose_fix_backtest.py
index 59385bf..8b3e403 100644
--- a/finance/trading/scripts/nonml_sweep_pass_prose_fix_backtest.py
+++ b/finance/trading/scripts/nonml_sweep_pass_prose_fix_backtest.py
@@ -130,6 +130,8 @@ def main():
                                        "Inventaire vérifié", "Cycle de MODIFICATION")):
             strategies.append(n)
 
+    L.append(f"- PASS qui sont des **stratégies** et non des scripts d'inventaire : **{len(strategies)}**")
+
     if strategies:
         L.append("## Le résultat qui prime sur la correction de prose")
         L.append("")
```

- lignes **ajoutées** : **4** — dont **2** de
  contenu et le reste des séparateurs vides
- lignes **supprimées ou modifiées** : **0**

> **Exactement deux instructions ajoutées, rien de retiré.** Le
> pré-enregistrement annonçait « une ligne par cas, et rien d'autre » ;
> `git diff` compte **4** insertions parce qu'il compte
> aussi les lignes vides de séparation. **Je publie les deux chiffres
> plutôt que celui qui colle à mon annonce.**

## La règle du #481, ré-appliquée avant et après

| Script | Sans témoin **avant** | Sans témoin **après** | Total titres |
|---|---|---|---|
| `nonml_six_reports_regeneration_backtest.py` | **1** | **0** | 2 → 2 |
| `nonml_sweep_pass_prose_fix_backtest.py` | **1** | **0** | 2 → 2 |

- titres conditionnels, **total avant** : **4** — **après** : **4**

> **Les deux cas passent de « sans témoin » à « avec témoin ».** La
> règle qui les avait dénoncés les reconnaît maintenant réparés — et
> c'est **la même règle, non modifiée**, qui rend les deux verdicts.

## Aucune exécution — et ce n'est pas une facilité

| Script | Effet de bord constaté |
|---|---|
| `nonml_six_reports_regeneration_backtest.py` | **exécute d'autres scripts du dépôt** |
| `nonml_sweep_pass_prose_fix_backtest.py` | **écrit 2 fichiers**, dont un qui n'est pas le sien |

> **Les exécuter pour « vérifier » la réparation causerait plus de dégâts
> que le défaut réparé.** Le #482 avait déjà refusé d'exécuter le premier
> pour cette raison exacte.

**Conséquence, qu'il faut dire sans l'atténuer : les rapports publiés de
ces deux cycles ne portent PAS encore le témoin.** Ils le porteront à leur
prochaine exécution légitime. **La réparation est dans le code, pas encore
dans les rapports** — et un lecteur qui ouvrirait ces rapports aujourd'hui
ne verrait aucun changement.

## Le périmètre — rien d'autre n'a bougé

- fichiers modifiés hors ceux de ce cycle : **2**
  - `finance/trading/scripts/nonml_six_reports_regeneration_backtest.py`
  - `finance/trading/scripts/nonml_sweep_pass_prose_fix_backtest.py`

> **Seuls les deux scripts visés sont modifiés**, et aucun rapport
> n'est régénéré.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| les 2 passent « avec témoin » | 2 | 2 | **vérifiée** |
| total de titres conditionnels inchangé | 4 | 4 | **vérifiée** |
| aucun autre cas ne change | 0 | 0 | **vérifiée** |

**Le compte de masquants passe de 4 à 2.** Les deux qui restent sont
`battery_coverage` l.159 et `net_pnl_correction` l.279, établis au
#481 et **non touchés ici** — leur garde ne porte pas sur une liste de
résultats, et la même recette ne s'y applique pas telle quelle.

## Critères de succès

1. Diff publié en entier, **2** instructions ajoutées, **0** supprimée(s) — **OUI**.
2. Règle du #481 ré-appliquée avant/après — **OUI**.
3. Aucune exécution des deux scripts — **OUI**.
4. Aucun autre fichier modifié, aucun rapport régénéré — **OUI**.
5. Le fait que les rapports ne portent pas encore le témoin, écrit — **OUI**.

**PASS** — le
critère porte sur le **procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).