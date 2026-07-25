# Audit critique — Code overlay.py + run_etape_d_optimize.py

## 🚨 Issues détectées (ordre de sévérité)

### Issue #1 : Vol-targeting qui monte avec la volatilité = broken en krach
**Code:** `src/overlay.py`, ligne 114
```python
vtar = realized_ann_vol_pct(r[:tr])  # Recalculé à chaque refit
```

**Problème:**
- `vol_target` = volatilité historique RÉALISÉE de Buy & Hold sur [0:tr]
- À chaque refit, si vol réalisée monte (krach), `vol_target` monte aussi
- Formule : `exposure = clip(vol_target / vol_fcst, 0, cap)`
- Conséquence : En krach, `vol_target` monte → numérateur monte → exposure réduite MOINS
- **C'est l'inverse de ce qu'on veut !** On veut réduire exposition PLUS en krach.

**Exemple concret (NDX 2000-2002 krach):**
- Pre-krach: vol_target = 15%, vol_fcst = 20% → exposure = 75%
- During krach: vol_target = 25%, vol_fcst = 60% → exposure = 42%
- Attendu: exposure = 15%/60% ≈ 25%
- Réel: 25%/60% ≈ 42% (pas assez réduit)

**Fix proposé:** `vol_target` doit être une constante historique (ex: moyenne pre-krach), pas recalculée dynamiquement.

---

### Issue #2 : Lookahead caché dans la recursion GARCH
**Code:** `src/overlay.py`, ligne 111 + `volatility.py::garch_path()`
```python
path = garch_path(r, p, gjr=True)  # r complète, params de r[:tr]
vol_ann_in = ANNUALIZE * np.sqrt(path[:tr])  # Prévisions "passées"
```

**Problème:**
- `garch_path(r, p, gjr=True)` évalue la variance COMPLÈTE (tous les t) avec params estimés sur r[:tr]
- Pour t < tr, la récursion GARCH utilise tous les rendements jusqu'à t-1 (OK)
- Mais pour t >= tr, on utilise params estimés sur données incluant t-1 (OK aussi)
- **CEPENDANT:** à chaque refit (tr = tr+21), les params changent
- Conséquence : path[t] se recalcule à chaque refit, créant une "variable" variance forecast pour le même t
- **C'est du lookahead proxy:** path[t] à tr=1000 vs path[t] à tr=1021 sont différents, même t.
- Implication : dans le backtest, vol_fcst[t] n'est pas une vraie prévision one-step-ahead, c'est une version "mise à jour" rétroactivement.

**Fix proposé:** Walk-forward strict : pour t in [tr, tr+refit], calculer path[t] uniquement avec params de r[:tr], ne pas recalculer.

---

### Issue #3 : Turnover calc oublie le flux initial (cash → position)
**Code:** `scripts/run_etape_d_optimize.py`, ligne 111
```python
turnover = float(np.mean(np.abs(np.diff(pos[idx], prepend=pos[idx][0]))))
```

**Problème:**
- `np.diff(pos[idx], prepend=pos[idx][0])` = [pos[T0] - pos[T0], pos[T0+1] - pos[T0], ...]
- Le premier élément est 0 (pas de changement de pos[T0] à pos[T0])
- Mais il y a un changement de cash (1.0) à pos[T0] au jour T0 !
- Cela réduit le turnover calculé.

**Dans backtest():**
- Comment backtest() calcule-t-il le coût ?
- Besoin de vérifier: est-ce sur np.diff() aussi, ou sur quelque chose d'autre ?
- **Risk:** Turnover calc et backtest() peuvent être désalignés.

---

### Issue #4 : Vol threshold fixé in-sample mais sur PRÉVISIONS passées, pas réalisations
**Code:** `src/overlay.py`, ligne 113
```python
vol_ann_in = ANNUALIZE * np.sqrt(path[:tr])  # Prévisions GJR-t
thresh = float(np.percentile(vol_ann_in, extreme_pctl))
```

**Problème:**
- `vol_ann_in` = vol GJR-t *prévues* sur la fenêtre d'entraînement
- Ce ne sont pas les vol *réalisées*, ce sont les prévisions passées
- Si le modèle GJR-t est biaisé (ex: sous-estime vol), le percentile sera biaisé
- Conséquence : le seuil de coupe peut ne pas correspondre aux vrais 95e percentile des réalisations

**Fix proposé:** Thresh doit être calculé sur vol RÉALISÉES (carré des rendements), pas vol prévues.

---

### Issue #5 : DSR variance calc suppose 12 combos indépendants (faux)
**Code:** `scripts/run_etape_d_optimize.py`, ligne 117
```python
var_trials = float(np.var(sr_daily, ddof=1))
```

**Problème:**
- Les 12 combos partagent le même `vol_fcst` et `vol_target`
- Ils ne diffèrent que par (cap, pctl) qui change l'exposition post-hoc (clip et extreme_cut)
- Conséquence : les 12 Sharpe journaliers ne sont pas i.i.d., ils sont corrélés
- La variance des Sharpe sous-estime la variance vraie de l'univers
- DSR sous-estime le risque de multiple testing

**Impact:** DSR peut être over-optimistic pour les 12 combos.

---

### Issue #6 : Composite 5y (1251 jours) trop petit pour être robuste
**Code implicitly** (CLAUDE.md, `results/etape_B_prediction.md`)
- Composite: 1251 séances ≈ 5 ans
- Walk-forward: T0=750 (3 ans) → OOS = 500 observations (~2 ans)
- Refit cycle de 21j → ~24 refits en OOS
- **Problem:** Avec si peu de refits, variance estimée très élevée, DSR très bruité.

---

### Issue #7 : Cross-market fail non investigué
**Code:** Backtest sur Russell/S&P/DAX monte que 0/3 combos généralisent
- Paramétrage NDX (cap 2.0×, pctl 90) échoue sur S&P 500
- Pas d'audit: pourquoi ? Vol distribution différente ? Model instability ?
- Implication : le modèle peut être NDX-lucky, pas universel.

---

## 🔍 Recommandation immédiate

Avant paper trading, besoin de :
1. **Fix #1 (critique):** vol_target ne doit pas être recalculée dynamiquement
2. **Fix #2 (critique):** Vrai walk-forward (pas de recalc rétroactive)
3. **Audit #3:** Aligner turnover calc avec backtest() cost model
4. **PBO/CSCV:** Mesurer le overfitting des 12 combos (voir calcul ci-dessous)
5. **Cross-market root cause:** Investiguer pourquoi NDX params échouent ailleurs

