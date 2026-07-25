# Hypothese regime-aware R5 (leçon du paradoxe H10)

## 1. Contexte

`H10` (results/hypothesis_10_mean_reversion_lowvol.json) a gate un signal **faible** (H1, RSI mean-reversion, Sharpe 0.213) par le regime de volatilite : resultat paradoxal, le gate **detruit** le signal (Sharpe -0.47 en tercile bas seul, -0.36 en version scalee). Question ici : le meme type de gate detruit-il aussi **R5** ("Fractional Differentiation"), repute plus robuste ?

**Correction methodologique** : le R5 original (`run_risky_hypotheses.py`, Sharpe brut affiche 0.534) standardise sa serie fractionnairement differenciee avec la **moyenne/ecart-type de l'echantillon complet** — lookahead flagrant, son chiffre est invalide. Ici R5 est reconstruit de facon strictement causale : `frac_diff` (fenetre fixe, deja utilisee et causale dans l'Etape B) + z-score sur fenetre **roulante** (250 j). Le protocole walk-forward suit exactement l'Etape B : T0=750, refit 21 j, **purge/embargo 21 j** (les seuils de regime de volatilite sont recalcules tous les 21 j a partir des donnees jusqu'a t-embargo uniquement — aucune fuite), couts 5 bps.

## 2. Univers fige (N=6 essais sur ce signal, pour le DSR)

| # | Variante | Regle |
|---|---|---|
| 0 | R5_base | signal causal, sans gate (reference) |
| 1 | R1_LowVolOnly | trade seulement si vol tercile BAS, sinon plat |
| 2 | R2_VolScaled | position × {1.0 bas, 0.5 moyen, 0.25 haut} |
| 3 | R3_TrendGate | trade seulement si EMA50 vs EMA200 s'aligne avec R5 |
| 4 | R4_DualGate | R1 ET R3 simultanement |
| 5 | R5x_Contrarian | ignore le signe de R5 : court en vol basse, long en vol haute |

## 3. Performance OOS (nette de couts, NDX)

Fenêtre OOS : 9522 jours (1988-09-19 → 2026-07-10).

| Variante | Sharpe ann. | Calmar | MDD | Turnover moy. | Profit factor | **DSR** |
|---|---|---|---|---|---|---|
| **Buy & Hold** | +0.52 | +0.08 | -82.9% | 0.00 | 1.10 | — |
| R5_base | -0.26 | -0.02 | -96.5% | 0.368 | 0.95 | 0.002 |
| R1_LowVolOnly | -0.17 | -0.01 | -74.1% | 0.124 | 0.95 | 0.009 |
| R2_VolScaled | -0.24 | -0.02 | -80.1% | 0.213 | 0.96 | 0.003 |
| R3_TrendGate | +0.16 | +0.03 | -65.5% | 0.188 | 1.04 | 0.371 |
| R4_DualGate | +0.02 | +0.00 | -47.3% | 0.072 | 1.01 | 0.117 |
| R5x_Contrarian | -0.02 | -0.00 | -90.8% | 0.061 | 1.00 | 0.080 |

*DSR calcule avec N=6 (les essais de cette hypothese uniquement). **Avertissement anti data-snooping** : cette hypothese s'inscrit dans une exploration bien plus large (H1-H12, R1-R10 dans `results/`) ; un DSR correctement deflate sur l'ensemble de cette exploration serait sensiblement **plus bas** que celui affiche ici (N reel ≫ 6). Ces chiffres ne remplacent pas l'univers fige et le SPA de l'Etape B/C.*

## 4. Statistiques de regime (OOS)

| Regime | % du temps OOS | Hit-rate directionnel R5_base |
|---|---|---|
| low | 31.7% | 53.0% |
| mid | 30.0% | 51.5% |
| high | 38.4% | 50.0% |

*0.0% des jours OOS sans regime defini (warmup des seuils, ignores dans le backtest -> position nulle).*

## 5. Verdict honnête

- **Le gating aide** : R3_TrendGate (Sharpe +0.16) bat R5_base (Sharpe -0.26). Contrairement au paradoxe H10, le regime-gating n'est pas systematiquement destructeur — mais cela reste a confirmer par le turnover/couts et le DSR (colonne ci-dessus).
- **R5_base lui-meme** (une fois le lookahead corrige) a un Sharpe negatif ou nul (-0.26) et reste en-dessous du Buy & Hold (+0.52). Le chiffre de 0.534 dans `risky_hypotheses.json` (methode non causale) n'est **pas reproductible** en walk-forward honnete : la robustesse pretee a R5 etait en grande partie un artefact de lookahead.
- Discipline : ceci reste **un essai de plus** sur un signal deja explore de facon non canonique (hors univers fige de l'Etape B) ; a ne pas confondre avec un edge valide au sens du SPA/DSR de l'Etape B/C.
