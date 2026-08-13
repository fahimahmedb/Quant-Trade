# Pré-enregistrement — Winners court terme + overlay tendance/vol-targeting, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Dixième candidat des PASS exposés au biais du survivant ; il en restera **3**
après celui-ci.

**Vérification préalable effectuée** (règle du #400) : recherche par fichier de
résultat, PREREG, script et historique du backlog. La seule entrée le mentionnant
est le **#47** (cycle d'origine, combinaison #14 + overlay). Aucun portage
point-in-time. Ce candidat n'a **ni `.npz` ni batterie Règle 9**.

Bilan de l'axe à ce stade : **16 PASS testés, 9 maintenus (dont 1 non
informatif), 7 tombés.**

## Retour à une architecture de PANIER

Les cinq portages précédents (#405 à #410) portaient sur des candidats à **P&L
indiciel**, dont l'univers de titres n'alimentait que la porte. Celui-ci est un
**panier de titres** : le portefeuille Winners (tercile du meilleur momentum
5 jours, rebalancé tous les 5 jours), avec pour référence ce même panier en 1,0×.

**Le biais du survivant agit donc sur les deux jambes**, comme aux #401 et #402
— tous deux tombés. Ce n'est pas une prédiction : les quatre candidats-paniers
testés jusqu'ici sont tombés, mais le #409 vient de montrer qu'un candidat
indiciel pouvait tomber aussi, et je n'inscris aucune règle tirée de ces
comptages.

## Un avertissement déjà présent dans le rapport d'origine

Le résultat du #47 porte la mention : *« Prudence forte héritée du #14 : le
portefeuille Winners affiche un edge extrême potentiellement propre au bull
market IA/semiconducteurs 2021-2026, généralisabilité non garantie. »*

Ce portage teste précisément une des dimensions de cette prudence — l'univers —
mais **pas** l'autre : la période reste dominée par le même marché. Un maintien
ne lèverait donc pas l'avertissement du #14 ; il ne lèverait que le doute sur
l'univers. C'est écrit ici pour qu'un éventuel PASS ne soit pas présenté comme
une validation plus large qu'il n'est.

## Hypothèse testée

Le verdict PASS de `winners_trend_vol_targeting_overlay` est-il conservé lorsque
l'univers de sélection des Winners est l'appartenance **réelle à chaque date** au
lieu de la liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `SIGNAL_WINDOW` | 5 |
| `REBAL_EVERY` | 5 |
| `TERCILE` | 1/3 |
| `CAP` | 2,0 |
| `INDEX_LOOKBACK` | 252 |
| `INDEX_THRESHOLD` | 0,95 |
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `COST_BPS` | 5,0 |

**Seul changement :** l'univers de sélection passe de `data/pead/prices/` à
`data/pead/prices_pit/`, avec appartenance résolue par
`ndx100_membership.tickers_as_of_date` à chaque date de rebalancement.

**Exécution causale** (patch #166/#167) : les poids décidés à la clôture de t−1
sont détenus pendant t. Ce point est critique pour ce candidat — son signal est un
momentum à 5 jours, donc bien plus rapide que les filtres lents des #401/#402, et
c'est exactement le profil pour lequel le #253 a montré qu'une fuite « même
barre » est destructrice.

**Agrégation :** rendements **simples** par titre, `Σ wᵢ·r_simple,ᵢ` (#378-#380),
`trading_metrics` reçoit `log1p(pnl)`.

**Fenêtre testable :** masque explicite des dates où l'appartenance point-in-time
est définie, **doublé d'une garde exécutable** — le script lève une exception si
la fenêtre démarre avant le 01/01/2015 (leçon du #405, appliquée depuis le #408).

## Critère de succès — IDENTIQUE à l'original

Le portefeuille Winners + overlay doit battre le portefeuille Winners 1,0×
**en Sharpe annualisé ET en rendement total**, net de coûts.

- **PASS** : les deux jambes atteintes. **FAIL** : au moins une manquée.

`n_trials = 1`. Verdict rapporté tel quel.

## Prédiction — non tranchée

Aucune, conformément à l'abstention motivée du #409 : deux mécanismes proposés
aux #407 et #408, deux contredits par la mesure.

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close.
3. Audit : recalcul par simulation en **nombre de parts** (chemin comptable pur),
   anti-lookahead par perturbation du futur, appartenance à la date de décision,
   causalité du décalage.
4. Si PASS, le rapport rappellera explicitement que l'avertissement du #14 sur la
   période **n'est pas levé** par ce cycle.
5. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
