# Pré-enregistrement — breadth de surperformance « petites caps » proxy, univers POINT-IN-TIME

**Écrit et committé AVANT tout calcul.** `n_trials = 1`.

## Contexte

Cinquième candidat réellement non vérifié des **9** PASS encore exposés au biais
du survivant.

**Vérification préalable effectuée** (règle du #400) : recherche par fichier de
résultat, PREREG, script et historique du backlog. Les seules entrées le
mentionnant sont le #123 (origine) et le #404 (correction d'un défaut que
j'avais introduit dans son script au #392). Aucun portage point-in-time.

Ce portage avait été entamé au #404 puis interrompu par la découverte du défaut.
Le script d'origine est désormais propre ; ce cycle reprend là où il s'était
arrêté.

Bilan de l'axe à ce stade : **11 PASS testés, 5 maintenus, 6 tombés.**

## Ce que ce candidat a de structurellement différent

Contrairement aux quatre précédents (#394, #401, #402, #403), **le P&L de ce
candidat n'est pas un panier de titres** : les deux jambes sont l'indice NDX-100
lui-même, en Buy & Hold pur ou avec exposition modulée. L'univers de titres
n'intervient **que dans la construction du signal** — la breadth de
surperformance du groupe « petite capitalisation » proxy.

Le biais du survivant ne peut donc agir ici que par un seul canal : un signal
calculé sur les 100 sociétés qui *ont survécu jusqu'en 2026* au lieu de celles
réellement cotées à chaque date. Ni la référence ni la jambe candidate ne sont
directement contaminées.

C'est la configuration du #396, dont j'avais tiré la conjecture « le P&L indiciel
survit, le panier tombe » — **conjecture démentie au #398**. Je ne la reformule
pas.

## Hypothèse testée

Le verdict PASS (niveau 1) de `smallcap_proxy_outperformance_breadth_overlay`
est-il conservé lorsque la breadth est calculée sur l'appartenance **réelle à
chaque date** au lieu de la liste NDX-100 figée de 2026 ?

## Protocole — RÉUTILISATION STRICTE (Règle 7)

**Aucun paramètre n'est modifié.** Repris à l'identique :

| Paramètre | Valeur |
|---|---|
| `IDIO_VOL_WINDOW` | 60 |
| `MOM_WINDOW` | 21 |
| `MEDIAN_WINDOW` | 252 |
| `MIN_LISTED` | 10 |
| `VOL_WINDOW` | 20 |
| `TARGET_VOL_ANNUAL` | 0,20 |
| `CAP` | 2,0 |
| `COST_BPS` | 5,0 |

**Seul changement :** l'univers servant à calculer la breadth passe de
`data/pead/prices/` à `data/pead/prices_pit/`, et **à chaque date** seuls les
titres membres du NDX-100 à cette date (`ndx100_membership.tickers_as_of_date`)
entrent dans le calcul de la volatilité idiosyncratique, du momentum 21 j et des
médianes transversales.

Le P&L, lui, reste **strictement inchangé** : indice NDX-100, rendements
logarithmiques, `exp(Σ pnl) − 1` pour le rendement total et `trading_metrics`
directement sur la série log — conventions rétablies au #404, non retouchées ici.

**Fenêtre testable :** la breadth n'est définie que là où l'appartenance
point-in-time l'est (à partir du 01/01/2015) **et** où au moins `MIN_LISTED`
titres membres sont éligibles. Masque explicite, via `notna()` sur la série de
porte non remplie — mécanisme déjà présent dans le script d'origine, conservé,
et qui évite le piège du #396.

## Critère de succès — IDENTIQUE à l'original

L'overlay doit battre Buy & Hold **en Sharpe annualisé ET en rendement total**,
net de coûts.

- **PASS niveau 1** : les deux jambes atteintes. **FAIL** : au moins une manquée.

Comme à l'origine, un PASS de niveau 1 **n'est pas un verdict final** (Règle 9).
Pour mémoire, la batterie renforcée du candidat d'origine donne **1/5** — il est
déjà l'un des plus fragiles du backlog. Ce contexte n'est pas une prédiction sur
le présent test, qui ne porte que sur le critère de niveau 1.

`n_trials = 1`. Verdict rapporté tel quel.

## Prédiction — non tranchée

Aucune attente formulée, pour la raison écrite plus haut : la seule conjecture
que j'aie émise sur cet axe a été démentie.

## Engagements

1. Résultat rapporté **tel quel**, sans réexécution après lecture.
2. Aucun retuning : si FAIL, l'entrée est close.
3. Audit à recalcul indépendant de la breadth (chemin de code disjoint),
   vérification anti-lookahead par mutation du futur, et contrôle que **seuls
   des membres à la date** entrent dans le calcul.
4. Le résultat **ne remplace pas** celui de l'original : les deux coexistent.
