# Pré-enregistrement — Bilan de la Réserve fédérale (WALCL, croissance), overlay défensif

**Committé AVANT tout calcul.** Cycle #347 du backlog non-ML.

## 1. Déclaration explicite de la tension avec le canal monétaire déjà clos (Règle 2, transparence)

Le canal "monétaire" est déjà clos à 0 PASS sur 2 constructions
(croissance M2 #203, vitesse de circulation M2V #320, toutes deux
FAIL). Tester une 3e variante liée à la politique monétaire comporte
un risque de sur-exploitation d'un canal déjà négatif.

**Décision prise ici, avant tout calcul** : ce cycle teste le bilan de
la Réserve fédérale (`WALCL`, taille totale des actifs détenus par la
Fed) car il mesure un mécanisme économique **DISTINCT** de M2/M2V :
M2 et M2V mesurent la masse monétaire DÉTENUE PAR LE PUBLIC (optique
monétariste, quantité de monnaie en circulation) et sa vitesse de
circulation, tandis que WALCL mesure directement la **taille du bilan
de la banque centrale elle-même** — l'instrument opérationnel direct
des programmes d'assouplissement quantitatif (QE) et de resserrement
quantitatif (QT), qui injectent ou retirent mécaniquement des
liquidités du système financier par achat/vente d'actifs. La
littérature documente ce canal comme distinct du canal monétariste
classique (ex. les épisodes QE 2020-2021 et QT 2022 sont explicitement
cités comme moteurs de performance des actifs risqués, indépendamment
des statistiques M2 elles-mêmes qui réagissent avec un délai et un
mécanisme de transmission différents).

**Engagement pris à l'avance, quel que soit le résultat** : **ce cycle
CLÔT le canal monétaire à 3 constructions, sans extension
supplémentaire sans nouvelle hypothèse économique clairement
distincte** — même discipline de bornage que celle déjà appliquée à
la sous-famille corrélation (#196), au canal inflation (#343), à la
classe d'actif crypto (#346) et à la famille VIX-dérivés (déclarée
close après le #346).

## 2. Données

**Nouvelle donnée à récupérer** : série FRED `WALCL` (Fed Total
Assets, rapport hebdomadaire H.4.1), gratuite, hebdomadaire depuis
décembre 2002, disponibilité déjà vérifiée par fetch de test (HTTP
200, 1234 valeurs jusqu'au 05/08/2026). **Non monotone** — contrairement
au déficit fédéral (#331) ou à la position extérieure nette (candidat
écarté au #343), le WALCL présente une vraie variation cyclique (QE
2008-2014/2020-2021, plateau, QT 2022-2026), limitant le risque de
motif "tendance séculaire pure" déjà documenté sur d'autres candidats
à ce backlog.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
justification que le reste de la famille macro-externe (politique de
la Fed comme jauge de liquidité globale, effets de contagion
documentés sur les marchés non-US via les taux de change et les flux
de capitaux).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- `WALCLGrowth(t) = log(WALCL(t)/WALCL(t-52))` (croissance sur 52
  semaines, **YOY_WEEKS=52 réutilisé par analogie directe avec
  YOY_MONTHS=12 du #203**, Règle 7 — même logique de glissement annuel
  appliquée à une fréquence hebdomadaire).
- Décalage de publication de 7 jours (**PUBLICATION_LAG_DAYS=7 réutilisé
  à l'identique du #204/#291**, même rapport hebdomadaire de la Fed,
  Règle 7).
- Seuil : **tercile EXPANDING** de `WALCLGrowth_lag(t)`.
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `WALCLGrowth_lag(t)` est dans son tercile expanding le PLUS BAS
  (contraction du bilan de la Fed la plus marquée = régime de QT
  actif = resserrement de liquidité), `1,0x` sinon (**direction
  réutilisée à l'identique du #203**, croissance basse = défensif).
  **Jamais de levier**. Coûts 5 bps (`COST_BPS` réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une fenêtre de glissement annuel
réutilisée par analogie directe, un critère multi-marché figé, aucun
balayage).

## 6. Prédiction déclarée à l'avance (Règle 2)

**Non tranchée à l'avance** : le mécanisme économique (QE/QT comme
moteur direct de liquidité) est solidement documenté et distinct du
canal monétariste classique déjà FAIL (M2/M2V), mais appartient à la
même famille large "politique monétaire" dont aucune variante n'a
encore réussi dans ce backlog. Résultat rapporté tel quel, sans
retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Le bilan de la Fed a connu très peu de cycles complets QE/QT sur
   l'historique disponible (2008-2009, 2020-2021 QE ; 2013 "taper",
   2018-2019 QT, 2022-2026 QT) — nombre d'épisodes limité, risque de
   sur-influence d'un petit nombre de régimes sur le tercile expanding.
2. Comme le reste de la famille macro-externe défensive, un design
   purement défensif sans levier compensatoire limite structurellement
   le rendement total.
3. Le marché anticipe généralement les décisions de politique
   monétaire (forward guidance) — le bilan RÉALISÉ (pas anticipé)
   pourrait réagir avec un délai trop long pour un mécanisme statique
   sans anticipation, risque similaire à celui documenté pour
   l'inversion de courbe des taux (#187).
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`scripts/nonml_fed_balance_sheet_overlay_backtest.py`,
`scripts/nonml_fed_balance_sheet_overlay_audit.py`,
`results/nonml_fed_balance_sheet_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
