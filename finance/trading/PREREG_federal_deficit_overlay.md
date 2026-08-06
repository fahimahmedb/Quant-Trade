# Pré-enregistrement — Déficit budgétaire fédéral US (FRED MTSDS133FMS)

**Committé AVANT tout calcul.** Cycle #331 du backlog non-ML.

## Hypothèse

Le solde budgétaire fédéral mensuel US (FRED `MTSDS133FMS`, recettes
moins dépenses, mensuel depuis 1980) mesure directement la POLITIQUE
FISCALE — premier canal FISCAL jamais exploité dans ce backlog,
distinct du secteur extérieur (#329, balance commerciale, FAIL) et du
canal monétaire (#203/#320, masse monétaire, clos 0/2). Un creusement
rapide et soutenu du déficit fédéral (au-delà de l'effet saisonnier
normal des dates de paiement d'impôts) peut refléter soit une réponse
contracyclique délibérée à un ralentissement économique déjà en cours
(dépenses de relance, stabilisateurs automatiques), soit une source
future de pression sur les taux/l'inflation — les deux lectures
suggèrent un lien avec le RÉGIME macroéconomique plutôt qu'une causalité
simple. Le protocole teste ici la lecture défensive standard de ce
backlog (détérioration = signal défavorable), cohérente avec la
convention appliquée à tous les autres signaux fiscaux/externes déjà
testés (#329 balance commerciale).

## Adaptation technique : réutilisation stricte, Règle 7

Nouvelle donnée à récupérer : série FRED `MTSDS133FMS` (gratuite,
mensuelle, 1980-2026, disponibilité confirmée par fetch le 06/08/2026,
`data/federal_deficit_monthly.csv`). **Adaptation déclarée ici, AVANT
tout calcul** : la série BRUTE mensuelle est EXTRÊMEMENT volatile
(inspection directe confirme des mois EXCÉDENTAIRES ponctuels — avril,
juin, septembre — dus aux dates légales de paiement des impôts
trimestriels/annuels), rendant un tercile sur la valeur mensuelle brute
non-interprétable comme signal de régime. Adaptation : somme glissante
sur 12 MOIS (`ROLLING_MONTHS=12`, déficit cumulé glissant sur une année
fiscale complète, lissant l'effet saisonnier) AVANT tercile expanding,
construction nouvelle mais mécaniquement simple (`pd.Series.rolling(12).sum()`,
aucun paramètre libre au-delà du choix économiquement motivé de 12 mois
= 1 cycle fiscal complet). `expanding_tercile_cut_low` (tercile le plus
BAS = déficit cumulé le plus large = défensif, même famille que #203/
#323/#326/#329/#331/#332) importée directement de
`nonml_m2_growth_overlay_backtest.py` (Règle 7). `CUT=0,5x` défensif,
`COST_BPS=5,0`, décalage de publication d'UN MOIS calendaire avant
`ffill`+`shift(1)` (le Monthly Treasury Statement est publié ~2-3
semaines après la fin du mois — marge conservatrice, même convention
que #195/#203/#323/#324/#326/#328/#331/#332).

## Définition (fixée ici, AVANT tout calcul)

- `DeficitTTM(t)` = somme glissante sur 12 mois de `MTSDS133FMS`.
- `GateDeficit(t)` = 1 si `DeficitTTM_lag(t-1)` (décalée d'un mois
  calendaire avant `ffill`+`shift(1)`) est dans son tercile expanding
  le plus BAS (déficit cumulé sur 12 mois le plus large observé à ce
  jour = défavorable), sinon 0.
- **Position** : `CUT=0,5x` si `GateDeficit(t)`, `1,0x` sinon.

## Univers et période

Les 5 échantillons déjà figés du projet : Composite, NDX-100, Russell
2000, S&P 500, DAX (`data/*.txt`), aucune nouvelle donnée de prix.

## Critère de succès (pré-enregistré, règle renforcée habituelle)

L'overlay bat Buy & Hold en Sharpe annualisé **ET** en rendement total
net de coûts sur **au moins 4 des 5 marchés** (coûts 5 bps). n_trials=1
(une seule direction testée — déficit cumulé le plus large = défensif —
pas de grille).

## Risque déclaré à l'avance

Comme la quasi-totalité de la famille macro-externe défensive déjà
testée (11 FAIL consécutifs #320-#330, 1 seul PASS net sur toute la
session, #200), le design purement défensif sans amplification limite
structurellement le gain de rendement même si le signal identifie un
vrai régime de risque. Par ailleurs, comme pour le #329 (balance
commerciale, même schéma "twin deficits"), le déficit fédéral US
présente une tendance de creusement séculaire de long terme
(particulièrement marquée depuis 2020), ce qui pourrait ancrer le
seuil expanding sur des valeurs anciennes moins négatives, rendant la
porte structurellement de plus en plus active en fin d'échantillon —
même risque de tendance que #327/#328/#331, à vérifier explicitement
par audit dédié plutôt que supposé. Rapporté honnêtement dans tous les
cas, sans retuning.

## Anti-cheat

Ce fichier committé avant tout calcul (le fetch de
`data/federal_deficit_monthly.csv` est une simple vérification de
disponibilité, aucun résultat n'existe avant ce commit). Sortie :
`results/nonml_federal_deficit_overlay_result.md`.
