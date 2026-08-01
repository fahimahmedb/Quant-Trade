# Quelles familles de stratégies ont un profil statistique compatible avec un DSR > 0,95 ?

**Revue de littérature — 01/08/2026.** Commandée par l'utilisateur après le
constat que 164 cycles non-ML et 4 cycles ML échouent presque tous au même
endroit : le Deflated Sharpe Ratio (Règle 9e), très en dessous du seuil 0,95,
malgré des Sharpe bruts parfois énormes.

**Renversement de logique demandé** : jusqu'ici la démarche a été « viser le
rendement d'abord, espérer que le DSR suive ». Cette revue cherche l'inverse —
quelles FAMILLES de stratégies ont un profil statistique (fréquence de pari,
nombre de paris indépendants, neutralité au marché, forme de la distribution)
qui rend un bon DSR plausible **par construction** plutôt que par chance.

**Contrainte non négociable rappelée d'emblée** : rien dans ce document ne
justifie de remettre `n_trials` à zéro. Le compteur de
`NONML_STRATEGY_BACKLOG.md` (164 hypothèses au moment de la rédaction) est le
compteur honnête de ce programme de recherche et doit continuer d'être utilisé,
y compris si le sujet change complètement (PROTOCOLE_ANTI_SNOOPING.md, Règle 2
et Règle 9e). Créer un backlog neuf pour repartir « propre » serait précisément
le data-snooping que ce projet combat.

---

## 0. Ce que la formule du DSR dit exactement (lecture du code déjà committé)

Avant toute littérature, il faut savoir sur quels leviers on peut agir.
`finance/src/prediction.py` (lignes 318-344) :

```python
def expected_max_sharpe(var_trials, n_trials):
    g = 0.5772156649                      # Euler-Mascheroni
    z1 = stats.norm.ppf(1 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1 - 1.0 / (n_trials * np.e))
    return sqrt(var_trials) * ((1 - g) * z1 + g * z2)

def dsr(sr_hat_daily, T, var_trials, n_trials, skew, kurt_excess):
    sr0   = expected_max_sharpe(var_trials, n_trials)
    denom = sqrt(1 - skew * sr_hat_daily + kurt_excess / 4.0 * sr_hat_daily**2)
    z     = (sr_hat_daily - sr0) * sqrt(T - 1) / denom
    return norm.cdf(z)
```

Soit, littéralement :

```
DSR = Phi( (SR_j - SR0) * sqrt(T-1) / sqrt(1 - skew*SR_j + (kurt_ex/4)*SR_j^2) )
```

**Il n'y a donc que quatre leviers, et ils ne pèsent pas du tout le même poids :**

| Levier | Entre comment | Ordre de grandeur du levier |
|---|---|---|
| `SR_j` (Sharpe **journalier** de la stratégie) | numérateur, linéaire | **dominant** |
| `SR0` (seuil de sélection) | numérateur, linéaire, soustractif | **dominant** |
| `T` (nombre d'observations) | `sqrt(T-1)` | modéré (loi en racine) |
| `skew`, `kurt_ex` | dénominateur, via `SR_j` et `SR_j²` | **second ordre à la fréquence quotidienne** |

Le dernier point est capital et rarement dit : à la fréquence quotidienne
`SR_j ≈ 0,09`, donc le terme d'asymétrie vaut `skew × 0,09` et le terme de
kurtosis `kurt_ex/4 × 0,008` — des corrections de l'ordre de **2 % et 0,5 %**
sur un dénominateur valant 1. Toute la littérature sur « l'asymétrie positive
protège le PSR » est vraie **en niveau**, mais son effet chiffré ici est
minuscule (quantifié en Phase 2, `results/nonml_dsr_decomposition_38.md`).

Et `SR0 = sqrt(var_trials) × E[max de n_trials normales]` :
- il croît **linéairement** en écart-type des Sharpe des essais (`sqrt(var_trials)`) ;
- il croît seulement **en `sqrt(2 ln n_trials)`** avec le nombre d'essais.

Concrètement, dans l'état actuel du backlog (`var_trials` = 8,0052e-04
journalier, extrait de 68 Sharpe du backlog ; `n_trials` = 164) :
`SR0 ≈ 0,0763/jour`, soit **1,21 de Sharpe annualisé rien que pour le seuil de
sélection**. C'est le chiffre à battre AVANT de commencer à gagner de l'argent.

*Note de précision technique, sans impact sur les verdicts déjà rendus.* La
formule canonique de Bailey & López de Prado (« The Sharpe Ratio Efficient
Frontier », 2012) écrit le dénominateur
`sqrt(1 - γ3·SR + ((γ4-1)/4)·SR²)` où **γ4 est la kurtosis NON excédentaire**
(γ4 = 3 pour une gaussienne). L'implémentation du repo utilise
`kurt_excess/4 = (γ4-3)/4` au lieu de `(γ4-1)/4`, soit un écart de `0,5·SR²`
sur le carré du dénominateur. À `SR_j = 0,089` cela vaut 0,004 sur ~1,03 :
l'implémentation du repo **surestime `z` de ~0,2 %**, donc le DSR rapporté est
très légèrement OPTIMISTE (0,7526 au lieu de 0,7523 pour le #38 — chiffré en
Phase 2). Aucun verdict ne change ; signalé au titre de la Règle 6.

---

## 1. Grinold : la loi fondamentale de la gestion active

**Source** : Grinold (1989), *The Fundamental Law of Active Management*, JPM ;
Grinold & Kahn, *Active Portfolio Management*. Redux : Ding & Martin (2017),
[The fundamental law of active management: Redux](https://www.sciencedirect.com/science/article/pii/S0927539817300543).
Exposés pédagogiques :
[AnalystPrep](https://analystprep.com/study-notes/cfa-level-2/state-and-interpret-the-fundamental-law-of-active-portfolio-management-including-its-component-terms-transfer-coefficient-information-coefficient-breadth-and-active-risk-aggressiveness/),
[Robeco](https://www.robeco.com/en-int/insights/2018/04/fundamental-law-of-active-management-shows-way-to-higher-information-ratio),
[Blank Capital Research](https://blankcapitalresearch.com/learn/grinold-fundamental-law-active-management).

```
IR ≈ IC × sqrt(BR)          (version étendue : IR ≈ TC × IC × sqrt(BR))
```

- `IC` = corrélation entre prévision et réalisation (la « qualité » d'un pari) ;
- `BR` = **ampleur** = nombre de paris **indépendants** par an ;
- `TC` = coefficient de transfert (part du signal réellement implémentée, ≤ 1).

**Ce que ça implique, très concrètement, pour ce backlog.** Presque tous les
164 cycles testés ici sont des paris de TIMING sur UN actif : « lever l'exposition
au NDX quand tel régime est actif ». L'ampleur d'un tel mécanisme est
structurellement minuscule. Prenons le #38 (le meilleur candidat) : le signal de
porte (indice à ≥95 % de son plus haut 252j) change d'état quelques fois par an,
et la sélection Leaders se rebalance 12 fois par an sur des titres tous longs,
tous très corrélés entre eux (bêta ≈ 1, corrélation moyenne par paires mesurée
au #90 : 0,278). Le nombre de paris VRAIMENT indépendants par an se compte en
dizaines, pas en milliers.

Une stratégie **market-neutral à N titres** rebalancée `f` fois par an a au
contraire `BR ≈ N × f` paris — à condition que les résidus soient réellement
peu corrélés, ce qui est justement la définition de la neutralité au marché
(on a retiré le facteur commun qui rendait les paris redondants).

Ordre de grandeur avec les données de ce repo (univers point-in-time NDX-100,
~100 titres investissables) :

| Construction | `BR` annuel plausible | `IC` requis pour `IR = 1,7` |
|---|---|---|
| Timing d'indice mensuel (famille #47/#54/#57…) | ~12 | 0,49 (irréaliste) |
| Sélection long-only tercile mensuelle (#4/#73/#82) | ~12-40 « effectifs » (forte corrélation résiduelle) | 0,27-0,49 (irréaliste) |
| Long/short dollar-neutre 100 titres, mensuel | ~1 200 bruts, disons 150-300 effectifs | **0,10-0,14** (élevé mais pas absurde) |
| Paires cointégrées, 30 paires, hebdo | ~1 560 bruts, disons 300-600 effectifs | **0,07-0,10** (plausible) |

Le tableau dit l'essentiel : **avec un IC réaliste de 0,05-0,10, seule une
construction à grande ampleur peut viser un IR (≈ Sharpe) de 1,7.** Aucune
quantité de raffinement du signal de timing d'indice ne peut y arriver, parce
que `sqrt(BR)` y est petit par construction. C'est l'explication théorique
directe du plafond observé empiriquement au #116 (« il faudrait un Sharpe
annualisé de 1,58 à 2,03 pour passer, supérieur à tous les repères
académiques ») et au #164 (« il faudrait ~67 ans de données »).

**Réserve honnête** : `BR` est le nombre de paris **indépendants**, pas le
nombre de lignes du portefeuille. Ding & Martin (2017) et la critique standard
de la loi rappellent que la version naïve surestime massivement `BR` dès que
les signaux se recoupent, et que `TC` est souvent 0,3-0,6 en pratique (coûts,
contraintes, plafonds). Le tableau ci-dessus est donc un ordre de grandeur
optimiste, pas une promesse.

---

## 2. Bailey & López de Prado : ce qu'ils recommandent, au-delà de la formule

**Sources** :
- Bailey, Borwein, López de Prado & Zhu (2014), *Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance*, Notices of the AMS 61(5)
  ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659),
  [version LBNL](https://sdm.lbl.gov/oapapers/ssrn-id2507040-bailey.pdf),
  [vulgarisation Significance/RSS 2021](https://rss.onlinelibrary.wiley.com/doi/10.1111/1740-9713.01588)).
- Bailey & López de Prado (2014), *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality*, JPM
  ([PDF auteur](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)).
- Bailey & López de Prado (2012), *The Sharpe Ratio Efficient Frontier*
  ([PDF auteur](https://www.davidhbailey.com/dhbpapers/sharpe-frontier.pdf)).
- López de Prado (2018), *The 10 Reasons Most Machine Learning Funds Fail*, JPM 44(6)
  ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3104816),
  [PDF GARP](https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf)).

Les résultats déjà utilisés dans ce repo (la formule DSR) ne sont que la partie
mesure. La partie **conception** de leurs écrits dit trois choses directement
actionnables ici :

1. **« Minimum Backtest Length ».** Bailey et al. montrent qu'il existe une
   longueur minimale d'échantillon en dessous de laquelle un Sharpe de 1 est
   attendu par pur hasard étant donné `N` essais : `MinBTL ≈ 2 ln(N) / SR²`
   (en années, SR annualisé). Avec `N = 164` et un objectif `SR = 1,0` :
   `MinBTL ≈ 2 × 5,1 / 1 = 10,2 ans`. Avec `SR = 1,7` : `3,5 ans`. **Autrement
   dit : à 11,5 ans d'échantillon, ce backlog n'a la puissance de valider qu'un
   Sharpe ≥ ~1,0-1,2 ; en viser moins est mathématiquement sans issue.** C'est
   exactement le mur du #163.
2. **Le paradigme « méta-stratégie » plutôt que « Sisyphe »** (raison n°1 des
   « 10 reasons »). Un chercheur isolé qui itère jusqu'à trouver quelque chose
   finit par produire soit un faux positif surajusté, soit du beta déguisé. La
   correction proposée n'est pas « chercher mieux », c'est **changer d'unité de
   production** : décider a priori d'une FAMILLE de mécanismes structurellement
   apparentés, les tester tous ensemble, et rapporter le résultat de la famille
   — pas le meilleur membre. Ce backlog fait l'inverse depuis 164 cycles (une
   hypothèse par cycle, la meilleure émergeant par accumulation), et c'est
   précisément ce qui gonfle `n_trials`.
3. **La non-normalité est intégrée exprès dans le DSR**, mais avec la mise en
   garde que l'effet est proportionnel à `SR` : la correction d'asymétrie est
   significative pour des séries **mensuelles** (où `SR_mensuel ≈ 0,3-0,5`), pas
   pour des séries quotidiennes (`SR_j ≈ 0,05-0,10`). Le repo travaillant en
   quotidien, **chercher un profil asymétrique positif ne rapportera presque
   rien au DSR** (quantifié en Phase 2) — même si c'est une excellente idée pour
   d'autres raisons (drawdown, robustesse en crise).

**Complément multiple-testing** : Harvey & Liu (2015), *Backtesting*
([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2345489),
[PDF CME](https://www.cmegroup.com/education/files/backtesting.pdf)) et Harvey,
Liu & Zhu (2016), *…and the Cross-Section of Expected Returns*
([NBER w20592](https://www.nber.org/system/files/working_papers/w20592/w20592.pdf))
proposent une décote (« haircut ») du Sharpe corrigée pour essais multiples.
Leur observation la plus utile ici : **la décote est NON LINÉAIRE — les Sharpe
très élevés sont peu décotés, les Sharpe marginaux le sont massivement.** C'est
la même conclusion que le DSR sous un autre angle : viser un Sharpe de 0,8 dans
un programme à 164 essais est sans espoir, viser 1,8 est qualitativement
différent.

---

## 3. Arbitrage statistique / pairs trading : pourquoi les Sharpe publiés sont plus élevés

**Sources** :
- Gatev, Goetzmann & Rouwenhorst (2006), *Pairs Trading: Performance of a Relative-Value Arbitrage Rule*, RFS 19(3), 797-827
  ([NBER w7032](https://www.nber.org/papers/w7032),
  [PDF Wharton](http://stat.wharton.upenn.edu/~steele/Courses/434/434Context/PairsTrading/PairsTradingGGR.pdf),
  [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=141615)).
- Avellaneda & Lee (2010), *Statistical Arbitrage in the U.S. Equities Market*, Quantitative Finance 10(7), 761-782
  ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1153505),
  [PDF Berkeley](https://traders.studentorg.berkeley.edu/papers/Statistical%20arbitrage%20in%20the%20US%20equities%20market.pdf)).
- Do & Faff (2010), *Does Simple Pairs Trading Still Work?*, Financial Analysts Journal 66(4)
  ([SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1656954),
  [T&F](https://www.tandfonline.com/doi/abs/10.2469/faj.v66.n4.1)).

**Ce qui est établi.** GGR (2006) : appariement par distance minimale sur prix
normalisés, données quotidiennes 1962-2002, rendements en excès annualisés
jusqu'à **11 %** pour des portefeuilles auto-financés de paires, **bêta proche
de zéro et Sharpe élevé dans tous les cas**. Avellaneda & Lee (2010) :
résidus d'une décomposition en composantes principales (ou régression sur ETF
sectoriels) modélisés comme processus à retour à la moyenne, **Sharpe moyen
1,44 net de coûts sur 1997-2007** (mais **seulement 0,9 sur 2003-2007**).

**Pourquoi le profil statistique est meilleur — trois mécanismes distincts :**
1. **Neutralité au marché → variance retirée, pas rendement.** Le dénominateur
   du Sharpe d'une stratégie long-only sur actions est dominé par la variance du
   facteur marché (~18-25 % annualisés). Une construction dollar-neutre annule
   ce terme au premier ordre ; il reste la variance idiosyncratique du spread
   (~5-12 %). Si l'alpha survit à la neutralisation, le Sharpe **monte
   mécaniquement**, sans qu'aucun signal n'ait été amélioré.
2. **Ampleur (Grinold).** Un portefeuille de 20-40 paires suivies
   simultanément produit des centaines de paris quasi-indépendants par an.
3. **Additivité en quadrature avec le marché.** Si un « sleeve » d'alpha de
   Sharpe `SR_a` est réellement décorrélé du marché de Sharpe `SR_m`, le
   portefeuille combiné optimal a `SR = sqrt(SR_m² + SR_a²)`. Avec la référence
   Leaders 1.0x du #38 (`SR_m = 0,79`) et un sleeve à `SR_a = 1,5`, le combiné
   atteint **1,70** — exactement la barre calculée pour le DSR. **C'est la seule
   voie identifiée dans cette revue qui permette de battre à la fois Buy&Hold en
   rendement (règle renforcée du backlog) ET d'atteindre le niveau de Sharpe
   qu'exige le DSR.**

**Réserve honnête, à ne pas enterrer.** Do & Faff (2010) documentent une
décroissance nette : le rendement mensuel moyen du top-20 paires passe de
**0,86 % (1962-1988) à 0,37 % (1989-2002) puis 0,24 % (2003-2009)**, et la
stratégie devient significativement non rentable après coûts sur la période
récente. Avellaneda & Lee constatent la même érosion (1,44 → 0,9 après 2003).
**Notre échantillon point-in-time commence en 2015** : il est entièrement dans
la zone où la littérature dit que le pairs trading naïf ne marche plus. Un
mécanisme de paires classique doit donc être testé **en s'attendant à un FAIL**,
et son intérêt est surtout de trancher empiriquement la question sur cet
univers précis. Ce qui reste plus solide dans la période récente, c'est la
famille **cross-sectionnelle** (long/short sur un score, pas paire par paire),
mieux diversifiée et moins dépendante d'une convergence par paire.

---

## 4. Asymétrie et son effet réel sur le DSR

**Sources** : littérature trend-following/CTA sur la convexité et le « crisis
alpha » ([The Hedge Fund Journal, *The Convexity of Trend Following*](https://thehedgefundjournal.com/the-convexity-of-trend-following/),
[Man Group](https://www.man.com/insights/trend-following-optimal-market-mix),
[CFM](https://www.cfm.com/wp-content/uploads/2022/12/39-A-Good-Time-for-Trend-Following-FINAL.pdf),
[Fidelity, *Trend-following crisis alpha*](https://institutional.fidelity.com/app/proxy/content?literatureURL=%2F9922231.PDF)) ;
côté asymétrie négative, Daniel & Moskowitz, *Momentum Crashes*, JFE
([NBER w20439](https://www.nber.org/system/files/working_papers/w20439/w20439.pdf),
[PDF auteur](https://www.kentdaniel.net/papers/published/mom12.pdf)).

**Ce que dit la littérature.** Le trend-following affiche une asymétrie
**positive** structurelle (beaucoup de petites pertes, rares gros gains) issue
de sa convexité mécanique ; le carry, la vente de volatilité et le momentum
long/short affichent l'inverse. Daniel & Moskowitz montrent que le momentum
long/short subit des « krachs » — chaînes de pertes fortes et persistantes en
sortie de marché baissier — donc une asymétrie **négative** marquée, en partie
prévisible (états de « panique », vol de marché élevée). Barroso &
Santa-Clara et Daniel & Moskowitz montrent tous deux qu'un redimensionnement
par la volatilité réalisée du portefeuille momentum double approximativement
son alpha et son Sharpe.

**Ce que ça vaut pour NOTRE DSR : presque rien, et il faut le dire.** Comme
établi en §0, à `SR_j ≈ 0,09` le terme `−skew·SR_j` pèse ~2 % du dénominateur.
Passer d'une asymétrie de −0,25 à +0,25 changerait `z` de ~4 % et le DSR de
l'ordre de **+0,005**. Chiffré exactement en Phase 2.

**Conclusion pratique, contre-intuitive** : l'argument « choisir une famille à
asymétrie positive pour aider le DSR » est **réfuté quantitativement à la
fréquence quotidienne**. En revanche, l'asymétrie reste un excellent critère
pour les contrôles (b) stress de crise et pour la gestion du risque — ce qui
n'est pas rien, puisque c'est précisément le contrôle que le #38 vient de
perdre au #163 (krach COVID). Le redimensionnement par la vol du portefeuille
(Daniel-Moskowitz / Barroso-Santa-Clara) est donc à retenir **pour le contrôle
(b)**, pas pour le DSR.

---

## 5. Combinaison de signaux faibles peu corrélés

**Sources** :
[Goldman Sachs AM, *How to Combine Investment Signals in Long/Short Strategies*](https://www.gsam.com/content/dam/gsam/pdfs/institutions/en/articles/2018/Combining_Investment_Signals_in_LongShort_Strategies.pdf) ;
[FactSet, *A Practical Approach to Weighting Signals*](https://insight.factset.com/a-practical-approach-to-weighting-signals) ;
[Alpha Architect, *Alpha from Short-Term Signals*](https://alphaarchitect.com/alpha-from-short-term-signals/) ;
[AQR, *Key Design Choices in Long/Short Equity* (2023)](https://www.aqr.com/-/media/AQR/Documents/Alternative-Thinking/AQR-Alternative-Thinking---Key-Design-Choices-in-Long-Short-Equity.pdf) ;
[QuantPedia, *Long-Short vs Long-Only Implementation of Equity Factors*](https://quantpedia.com/long-short-vs-long-only-implementation-of-equity-factors/) ;
Firoozye et al., [*Canonical Portfolios: Optimal Asset and Signal Combination*](https://arxiv.org/pdf/2202.10817).

Résultat central et robuste : **le ratio d'information d'un composite de `k`
signaux d'IC individuel `ic` et de corrélation moyenne `rho` entre eux vaut
approximativement `ic × sqrt(k / (1 + (k-1)ρ))`.** Avec `k = 4` signaux et
`ρ = 0,3`, le gain est ×1,63 sur l'IC ; avec `ρ = 0,6` il tombe à ×1,26. Le
gain vient de la DÉCORRÉLATION, pas du nombre.

Observation empirique de QuantPedia et AQR qui compte beaucoup ici : **les
implémentations long-only (« long-hedged ») de facteurs différents sont
BEAUCOUP plus corrélées entre elles que leurs versions long/short.** Autrement
dit, empiler des tilts long-only — ce que fait ce backlog depuis 164 cycles —
apporte beaucoup moins de diversification qu'empiler les mêmes signaux en
long/short. C'est une explication directe du plafond observé aux #81/#98/#106
(les portes AND se combinent, mais l'edge ne s'additionne jamais vraiment).

**Ce que ça implique ici** : un composite de 3-5 signaux cross-sectionnels
DÉJÀ testés individuellement dans ce backlog (#4 52w-high titre, #73 momentum
12-1, #82 momentum de constance, #15 low-vol), agrégés par z-scores
équipondérés (aucun poids ajusté = aucun degré de liberté ajouté) et
implémentés en **dollar-neutre**, est un mécanisme testable immédiatement avec
les données déjà committées, et c'est la construction que la littérature
désigne comme la plus susceptible d'améliorer l'IR sans améliorer aucun signal.

---

## 6. Dépôts open-source : que font-ils différemment ?

Outils de mesure (pour vérifier notre propre implémentation) :
- [esvhd/pypbo](https://github.com/esvhd/pypbo) — PSR, Minimum Track Record Length, Minimum Backtest Length, DSR, et surtout **Probability of Backtest Overfitting** (CSCV) qui n'est PAS implémenté dans ce repo.
- [rubenbriones/Probabilistic-Sharpe-Ratio](https://github.com/rubenbriones/Probabilistic-Sharpe-Ratio) — implémentation de référence du PSR/DSR de López de Prado ([source](https://github.com/rubenbriones/Probabilistic-Sharpe-Ratio/blob/master/src/sharpe_ratio_stats.py)).
- [Nikhil-Kumar-Patel/The-deflated-sharpe-ratio](https://github.com/Nikhil-Kumar-Patel/The-deflated-sharpe-ratio).
- [braverock/quantstrat — haircut.Sharpe.R](https://github.com/braverock/quantstrat/blob/master/R/haircut.Sharpe.R) — implémentation du haircut de Harvey & Liu.
- [Portfolio Optimizer — PSR, hypothesis testing & MinTRL](https://portfoliooptimizer.io/blog/the-probabilistic-sharpe-ratio-hypothesis-testing-and-minimum-track-record-length-for-the-difference-of-sharpe-ratios/).

Stratégies stat-arb open-source :
- [rzhadev1/statarb](https://github.com/rzhadev1/statarb) — implémentation directe d'Avellaneda-Lee (PCA + résidus OU).
- [anthonyli01/Statistical-Arbitrage-Pairs-Trading-Strategy](https://github.com/anthonyli01/Statistical-Arbitrage-Pairs-Trading-Strategy) — cointégration, Kalman, copules. Note explicite de l'auteur : *« since it is a market-neutral strategy, we will analyse the performance on its alpha rather than sharpe ratio »*.
- [QuantConnect/Research — Pairs Trading Based on Cointegration](https://github.com/QuantConnect/Research/blob/master/Analysis/05%20Pairs%20Trading%20Strategy%20Based%20on%20Cointegration.ipynb).
- [sap215/StatArbPairsTrading](https://github.com/sap215/StatArbPairsTrading), [muMAJJI/Trading---Pair-Trading](https://github.com/muMAJJI/Trading---Pair-Trading), [arnavkohli/statistical-arbitrage-pairs-trading](https://github.com/arnavkohli/statistical-arbitrage-pairs-trading).

**Ce qu'ils font systématiquement différemment de ce backlog** — et c'est
l'observation la plus utile de la section :

| Dimension | Ce backlog (164 cycles) | Dépôts stat-arb |
|---|---|---|
| Nombre de positions simultanées | 1 (exposition scalaire à un indice) ou ~33 titres tous longs | 20-100 **paires ou spreads**, longs ET courts |
| Exposition marché | 1,0x à 2,0x en permanence | ≈ 0 par construction |
| Source du rendement | prime de risque actions + timing | convergence de spreads idiosyncratiques |
| Fréquence de décision | mensuelle à annuelle | quotidienne à hebdomadaire |
| Métrique revendiquée | Sharpe + rendement total vs Buy&Hold | alpha, bêta ≈ 0, Sharpe **sans** comparaison au marché |
| Validation | (ici) SPA + DSR + batterie Règle 9 | **le plus souvent AUCUNE correction pour essais multiples** |

Dernière ligne à retenir : **aucun des dépôts consultés ne rapporte de DSR ni
de PSR sur sa propre stratégie.** Ils affichent des Sharpe de 1,5-2,5 sans
correction pour essais multiples ; ce ne sont donc pas des contre-exemples à
notre plafond, ce sont des exemples de ce que le DSR est fait pour décoter.
Le seul enseignement transférable est **structurel** (neutralité, ampleur,
fréquence), pas la performance annoncée.

---

## 7. Synthèse : les trois pistes les plus prometteuses, et ce qu'elles impliquent

Rappel de la barre à franchir (calculée en Phase 2, ordres de grandeur ici) :
avec `n_trials ≈ 165` et `T ≈ 2 900` séances, il faut un **Sharpe annualisé de
~1,70** ; avec `T ≈ 1 150` séances, ~2,0. La question n'est donc jamais « ce
mécanisme a-t-il un edge ? » mais « ce mécanisme peut-il avoir un Sharpe de
1,7 sur 11 ans ? ».

### Piste A (la plus prometteuse) — Long/short dollar-neutre cross-sectionnel, puis combiné au marché en « alpha portable »

- **Pourquoi son profil statistique aide** : (i) la neutralité retire la
  variance du facteur marché du dénominateur sans retirer l'alpha (§3.1) ;
  (ii) l'ampleur passe de ~12 à ~1 200 paris bruts par an (§1) ; (iii) la
  combinaison en quadrature avec le marché (`sqrt(SR_m² + SR_a²)`) est le seul
  mécanisme identifié qui permette de satisfaire SIMULTANÉMENT la règle
  renforcée du backlog (battre Buy&Hold en Sharpe **et** en rendement) et le
  niveau de Sharpe qu'exige le DSR (§3.3).
- **Faisable avec les données déjà committées** : univers point-in-time
  `finance/trading/data/pead/prices_pit/` (214 tickers, 2015-2026) +
  `scripts/ndx100_membership.py`. Aucun fetch réseau.
- **Ce que ça implique concrètement** : composite équipondéré de z-scores de
  signaux DÉJÀ testés individuellement (#4, #73, #82, #15 — donc aucun nouveau
  degré de liberté de signal), poids `w ∝ z − mean(z)` normalisés à
  `sum|w| = 2`, rebalancement 21 jours (identique à #73/#82), coût 5 bps sur le
  turnover, puis sleeve additionné au cœur Buy&Hold à budget de risque FIXÉ
  a priori (vol cible du sleeve, pas de coefficient optimisé).
- **Risque principal, déclaré d'avance** : la jambe courte. Ce backtest ne
  modélise ni coût d'emprunt de titres, ni contrainte de disponibilité, ni
  rappel de prêt. Sur un univers NDX-100 (très grandes capitalisations
  liquides) c'est la situation la plus favorable possible, mais l'omission doit
  être écrite dans le PREREG et rappelée dans le rapport.

### Piste B — Paires (méthode distance de Gatev et al.), N paires suivies simultanément

- **Pourquoi son profil statistique aide** : c'est le cas d'école de l'ampleur
  de Grinold et de la neutralité au marché (§3). Un seul mécanisme
  pré-enregistré couvre des centaines de paris quasi indépendants — à la
  différence des 164 cycles précédents qui testaient un pari à la fois.
- **Faisable avec les données déjà committées** : mêmes prix point-in-time.
- **Ce que ça implique concrètement** : formation sur 12 mois (distance
  minimale sur prix normalisés, exactement GGR), trading sur les 6 mois
  suivants, ouverture à 2σ d'écart, fermeture au croisement, top-N paires,
  toutes suivies simultanément.
- **Risque principal, déclaré d'avance** : la littérature (Do & Faff 2010) dit
  que ce mécanisme **ne marche plus** après 2003, et notre échantillon commence
  en 2015. La probabilité a priori d'un FAIL est élevée ; l'intérêt du test est
  de trancher sur cet univers, et de fournir un point de comparaison
  d'ampleur/neutralité au regard de la piste A.

### Piste C (secondaire) — Momentum résiduel / momentum redimensionné par sa propre volatilité

- **Pourquoi** : Daniel & Moskowitz (§4) montrent que le redimensionnement par
  la vol réalisée du portefeuille long/short double approximativement le Sharpe
  du momentum et supprime l'essentiel des « krachs ». C'est le levier le plus
  documenté pour améliorer à la fois le Sharpe **et** le contrôle (b) de la
  Règle 9 — celui que le #38 vient de perdre.
- **Réserve** : c'est une variante de la piste A, pas un mécanisme
  indépendant ; à ne tester qu'après A, et à compter comme un essai
  supplémentaire.

### Ce que cette revue REJETTE explicitement

- **Chercher une asymétrie positive pour aider le DSR** : effet quantifié
  ~+0,005, négligeable à la fréquence quotidienne (§0, §4). À poursuivre pour
  le contrôle de crise, pas pour le DSR.
- **Continuer à allonger l'historique** : déjà tranché quantitativement au #164
  (~67 ans nécessaires).
- **Une 17e variante de porte pour le vol-targeting hiérarchique d'indice** :
  la loi fondamentale explique pourquoi c'est structurellement sans issue
  (`sqrt(BR)` trop petit), ce qui confirme théoriquement le constat empirique
  des #111-#132.
- **Réduire `n_trials` en changeant de sujet** : interdit (Règle 2). Le
  compteur du backlog continue.

---

## 8. Traçabilité

Aucun calcul n'a été effectué pour produire ce document — il ne contient que
des citations de littérature, la lecture du code déjà committé
(`finance/src/prediction.py:318-344`) et des chiffres déjà publiés dans ce repo
(#116, #163, #164, `results/nonml_dsr_power_analysis_38.md`). Les ordres de
grandeur annoncés au §7 (Sharpe requis ~1,70) sont recalculés et publiés en
Phase 2 dans `results/nonml_dsr_decomposition_38.md`.
