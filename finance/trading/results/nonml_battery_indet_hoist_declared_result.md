# **Hisser `indet`**, déclaré d'avance (pré-enregistré)

Le **#490** avait mesuré que ce geste exigeait de hisser un calcul, que
son pré-enregistrement interdisait. Il l'a appliqué **en publiant que le
hissage aurait été anodin**. **Ce cycle le déclare et le fait.**

> **Je sais que ce hissage marche** — le #490 l'a établi. **Le résultat
> sur la règle du #481 est donc non informatif**, et **aucune prédiction
> ne porte dessus.** Ce qui était ouvert : le diff tient-il en deux
> lignes, et le cas limite change-t-il ?

## 1. Le diff, publié en entier

```diff
diff --git a/finance/trading/scripts/nonml_battery_coverage_backtest.py b/finance/trading/scripts/nonml_battery_coverage_backtest.py
index 792b686..cb692fd 100644
--- a/finance/trading/scripts/nonml_battery_coverage_backtest.py
+++ b/finance/trading/scripts/nonml_battery_coverage_backtest.py
@@ -143,6 +143,8 @@ def main():
     L.append("")
     L.append(f"- exécutées : **{len(executes)}**")
     L.append(f"- non traitées : **{len(non_traites)}**")
+    indet = sum(1 for _, _, c in executes if c and c[2] == "indéterminé")
+    L.append(f"- rapports classés « indéterminé » par la règle unifiée : **{indet}**")
     L.append("")
     if executes:
         L.append("| Candidat | Verdict de la batterie | Contrôles ✔ / ✘ |")
@@ -154,9 +156,6 @@ def main():
         n_pass = sum(1 for _, v, _ in executes if v.startswith("**VALID"))
         L.append(f"**{n_pass} / {len(executes)}** validés par la batterie.")
         L.append("")
-        indet = sum(1 for _, _, c in executes if c and c[2] == "indéterminé")
-        L.append(f"- rapports classés « indéterminé » par la règle unifiée : **{indet}**")
-        L.append("")
         if indet:
             L.append("### Une limite de la règle unifiée, découverte ici")
             L.append("")
```

- instructions **ajoutées** : **2**
- instructions **supprimées** : **3**

> **Ma prédiction annonçait 2 et 2 ; la mesure donne 2 et 3.** Elle est **réfutée**.

La suppression surnuméraire est un `L.append("")` — **un
séparateur devenu redondant** une fois les lignes remontées, puisqu'il
en existait déjà un à leur nouvelle place.

**Le geste est matériellement de deux lignes et textuellement de
trois.** Je ne présente pas cela comme « essentiellement vérifié » :
**la prédiction était chiffrée, elle est fausse.** Le #490 refusait
donc un geste très légèrement plus large qu'il ne le pensait.

## 2. Le changement de comportement, annoncé avant d'être mesuré

| | Ligne d'affectation | Profondeur |
|---|---|---|
| **avant** | 157 | **1** |
| **après** | 146 | **0** |

- `indet` est désormais au **niveau libre** : **OUI**

Le pré-enregistrement l'avait dit avant de le mesurer :

> Si `executes` est **vide**, le bloc ne s'exécute pas aujourd'hui et
> **aucun compte n'est publié**. Après hissage, le témoin paraîtra
> **quand même**, avec la valeur **0**.

**C'est un changement de sortie, pas un simple déplacement** — et c'est
exactement l'effet recherché : un témoin qui ne paraît que sous condition
n'est pas un témoin inconditionnel.

## 3. Le dépôt entier, avant et après

| | Avec témoin | **Sans témoin** | Garde non nommée |
|---|---|---|---|
| **avant** | 40 | **13** | 9 |
| **après** | 41 | **12** | 9 |

- diminution du compte « sans témoin » : **1**

**Ce résultat est non informatif** : le #490 avait déjà établi que le
hissage satisferait la règle. Il est publié parce que le critère 3 le
demande, **pas parce qu'il apprend quelque chose**.

## 4. Aucune exécution

- rapport de `battery_coverage` : **inchangé**

`battery_coverage` **exécute la batterie de validation** ; il n'est pas
lancé. **Son témoin reste dans le code, pas dans son rapport** — quatrième
cycle consécutif à devoir le dire (#487, #489, #490, #491).

## Mes trois prédictions, confrontées

*(Aucune ne porte sur la règle du #481 — c'était l'engagement.)*

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| 2 suppressions et 2 ajouts | 2 / 2 | 3 / 2 | **réfutée** |
| « sans témoin » diminue de 1 | 1 | 1 | **vérifiée** |
| autres classes inchangées | — | avec 40→41, non nommée 9→9 | **vérifiée** |

## Critères de succès

1. Diff publié, **2** ajouts / **3** suppressions — **OUI** *(2 annoncés, prédiction réfutée)*.
2. Changement du cas limite énoncé et vérifié par AST — **OUI**.
3. Compte du dépôt publié avant/après — **OUI**.
4. `battery_coverage` non exécuté — **OUI**.
5. Résultat sur la règle présenté comme non informatif — **OUI**.

**PASS** — le critère porte
sur le **procédé**. *(Prédiction 1 réfutée ; le critère porte sur ce qui a été fait et publié, pas sur la
justesse de mes annonces.)*

Simulation 300 € et robustesse **sans objet** : aucune position, aucun
paramètre de stratégie.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).