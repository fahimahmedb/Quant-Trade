# Les **2 masquants restants** (pré-enregistré)

Le **#487** avait laissé ces deux-là avec une justification :

> **leur garde ne porte pas sur une liste de résultats**, et la même
> recette ne s'y applique pas telle quelle.

**Cette phrase n'avait jamais été vérifiée.**

## Volet A — la phrase du #487 est-elle exacte ?

Établi par **AST** sur l'affectation de chaque variable de garde :

| Script | Variable | Type réel |
|---|---|---|
| `nonml_battery_coverage_backtest.py` | `indet` | **entier** (appel — `sum`/`len`) |
| `nonml_net_pnl_correction_backtest.py` | `incoh` | **liste** (compréhension) |

> **La phrase du #487 est inexacte.** `incoh` est bel et bien une
> **liste** — une compréhension de liste, exactement la forme que le
> #487 disait absente.

**Je l'ai écrite, et elle m'a servi de raison commode pour ne pas
finir le travail.** La vraie différence entre les deux cas n'est pas
« liste ou non » mais **le type du témoin à écrire** : `len(x)` pour
une liste, la valeur elle-même pour un entier. **Les deux admettent un
témoin.**

## Volet B — le diff, publié en entier

```diff
diff --git a/finance/trading/scripts/nonml_battery_coverage_backtest.py b/finance/trading/scripts/nonml_battery_coverage_backtest.py
index 27135ab..792b686 100644
--- a/finance/trading/scripts/nonml_battery_coverage_backtest.py
+++ b/finance/trading/scripts/nonml_battery_coverage_backtest.py
@@ -155,6 +155,8 @@ def main():
         L.append(f"**{n_pass} / {len(executes)}** validés par la batterie.")
         L.append("")
         indet = sum(1 for _, _, c in executes if c and c[2] == "indéterminé")
+        L.append(f"- rapports classés « indéterminé » par la règle unifiée : **{indet}**")
+        L.append("")
         if indet:
             L.append("### Une limite de la règle unifiée, découverte ici")
             L.append("")
diff --git a/finance/trading/scripts/nonml_net_pnl_correction_backtest.py b/finance/trading/scripts/nonml_net_pnl_correction_backtest.py
index a9a4ef0..eda5a07 100644
--- a/finance/trading/scripts/nonml_net_pnl_correction_backtest.py
+++ b/finance/trading/scripts/nonml_net_pnl_correction_backtest.py
@@ -275,6 +275,9 @@ def main():
     # Incoherence exposee par le rafraichissement : prose figee vs compte calcule.
     incoh = [ln for ln in apres_txt
              if "PASS sont les deux" in ln and "**2**" not in ln]
+    L.append(f"- incohérences prose/compte exposées par le rafraîchissement : **{len(incoh)}**")
+    L.append("")
+
     if incoh:
         L.append("### Une incohérence exposée par le rafraîchissement")
         L.append("")
```

- **lignes de témoin** ajoutées : **2** — instructions au
  total : **4** *(chaque témoin est suivi d'un
  `L.append("")` de séparation)*
- lignes supprimées : **0**

### La règle du #481, ré-appliquée

| Script | Sans témoin **avant** | **après** |
|---|---|---|
| `nonml_battery_coverage_backtest.py` | **1** | **1** |
| `nonml_net_pnl_correction_backtest.py` | **1** | **0** |

> **Le déplacement n'a eu lieu que pour un des deux.**

La cause est identifiable, et c'est **un angle mort connu de ma propre
règle** : dans `battery_coverage`, la variable `indet` est calculée
**à l'intérieur d'un bloc englobant**, et mon témoin y est donc
écrit lui aussi. **La règle du #481 ne cherche un témoin qu'au niveau
non gardé** — c'est exactement le premier des deux angles morts que
le **#484** avait mesurés.

**Le témoin est fonctionnellement présent** : un lecteur voit le
compte chaque fois que le bloc englobant s'exécute. **Ma règle ne
sait pas le voir.**

> **Je ne déplace pas la ligne après coup.** Retoucher le patch
> jusqu'à ce qu'il satisfasse ma propre métrique serait itérer sur le
> résultat — le pré-enregistrement l'interdit, et le #487 avait pris
> le même engagement. **Le patch est publié comme insuffisant au
> regard de la règle, et suffisant au regard du lecteur.**

## Volet C — exécution asymétrique, déclarée d'avance

| Script | Effet de bord | Exécuté ? |
|---|---|---|
| `nonml_battery_coverage_backtest.py` | **exécute la batterie de validation** | **NON** |
| `nonml_net_pnl_correction_backtest.py` | n'écrit que **son propre rapport** | **oui** |

| Script | État | Passage 1 | Passage 2 | Lignes de diff |
|---|---|---|---|---|
| `nonml_battery_coverage_backtest.py` | non exécuté | — | — | 0 |
| `nonml_net_pnl_correction_backtest.py` | idempotent | `8ca03b19cc4486` | `8ca03b19cc4486` | 84 |

### Le diff du rapport de `nonml_net_pnl_correction_backtest.py`

- lignes ajoutées : **48** — supprimées : **29**

```diff
--- committé
+++ régénéré
@@ -25,2 +25,2 @@
-- séries lues **avant** : **218**
-- séries lues **après** : **218**
+- séries lues **avant** : **219**
+- séries lues **après** : **219**
@@ -59,2 +59,2 @@
-- lignes avant : **96** — lignes après : **92** (écart -4)
-- lignes **modifiées** : **10**
+- lignes avant : **96** — lignes après : **127** (écart +31)
+- lignes **modifiées** : **58**
@@ -62 +62 @@
-**1 ligne imputable à la correction ; 9 à la dérive du
```

> **Le diff ne se réduit pas au témoin.** Le pré-enregistrement
> l'interdisait alors : **le rapport régénéré n'est pas
> committé**, et le diff est publié.

### Restauration

Le rapport régénéré n'étant **pas committé**, il ne doit pas rester
modifié dans l'arbre.

- résidus sous `results/` après restauration : **0**

### Ce qui reste invisible

- `nonml_battery_coverage_result.md` : **inchangé**

**Le témoin de `battery_coverage` est dans le code, pas encore dans
son rapport** — comme les deux du #487. Il y paraîtra à la prochaine
exécution légitime de la batterie.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| les 2 admettent un témoin | 2 | 2 | **vérifiée** |
| masquants 2 → 0 | 0 | non | **réfutée** |
| la phrase du #487 est inexacte | oui | oui | **vérifiée** |

**La prédiction 3 se vérifie, et elle m'accuse.** Le #487 s'était
donné une raison commode de ne pas finir : il suffisait de regarder
le type de la variable pour voir qu'elle était fausse. **Deux cycles
ont été dépensés pour ce que le premier pouvait faire.**

## Critères de succès

1. Type de chaque garde publié, phrase du #487 **rétractée** — **OUI**.
2. Diff publié en entier, **4** instructions — **OUI**.
3. Règle du #481 avant/après — **NON**.
4. Exécution asymétrique respectée, vérifiée par l'état git — **OUI**.
5. Rapport régénéré committé seulement si borné au témoin — **OUI**.

**FAIL** — le critère porte sur le
**procédé**.

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).