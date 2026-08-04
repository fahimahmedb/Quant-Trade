# Pré-enregistrement — Indice d'activité nationale de la Fed de Chicago (CFNAI), overlay défensif

**Committé AVANT tout calcul.** Cycle #206 du backlog non-ML.

## 1. Hypothèse et lien avec les cycles existants

Le Chicago Fed National Activity Index (FRED `CFNAI`, mensuel) agrège
85 séries mensuelles couvrant production, emploi, consommation/ventes,
logement — c'est un indicateur COMPOSITE, utilisé par la Fed elle-même
comme jauge de probabilité de récession en temps réel. Distinct de tous
les signaux ISOLÉS déjà testés (demandes de chômage #204 = emploi seul,
sentiment #205 = perception seule, M2 #203 = liquidité seule, spread de
crédit #199 = risque de défaut seul) : ici le signal résume PLUSIEURS
dimensions économiques simultanément. Construit pour osciller autour de
0 (0 = croissance tendancielle, négatif = croissance sous la tendance) —
un CFNAI durablement sous -0,7 est le seuil documenté par la Fed de
Chicago elle-même comme signalant historiquement une récession en cours
ou imminente.

## 2. Donnée (nouvelle, à récupérer — fetch réseau, traitement mensuel)

Série FRED `CFNAI` (mensuelle, historique complet 1967-2026 confirmé
par fetch) — gratuite. **Traitement causal** : le CFNAI est publié
environ 3-4 semaines après la fin du mois qu'il résume (délai de
compilation des 85 composantes) — même traitement conservateur que les
#195/#203/#204/#205 (décalage d'un mois calendaire complet avant
`ffill`, puis `shift(1)` jour de bourse), déclaré avant tout calcul.
Sauvegardée dans `data/cfnai_monthly.csv`, aucune modification.

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Alignement causal : décalage d'un mois + `ffill` + `shift(1)` (§2),
  cohérent avec le traitement mensuel déjà utilisé aux #175/#178/#186/
  #187/#191/#192/#193/#195/#196/#197/#198/#199/#200/#202/#203/#204/#205,
  Règle 7.
- Seuil : **tercile EXPANDING** de `CFNAI_lag(t)` (technique établie,
  #169/#177/#183/#191/#192/#193/#195/#196/#197/#198/#199/#200/#202/
  #203/#204/#205).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `CFNAI_lag(t)` est dans son tercile expanding le PLUS BAS (activité
  économique la plus faible/négative — risque de ralentissement ou
  récession, **direction analogue au #203 M2**, pas au #199/#200/#202/
  #205 qui coupaient sur le tercile le plus HAUT d'un indicateur de
  risque), `1,0x` sinon. **Jamais de levier**. Coûts 5 bps.

## 5. Critère de succès (RENFORCÉ, figé — même seuil que les cycles #175-#205)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, un plancher réutilisé, un critère
multi-marché figé, aucun balayage).

## 6. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. Comme pour la grande majorité des signaux macro-externes déjà testés
   (15 hypothèses, 2 PASS niveau 1 seulement, aucun PASS RENFORCÉ), la
   probabilité de base d'un FAIL reste élevée.
2. Le fait d'être un indicateur COMPOSITE ne garantit pas qu'il
   généralise mieux qu'un indicateur isolé — les 15 hypothèses
   précédentes de cette famille (rates/crédit/inflation/dollar/
   liquidité/corrélation/sentiment/emploi) ont presque toutes échoué
   malgré des motivations économiques individuellement solides.
3. Comme aux #175/#178/#186/#187/#191/#192/#193/#195/#196/#197/#198/
   #199/#202/#203/#204/#205, un design purement défensif sans levier
   compensatoire limite structurellement le rendement total.
4. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.
