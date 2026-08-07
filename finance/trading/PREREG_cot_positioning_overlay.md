# Pré-enregistrement — Positionnement spéculatif net CFTC (COT, futures NASDAQ-100), overlay défensif

**Committé AVANT tout calcul.** Cycle #360 du backlog non-ML.

## 1. Contexte et hypothèse (nouvelle catégorie de mécanisme)

**Nouvelle source de données, jamais utilisée dans ce backlog** : les
rapports hebdomadaires "Commitment of Traders" (COT) de la CFTC
(Commodity Futures Trading Commission, régulateur fédéral US),
gratuits, publiés chaque semaine depuis les années 1980
(`cftc.gov/files/dea/history/`), donnant le positionnement AGRÉGÉ des
différentes catégories d'intervenants (spéculateurs "non-commerciaux",
"commerciaux"/hedgers, non-déclarants) sur les marchés à terme
réglementés US.

**Mécanisme authentiquement nouveau dans ce backlog** : jusqu'ici,
tous les signaux testés reposent sur le PRIX (momentum), le RENDEMENT
(spread de taux), ou la VOLATILITÉ IMPLICITE (options) d'un actif.
Le COT mesure le **POSITIONNEMENT** du marché à terme lui-même — combien
de contrats nets les spéculateurs (traders non-commerciaux, souvent des
CTA/fonds systématiques suiveurs de tendance) détiennent long vs short.
**Hypothèse contrariante documentée dans la littérature académique et
professionnelle** (Wang 2001-2003, Sanders & Irwin, pratique "Commitment
of Traders sentiment index" popularisée par Larry Williams) : un
positionnement spéculatif net-LONG EXTRÊME reflète un consensus haussier
déjà largement engagé (trade "crowded") — peu de munitions acheteuses
restantes, risque de dénouement/liquidation asymétrique à la baisse en
cas de choc. C'est un signal de POSITIONNEMENT/FLUX, pas de prix ni de
volatilité — catégorie mécanique entièrement distincte de tout ce qui a
été testé jusqu'ici dans ce backlog.

## 2. Données

**Nouvelle donnée** : rapport COT "Legacy" combiné (futures seuls),
série `NASDAQ-100 Consolidated - CHICAGO MERCANTILE EXCHANGE` (agrège
le contrat E-mini standard et le Micro E-mini depuis leur introduction
— série disponible et nommée de façon cohérente en continu depuis le
15/06/2010, vérifié explicitement sur 17 fichiers annuels 2010-2026,
842 observations hebdomadaires, aucun doublon, aucun trou >8 jours).

**Limite reconnue à l'avance** : la dénomination "NASDAQ-100
Consolidated" n'existe QUE depuis 2010 (avant cela, seule la série
"NASDAQ-100 STOCK INDEX" standalone existe, distincte car elle
n'inclut pas les contrats Mini/Micro). **Décision : ne PAS raccorder
("splicer") les deux séries** pour éviter tout artefact de saut de
niveau à la jonction (le total de contrats et l'univers de
déclarants diffèrent structurellement entre les deux définitions) —
historique volontairement limité à 2010-2026 (~16 ans, 842 semaines),
plus court que la majorité des candidats macro-externes (40 ans) mais
plus long que la plupart des candidats Yahoo Finance récents (2018-2021
pour Bitcoin/BDRY).

**Construction du signal** à partir des colonnes brutes du rapport :
`net_pct(t) = 100 × (NC_Long(t) − NC_Short(t)) / OpenInterest(t)`
(positionnement spéculatif net normalisé par l'open interest total,
nécessaire car l'open interest a été multiplié par ~5 entre 2010 et
2026 — une comparaison en contrats bruts serait invalide sur un
tercile expanding).

**Décalage de publication** : le rapport "en date du" mardi est publié
le vendredi suivant à 15h30 ET (~3 jours calendaires). **Décalage
conservateur de 5 jours calendaires** (`PUBLICATION_LAG_DAYS=5`,
marge de sécurité sur le délai réel de 3 jours, même philosophie que
le délai de 7j déjà utilisé pour les demandes chômage hebdomadaires
ICSA au #204/#322), puis alignement causal quotidien standard
`ffill+shift(1)` (Règle 7).

## 3. Marchés testés (figés)

5 marchés (Composite, NDX, Russell 2000, S&P 500, DAX) — même
convention que tout signal macro-externe/positionnement appliqué
uniformément (le positionnement sur futures NASDAQ-100 est traité
comme une jauge de sentiment spéculatif systémique, pas seulement
spécifique au NDX), cohérent avec la pratique établie (ex. dollar
DXY #198 appliqué aux 5 marchés bien que spécifique au change).

## 4. Mécanisme (figé, PUREMENT DÉFENSIF, jamais de levier)

- Seuil : **tercile EXPANDING** de `net_pct_lag(t)` sur le NIVEAU BRUT
  (construction réutilisée à l'identique du #357 MOVE/#341 SKEW/#291
  NFCI, Règle 7).
- `position(t) = 0,5x` (**CUT=0,5 réutilisé à l'identique**) si
  `net_pct_lag(t)` est dans son tercile expanding le PLUS HAUT
  (positionnement spéculatif net-long le plus extrême = trade
  "crowded" = défensif, direction contrariante documentée à l'avance
  au §1), `1,0x` sinon. **Jamais de levier**. Coûts 5 bps (`COST_BPS`
  réutilisé).

## 5. Critère de succès (RENFORCÉ, figé — même seuil que toute la famille macro-externe)

> **PASS si et seulement si ≥4 des 5 marchés** battent Buy & Hold en
> Sharpe ET rendement total net de coûts.

**n_trials = 1** (un signal, une direction contrariante déclarée à
l'avance sur la base de la littérature documentée, aucun balayage,
aucun test de la direction opposée).

## 6. Prédiction déclarée à l'avance (Règle 2)

**FAIL anticipé, mais pas exclu** : nouvelle catégorie mécanique
authentiquement distincte de tout ce qui a été testé (positionnement
vs prix/rendement/volatilité), donc pas directement comparable aux
familles déjà closes. Cependant, fréquence hebdomadaire (rapport une
fois par semaine, contre quotidien pour tous les signaux déjà testés)
et historique le plus court après Bitcoin/BDRY constituent des limites
structurelles reconnues à l'avance. Résultat rapporté tel quel, sans
retuning après calcul.

## 7. Ce qui pourrait faire échouer cette hypothèse (déclaré à l'avance)

1. **Fréquence hebdomadaire** — le signal ne se met à jour qu'une fois
   par semaine ; combiné au décalage de publication de 5j, l'essentiel
   de la semaine suivante utilise une information vieille de 5-12
   jours, contrairement aux signaux quotidiens/mensuels déjà testés.
2. **Historique le plus court après Bitcoin/BDRY** (2010+, ~16 ans,
   842 observations hebdomadaires seulement) — puissance statistique
   réduite pour un tercile expanding, en particulier sur les
   premières années où l'échantillon de référence est petit.
3. **Direction contrariante non garantie à cette fréquence/cet
   horizon** — la littérature COT est majoritairement établie sur les
   matières premières (pétrole, or, devises) et les futures actions
   larges (S&P 500), pas spécifiquement le NASDAQ-100 ; l'effet peut
   ne pas se transmettre à un indice technologique à plus forte
   composante momentum.
4. **Le contrat NASDAQ-100 Consolidated combine des tailles de
   contrat différentes (E-mini + Micro E-mini)** — un changement de
   mix de participants (ex. plus de retail via Micro E-mini depuis son
   lancement 2019) pourrait introduire une rupture de régime non liée
   au signal économique lui-même.
5. Aucune valeur ci-dessus ne sera modifiée après avoir vu un résultat.

## 8. Sortie

`data/nasdaq100_cot_positioning_weekly.csv` (déjà committé avec ce
PREREG — donnée brute, aucun calcul de signal dedans),
`scripts/nonml_cot_positioning_overlay_backtest.py`,
`scripts/nonml_cot_positioning_overlay_audit.py`,
`results/nonml_cot_positioning_overlay_{result,audit,anti_cheat}.md`.
Si PASS : `..._robustness.md`, `..._sim_300e.md` également.
