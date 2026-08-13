# Pré-enregistrement — Low-Vol + overlay SMA200, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Onzième candidat des PASS exposés au biais du survivant ; il en restera **2**
après celui-ci.

**Vérification préalable effectuée** (règle du #400) : recherche par fichier de
résultat, PREREG, script et historique du backlog. La seule entrée le mentionnant
est le **#43** (cycle d'origine, combinaison #15 + #29). Aucun portage
point-in-time. Ce candidat n'a **ni `.npz` ni batterie Règle 9**.

Bilan de l'axe à ce stade : **17 PASS testés, 9 maintenus (dont 1 non
informatif), 8 tombés.**

## Architecture — panier, comme au #411

Portefeuille **Low-Vol** : tercile de plus faible volatilité réalisée 60 jours,
rebalancé tous les 21 jours ; référence = ce même panier en 1,0×, exposition
portée à 2,0× quand l'indice est au-dessus de sa SMA200.

Le biais du survivant agit donc **sur les deux jambes**. Les cinq candidats à
panier testés jusqu'ici sont tombés — ce n'est pas une prédiction, le #409 ayant
montré qu'un candidat indiciel pouvait tomber aussi, et je n'inscris aucune règle
tirée de ces comptages.

## Contrôle d'attribution — pré-enregistré cette fois

Au #411, la référence Winners s'effondrait (Sharpe +0,96 → +0,44) mais la fenêtre
avait changé en même temps que l'univers. J'avais dû ajouter **après coup** un
diagnostic restreignant le calcul point-in-time à la fenêtre d'origine, qui a
montré que l'effondrement venait bien de l'univers (+250,7 % → +38,1 % à fenêtre
identique).

Ce diagnostic est ici **pré-enregistré et systématique** : l'audit calculera le
portefeuille de référence point-in-time sur la fenêtre du cycle d'origine
(2021-03-31 → 2026-07-27), afin de séparer effet d'univers et effet de période.
Un diagnostic utile trouvé après coup une fois doit devenir un contrôle déclaré
la fois suivante — sinon il ne sert qu'à expliquer les résultats qui m'arrangent.

Ce contrôle **ne conditionne aucun verdict**.

## Hypothèse testée

Le verdict PASS de `lowvol_sma200_overlay` est-il conservé lorsque l'univers de
sélection du panier Low-Vol est l'appartenance **réelle à chaque date** au lieu
de la liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `VOL_WINDOW` | 60 |
| `REBAL_EVERY` | 21 |
| `TERCILE` | 1/3 |
| `CAP` | 2,0 |
| `SMA_WINDOW` | 200 |
| `COST_BPS` | 5,0 |

**Seul changement :** l'univers de sélection passe de `data/pead/prices/` à
`data/pead/prices_pit/`, avec appartenance résolue à chaque date de
rebalancement. Le signal SMA200 porte sur l'**indice** et est inchangé.

**Exécution causale** (#166/#167). **Agrégation** : rendements simples par titre,
`trading_metrics` reçoit `log1p(pnl)` (#378-#380).

**Fenêtre testable :** masque explicite, **doublé d'une garde exécutable** — le
script lève une exception si la fenêtre démarre avant le 01/01/2015.

## Critère de succès — IDENTIQUE à l'original

Le portefeuille Low-Vol + overlay doit battre le portefeuille Low-Vol 1,0×
**en Sharpe annualisé ET en rendement total**, net de coûts.

- **PASS** : les deux jambes atteintes. **FAIL** : au moins une manquée.

`n_trials = 1`. Verdict rapporté tel quel.

## Prédiction — non tranchée

Aucune, abstention motivée maintenue depuis le #409.

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close.
3. Audit : simulation en **nombre de parts**, anti-lookahead, appartenance à la
   date de décision, causalité du décalage, **et contrôle d'attribution
   univers / période** décrit plus haut.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
