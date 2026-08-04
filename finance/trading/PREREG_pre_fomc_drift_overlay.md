# Pré-enregistrement — Effet pré-FOMC drift (Lucca & Moench 2015), overlay levé

**Committé AVANT tout calcul.** Cycle #171 du backlog non-ML. Sous la
**Règle 9** de `PROTOCOLE_ANTI_SNOOPING.md`.

## 1. Hypothèse et sourcing des dates (AVANT tout calcul, Règle 2)

Lucca & Moench (2015, *The Pre-FOMC Announcement Drift*, Journal of
Finance) documentent un rendement anormalement positif du S&P 500 dans
les ~24h précédant l'annonce de décision de taux de la Fed (14h,
2e jour de chaque réunion FOMC programmée). Jamais testé dans ce backlog
— distinct de tous les effets calendaires déjà couverts (ToM #8, Halloween
#20, jour de semaine #3, jours fériés #7/#27).

**Les dates ne sont PAS détectables depuis les données de prix elles-mêmes**
(contrairement aux effets calendaires déjà testés, ex. jour-du-mois) — elles
proviennent d'un événement institutionnel externe. Sourcées AVANT ce
document depuis la page officielle de la Fed, calendriers annuels
`federalreserve.gov/monetarypolicy/fomchistorical<année>.htm` (2015-2020)
et `federalreserve.gov/monetarypolicy/fomccalendars.htm` (2021-2026),
consultées le 01/08/2026. **Seules les réunions PROGRAMMÉES à échéance
fixe (8 par an, annonce le 2e jour) sont retenues** — exclusion explicite
et déclarée des réunions d'urgence non programmées et des "notation
votes" (pas d'annonce publique associée au même mécanisme d'anticipation) :
2019 : conf. call du 4 octobre (non programmée) exclue. 2020 : réunions
d'urgence des 2 et 15 mars exclues, réunion des 17-18 mars ANNULÉE exclue,
notation votes des 19/23/31 mars et du 27 août exclues. 2025 : notation
vote du 22 août exclu.

**Liste complète des dates d'annonce retenues** (2e jour de chaque réunion
programmée, format JJ/MM/AAAA) :

2015 : 28/01, 18/03, 29/04, 17/06, 29/07, 17/09, 28/10, 16/12
2016 : 27/01, 16/03, 27/04, 15/06, 27/07, 21/09, 02/11, 14/12
2017 : 01/02, 15/03, 03/05, 14/06, 26/07, 20/09, 01/11, 13/12
2018 : 31/01, 21/03, 02/05, 13/06, 01/08, 26/09, 08/11, 19/12
2019 : 30/01, 20/03, 01/05, 19/06, 31/07, 18/09, 30/10, 11/12
2020 : 29/01, 29/04, 10/06, 29/07, 16/09, 05/11, 16/12
2021 : 27/01, 17/03, 28/04, 16/06, 28/07, 22/09, 03/11, 15/12
2022 : 26/01, 16/03, 04/05, 15/06, 27/07, 21/09, 02/11, 14/12
2023 : 01/02, 22/03, 03/05, 14/06, 26/07, 20/09, 01/11, 13/12
2024 : 31/01, 20/03, 01/05, 12/06, 31/07, 18/09, 07/11, 18/12
2025 : 29/01, 19/03, 07/05, 18/06, 30/07, 17/09, 29/10, 10/12
2026 (jusqu'à la fin des données disponibles, 13/07/2026) : 28/01, 18/03, 29/04

Total : 95 dates d'annonce (2026 partiel, réunions ultérieures hors
couverture des données de prix). Cette liste est figée dans
`scripts/nonml_pre_fomc_drift_overlay_backtest.py` (constante `FOMC_DATES`)
et ne sera PAS modifiée après avoir vu un résultat.

## 2. Marchés testés (figés, mêmes 5 marchés que tous les cycles calendaires)

Composite, NDX, Russell 2000, S&P 500, DAX — cohérent avec le protocole
établi pour tous les effets calendaires du backlog (#2, #3, #6, #7, #8,
#20, #26, #27…). **Prudence déclarée à l'avance** : le mécanisme de
Lucca & Moench est documenté sur le S&P 500 (marché américain) ; son
application à NDX/Russell 2000 (mêmes heures de marché) est directe,
mais DAX (fuseau horaire européen, décision Fed annoncée après la
clôture allemande) teste plutôt un effet de SPILLOVER/anticipation
qu'une réplique directe — signalé, pas un obstacle au test (la
littérature documente aussi des effets internationaux de la politique
monétaire US).

## 3. Mécanisme (figé, design overlay — cohérent avec la leçon du #7 vs #8 :
un overlay qui reste investi 1.0x en permanence bat toujours un design
flat-hors-fenêtre)

```
position(t) = 2.0x   si t est le jour de bourse PRÉCÉDANT immédiatement
                       une date d'annonce FOMC de la liste ci-dessus
                       (dans le calendrier de bourse propre à CHAQUE marché)
            = 1.0x   sinon
```

- Alignement calendaire **data-driven par marché** : pour chaque date
  d'annonce, le jour de décision est le dernier jour de bourse
  STRICTEMENT ANTÉRIEUR à cette date dans l'index de dates du marché
  testé (pas une correspondance calendaire naïve — gère nativement les
  jours fériés/weekends propres à chaque marché).
- CAP=2.0x réutilisé tel quel (valeur standard de tout le backlog),
  aucun paramètre de fenêtre à choisir (fenêtre = exactement 1 jour de
  bourse, celui qui précède l'annonce — le choix le plus simple et le
  plus proche de la définition originale des ~24h).
- Coûts 5 bps.

## 4. Critère de succès (RENFORCÉ, figé — même seuil que tous les cycles calendaires)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (une liste de dates figée avant tout calcul, un design
overlay, un critère multi-marché, aucun balayage).

## 5. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le nombre de jours investis à 2x est faible (~95 jours sur plusieurs
   milliers de séances selon le marché, <2% du temps) — un edge réel
   mais de faible ampleur pourrait ne pas suffire à battre BH net de
   coûts, comme observé pour d'autres effets calendaires ponctuels
   (#2 ToM, #26 triple witching, #27 jours fériés).
2. Le proxy quotidien (rendement close-à-close du jour PRÉCÉDANT
   l'annonce) est une approximation du signal intraday original
   (~24h avant 14h) — l'effet pourrait être dilué ou déphasé par cette
   granularité journalière.
3. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
