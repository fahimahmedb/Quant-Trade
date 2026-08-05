# Synthèse consolidée v4 — cycles #156 à #243 (88 cycles depuis la v3)

Ce document complète (ne remplace pas) `..._v3.md` (couvrait #1-155). Pas
de nouveau calcul : consolidation honnête des résultats déjà committés,
même esprit que v1/v2/v3. Backlog au moment de la rédaction : **88 PASS
niveau 1 sur 244 hypothèses testées, 0 PASS RENFORCÉ Règle 9 sur
l'ensemble du backlog** (aucune exception, jamais un candidat n'a
franchi les 5 contrôles simultanément — voir section « plafond
structurel » ci-dessous).

## A. Rétrospective Règle 9 appliquée aux meilleurs candidats historiques (#161-164)

La Règle 9 (batterie renforcée) a été appliquée rétroactivement au
meilleur candidat brut jamais obtenu (#38, momentum, Sharpe brut
+0,78→+1,50, committé avant l'introduction de la Règle 9). **#161** :
**4/5 — meilleur score jamais obtenu**, SPA p=0,0000 (1ère fois qu'un
candidat individuel passe le SPA), DSR=0,730 (le plus proche de 0,95
jamais atteint). Un biais du survivant potentiel (univers NDX-100 de
2026 appliqué rétroactivement à 1970) a motivé une ré-exécution sur
historique étendu (**#162**, non concluante, univers non défendable) puis
sur l'univers **point-in-time réel** du NDX-100 (**#163**, source de
données vendorée, couverture 87,6% mesurée date par date) : **le biais du
survivant est réfuté** comme explication de l'edge (DSR **record du
backlog à 0,754**, SPA le plus net jamais obtenu, t=7,637), mais le
contrôle de crise échoue pour une **raison économique réelle** documentée
(l'overlay double l'exposition près des plus hauts, configuration exacte
de février 2020). **#164** applique la même infrastructure au #14
(momentum court terme) : PASS maintenu mais edge réduit d'~21% une fois
le biais du survivant corrigé — le flag de prudence posé à sa création
est confirmé a posteriori avec un chiffre dessus. Un complément de
puissance statistique montre qu'il faudrait **~67 ans de données** pour
que le #38 franchisse seul le seuil DSR par accumulation d'historique —
limite structurelle, pas un problème de taille d'échantillon.

## B. Correction d'intégrité : bug d'exécution « même barre » (#166-167)

Un bug d'exécution a été découvert et corrigé rétroactivement : plusieurs
candidats (#38, #14, #4) exécutaient leur signal sur la MÊME barre que
sa formation plutôt qu'à la barre suivante (fuite d'information). Une
fois l'exécution rendue strictement causale, ces trois candidats
**basculent de PASS à FAIL** — reclassification actée dans le compteur
(75→72 PASS niveau 1 à ce moment). C'est la correction d'intégrité la
plus significative de tout le backlog en nombre de candidats affectés.
**#167** corrige par ailleurs le contrôle de coûts de la batterie Règle 9
du #165 (rebalancement hebdomadaire, 2/5→3/5) sans retuning du signal.

## C. Portefeuille « volatility-managed » (Moreira & Muir) — prévision de vol comme ESTIMATEUR (#165, #168-170)

**#165** : première monétisation de l'edge de volatilité de l'Étape C
(GJR-GARCH-t) en edge de RENDEMENT plutôt qu'en risk management passif —
`position = clip(20%/vol_PRÉVUE, 0, 2x)`. PASS niveau 1 (Sharpe +0,52→
+0,67, MDD -82,9%→-59,9%, marges de crise les plus larges du backlog),
mais **Règle 9 seulement 2/5→3/5** (SPA p=1,0000, edge concentré sur les
épisodes de crise, pas un excès de rendement quotidien régulier). Les
tentatives de généraliser ce mécanisme (**#168** porte directionnelle
52w-high, **#169** régime discret, **#170** signal de direction) **échouent
toutes les trois** — le mécanisme ne généralise pas au-delà de NDX ni
au-delà de son usage défensif d'origine.

## D. Exploration calendrier/macro (#171-206)

Sous-famille FOMC (**#171/#173/#174**) : FAIL net sur les trois variantes
(pré-FOMC, post-FOMC, semaine complète). Signaux de taux au NIVEAU
(**#175** DGS3MO, **#186** DGS10, **#187** inversion de courbe, **#202**
TIPS réel) : FAIL structurel systématique — seuls les ÉCARTS/spreads
(pas les niveaux) portent parfois un edge (confirmé positivement une
seule fois, **#200** anticipations d'inflation T10YIE, PASS 5/5 plateau
parfait, seul PASS propre sur les 5 marchés de toute la famille macro-
externe). Cycle électoral : théorie de Hirsch confirmée pour les deux
extrêmes seulement (**#176** mid-term PASS 4/4, **#30** historique déjà
connu) mais **#180/#181** (années 1 et 4) FAIL net — seules les
combinaisons Halloween×électoral (**#179/#182/#184**) atteignent des
plateaux parfaits. Famille macro-externe défensive élargie (**#191**
VRP VIX-RV, **#192** force relative Russell/S&P, **#195** différentiel de
taux US-DE, **#196** corrélation NDX-Russell domestique, **#197** vol du
gap, **#198** force du dollar, **#199** spread de crédit, **#203** M2,
**#204** jobless claims, **#205** confiance consommateurs, **#206** indice
Chicago Fed) : **FAIL sur 11 des 13 hypothèses testées**, seuls **#193**
(corrélation NDX-DAX, PASS 4/5) et **#200** passent. La Règle 9 appliquée
aux meilleurs PASS calendaires (**#188-190**) confirme 0 PASS RENFORCÉ
mais établit un jalon : **3/4 passent le SPA pour la première fois pour
des signaux purement calendaires** (contre systématiquement en échec pour
la lignée vol-targeting scalaire à la même époque, cf. section E).

## E. Règle 9 rétroactive sur la famille fondatrice #46 (#207-214)

Les 7 dérivés directs du mécanisme #46 (vol-targeting hiérarchique de
base) sont tous soumis à la Règle 9 : **0/7 PASS RENFORCÉ**. Meilleurs
scores 4/5 (**#209** Parkinson, DSR=0,0040 le meilleur du backlog côté
scalaire à l'époque ; **#210** calendrier, SPA p=0,0006 le meilleur de
tout le backlog scalaire). Plus faibles : **#212/#213** (2/5), confirmant
que la LENTEUR DE MISE À JOUR de la porte (pas le type de signal
sous-jacent) est le facteur dominant de fragilité pour la stabilité
temporelle.

## F. Méga-famille estimateurs/portes de vol-targeting (#215-243) — le cœur de cette période

C'est la famille dominante depuis la v3 : **29 cycles** (215-243),
explorant systématiquement deux axes du mécanisme #46 (`position =
clip(20%/vol_estimée, floor, 2.0x)`) — remplacer l'ESTIMATEUR de
volatilité réalisée, ou ajouter une PORTE conditionnant l'amplification.

**Estimateurs testés (8 au total, remplacent le dénominateur)** :

| Estimateur | Cycle | Verdict niveau 1 | Règle 9 |
|---|---|---|---|
| Close-to-close (#46, référence) | fondateur | — | 0/7 (section E) |
| Parkinson | #50 | PASS | 4/5 (#209) |
| Garman-Klass | #215 | PASS net 5/5, plateau 8/8 | 4/5 (#224) |
| Rogers-Satchell | #221 | PASS net 5/5, plateau 8/8 | 4/5 (#228) |
| Yang-Zhang | #222 | PASS net 5/5, meilleur MDD | 4/5 (#229, tous contrôles sauf DSR) |
| EWMA | #231 | PASS 4/5, meilleur MDD absolu | 3/5 (#232, seul le SPA échoue) |
| ATR (Wilder) | #233 | **FAIL 3/5** — 1er échec de la lignée | non exécutée (FAIL) |
| HAR-P (Corsi) | #236 | **FAIL 2/5** — Composite trop court | non exécutée (FAIL) |

**Constat** : les 4 estimateurs à fondement statistique rigoureux
(range-based Parkinson/GK/RS/YZ) passent tous nettement ; les 2
heuristiques de gestion technique (ATR, conversion approximative) sont
les 2 SEULS échecs de la lignée. L'EWMA (récursion à mémoire
exponentielle, causalement adaptée) obtient le meilleur profil de crise
absolu mais échoue le SPA — confirme la dissociation déjà documentée
SPA/autres contrôles (cf. #208 vs #207).

**Portes testées (12+ au total, filtrent QUAND amplifier, dénominateur #46 inchangé)** :

| Porte | Cycle | Verdict niveau 1 | Règle 9 |
|---|---|---|---|
| Tendance/calendrier/breadth/dispersion/annuelle | #47/#54/#57/#68/#78/#80 | PASS (variable) | 2-4/5 (#208/#210-214) |
| Risque de gap (amplitude brute) | #216 | FAIL 2/5 | — |
| Variance Ratio Lo-MacKinlay | #217 | PASS 4/5, porte la plus rare | 1/5 (#225) |
| Skewness glissante | #218 | FAIL 3/5 | — |
| Kurtosis glissante | #219 | PASS 4/5, plateau parfait 8/8 | 3/5 (#226) |
| Vol-de-la-vol glissante | #220 | PASS 4/5 | 4/5 (#227) |
| Clustering ARCH (lag 1) | #223 | PASS 4/5, 5e audit parfait | 1/5 (#230) |
| Prévision GJR-t (walk-forward) | #234 | PASS marginal, NDX seul, marge Sharpe la plus faible jamais observée | 1/5 (#235, pire coûts/stabilité) |
| Ratio vol Parkinson/close-to-close | #239 | **FAIL 1/5 — pire score de toute la lignée** | — |
| ν glissant MLE Student-t | #237 | PASS 4/5, **fragilité numérique documentée de l'estimateur** | **4/5 (#238), un des meilleurs scores du backlog** |
| Combinaison ET kurtosis+ν | #240 | PASS 4/5, même pattern que ses composantes | 4/5 (#241), SPA légèrement moins net |
| Clustering ARCH par Ljung-Box (multi-retards) | #242 | PASS 4/5, robustesse fragile (point isolé) | **2/5 (#243) — le plus faible de la sous-famille moments/clustering** |

**Trois enseignements méthodologiques nouveaux de cette période**,
distincts de tout ce qui précède dans le backlog :

1. **La fragilité de robustesse (grille de perturbation) est prédictive
   d'un score Règle 9 faible, mais la fragilité NUMÉRIQUE d'un
   estimateur (non-identifiabilité MLE) ne l'est PAS.** Le #242
   (Ljung-Box, robustesse = point isolé sur les grilles CAP/fenêtre)
   obtient le pire score de sa sous-famille en Règle 9 (2/5) — confirmé
   comme prévu au PREREG. À l'inverse, le #237 (ν Student-t, MLE non
   contraint divergeant vers des valeurs arbitraires sur ~0-6% des
   séances) obtient l'un des MEILLEURS scores Règle 9 du backlog entier
   (4/5, SPA p=0,0022) — la fragilité affecte la magnitude de
   l'estimateur, pas la décision binaire de la porte qui pilote le
   trading.
2. **Combiner deux signaux corrélés ne renforce ni ne dégrade
   qualitativement le profil.** Le #240 (conjonction ET kurtosis+ν)
   reproduit EXACTEMENT le pattern de marchés PASS/FAIL de ses deux
   composantes prises séparément, et son score Règle 9 (#241, SPA
   p=0,0134) est légèrement MOINS net que sa meilleure composante seule
   (#237/#238, p=0,0022) plutôt que meilleur — l'accord de deux mesures
   corrélées de la même propriété (épaisseur des queues) ne produit pas
   un signal qualitativement différent.
3. **Le signal de gap/discontinuité de marché est le seul thème
   systématiquement et doublement réfuté** dans cette famille : le gap
   brut (#216, FAIL 2/5) ET sa reformulation en ratio avec la vol
   close-to-close (#239, FAIL 1/5, pire score de la lignée) échouent
   tous les deux — à la différence des moments statistiques (kurtosis,
   vol-de-la-vol) qui généralisent nettement mieux.

**DAX est devenu le marché systématiquement le plus difficile** de cette
période : sur les 12 portes testées #216-242, DAX est en échec sur au
moins une jambe dans la majorité des cas, davantage que tout autre
marché — un constat purement descriptif, aucune explication causale
testée à ce stade.

## Plafond structurel DSR (mise à jour du #116)

Le #116 (cycle #116, n_trials=110) avait établi que le Sharpe annualisé
nécessaire pour franchir DSR>0,95 valait 1,58 à 2,03 — déjà au-dessus de
tous les repères académiques standards. **n_trials a plus que doublé
depuis (244 aujourd'hui)** : le seuil requis n'a fait que grimper. Sur
les 88 cycles de cette période, **DSR a échoué SANS AUCUNE EXCEPTION**
(les meilleures valeurs individuelles restent le #163 à 0,754 et le
#209/#210 côté scalaire à ~0,004-0,02) — le plafond structurel identifié
au #116 continue de tenir intégralement à cette échelle de n_trials.

## Ce que cette période apprend, au-delà de son score

1. **La discipline méthodologique du backlog s'est encore renforcée** :
   correction rétroactive d'un bug d'exécution touchant 3 candidats
   (section B), correction complète d'un biais du survivant avec source
   de données point-in-time vendorée (section A), et — nouveauté de
   cette période — un cas explicite de fragilité d'estimateur découverte
   en audit et délibérément NON corrigée après avoir vu un résultat PASS
   (#237, conformément à la Règle 2), documentée honnêtement plutôt que
   dissimulée.
2. **Les rendements marginaux décroissent visiblement dans la
   méga-famille vol-targeting.** Les 9 premiers cycles de la famille
   estimateurs/portes récente (#215-223) comptent 7 PASS nets pour 2
   FAIL (skewness, gap) ; les 8 cycles suivants (#231-243, hors Règle 9)
   comptent 4 PASS marginaux/fragiles (#231, #234, #237, #240, #242)
   pour 3 FAIL nets (#233, #236, #239) — un taux d'échec en hausse
   cohérent avec un espace d'hypothèses "faciles" en cours
   d'épuisement, malgré la découverte régulière de nouveaux outils déjà
   implémentés à réutiliser (EWMA, HAR-P, ν Student-t, Ljung-Box).
3. **Le meilleur outil de risk management du backlog reste le #149**
   (non retesté depuis la v3, VaR/ES meilleurs que le #134 sur toutes
   les mesures) — aucun candidat de la méga-famille #215-243 ne l'a
   supplanté sur ce plan, la plupart de ces cycles optimisant plutôt un
   Sharpe/rendement niveau 1 que la réduction de risque de queue
   explicitement.

**Recommandation honnête (pas une décision unilatérale, comme aux v1-v3)**
: le rythme d'idées réellement neuves ET bien motivées dans la
méga-famille vol-targeting ralentit visiblement (3 FAIL sur les 4
derniers cycles de découverte non-Règle-9 : #233/#236/#239, contre
1 seul FAIL — #234 marginal — sur la période #234-#242 en comptant les
PASS fragiles). Deux voies non tranchées, dans la continuité de celles
déjà posées aux v1-v3 sans jamais avoir été formellement arbitrées par
l'utilisateur : (a) considérer la méga-famille vol-targeting comme
substantiellement explorée et recentrer l'effort sur la formalisation
des meilleurs candidats (#149 en risk management, #237/#238 comme
meilleur SPA récent malgré sa fragilité numérique) plutôt que sur
l'ajout de nouvelles variantes marginales ; (b) élargir consciemment à
une catégorie de données ou de mécanisme non encore explorée (au-delà
des outils déjà implémentés dans le repo) si l'utilisateur souhaite
continuer l'exploration systématique. La boucle autonome continue en
attendant, en select­ionnant les pistes restantes les mieux motivées
plutôt que d'empiler des variantes de plus en plus marginales.
