# Pré-enregistrement — Momentum 12-1 (#73) + double-tri par volume/turnover (nouvelle catégorie de données)

**Committé AVANT toute récupération de nouvelle donnée et AVANT tout
calcul.** Cycle #258 du backlog non-ML.

## Motivation et nouveauté

Après le constat de recherche d'idées fraîches du cycle #257 (six
catégories déjà couvertes de façon dense — calendaire, momentum/
reversal/qualité, largeur de marché, dispersion/corrélation, macro
externe FRED, volatilité de second ordre), la seule catégorie de données
réellement absente identifiée était le **volume**. Vérification directe
(avant tout engagement) : `data/pead/prices/*.json` ne contient que
`{"ts", "close"}` — le champ `volume` n'a jamais été extrait, bien que
la même API Yahoo Finance déjà utilisée et validée dans ce projet
(`scripts/pead_fetch_data.py::fetch_prices`, source de tous les prix
titre par titre déjà exploités aux #4/#14/#15/#73/#78/#79/#82/#84 etc.)
le fournisse nativement (`chart.result[0].indicators.quote[0].volume`,
vérifié par un appel de test avant ce document).

**Hypothèse académique motivante** (Lee & Swaminathan 2000, "Price
Momentum and Trading Volume", *Journal of Finance*) : les gagnants
passés à FAIBLE volume de transaction (turnover) surperforment les
gagnants passés à FORT volume — interprété comme un proxy de
reconnaissance/couverture des investisseurs (les titres peu échangés
intègrent l'information plus lentement, prolongeant la dérive de
momentum). Signal jamais testé dans ce backlog — orthogonal à tous les
signaux prix/rendement/macro déjà couverts.

## Univers et données

- Prix déjà en local (`data/pead/prices/*.json`, univers NDX-100,
  ~2021-2026, mêmes 99 tickers que #73/#79/#82).
- **Nouvelle donnée à récupérer** : volume quotidien pour les mêmes
  tickers et la même période, via `query2.finance.yahoo.com/v8/finance/
  chart/<ticker>` (champ `volume`, même endpoint que les prix, aucun
  nouveau risque de source). Stocké dans `data/pead/volume/<ticker>.json`
  (`{"ts":[...], "volume":[...]}`), script séparé du fetch de prix
  existant pour ne jamais modifier `pead_fetch_data.py` (Règle : ne pas
  toucher aux données déjà validées).
- **Limite déclarée à l'avance** : le volume EN ACTIONS (pas le nombre
  de titres en circulation) sert de proxy de turnover via le volume EN
  DOLLARS (`close × volume`), pas un vrai taux de rotation
  (`volume / actions en circulation`, donnée non disponible gratuitement
  ici) — biais de taille de capitalisation possible (les méga-caps ont un
  volume $ élevé indépendamment du turnover réel), signalé explicitement
  et non corrigé après coup si le résultat est décevant.

## Méthode (double tri, réutilisation stricte de #73 pour la jambe momentum)

1. **Premier tri (momentum, paramètres identiques à #73, Règle 7)** :
   `momentum(t) = close(t-SKIP)/close(t-LOOKBACK) - 1` avec
   `SKIP=21, LOOKBACK=252`, tercile supérieur (33/99 titres).
2. **Second tri (turnover, nouveau)** : parmi ce tercile momentum,
   calcul du volume moyen en dollars sur une fenêtre glissante
   `TURNOVER_WINDOW=126` séances (≈6 mois, cohérent avec la
   méthodologie originale de Lee & Swaminathan qui utilise un turnover
   sur plusieurs mois), **décalé d'un jour avant usage** (convention
   causale `lag_one_day`, appliquée dès la construction — pas une
   correction après coup comme aux cycles #252-257) pour éviter toute
   fuite « même barre ». Sélection du **tiers à turnover le plus FAIBLE**
   parmi le tercile momentum (≈11 titres), poids égaux.
3. Rebalancement mensuel (`REBAL_EVERY=21`, identique à #73/#79/#82).
4. Coûts 5 bps aller-retour (Règle 7).

## Référence et critère de succès (renforcé, identique à #79)

Référence = **Momentum 12-1 seul (#73), PAS Buy&Hold** (même convention
que le double-tri #79 momentum+lowvol). PASS si Sharpe portefeuille
double-trié > Sharpe #73 ET rendement total net > rendement #73.

## Risques déclarés à l'avance

1. Le fetch réseau du volume peut échouer partiellement (tickers
   radiés/renommés) — tout ticker sans volume exploitable sur la période
   sera exclu de l'univers éligible, documenté dans le résultat, jamais
   ignoré silencieusement.
2. Le proxy volume-dollars (pas turnover vrai) peut ne capturer qu'un
   effet de taille déjà testé indirectement ailleurs (ex. #123 proxy
   petite capitalisation intra-NDX-100) plutôt que l'effet de
   reconnaissance des investisseurs de Lee & Swaminathan — limite
   méthodologique reconnue à l'avance, pas un prétexte a posteriori pour
   retenter avec un vrai turnover si le résultat est FAIL.
3. Par précédent (#79, double-tri momentum+lowvol, FAIL — le second tri
   dilue l'edge de #73), il n'y a AUCUNE attente directionnelle
   garantie ; ce cycle rapportera le résultat tel quel.

## Anti-cheat

Ce fichier committé et poussé AVANT tout fetch de volume et tout calcul.
Sortie attendue : `results/nonml_momentum_turnover_doublesort_result.md`.
Script : `scripts/nonml_momentum_turnover_doublesort_backtest.py`.
`causal=True` appliqué dès la construction initiale (pas une correction
ultérieure) — leçon directement tirée du balayage #252-257.
