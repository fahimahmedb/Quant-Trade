# Pré-enregistrement — Vérification point-in-time des candidats volume (#258, #261)

**Committé AVANT tout fetch et tout calcul.** Cycle #264 du backlog
non-ML.

## Contexte et motivation

Les deux candidats de la catégorie volume (#258 momentum+turnover,
#261 Amihud illiquidité) sont construits sur `data/pead/prices/*.json`
+ `data/pead/volume/*.json` — l'univers de 99 tickers est la liste des
membres **actuels (2026)** du NDX-100 (`ndx100_constituents.json`),
appliquée à la fenêtre 2021-2026 pour #258 et 2021-2027 pour #261.
Même défaut structurel que le #38 original (corrigé au #163 via
l'univers point-in-time réel) : les titres retirés de l'indice entre
leur date de sortie et 2026 ne figurent PAS dans l'univers testé, alors
qu'ils y appartenaient réellement à l'époque — biais du survivant, ici
sur une fenêtre plus courte (5-6 ans, contre 55 ans pour le #162/#163),
donc probablement moins sévère mais jamais mesuré pour ces deux
candidats.

L'infrastructure existe déjà : `data/ndx100_history/` +
`scripts/ndx100_membership.py::tickers_as_of_date` (composition
historique, vendorée au #163) et `data/pead/prices_pit/` (214 tickers,
prix 2015-2026, déjà récupéré au #163). **Il manque le VOLUME pour ce
panneau PIT** — jamais récupéré, à faire dans ce cycle (même source
Yahoo déjà validée aux #163/#258).

## Méthode

1. Fetch du volume pour les 214 tickers de `data/pead/prices_pit/`
   (script dédié `fetch_volume_data_pit.py`, ne modifie ni
   `fetch_volume_data.py` ni les données déjà committées).
2. Ré-exécution de #258 (momentum+turnover) et #261 (Amihud illiquidité)
   sur l'univers point-in-time réel (`tickers_as_of_date`, ancrage
   2015-01-01 comme au #163 — pas 2021, pour bénéficier du même
   allongement d'échantillon qui avait été décisif pour le #38 au #163),
   construction causale dès le départ (`lag_one_day`, aucun changement
   par rapport aux scripts #258/#261 sinon le filtre d'univers).
3. Référence identique à chaque backtest d'origine (momentum 12-1 seul
   pour #258 ; Buy&Hold équipondéré pour #261), reconstruite sur le même
   univers PIT pour une comparaison cohérente.

## Résultat attendu (aucune prédiction chiffrée)

Par analogie avec le #163 (l'edge du #38 avait SURVÉCU à la correction
PIT, contrairement à l'intuition initiale), aucun sens de variation
n'est anticipé — le #163 a explicitement réfuté l'hypothèse "l'edge est
un artefact tautologique du survivant". Rapporté tel quel.

## Risques déclarés à l'avance

1. Le fetch réseau (214 tickers) peut échouer partiellement — tout
   ticker sans volume exploitable sera exclu et documenté, jamais
   ignoré silencieusement.
2. L'échantillon PIT remonte à 2015, mais le volume Yahoo peut être
   incomplet ou absent pour des tickers radiés depuis longtemps
   (36 des 214 déjà signalés sans série de prix au #163) — même
   limite reconnue, pas une nouvelle découverte.
3. Ce cycle traite les DEUX candidats volume dans un seul PREREG (comme
   le #252 avait groupé #14+#38) car ils partagent strictement la même
   nouvelle donnée à récupérer et la même méthode de correction —
   pas une manière de diluer le compte d'hypothèses (chacun reste compté
   séparément dans le tracker).

## Anti-cheat

Ce fichier committé et poussé AVANT tout fetch et tout calcul. Sorties
attendues : `results/nonml_momentum_turnover_doublesort_pit_universe.md`
et `results/nonml_amihud_illiquidity_tilt_pit_universe.md` (nouveaux
fichiers, ne modifient pas les résultats d'origine #258/#261).
