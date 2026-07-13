"""Etape B - modele de prediction directionnelle : features + triple barrier +
walk-forward purge/embargo + metriques de trading + Deflated Sharpe Ratio.
Produit results/etape_B_prediction.md.

PROTOCOLE FIGE AVANT EXECUTION (anti data-snooping, cf. Etape C) :
- Univers de 4 signaux declares, aucun ajout a posteriori (N=4 pour le DSR) :
    1. Buy & Hold (toujours long)          - benchmark de reference
    2. Momentum (signe du rendement 10 j)  - regle simple, zero apprentissage
    3. Regression logistique L2            - modele parcimonieux (litterature :
                                             la parcimonie bat souvent XGBoost)
    4. Gradient boosting (HistGB)          - analogue XGBoost/LightGBM
- Labeling : triple barrier H=5 j, barrieres +/-1.5*sigma_local (ewm 20 j)
- Features : cf. src/prediction.py (techniques + regime + fracdiff), causales
- Walk-forward : fenetre initiale 750 obs, expansive, re-estimation mensuelle
  (21 j), PURGE/EMBARGO de 5 j (= horizon du label)
- Couts : 5 bps aller-retour par changement de position
- Evaluation : Sharpe/Sortino/Calmar/MDD/profit factor NETS ; Deflated Sharpe
  Ratio (N=4 essais) ; test de lookahead par delai d'execution 0/1/2/3 barres
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc  # noqa: E402
from prediction import (  # noqa: E402
    backtest,
    build_features,
    dsr,
    trading_metrics,
    triple_barrier_labels,
    walk_forward_signals,
)

# ------------------------------------------------------------------ protocole
T0, REFIT_EVERY, EMBARGO, H = 750, 21, 5, 5
VOL_SPAN, BARRIER_MULT = 20, 1.5
COST_BPS = 5.0
SEED = 42

DATA = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data" / "nasdaq_composite_daily.txt")
OUT = sys.argv[2] if len(sys.argv) > 2 else str(ROOT / "results" / "etape_B_prediction.md")

df = load_ohlc(DATA).set_index("date")
close = df["close"].astype(float)
logp = np.log(close)
# rendement futur t->t+1 (la position decidee en t le capture)
r_fwd = logp.shift(-1) - logp
r_fwd = r_fwd.values

X = build_features(df)
y = triple_barrier_labels(df.reset_index(), horizon=H, vol_span=VOL_SPAN,
                          mult=BARRIER_MULT)
y.index = df.index
n = len(df)
dates = df.index


def logistic():
    return LogisticRegression(C=0.5, max_iter=1000)


def hgb():
    return HistGradientBoostingClassifier(
        max_depth=3, max_iter=150, learning_rate=0.05,
        l2_regularization=1.0, min_samples_leaf=40, random_state=SEED)


# ------------------------------------------------------------- signaux figes
pos = {}
pos["BuyHold"] = np.ones(n)
mom = (logp - logp.shift(10)).values
pos["Momentum"] = np.where(np.isfinite(mom), np.sign(mom), 0.0)
pos["Momentum"][pos["Momentum"] == 0] = 1.0  # convention : long par defaut
pos["LogitL2"] = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), logistic,
                                      T0, REFIT_EVERY, EMBARGO, standardize=True)
pos["HistGB"] = walk_forward_signals(X, y, pd.Series(r_fwd, index=dates), hgb,
                                     T0, REFIT_EVERY, EMBARGO, standardize=False)
MODELS = ["BuyHold", "Momentum", "LogitL2", "HistGB"]

# fenetre OOS commune (a partir de T0, la ou tous les modeles decident)
oos = np.arange(T0, n - 1)  # -1 : r_fwd[n-1] est NaN (pas de lendemain)

# ------------------------------------------------------------- backtests OOS
pnl = {m: backtest(pos[m], r_fwd, COST_BPS)[oos] for m in MODELS}
metr = {m: trading_metrics(pnl[m]) for m in MODELS}

# directional accuracy des modeles ML (sur labels binaires non nuls, OOS)
ylab = (y.values > 0).astype(float)
acc = {}
for m in ("Momentum", "LogitL2", "HistGB"):
    p = pos[m][oos]
    yt = ylab[oos]
    valid = np.isfinite(p) & np.isfinite(y.values[oos])
    pred_up = (p[valid] > 0).astype(float)
    acc[m] = float((pred_up == yt[valid]).mean())

# ------------------------------------------- Deflated Sharpe Ratio (N=4 essais)
sr_daily = {m: metr[m]["sharpe_daily"] for m in MODELS}
var_trials = float(np.var(list(sr_daily.values()), ddof=1))
T_oos = len(oos)
dsr_out = {}
for m in MODELS:
    dsr_out[m] = dsr(sr_daily[m], T_oos, var_trials, n_trials=len(MODELS),
                     skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])

# -------------------------------------- test de lookahead (delai d'execution)
best = max(("LogitL2", "HistGB"), key=lambda m: metr[m]["sharpe_ann"])
delay_sh = {}
for d in (0, 1, 2, 3):
    delay_sh[d] = trading_metrics(backtest(pos[best], r_fwd, COST_BPS, delay=d)[oos])["sharpe_ann"]

# ------------------------------------------- analyse cout de rupture (break-even)
be = {}
for m in ("Momentum", "LogitL2", "HistGB"):
    turn = np.abs(np.diff(pos[m][oos], prepend=pos[m][oos][0])).mean()
    gross_daily = (pos[m] * r_fwd)[oos]
    gross_mu = np.nanmean(gross_daily)
    be[m] = 1e4 * gross_mu / turn if turn > 0 else np.nan  # bps/trade a Sharpe=0


# ------------------------------------------------------------------ rapport md
lines = []
w = lines.append
w("# Étape B — Modèle de prédiction directionnelle (NASDAQ Composite, quotidien)\n")

w("## 1. Cadrage (dicté par l'Étape A et la revue de littérature)\n")
w("- L'Étape A a **rejeté l'exploitabilité de l'autocorrélation du rendement** "
  "(random walk non rejeté, z\\* robustes non significatives). On ne prédit donc "
  "**pas un prix** (naïve forecast → R² artificiel) mais une **direction**.")
w("- Cible : **triple barrier** (López de Prado) H=5 j, barrières "
  f"±{BARRIER_MULT}·σ_local (σ = ewm {VOL_SPAN} j) → labels adaptatifs au régime.")
w(f"- Features causales (cf. `src/prediction.py`) : rendements retardés, momentum, "
  "ratios de moyennes, volatilité rolling, Parkinson, drawdown, RSI, MACD, "
  "Bollinger %b, ATR, Stochastic, **differenciation fractionnaire** (d=0.4).")
w(f"- Walk-forward expansif : train initial {T0} obs, ré-estim. tous les "
  f"{REFIT_EVERY} j, **purge/embargo {EMBARGO} j** (= H, anti-fuite de labels). "
  f"Coûts **{COST_BPS:.0f} bps** aller-retour. OOS = {T_oos} jours "
  f"({dates[oos[0]]:%d/%m/%Y} → {dates[oos[-1]]:%d/%m/%Y}).\n")

w("## 2. Univers de signaux (FIGÉ avant évaluation — N=4 pour le DSR)\n")
w("| # | Signal | Nature |")
w("|---|---|---|")
w("| 1 | Buy & Hold | benchmark, toujours long |")
w("| 2 | Momentum (signe rdt 10 j) | règle simple, sans apprentissage |")
w("| 3 | Régression logistique L2 | modèle parcimonieux |")
w("| 4 | Gradient boosting (HistGB) | analogue XGBoost/LightGBM |")
w("")

w("## 3. Performance out-of-sample (nette de coûts)\n")
w("| Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Profit factor | Hit rate |")
w("|---|---|---|---|---|---|---|---|")
for m in MODELS:
    x = metr[m]
    w(f"| {m} | {x['sharpe_ann']:+.2f} | {x['sortino_ann']:+.2f} | "
      f"{x['calmar']:+.2f} | {x['ann_return_pct']:+.1f} % | {x['max_drawdown_pct']:.1f} % | "
      f"{x['profit_factor']:.2f} | {100*x['hit_rate']:.1f} % |")
w("\n*Le R² est volontairement absent : c'est une métrique trompeuse pour le "
  "trading (un R²≈0.97 peut n'être qu'un naïve forecast). Seules les métriques "
  "de risque/rendement nettes comptent.*\n")

w("## 4. Précision directionnelle (accuracy) sur l'OOS\n")
w("| Signal | Accuracy directionnelle |")
w("|---|---|")
for m in ("Momentum", "LogitL2", "HistGB"):
    w(f"| {m} | {100*acc[m]:.2f} % |")
w("\n*Repère : une accuracy de 53–55 % suffit à générer de l'alpha si bien tradée ; "
  "≈50 % = pas d'edge directionnel.*\n")

w("## 5. Deflated Sharpe Ratio (Bailey & López de Prado, 2014)\n")
w(f"Correction du data-snooping (N={len(MODELS)} essais, "
  f"σ²(SR essais)={var_trials:.4e}) et de la non-normalité des rendements. "
  "DSR = P(vrai Sharpe > 0 | sélection sur le max).\n")
w("| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |")
w("|---|---|---|---|---|")
for m in MODELS:
    d = dsr_out[m]
    w(f"| {m} | {sr_daily[m]:+.4f} | {d['sr0_daily']:.4f} | {d['z']:+.2f} | "
      f"**{d['dsr']:.3f}** |")
w("\n*DSR > 0.95 = Sharpe crédible après correction ; DSR faible = performance "
  "probablement due au hasard / à la sélection.*\n")

w("## 6. Test de détection du lookahead (délai d'exécution)\n")
w(f"Signal testé : **{best}**. Un vrai edge se dégrade **graduellement** avec le "
  "délai ; un lookahead s'effondre **verticalement** entre 0 et 1 barre.\n")
w("| Délai (barres) | 0 | 1 | 2 | 3 |")
w("|---|---|---|---|---|")
w(f"| Sharpe ann. | {delay_sh[0]:+.2f} | {delay_sh[1]:+.2f} | "
  f"{delay_sh[2]:+.2f} | {delay_sh[3]:+.2f} |")
collapse = (delay_sh[0] - delay_sh[1])
grad = "graduelle → **pas de lookahead détecté**" if abs(collapse) < abs(delay_sh[0]) * 0.6 + 0.3 \
    else "effondrement 0→1 → **lookahead suspecté**"
w(f"\n*Dégradation 0→1 : {collapse:+.2f} de Sharpe — {grad}.*\n")

w("## 7. Analyse du coût de rupture (break-even)\n")
w("Coût maximal (bps/trade) supportable avant Sharpe nul, au turnover observé :\n")
w("| Signal | Break-even (bps/trade) | vs coût réel 5 bps |")
w("|---|---|---|")
for m in ("Momentum", "LogitL2", "HistGB"):
    verdict = "marge positive" if be[m] > COST_BPS else "sous le coût réel → non rentable"
    w(f"| {m} | {be[m]:+.2f} | {verdict} |")
w("")

w("## 8. Verdict honnête\n")
best_dsr = max(MODELS, key=lambda m: dsr_out[m]["dsr"])
active = ("Momentum", "LogitL2", "HistGB")
best_active = max(active, key=lambda m: metr[m]["sharpe_ann"])
any_credible = any(dsr_out[m]["dsr"] > 0.95 and metr[m]["sharpe_ann"] > metr["BuyHold"]["sharpe_ann"]
                   for m in active)
n_years = (dates[oos[-1]] - dates[oos[0]]).days / 365.25
w(f"- Échantillon OOS : {T_oos} jours (~{n_years:.0f} ans, "
  f"{dates[oos[0]]:%m/%Y}→{dates[oos[-1]]:%m/%Y}). Meilleur DSR : "
  f"**{best_dsr}** ({dsr_out[best_dsr]['dsr']:.3f}).")
if any_credible:
    w(f"- **{best_active} bat le Buy & Hold avec un DSR > 0.95** : edge "
      "directionnel crédible sur cet échantillon, à confirmer en live (haircut).")
else:
    ba = metr[best_active]
    profitable = ba["sharpe_ann"] > 0 and be[best_active] > COST_BPS
    w("- **Aucun signal actif ne bat le Buy & Hold avec un DSR > 0.95.** "
      + (f"Le meilleur signal actif ({best_active}) est cependant **rentable net de "
         f"coûts** (Sharpe {ba['sharpe_ann']:+.2f}, break-even {be[best_active]:.0f} bps "
         f"> {COST_BPS:.0f} bps réels) mais reste **en-dessous du simple achat-conservation** "
         "sur base ajustée du risque et déflatée."
         if profitable else
         "Pas d'edge directionnel robuste net de coûts ; accuracy ≈ 50 % le confirme.")
      + " Cohérent avec l'Étape A (efficience à court terme).")
w("- **Discipline** : l'univers (N=4) et le protocole sont figés dans ce script "
  "AVANT évaluation. On n'élargit pas l'univers jusqu'à obtenir un chiffre "
  "plaisant : le renforcement passe par **plus de données** (historique ≥ 2000, "
  "2008 et dot-com), de **meilleures features** (microstructure intraday, "
  "sentiment FinBERT), ou un **horizon différent** — puis re-test unique au DSR.")
w("- Rappel litt. : dégradation médiane backtest→live de **73 %** (Suhonen et al.) ; "
  "tout Sharpe backtest > 3 est un **red flag**. Les attentes sont calibrées en "
  "conséquence.\n")

out = Path(OUT)
out.write_text("\n".join(lines))
print("\n".join(lines))
