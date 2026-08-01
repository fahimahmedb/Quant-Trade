# Décomposition chiffrée du DSR du #38 — pourquoi 0,754 et pas 0,95 ?

**Analyse diagnostique, pas un nouveau backtest.** Aucune nouvelle hypothèse, aucun paramètre du #38 touché, aucun nouveau pré-enregistrement : tous les chiffres ci-dessous sont recalculés à partir des poids déjà committés du cycle #163 (`build_weights()` du backtest d'origine, univers point-in-time réel 2015-2026) et de `finance/src/prediction.py::dsr` tel quel. Produit par `scripts/nonml_dsr_decomposition_38.py` (Règle 6).

Question : le #38 est le meilleur candidat du backlog (DSR = 0,754, record). Qu'est-ce qui pèse le plus sur son DSR — l'asymétrie de sa distribution, le nombre d'essais, ou la taille d'échantillon ? La réponse est chiffrée par contrefactuels, pas devinée.

## 1. Entrées mesurées (recalculées, non recopiées)

| Quantité | Valeur |
|---|---|
| Séances `T` | 2907 (2015-01-02 → 2026-07-27) |
| Sharpe quotidien candidat `SR_j` | +0.089172 |
| Sharpe annualisé candidat | +1.4156 |
| Sharpe annualisé référence (Leaders 1.0x) | +0.7850 |
| **Asymétrie (skew) du PnL candidat** | **-0.2498** |
| **Kurtosis excédentaire du PnL candidat** | **+2.4710** |
| Asymétrie / kurtosis exc. de la référence | -0.6490 / +7.4909 |
| `n_trials` (backlog, lu automatiquement) | 164 |
| `var_trials` journalière (68 Sharpe extraits) | 8.005201e-04 |
| écart-type des Sharpe d'essai (annualisé) | 0.4491 |
| Seuil de sélection `SR0` (journalier) | 0.076392 |
| `SR0` équivalent annualisé | 1.2127 |
| `z` | +0.679741 |
| **DSR** | **0.7517** |

*Traçabilité du DSR de référence.* Le rapport du cycle #163 affiche **0,754** (calculé avec `n_trials = 162`, la taille du backlog AVANT ce cycle, comme l'impose la Règle 9e) ; l'analyse de puissance du #164 affiche 0,753 (`n_trials = 163`) ; ce document affiche **0.7517** (`n_trials = 164`, valeur courante lue automatiquement dans le backlog). L'écart est **entièrement** dû à l'incrémentation du compteur d'essais, pas à un recalcul divergent — et il illustre déjà, à lui seul, le point n°2 de la conclusion : chaque cycle supplémentaire dégrade mécaniquement le DSR de tous les candidats du backlog.

Lecture immédiate : le candidat doit franchir un seuil de sélection de **1.21 de Sharpe annualisé** avant même de commencer à compter. Il en affiche +1.42. L'excédent réel n'est donc que de **+0.20** de Sharpe annualisé — c'est CE chiffre, et non le +1.42 affiché partout, qui est testé.

## 2. Contrefactuels — qu'est-ce qui pèse le plus ?

Chaque ligne ne change QU'UNE quantité, toutes choses égales par ailleurs.

| Contrefactuel | `SR0` | `z` | **DSR** | Δ DSR |
|---|---|---|---|---|
| **Référence (#163 tel quel)** | 0.0764 | +0.6797 | **0.7517** | — |
| (a) asymétrie neutralisée (`skew = 0`) | 0.0764 | +0.6872 | **0.7540** | +0.0024 |
| (b) kurtosis excédentaire neutralisée (`kurt_ex = 0`) | 0.0764 | +0.6814 | **0.7522** | +0.0005 |
| (a+b) distribution parfaitement gaussienne | 0.0764 | +0.6889 | **0.7546** | +0.0029 |
| (c) `n_trials` 10× plus petit (164 → 16) | 0.0509 | +2.0335 | **0.9790** | +0.2273 |
| (c′) `n_trials = 1` — **INTERDIT (Règle 2)**, montré pour référence seule | 0.0000 | +4.7430 | **1.0000** | +0.2483 |
| (d) échantillon ×2 à edge journalier constant (T = 5814) | 0.0764 | +0.9614 | **0.8318** | +0.0802 |
| (d) échantillon ×5 à edge journalier constant (T = 14535) | 0.0764 | +1.5202 | **0.9358** | +0.1841 |

### Hiérarchie des leviers (par |Δ DSR| décroissant)

1. **n_trials ÷10 (c)** : +0.2273
2. **échantillon ×5 (d)** : +0.1841
3. **distribution gaussienne (a+b)** : +0.0029
4. **asymétrie (a)** : +0.0024
5. **kurtosis (b)** : +0.0005

## 3. Combien faudrait-il, exactement ?

- **Sharpe requis à échantillon et `n_trials` inchangés** : `SR_j = 0.107419` soit **1.71 de Sharpe annualisé** (contre +1.42 observé, soit **×1.20**).
- **Échantillon requis à edge constant** : `T = 17,017` séances, soit **~68 ans** (confirme `results/nonml_dsr_power_analysis_38.md`).
- **`n_trials` maximal compatible avec DSR > 0,95**, à edge et échantillon inchangés : **28** (contre 164 réellement testés). *Information de diagnostic uniquement — la Règle 2 interdit de choisir `n_trials` pour obtenir un résultat.*

## 4. Contrôle de la convention de kurtosis (Règle 6)

La formule canonique de Bailey & López de Prado (« The Sharpe Ratio Efficient Frontier », 2012) écrit le dénominateur `sqrt(1 − γ3·SR + ((γ4−1)/4)·SR²)` où **γ4 est la kurtosis NON excédentaire** (γ4 = 3 pour une gaussienne). `finance/src/prediction.py::dsr` utilise `kurt_excess/4 = (γ4−3)/4`, soit un écart de `0,5·SR²` sur le carré du dénominateur.

| Convention | dénominateur | `z` | DSR |
|---|---|---|---|
| repo (`kurt_excess/4`) | 1.013502 | +0.679741 | 0.7517 |
| canonique (`(γ4−1)/4`) | 1.015462 | +0.678430 | 0.7513 |

**Écart : -0.00042 de DSR.** L'implémentation du repo est donc marginalement OPTIMISTE (elle sous-estime le dénominateur, donc surestime `z`). Aucun verdict déjà rendu ne change — tous les FAIL du backlog sont très loin du seuil, et cet écart les enfoncerait plutôt. Signalé pour traçabilité, pas corrigé ici (corriger `dsr()` modifierait rétroactivement 20 rapports déjà committés ; ce serait une décision de protocole, pas une décision d'analyse).

## 5. Conclusion — quel levier est le plus prometteur, à partir de CE diagnostic

**1. Les leviers distributionnels sont morts.** Neutraliser l'asymétrie rapporte +0.0024 de DSR, neutraliser la kurtosis +0.0005, et rendre la distribution parfaitement gaussienne +0.0029. La raison est structurelle et vaudra pour TOUTE stratégie évaluée en quotidien dans ce repo : le terme d'asymétrie vaut `skew × SR_j` ≈ 0.0223 et celui de kurtosis `kurt_ex/4 × SR_j²` ≈ 0.0049, face à un 1 au dénominateur. **L'intuition « chercher une famille à asymétrie positive pour aider le DSR » est donc quantitativement réfutée à cette fréquence** — c'est une bonne idée pour le contrôle de crise (Règle 9b, précisément celui que le #38 vient de perdre), pas pour le DSR.

**2. Le levier dominant est le rapport `SR_j / SR0`, de très loin.** Diviser `n_trials` par 10 ferait passer le DSR de 0.752 à 0.979 (+0.227) — c'est-à-dire que **le nombre d'hypothèses testées dans ce programme de recherche pèse plus lourd sur le verdict du #38 que toutes ses propriétés statistiques réunies.** C'est un constat désagréable mais central : ce n'est pas la stratégie qui échoue, c'est la stratégie *dans ce contexte de recherche*. Et ce levier n'est **pas actionnable honnêtement** : `n_trials` ne peut que croître (Règle 2), il vaudra 165, 166… au prochain cycle. Chaque cycle supplémentaire relève `SR0` et éloigne la cible.

**3. La taille d'échantillon est un levier réel mais insuffisant.** ×2 donne 0.832, ×5 donne 0.936 — toujours sous 0,95. Déjà tranché au #164 (~67 ans requis) ; ce diagnostic le confirme par un autre chemin.

**4. Le seul levier honnête et suffisant est donc le niveau du Sharpe quotidien.** Il faudrait **1.71 de Sharpe annualisé** (×1.20 l'actuel) sur le même échantillon. **Aucun réglage du #38 ne peut produire ça** : sa robustesse est déjà un plateau parfait, son SPA passe déjà à p=0,0000, et un Sharpe de 1,7 n'est pas atteignable par un portefeuille long-only levé dont la volatilité est dominée par celle du marché.

**5. Conséquence de conception, tirée de CE diagnostic et pas d'une intuition générale.** Puisque (i) la forme de la distribution ne compte pas, (ii) `n_trials` ne peut que grandir, (iii) l'historique est borné, alors la seule voie est un mécanisme dont le Sharpe quotidien est structurellement plus élevé — pas parce qu'il gagne plus, mais parce que **son dénominateur est plus petit**. Le #38 a une volatilité annualisée de 28.5 %, presque entièrement du risque de marché : il porte une exposition de 1,0x à 2,0x en permanence. Une construction **dollar-neutre** retire ce terme du dénominateur sans retirer l'alpha, et une construction à **grande ampleur** (au sens de Grinold, `IR ≈ IC·sqrt(BR)`) est le seul moyen documenté d'obtenir un IC modeste × un grand nombre de paris indépendants. C'est la conclusion qui motive la Phase 3 (voir `RECHERCHE_dsr_par_construction.md`, §7 piste A).

**6. Ce que ce diagnostic NE dit pas.** Il ne dit pas qu'un mécanisme dollar-neutre atteindra 1,7 de Sharpe sur cet univers — la littérature (Do & Faff 2010) documente au contraire une érosion forte des stratégies relative-value après 2003, et notre échantillon commence en 2015. Il dit seulement que c'est la **seule famille dont le profil statistique rend la barre atteignable en principe**. Si elle échoue aussi, la conclusion honnête sera qu'aucune stratégie testable avec ces données ne peut franchir la Règle 9e — ce qui serait une information de premier ordre pour la suite du projet.

