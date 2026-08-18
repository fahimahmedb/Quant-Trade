# Un témoin de vraisemblance pour les détecteurs jamais testés

Le **#514** n'a testé que la couche contextuelle du #502. Trois couches
sous-jacentes — utilisées par toute la série #500-#514 — n'avaient
**jamais** subi de témoin.

## La méthode, citée verbatim

> `lift = P(A ET B) / (P(A) × P(B))` — **≥ 3** : discrimine ; **< 3** : recoupe deux événements fréquents, sans plus.

## D500 — l'extraction du #500

`A` = la chaîne contient `#NNN` ; `B` = elle contient un nombre en gras.

- chaînes publiées analysées : **23415**
- `P(A)` = **996**/23415 = 4,3 %
- `P(B)` = **113**/23415 = 0,5 %
- `P(A∩B)` observé = **31**/23415 = 0,1 %
- attendu sous indépendance = 0,02 %
- **lift = 6,4**
- verdict : **DISCRIMINE**

## D497-P10 — la primitive « exécution en process »

`A` = le script importe un module `nonml_*` ; `B` = il appelle `.main()`
sur **n'importe quel** objet, sans exiger que ce soit l'alias importé.

- scripts analysés : **1007**
- `P(A)` = **83**/1007 = 8,2 %
- `P(B)` = **8**/1007 = 0,8 %
- `P(A∩B)` observé — **la vraie règle P10**, même alias — = **8**/1007 = 0,8 %
- attendu sous indépendance = 0,07 %
- **lift = 12,1**
- verdict : **DISCRIMINE**

## D501 — la confirmation brute « en gras quelque part »

`decoy(v)` = complément à 9 chiffre par chiffre sur la partie entière
de `v` (`d → 9-d`) ; partie décimale inchangée ; **indéterminé et
exclu** si le chiffre de tête du complément vaut `0`.

- valeurs empruntées : **39**
- indéterminées (exclues) : **1**
- évaluées : **38**

| | Trouvée en gras quelque part | Taux |
|---|---|---|
| **valeur réelle** | **38**/38 | **100,0 %** |
| **decoy** (complément à 9) | **25**/38 | **65,8 %** |

- rapport réel/decoy : **1,5**
- verdict : **NE DISCRIMINE PAS**

## Le résumé

| Détecteur | Mesure | Seuil | Verdict |
|---|---|---|---|
| **D500** (#500) | lift 6,4 | ≥ 3 | **PASSE** |
| **D497-P10** (#497) | lift 12,1 | ≥ 3 | **PASSE** |
| **D501** (#501) | rapport 1,5 | ≥ 3 | **ÉCHOUE** |

- détecteurs qui discriminent : **2** sur **3**

> **Le schéma annoncé au pré-enregistrement se confirme.** Les deux
> couches structurelles (extraction du #500, primitive P10 du #497)
> mesurent une conjonction réelle. **La confirmation brute du #501 —
> « en gras quelque part », sans contrainte de sujet — ne discrimine
> pas** : un decoy fabriqué par une transformation arbitraire des
> chiffres se retrouve « confirmé » presque aussi souvent que la
> vraie valeur. **C'est exactement pourquoi le #502 a dû ajouter les
> mots-clés** : sans eux, la couche #501 seule ne prouvait rien, et
> ce cycle en donne enfin la mesure.

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| D500 discrimine (lift ≥ 3) | oui | 6,4 | **vérifiée** |
| D497-P10 discrimine (lift ≥ 3) | oui | 12,1 | **vérifiée** |
| D501 NE discrimine PAS (rapport < 3) | non | 1,5 | **vérifiée** |

## Aucune exécution

- fichiers modifiés par ce cycle hors les siens : **0**

Fonctions **importées** des backtests des #500, #501 et #497 — jamais
recopiées, jamais leur `main()`.

## Critères de succès

1. Les trois définitions (A, B, decoy) citées verbatim — **OUI**.
2. Les trois lifts/rapports publiés avec leurs effectifs — **OUI**.
3. Verdict rendu pour chacun des trois au seuil de 3 — **OUI**.
4. Indéterminés de D501 comptés (**1**) — **OUI**.
5. Aucun script exécuté, arbre propre — **OUI**.

**PASS** — le critère porte sur le **procédé**. **Il ne dépend pas
du succès des détecteurs testés**, seulement de la publication honnête
de leur verdict (leçon du #513).

## Portée — ce que ce cycle ne retranche pas

Un détecteur qui échoue ici **n'invalide pas rétroactivement** un cycle
qui l'utilisait en combinaison avec la couche contextuelle du #502,
déjà testée et validée au #514. La portée est **la couche testée**, pas
la chaîne complète.

Simulation 300 € et robustesse **sans objet** : cycle de vérification,
aucune position, aucun paramètre numérique de stratégie.

> **Rapport dépendant du dépôt** — il décrit l'état des scripts, du
> registre et des rapports à la date de son exécution.
