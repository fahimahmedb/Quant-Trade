# Pré-enregistrement — Momentum de l'ETF obligataire Trésor long terme (TLT), overlay défensif

**Committé AVANT tout calcul.** Cycle #352 du backlog non-ML.

## 1. Déclaration explicite (Règle 2, transparence) — pourquoi TLT plutôt que SLV, et pourquoi ce n'est pas redondant avec l'or

Trois pistes avaient été identifiées et vérifiées disponibles au #348
(après la découverte de Yahoo Finance comme source fonctionnelle) :
argent métal (SLV), obligataire Trésor long terme (TLT), rotation
sectorielle (XLK/XLP). Ce cycle tranche pour **TLT**, écartant SLV
pour ce cycle (mécanisme quasi-identique à l'or — métal précieux —
déjà testé et FAIL, redondance trop proche sans nouvelle hypothèse) et
XLK/XLP (catégorie différente, à traiter séparément si retenue).

**TLT n'est PAS redondant avec l'or (#348, FAIL 3/5)** : deux
mécanismes économiques distincts de flight-to-quality.
- L'or (#348) est un actif SANS RENDEMENT, valeur refuge historique
  contre le risque monétaire/géopolitique, décorrélé des taux
  d'intérêt.
- TLT (iShares 20+ Year Treasury Bond ETF) est un actif à REVENU FIXE :
  sa hausse reflète une BAISSE DES TAUX LONGS, documentée depuis les
  années 2000 comme le canal de flight-to-quality DOMINANT des marchés
  actions US (corrélation actions-obligations structurellement
  négative en régime de risque, ex. 2008, mars 2020) — un mécanisme de
  transmission entièrement différent (politique monétaire/croissance
  anticipée, pas prime de risque géopolitique/monétaire pure).

**Également distinct du proxy obligataire déjà utilisé au #134**
(diversification défensive) : le #134 utilisait une **approximation en
forme fermée** du rendement obligataire à partir du taux nominal
`DGS10` (formule de duration modifiée, aucune donnée de prix réelle) —
ici, **TLT est le prix RÉEL d'un ETF négocié en bourse**, reflétant
les flux de marché effectifs (offre/demande, primes de risque
réalisées), pas un modèle.

## 2. Données

**Nouvelle donnée** : ETF `TLT` (iShares 20+ Year Treasury Bond ETF)
via l'API publique Yahoo Finance (même mécanisme de fetch que #348,
confirmé fonctionnel), gratuite, quotidienne depuis le 30/07/2002,
disponibilité déjà vérifiée par fetch de test (HTTP 200, 6043 valeurs
jusqu'au 06/08/2026).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe/matières
premières (jauge de risque global via les marchés obligataires US,
appliquée uniformément).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier — STRICTEMENT IDENTIQUE au #348)

Construction IDENTIQUE au #348 (Règle 7), seule la série change :

- `TLTmom(t) = log(TLT(t)/TLT(t-21))` (**RET_WINDOW=21 réutilisé à
  l'identique** des #198/#283/#284/#326/#344/#346/#348).
- Alignement causal `ffill+shift(1)` (Règle 7 standard).
- `position(t) = 0,5x` si `TLTmom_lag(t)` est dans son tercile
  expanding le **PLUS HAUT** (hausse marquée de TLT = baisse des taux
  longs = flight-to-quality, **même direction que l'or #348**,
  déclarée ici par cohérence économique — un TLT en hausse signale un
  régime de risque actions, pas une opportunité), `1,0x` sinon.
  **Jamais de levier**. Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une fenêtre réutilisée, une direction
déclarée à l'avance par cohérence économique, aucun balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : le canal actions-obligations est
documenté comme le mécanisme de flight-to-quality le plus robuste de
la littérature (plus robuste que l'or selon une partie de la
littérature macro-financière post-2000), ce qui pourrait suggérer un
profil supérieur à l'or (#348, FAIL 3/5, 2e meilleur score matières
premières). Mais la famille matières premières/valeur-refuge de ce
backlog est 0/4 à ce stade (pétrole, cuivre, gaz, or) — un design
purement défensif sans levier compensatoire a systématiquement limité
le rendement total dans ce backlog, quel que soit l'actif sous-jacent.
Résultat rapporté tel quel, sans retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme le reste de la famille macro-externe défensive, un design
   purement défensif sans levier compensatoire limite structurellement
   le rendement total.
2. La corrélation actions-obligations n'est PAS stable dans le temps
   (régime de corrélation POSITIVE documenté en 2022, hausse des taux
   et baisse des actions SIMULTANÉES) — un signal supposé stable sur
   toute la fenêtre pourrait être structurellement non stationnaire,
   limite reconnue à l'avance (distincte d'un bug).
3. Le tracking d'un ETF (frais de gestion ~0,15%/an, effets de
   convexité obligataire) introduit un léger écart au taux nominal
   pur, traité comme un proxy acceptable (même limite déjà reconnue
   pour GLD au #348).
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_treasury_bond_etf_overlay_backtest.py`,
`scripts/nonml_treasury_bond_etf_overlay_audit.py`,
`results/nonml_treasury_bond_etf_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
