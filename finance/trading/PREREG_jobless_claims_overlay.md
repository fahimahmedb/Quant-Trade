# Pré-enregistrement — Demandes initiales d'allocations chômage (ICSA), overlay défensif

**Committé AVANT tout calcul.** Cycle #204 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

Les demandes initiales d'allocations chômage (FRED `ICSA`, hebdomadaire,
Département du Travail américain) sont l'un des indicateurs du MARCHÉ DU
TRAVAIL les plus réactifs en temps réel — une hausse tendancielle
signale une détérioration de l'emploi, documentée comme un indicateur
avancé de récession. Distinct de TOUS les signaux déjà testés dans ce
backlog : angle MARCHÉ DU TRAVAIL (pas taux/crédit/inflation/liquidité/
corrélation/volatilité déjà couverts), et **fréquence HEBDOMADAIRE
jamais utilisée** (entre le quotidien des séries de taux/vol et le
mensuel de M2/DE10Y).

## 2. Donnée (nouvelle, à récupérer — fetch réseau, traitement de fréquence et de délai de publication)

Série FRED `ICSA` (Initial Claims, hebdomadaire, historique complet
1967-2026 confirmé par fetch) — gratuite. **Convention de publication**
(déclarée avant calcul) : chaque observation datée au samedi de fin de
semaine (ex. "2026-07-25") est publiée le jeudi SUIVANT par le
Département du Travail (~5 jours calendaires plus tard). Pour rester
conservateur sans introduire de fuite, la date de disponibilité causale
est décalée de **7 jours calendaires complets** (`pd.Timedelta(days=7)`)
avant le `ffill` — une semaine de marge, délibérément plus prudente que
le délai réel de 5 jours, pour absorber toute imprécision de convention
de date. Sauvegardée dans `data/icsa_weekly.csv`, aucune modification.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Lissage : moyenne glissante **4 semaines** (convention standard pour
  cette série bruitée, largement utilisée par les analystes du marché
  du travail — pas une fenêtre choisie pour ce backlog, un standard
  externe).
- `ClaimsYoY(t) = log(ClaimsMA4(t) / ClaimsMA4(t-52))` (glissement
  annuel, 52 semaines — même logique que le glissement 12 mois du #203,
  évite de comparer des niveaux bruts sur 60 ans de croissance
  démographique de la population active).
- Alignement causal : décalage de 7 jours (§2) + `ffill` (calendrier du
  marché cible) + `shift(1)` (jour de bourse) — cohérent avec
  `load_rate_lag()` déjà utilisée aux #175/#178/#186/#187/#191/#192/
  #193/#195/#196/#197/#198/#199/#200/#202/#203, Règle 7.
- Seuil : **tercile EXPANDING** de `ClaimsYoY_lag(t)` (technique
  établie, #169/#177/#183/#191/#192/#193/#195/#196/#197/#198/#199/#200/
  #202/#203).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `ClaimsYoY_lag(t)` est dans son tercile expanding le PLUS HAUT
  (demandes de chômage en hausse marquée sur un an — détérioration du
  marché du travail), `1,0x` sinon. **Jamais de levier**. Coûts 5 bps.

## 5. Critère de succès (RENFORCÉ, figé — même seuil que les cycles #175-#203)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un lissage standard
externe, un critère multi-marché figé, aucun balayage).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme pour la grande majorité des signaux de NIVEAU/RÉGIME
   macro-externes déjà testés (13 hypothèses, 2 PASS niveau 1
   seulement), la probabilité de base d'un FAIL reste élevée.
2. Les demandes de chômage sont documentées comme un indicateur
   COÏNCIDENT à RETARD (la détérioration du marché du travail suit
   souvent le début d'une correction de marché plutôt que de la
   précéder nettement) — le signal pourrait arriver trop tard.
3. Comme aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/#198/
   #199/#202/#203, un design purement défensif sans levier
   compensatoire limite structurellement le rendement total.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
