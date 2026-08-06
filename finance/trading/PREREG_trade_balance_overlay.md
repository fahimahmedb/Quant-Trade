# Pré-enregistrement — Balance commerciale US (FRED BOPGSTB)

**Committé AVANT tout calcul.** Cycle #327 du backlog non-ML.

## Hypothèse

La balance commerciale US (FRED `BOPGSTB`, biens et services, mensuelle
depuis 1992) mesure le solde net des échanges avec le reste du monde —
premier canal SECTEUR EXTÉRIEUR jamais exploité dans ce backlog.
Distinct de tous les canaux domestiques déjà testés (taux, crédit,
immobilier, marché du travail, monétaire, fondamental entreprise) et
des prix de matières premières (#283/#284/#326, qui mesurent un PRIX,
pas un FLUX physique net). Un creusement rapide du déficit commercial
est documenté dans la littérature "twin deficits" comme un signal
potentiel de vulnérabilité externe (besoin de financement extérieur
croissant), bien que la littérature reconnaisse aussi une lecture
procyclique (économie domestique forte → plus d'importations). Le
protocole teste ici la lecture défensive (creusement rapide du déficit
= signal de vulnérabilité), cohérente avec la convention "détérioration
= défensif" appliquée à tous les autres signaux de ce backlog.

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `BOPGSTB` (gratuite,
mensuelle, 1992-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/trade_balance_monthly.csv`). La série étant TOUJOURS NÉGATIVE
sur toute la période disponible (déficit commercial persistant depuis
1992), un glissement en LOG (comme pour M2/DGORDER/PAYEMS) est
mathématiquement impossible (log d'un nombre négatif). Adaptation
déclarée ici, AVANT tout calcul : utilisation du NIVEAU BRUT (comme
BAA10Y #199, NFCI #291) avec `expanding_tercile_cut_low` (tercile le
plus BAS = déficit le plus large = défensif) importée directement de
`nonml_m2_growth_overlay_backtest.py` (Règle 7, la fonction opère sur
n'importe quel array numérique, ici appliquée à un niveau plutôt qu'à
une croissance). `CUT=0,5x` défensif, `COST_BPS=5,0`. Décalage de
publication : le communiqué BOPGSTB (Census/BEA) est publié ~5-6
semaines après la fin du mois (délai plus long que la plupart des
séries mensuelles déjà testées, ~1 mois) — décalage conservateur de
DEUX MOIS calendaires avant `ffill`+`shift(1)`, même convention que le
Case-Shiller (#294, qui a un délai de publication similaire).

## Définition (fixée ici, AVANT tout calcul)

- `GateTrade(t)` = 1 si `BOPGSTB_lag(t-1)` (décalée de 2 mois
  calendaires avant `ffill`+`shift(1)`) est dans son tercile expanding
  le plus BAS (déficit commercial le plus large observé à ce jour =
  défavorable), sinon 0.
- **Position** : `CUT=0,5x` si `GateTrade(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — déficit le plus large = défensif — pas
de grille).

## Risque déclaré à l'avance

Comme la quasi-totalité de la famille macro-externe défensive déjà
testée (7 FAIL consécutifs #320-#326), le design purement défensif
sans amplification limite structurellement le gain de rendement même
si le signal identifie un vrai régime de risque. Par ailleurs, la
lecture économique du déficit commercial est AMBIGÜE dans la
littérature (procyclique vs signal de vulnérabilité) — contrairement à
la plupart des signaux déjà testés dont la direction défensive est
plus consensuelle — ce qui pourrait signifier que la direction choisie
ici (déficit large = défensif) n'est pas la bonne lecture pour les
marchés actions US, ou que le lien est simplement trop indirect/lent
pour ce protocole. Rapporté honnêtement dans tous les cas, sans
retuning, quelle que soit la lecture confirmée ou infirmée.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/trade_balance_monthly.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_trade_balance_overlay_result.md`.
