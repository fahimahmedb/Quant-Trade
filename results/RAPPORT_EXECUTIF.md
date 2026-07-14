# RAPPORT EXÉCUTIF — Projet Quant-Trade (NASDAQ)

*Destinataire : décision d'allocation (CIO / PM / trader). Sources : exclusivement les fichiers `results/` du repo (étapes A, B, C, D, meta-labeling, pipeline intégrée). Aucun chiffre inventé. Tous les résultats sont **hors échantillon** (le modèle n'a jamais « vu » les données sur lesquelles il est jugé) et **nets de frais** (5 points de base par aller-retour).*

---

## Page 1 — Synthèse exécutive

### Contexte et objectif

Projet de recherche quantitative sur les indices NASDAQ, mené sur deux jeux de données : le NASDAQ Composite sur 5 ans (2021–2026, échantillon de contrôle) et surtout le **NASDAQ-100 (NDX) sur 40 ans** (1985–2026, 10 273 séances, couvrant les krachs de 1987, 2000-2002, 2008, 2020 et 2022). Objectif initial : gagner de l'argent en prédisant la direction de l'indice. Objectif révisé en cours de route, à la lumière des résultats : **piloter le risque** (la taille de la position) plutôt que deviner la direction.

### Ce qu'on a construit (en 3 phrases)

1. Un **diagnostic** (Étape A) qui répond à la question « le marché est-il prévisible ? » : sur 40 ans, une très faible prévisibilité de la *direction* est détectée (statistiquement réelle, p=0,007, mais économiquement mince), et une très forte prévisibilité de l'*agitation* (la volatilité) est confirmée.
2. Des **modèles de prédiction de direction** (Étape B, complétés par un filtre de confiance dit « meta-labeling ») et un **modèle de prévision de la volatilité** (Étape C, famille GARCH), chacun évalué contre des tests statistiques sévères qui corrigent le fait d'avoir essayé plusieurs modèles (on ne garde pas « le chanceux »).
3. Un **overlay défensif** (Étape D) qui reste investi dans l'indice mais réduit automatiquement l'exposition quand la volatilité prévue monte, et coupe la position dans les régimes de tempête extrême.

### Trouvailles clés (chiffres réels, NDX 40 ans)

- **Prédire la direction ne bat pas l'achat-conservation.** Le meilleur signal directionnel (régression logistique) est rentable net de frais (+8,3 %/an, précision 53,7 %) mais reste **derrière Buy & Hold** (+14,5 %/an) et sa performance n'est pas statistiquement crédible après correction du biais de sélection (probabilité de « vrai » edge : 37 %, contre 84 % pour Buy & Hold ; seuil de crédibilité : 95 %).
- **Prédire la volatilité fonctionne, et c'est prouvé.** Le modèle GJR-GARCH-t prévoit l'ampleur des secousses mieux que le modèle de référence, et cet avantage **survit au test anti-hasard le plus sévère** (SPA de Hansen : p=0,0000 à 1 jour, p=0,0034 à 5 jours, sur 9 522 prévisions). C'est la brique la plus solide du projet.
- **L'overlay défensif construit sur cette brique atteint son objectif chiffré** : pire chute ramenée de **−82,9 % à −55,1 %** (réduction relative de 33,5 %) tout en faisant **+16,5 %/an contre +14,5 %** pour Buy & Hold — meilleur rendement ET meilleur risque.
- **Verdict de rentabilité : OUI, mais pas là où on le cherchait.** L'argent n'est pas dans la prédiction de la direction (personne n'y arrive de façon crédible ici) ; il est dans la **gestion de l'exposition** pilotée par la volatilité prévue.

---

## Page 2 — Tableau de bord comparatif

Toutes les stratégies ci-dessous : NDX, ~38 ans hors échantillon (09/1988 → 07/2026), nettes de frais de 5 pb.

*Lecture : Sharpe = rendement par unité de risque (~0,5 ordinaire, >1 bon). MDD = pire chute depuis un sommet ("sur 40 ans, le pire moment"). Calmar = rendement annuel divisé par la pire chute (plus haut = mieux). DSR = probabilité que la performance soit un vrai talent et non de la chance (crédible au-dessus de 0,95).*

| Stratégie | Rendement ann. | Sharpe | MDD (pire chute) | Calmar | DSR |
|---|---|---|---|---|---|
| **Buy & Hold** (référence) | **+14,5 %** | +0,52 | −82,9 % | +0,08 | 0,842¹ |
| Momentum 10 j | −7,1 % | −0,28 | −97,6 % | −0,02 | 0,000 |
| Logistique L2 (LogitL2) | +8,3 % | +0,30 | −64,2 % | +0,08 | 0,372 |
| Gradient boosting (HistGB) | +6,1 % | +0,23 | −77,7 % | +0,04 | 0,214 |
| LogitL2 + meta-labeling | +1,1 % | +0,24 | −18,1 % | +0,06 | 0,247 |
| LogitL2 + overlay | +11,6 % | +0,46 | −44,9 % | +0,18 | 0,968² |
| LogitL2 + meta + overlay (pipeline complète) | +0,7 % | +0,22 | −14,0 % | +0,05 | 0,645² |
| BH + vol-targeting (cap 1,5×, coupe 95ᵉ) | +16,4 % | +0,66 | −63,3 % | +0,15 | 1,000³ |
| **BH + overlay optimisé (cap 2,0×, coupe 90ᵉ)** | **+16,5 %** | +0,65 | **−55,1 %** | **+0,19** | 1,000³ |

¹ DSR de l'univers Étape B (4 essais). ² DSR de l'univers pipeline (5 variantes). ³ DSR de la grille D (12 combinaisons) — les DSR ne sont comparables qu'au sein d'un même univers.

**En clair** : sur 40 ans, l'achat-conservation du NDX a rapporté +14,5 % par an mais a fait subir une perte de 83 % au pire moment (2000-2002 : 100 000 € devenaient ~17 000 €). L'overlay optimisé a rapporté +16,5 % par an avec une pire perte de 55 % — toujours violente, mais un investisseur sur deux fois moins de chemin à remonter (+123 % pour récupérer, contre +485 %).

### Gagnant par métrique

| Métrique | Gagnant | Valeur |
|---|---|---|
| **Sharpe** | BH + vol-targeting (1,5×, 95ᵉ) | +0,66 (vs +0,52 BH) |
| **MDD** (parmi les stratégies qui gagnent >10 %/an) | BH + overlay optimisé (2,0×, 90ᵉ) | −55,1 % (vs −82,9 % BH) |
| **MDD absolu** | Pipeline complète | −14,0 % — mais ne rapporte que +0,7 %/an : inutilisable |
| **Calmar** | BH + overlay optimisé (2,0×, 90ᵉ) | +0,19 (vs +0,08 BH) |
| **Rendement brut** | BH + overlay optimisé | +16,5 %/an |

Sur le Composite 5 ans (échantillon de contrôle), le verdict est le même en plus sévère : Buy & Hold fait +18,9 %/an (MDD −24,3 %) et **aucune** stratégie active ni aucun overlay n'atteint son critère de succès — l'échantillon est trop court et ne contient pas de vraie tempête.

---

## Page 3 — Recommandation, risques, prochaines étapes

### Recommandation de production

**Utiliser : NDX Buy & Hold + overlay défensif (vol-targeting cap 2,0×, coupe d'exposition au 90ᵉ percentile de volatilité prévue, moteur GJR-GARCH-t).**

Pourquoi celle-là :
- Elle domine Buy & Hold sur **toutes** les métriques à la fois (+16,5 % vs +14,5 %/an, Sharpe +0,65 vs +0,52, pire chute −55 % vs −83 %, Calmar ×2,4).
- Elle repose sur la **seule brique statistiquement prouvée** du projet (la prévision de volatilité, validée par le test SPA à p<0,01 sur 38 ans hors échantillon), pas sur une prédiction de direction fragile.
- Le critère de succès (réduction de la pire chute >25 % en conservant ≥80 % du rendement) est atteint par **4 des 12 réglages** de la grille figée à l'avance — le résultat n'est pas un point chanceux isolé : au percentile 90, il tient pour les quatre niveaux de cap testés.
- Elle ne trade presque pas : ~0,06 aller-retour par jour, donc peu sensible aux frais réels.

**Ne PAS utiliser** : les signaux directionnels seuls (Momentum perd de l'argent ; LogitL2 et HistGB gagnent mais moins que ne rien faire), la pipeline complète signal+meta+overlay (protège très bien mais ne rapporte plus rien : +0,7 %/an), et le meta-labeling comme source de gain (il réduit les coûts et le drawdown du signal, il ne crée aucun edge).

**Limites explicites de la recommandation** :
- Le réglage optimal (2,0× / 90ᵉ) sort d'une grille testée uniquement sur NDX ; il n'a pas été re-vérifié sur le Composite ni sur un autre indice. Le réglage cap 1,0×–1,5× au 90ᵉ percentile, presque aussi bon et sans levier, est l'alternative prudente.
- Le cap 2,0× implique de l'emprunt ou des futures : le coût de financement du levier n'est **pas** modélisé dans le backtest.
- Règle empirique de la littérature citée dans le repo : la performance réelle se dégrade en médiane de ~73 % entre backtest et live. Attendre en pratique nettement moins que les chiffres ci-dessus.

### Risques résiduels

1. **Le drawdown reste sévère.** −55 % au pire moment, ce n'est pas une stratégie « défensive » au sens du grand public. Quiconque ne peut pas supporter de perdre la moitié du capital ne doit pas être 100 % NDX, overlay ou pas.
2. **Fenêtres longues sans gain.** L'historique contient des traversées du désert de plusieurs années (le NDX a mis des années à récupérer 2000-2002) ; le Sharpe de ~0,65 est une moyenne sur 38 ans, pas une promesse annuelle.
3. **Limite d'échantillon.** 40 ans ≈ une dizaine de cycles de marché seulement, sur **un seul indice, un seul pays, une seule classe d'actifs** — et le plus performant de l'histoire moderne (biais de choix d'indice). Sur 5 ans, le même overlay échoue à son critère : la valeur ajoutée vient des krachs, qui sont rares.
4. **Risque de modèle.** La coupe d'exposition dépend d'un seuil (90ᵉ percentile) calibré sur le passé ; une tempête d'un type nouveau (gap overnight, crise de liquidité intraday) peut être plus rapide que le modèle, qui travaille en données quotidiennes.

### Que faire maintenant

1. **Valider hors NDX** : rejouer l'overlay (protocole figé, mêmes tests) sur S&P 500, indices européens/japonais — si l'effet est réel, il doit se retrouver ailleurs. C'est le test le plus discriminant et le moins cher.
2. **Données intraday** : la volatilité réalisée intraday (plutôt que la formule de Parkinson sur données quotidiennes) est la voie identifiée pour affiner le moteur C — le fichier C conclut explicitement que le progrès viendra de la finesse des données, plus du volume d'historique.
3. **Alpha directionnel : chercher ailleurs, pas plus fort.** L'Étape B montre qu'ajouter des modèles sur les mêmes données quotidiennes ne donne rien ; les pistes déclarées sont de nouvelles sources (microstructure intraday, sentiment), re-testées une seule fois sous DSR/SPA.
4. **Paper trading / pilote à petite taille** de l'overlay (variante sans levier, cap 1,0×, 90ᵉ percentile) pour mesurer l'écart backtest→réel avant tout déploiement significatif.
5. **Gouvernance inchangée** : conserver la discipline anti-data-snooping du repo (univers figés avant évaluation, comptage des essais, tests SPA/DSR, R² banni). C'est elle qui rend les chiffres de ce rapport dignes de confiance.

---

*Rapport établi le 14/07/2026 à partir de : `etape_A_*.md`, `etape_B_*.md`, `etape_C_*.md`, `etape_D_overlay.md`, `etape_D_overlay_optimized.md`, `meta_labeling.md`, `meta_labeling_multi.md`, `integrated_pipeline.md`.*
