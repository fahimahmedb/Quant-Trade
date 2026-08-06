# Synthèse consolidée v8 — cycles #290-296, bilan de la campagne macro-externe étendue (#276-296)

Pas un nouveau backtest. Consolide 7 cycles depuis la v7 (#288,
couvrait jusqu'au #289). État au moment de cette synthèse : **91 PASS
niveau 1 sur 301 hypothèses testées**, 0 PASS RENFORCÉ Règle 9 sur
l'ensemble du backlog.

## A. Cycles #290-296 en détail

- **#290 — batterie Règle 9 sur le NFCI (#291)** : 2/5. Coûts ÉCHEC
  dès 5 bps nominal — la batterie tourne conventionnellement sur NDX,
  précisément le seul marché où le NFCI échouait déjà le rendement
  dans le backtest d'origine (cohérent, pas une surprise). Crise OK
  (4/4), stabilité OK (3/4 folds), SPA et DSR ÉCHEC.
- **#291 — indice de stress financier STLFSI4** : FAIL 3/5, RÉFUTE la
  prédiction confirmatoire explicite. Construction identique au NFCI
  (PASS) mais résultat par marché DIFFÉRENT (NDX passe ici, échouait
  pour NFCI ; Composite et S&P 500 échouent ici, passaient pour NFCI)
  — contrairement à la lignée d'estimateurs de volatilité range-based
  (Parkinson/Garman-Klass/Rogers-Satchell, résultats quasi identiques),
  deux indices composites de stress financier de sources différentes
  ne généralisent PAS de façon identique.
- **#292 — prix immobiliers Case-Shiller** : FAIL 1/5. Clôture la
  famille immobilière (HOUST #283 + Case-Shiller #294) à **0 PASS sur
  2** — ni l'activité de construction ni la valorisation des logements
  existants ne sont exploitables.
- **#293 — ventes au détail RSXFS** : FAIL 1/5. Clôture DÉFINITIVEMENT
  le canal "activité économique réelle" à **0 PASS sur 4 constructions
  distinctes** (composite CFNAI, marché du travail ICSA, enquête
  UMCSENT, consommation directe RSXFS) — contraste net et maintenant
  bien établi avec le stress des marchés financiers eux-mêmes qui
  généralise nettement mieux.
- **#294 — prêts commerciaux et industriels BUSLOANS** : FAIL 1/5. 3e
  canal de crédit testé (après spread de marché #199 et défauts de
  consommation #286/#288/#289), résultat distinct des deux autres —
  aucun schéma unifié simple sur l'ensemble du canal crédit.

## B. Bilan de la campagne macro-externe étendue #276-296 (21 cycles)

Cette session a exploré de façon systématique et disciplinée un très
large éventail de catégories de données macro-économiques librement
disponibles (FRED), au-delà des ~200 hypothèses déjà couvertes avant
le #276. Récapitulatif par catégorie :

| Catégorie | Cycles | PASS niveau 1 | Meilleur score Règle 9 |
|---|---|---|---|
| Doublons corrigés (leçon anti-snooping) | #276 (×2) | — | — |
| Calendaire (mi-mois, expiration mensuelle) | #277, #278 | 0/2 | — |
| Régime nouveau (durée drawdown, vitesse taux) | #280, #281 | 0/2 | — |
| Matière première (cuivre, pétrole) | #282, #283 | 0/2 | 3/5 (cuivre, le plus proche du seuil) |
| Cross-marché (avance-retard DAX→US) | #279 | 0/1 | — |
| Stress d'endettement des ménages | #284, #286, #287 | 1/3 (crédit carte) | 3/5 (le meilleur de la session) |
| Immobilier (activité + valorisation) | #283 bis, #292 | 0/2 | — |
| Stress financier composite (2 sources) | #289, #291 | 1/2 (NFCI) | 2/5 (NFCI) |
| Activité économique réelle (4 constructions) | #204/#205/#206 (avant #276) + #293 | 0/4 | — |
| Crédit bancaire aux entreprises | #294 | 0/1 | — |

**+2 PASS niveau 1 nets sur toute la campagne** (89→91), les deux
meilleurs scores Règle 9 de la session (3/5 crédit carte, 2/5 NFCI),
tous deux restant sous les Candidats A et B existants du guide de
déploiement (4/5 chacun) — aucune promotion.

## C. Enseignement transversal principal de la campagne

Le contraste le plus net et le plus reproductible de cette campagne
est celui entre deux familles de signaux macro-externes :

- **Signaux de STRESS DES MARCHÉS FINANCIERS eux-mêmes** (spread de
  crédit BAA10Y #199, défaut de paiement cartes de crédit #286, indice
  composite NFCI #291) : généralisent significativement mieux, avec
  2 PASS niveau 1 sur 3 hypothèses et les 2 meilleurs scores Règle 9
  de la session.
- **Signaux d'ACTIVITÉ ÉCONOMIQUE RÉELLE** (CFNAI, ICSA, UMCSENT,
  RSXFS — 4 constructions distinctes) et **secteurs spécifiques**
  (immobilier, crédit bancaire aux entreprises) : 0 PASS sur 8
  hypothèses combinées.

Ce contraste est cohérent avec une intuition économique simple : les
marchés financiers actions réagissent plus directement et plus vite
aux tensions perçues SUR LES MARCHÉS eux-mêmes (contagion, corrélation
de risque) qu'aux statistiques d'activité réelle publiées avec délai
et souvent déjà partiellement intégrées dans les prix par d'autres
canaux (taux, spreads) au moment de leur publication.

**Limite déclarée honnêtement** : ce contraste repose sur un petit
nombre d'hypothèses (3 stress financier vs 8 activité/secteur) et
n'a pas été soumis lui-même à un test statistique formel — c'est une
observation qualitative utile pour orienter la recherche future, pas
une loi établie.

## D. Trois leçons méthodologiques consolidées (rappel de la v7,
confirmées par les cycles #290-296)

1. Le bug "même barre" (décalage causal par position d'index plutôt
   que par date réelle) continue d'être la source d'erreur la plus
   récurrente de ce backlog.
2. Un bug peut se cacher dans le script d'AUDIT lui-même (#283/HOUST),
   pas seulement dans le backtest — la vérification indépendante n'est
   pas elle-même à l'abri d'erreurs.
3. Une anomalie de taux de coupure élevé sur un marché à fenêtre
   courte (Composite, 2021-2026) n'est PAS automatiquement un bug —
   confirmée à 4 reprises cette session (#286 70,0%, #289 60,9%,
   #294 72,0%, #295 61,2%), toujours expliquée par un contexte macro
   réel (hausse post-COVID des défauts, ralentissement immobilier),
   jamais une erreur de calcul.

## E. Constat de fin de campagne et recommandation

Après 21 cycles consécutifs consacrés à l'exploration macro-externe,
le rythme de découverte de nouvelles idées librement disponibles et
non-redondantes s'est nettement ralenti (0 à 1 idée par cycle sur les
5 derniers cycles de clôture, contre 2-3 en début de campagne). Ce
constat rejoint et renforce celui déjà posé au #257 pour les catégories
prix/stock-selection/calendaire : le champ des données macro FRED
librement disponibles et économiquement motivées apparaît désormais
très largement exploré pour ce backlog.

**Deux voies productives pour la suite**, sans qu'aucune ne soit
imposée par cette synthèse :
1. Une nouvelle catégorie de données apportée par l'utilisateur
   (classification sectorielle, données d'options, volume titre par
   titre à l'échelle complète) — inchangé depuis le #257.
2. Un pivot vers l'Étape D (overlay défensif combinant B+C) définie
   dans `CLAUDE.md`, qui n'a pas encore été construite et pourrait
   directement exploiter les deux meilleurs résultats de cette
   campagne (crédit carte #286, NFCI #291) comme composantes d'un
   mécanisme de risk-management plus large, aux côtés des Candidats A
   et B déjà établis.
