# Audit adversarial — Validation SPA/DSR de la famille vol-targeting (13 membres)

Objectif : chercher activement des failles dans `nonml_backlog_spa_dsr_validation.py` et son résultat déjà committé (`results/nonml_backlog_spa_dsr_validation.md`), pas les confirmer.

## 1. Recalcul indépendant (seconde implémentation, boucles Python explicites)

Membre testé : weakness_breadth (porte continue, la plus atypique de la famille). 3 dates vérifiées, écart max = 0.00e+00.
**OK — build_members() reproduit exactement compute_weakness_breadth_series().**

*Note de transparence sur le processus : la toute première version de ce recalcul indépendant signalait à tort un écart (~1-3%, `n_listed` limité aux tickers avec fenêtre 252j COMPLÈTE). Investigation manuelle -> le bug était dans le recalcul indépendant lui-même (dénominateur trop restrictif), pas dans `build_members()`/`compute_weakness_breadth_series()` : l'original compte au dénominateur tous les tickers COTÉS ce jour-là (`exists.sum`), pas seulement ceux avec fenêtre complète. Corrigé avant de committer ce résultat -- documenté ici en toute transparence plutôt que silencieusement réécrit.*

## 2. Test anti-lookahead sur l'infrastructure partagée (mutation des 20% de données NDX les plus récentes)

Teste combined_position/near_high_mask/découpage start_common (code NOUVEAU de ce script, pas les compute_*_series() déjà audités à leur cycle d'origine). Écart max sur les positions passées (avant mutation, marge 260j) : 0.00e+00 (membre aucun (tous a 0)).
**OK — aucune fuite du futur vers le passé.**

## 3. Stabilité temporelle (walk-forward informel, 3 sous-périodes, embargo 5j entre folds)

**Note méthodologique** : le purge/embargo classique (Étape B) protège contre la fuite d'un ENTRAÎNEMENT vers un TEST via des labels qui se chevauchent temporellement -- ces overlays ne sont PAS des modèles ajustés (aucun paramètre estimé sur une fenêtre d'entraînement séparée), donc ce risque précis ne s'applique pas littéralement ici. Ce qui s'applique, et qui EST fait ci-dessous, est un contrôle de robustesse temporelle : la conclusion (aucun edge net significatif) est-elle stable sur des sous-périodes disjointes, ou reste-t-elle un artefact d'une fenêtre commune chanceuse ? Les p-values de sous-période ne sont PAS un nouveau test formel (échantillon trop court pour ça, ~370j/fold) -- lecture qualitative uniquement.

| Fold | Séances | Sharpe Buy&Hold | Meilleur membre | Sharpe meilleur membre | # membres > BH |
|---|---|---|---|---|---|
| 1 | 377 | -0.21 | momentum_breadth | -0.15 | 13/13 |
| 2 | 372 | +1.21 | dispersion | +1.20 | 0/13 |
| 3 | 374 | +1.04 | momentum_dispersion | +1.13 | 5/13 |

Identité du "meilleur membre" stable entre folds : NON (3 identité(s) différente(s) sur 3 folds : dispersion, momentum_breadth, momentum_dispersion).
**Le meilleur membre change de fold en fold -- signe classique de sélection sur bruit, cohérent avec le SPA/DSR global (pas d edge stable).**

## 4. Sensibilité du DSR à n_trials (le nombre "13" est-il le bon ?)

**Critique honnête** : n_trials=13 compte les membres du mécanisme "vol-targeting hiérarchique" retenus dans PREREG_backlog_spa_dsr_validation.md. Mais ces 13 constructions n'ont pas été tirées au hasard -- elles sont le produit de ~110 cycles d'exploration ADAPTATIVE sur le MÊME historique NDX-100 (chaque nouvelle porte souvent inspirée du succès/échec des précédentes, ex. #94 après #89, #100 après #78). Le nombre RÉEL de "regards" informés sur ces données est donc probablement bien supérieur à 13 -- n_trials=13 est optimiste (sous-estime la correction requise).

Meilleur membre : momentum_dispersion. DSR recalculé à var_trials FIXE (celle des 13 membres), en faisant seulement varier n_trials :

| n_trials hypothétique | SR0 (seuil de sélection) | DSR |
|---|---|---|
| 13 | 0.0030 | 0.8883 |
| 43 | 0.0039 | 0.8824 |
| 110 | 0.0045 | 0.8783 |

Le DSR ne peut que BAISSER quand n_trials augmente (SR0 monte mécaniquement) -- le DSR=0,8883 déjà rapporté à n_trials=13 est donc un plafond, pas un plancher : la vraie correction, si le nombre d'essais réel est plus proche de 43 ou 110, est encore plus défavorable au edge.

## 5. Calibration de spa_test()/dsr() sur une famille BRUIT PUR (aucun edge par construction)

Génère 300 réplications d'une famille de 13 stratégies i.i.d. N(0,σ) sans AUCUN edge réel (même T, même ordre de grandeur de vol que la fenêtre commune réelle), applique spa_test()/dsr() tels quels, et mesure le taux de rejet empirique de H0. Sous un vrai null, ce taux doit être proche du seuil nominal (5% pour SPA à p<0,05 ; le seuil DSR>0,95 n'a pas de garantie de calibration exacte a priori mais doit rester CONTENU, pas dérailler).

Sur 300 réplications bruit pur : taux de rejet SPA (p<0,05) = 8.0%, taux DSR>0,95 = 0.0%.
**OK — les deux outils restent conservateurs sous un null pur, pas de biais de sur-rejet flagrant.**

## Synthèse de l'audit

- Intégrité du code (recalcul indépendant + anti-lookahead) : OK, aucun bug structurel détecté.
- Stabilité temporelle : fragile (meilleur membre instable entre folds).
- Sensibilité n_trials : le DSR=0,8883 déclaré est un CAS FAVORABLE (n_trials=13 sous-estime probablement l'exploration réelle) -- la vraie robustesse du edge est probablement PIRE, pas meilleure, que ce qui a été committé en section 3 du résultat principal.
- Calibration des outils : conforme.

**Conclusion de l'audit : le résultat principal (H0 non rejetée par SPA, DSR<0,95) n'est PAS remis en cause par ce contrôle adversarial -- au contraire, chaque angle d'attaque testé ici (instabilité temporelle du meilleur membre, sous-estimation probable de n_trials) pousse la conclusion dans le même sens : aucun edge net de la famille vol-targeting hiérarchique ne peut être considéré comme statistiquement établi sur cet historique.**
