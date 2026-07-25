"""Signaux alternatifs (A1-A6) - univers ignore par l'Etape B, teste separement.

MISSION : l'Etape B a fige un univers N=4 (BuyHold, Momentum, LogitL2, HistGB)
et conclu que Buy & Hold reste la meilleure strategie testee (cf. CLAUDE.md).
Ce script teste un DEUXIEME univers, DISJOINT et FIGE AVANT EVALUATION, de
6 signaux "a base de regle" jamais evalues rigoureusement dans ce repo avec
le protocole walk-forward strict (les scripts run_hypothesis_*.py anterieurs
calculent certains indicateurs/seuils sur l'ECHANTILLON COMPLET - percentile
95 de la vol sur toute la serie, frac_diff standardise globalement - ce qui
introduit un lookahead ; ce script ne reproduit PAS ce biais).

Univers FIGE (N=6, aucun ajout a posteriori) :
  A1  RSI(14) simple            - mean-reversion classique (seuils 30/70),
                                   sert de baseline de comparaison pour A2.
  A2  RSI(14) + vol-targeting   - meme signal RSI qu'A1, expose via un
                                   overlay vol-targeting + coupe defensive
                                   (analogue a l'hypothese H12 du repo, qui
                                   combinait FracDiff + vol-targeting ; ici
                                   on remplace FracDiff par RSI). cap=1.5x,
                                   coupe a 0.5x au-dela du 95e percentile
                                   in-sample de la vol realisee (calcule
                                   EN WALK-FORWARD, jamais sur tout
                                   l'echantillon - correction du biais H12).
  A3  CCI(20)                   - alternative de mean-reversion a RSI,
                                   seuils textbook +/-100.
  A4  Donchian(20) breakout     - suivi de tendance classique (turtle
                                   trading), casse du plus haut/bas sur
                                   20 seances, position tenue jusqu'a la
                                   casse opposee.
  A5  ATR trend + stop          - entree sur expansion de volatilite (ATR14
                                   > 1.2x sa moyenne mobile 50j) dans le sens
                                   de la tendance (close vs EMA50), sortie
                                   par stop suiveur de type Chandelier
                                   (k=3x ATR14 depuis l'extreme atteint).
  A6  Autocorrelation (ACF-1)   - version RAFFINEE du R10 (deja teste,
                                   Sharpe -0.198, cf. HYPOTHESIS_TESTING_
                                   RESULTS.md). Bug de R10 : position =
                                   signe(ACF) SEUL, independant du sens du
                                   dernier rendement -> pas un signal
                                   directionnel coherent. Fix : position =
                                   signe(ACF_1) * signe(r_t) SI |ACF_1| est
                                   statistiquement significative (test
                                   asymptotique |ACF|>1.96/sqrt(fenetre)),
                                   sinon plat. ACF>0 -> on suit le dernier
                                   rendement (regime de tendance) ; ACF<0
                                   -> on le fade (regime de retour a la
                                   moyenne). Fenetre 60j (vs 50j pour R10).

Toutes les regles sont CAUSALES (n'utilisent que l'information disponible a
la cloture du jour t) et tous les seuils/parametres sont FIXES A PRIORI
(valeurs textbook standard), jamais recalibres apres avoir vu les resultats
OOS. Pour A2, le seuil de coupe et le vol_target sont recalcules en
walk-forward (refit tous les REFIT_EVERY jours, uniquement sur le passe -
meme discipline que src/overlay.py::walk_forward_vol_forecast).

Protocole d'evaluation (identique a l'Etape B, meme fenetre pour
comparabilite directe) :
  NDX (nasdaq100_daily.txt), T0=750, refit=21j, embargo=21j, couts=5 bps
  aller-retour. Le refit/embargo n'a de sens mecanique que pour A2 (seul
  signal ici avec un parametre recalibre en walk-forward) ; les 5 autres
  signaux (A1, A3, A4, A5, A6) sont des regles deterministes sans
  estimation -> aucun risque de fuite train/test, l'embargo ne s'applique
  donc pas litteralement mais la fenetre OOS commune (a partir de T0) est
  conservee pour que les resultats restent comparables aux Etapes B/D.

Sortie : results/alt_signals_A1_A6.md (tableau classe par Sharpe) et
results/alt_signals_A1_A6.json (donnees completes).

DSR (Deflated Sharpe Ratio) : univers de N=7 essais (BuyHold + A1..A6),
meme convention que scripts/run_etape_b.py (BuyHold compte comme un essai
parmi les variantes comparees, pas juste un chiffre de reference externe).
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

FILE = Path(__file__).resolve()
FINANCE = FILE.parents[2]          # .../finance
REPO_ROOT = FILE.parents[3]        # .../Quant-Trade
RESULTS_DIR = FILE.parents[1] / "results"  # .../finance/trading/results
sys.path.insert(0, str(FINANCE / "src"))
warnings.filterwarnings("ignore")

from data_loader import load_ohlc  # noqa: E402
from prediction import backtest, dsr, trading_metrics  # noqa: E402
from prediction import _atr as atr_ind  # noqa: E402
from prediction import _rsi as rsi_ind  # noqa: E402

# ------------------------------------------------------------------ protocole
T0, REFIT_EVERY, EMBARGO = 750, 21, 21
COST_BPS = 5.0
TRADING_DAYS = 252

DATA = sys.argv[1] if len(sys.argv) > 1 else str(REPO_ROOT / "data" / "nasdaq100_daily.txt")
OUT_MD = sys.argv[2] if len(sys.argv) > 2 else str(RESULTS_DIR / "alt_signals_A1_A6.md")
OUT_JSON = sys.argv[3] if len(sys.argv) > 3 else str(RESULTS_DIR / "alt_signals_A1_A6.json")

df = load_ohlc(DATA).set_index("date")
close = df["close"].astype(float)
high = df["high"].astype(float)
low = df["low"].astype(float)
logp = np.log(close)
r = logp.diff()                 # rendement log du jour t, connu a la cloture t
r_fwd = (logp.shift(-1) - logp).values  # rendement t -> t+1 (applique a la position decidee en t)
n = len(df)
dates = df.index

r_np = r.values


# ----------------------------------------------------------------------------
# A1 - RSI(14) simple (baseline mean-reversion)
# ----------------------------------------------------------------------------
def signal_A1_rsi() -> np.ndarray:
    rsi = rsi_ind(close, 14)
    pos = np.zeros(n)
    pos[rsi.values < 30] = 1.0   # survendu -> long (rebond attendu)
    pos[rsi.values > 70] = -1.0  # surachete -> short
    return pos


# ----------------------------------------------------------------------------
# A2 - RSI(14) + overlay vol-targeting (walk-forward, sans fuite)
# ----------------------------------------------------------------------------
def signal_A2_rsi_voltarget(base_signal: np.ndarray) -> dict:
    """Expose le signal RSI (A1) via un overlay vol-targeting + coupe defensive.

    Parametres fixes a priori (analogues a l'hypothese H12 du repo) :
      cap = 1.5x, coupe = 0.5x l'exposition si vol realisee annualisee
      depasse le 95e percentile IN-SAMPLE (walk-forward, refit REFIT_EVERY j).
    vol_target : vol realisee annualisee de Buy & Hold sur [0:T0], FIXEE une
    fois pour toutes (meme discipline anti-fuite que src/overlay.py, qui a
    corrige exactement ce bug le 2026-07-14 : ne jamais recalculer la cible
    avec des rendements posterieurs a T0).
    """
    cap, cut_frac, pctl = 1.5, 0.5, 95.0
    vol20_ann = r.rolling(20).std().values * np.sqrt(TRADING_DAYS)
    vol_target_const = float(np.nanstd(r_np[:T0], ddof=1) * np.sqrt(TRADING_DAYS))

    exposure = np.zeros(n)
    thresh_used = np.full(n, np.nan)
    for tr in range(T0, n, REFIT_EVERY):
        block = range(tr, min(tr + REFIT_EVERY, n))
        past_vol = vol20_ann[:tr]
        past_vol = past_vol[np.isfinite(past_vol)]
        thresh = float(np.percentile(past_vol, pctl)) if len(past_vol) > 0 else np.nan
        for t in block:
            v = vol20_ann[t]
            if not np.isfinite(v) or v <= 0:
                continue
            expo = np.clip(vol_target_const / v, 0.0, cap)
            if np.isfinite(thresh) and v > thresh:
                expo *= cut_frac
            exposure[t] = expo
            thresh_used[t] = thresh
    pos = exposure * base_signal
    pos[:T0] = 0.0  # avant T0 : hors evaluation (warmup, meme convention que B/D)
    return {"pos": pos, "vol_target_ann_pct": vol_target_const * 100}


# ----------------------------------------------------------------------------
# A3 - CCI(20) mean-reversion (alternative a RSI)
# ----------------------------------------------------------------------------
def signal_A3_cci() -> np.ndarray:
    tp = (high + low + close) / 3.0
    sma_tp = tp.rolling(20).mean()
    mad = (tp - sma_tp).abs().rolling(20).mean()
    cci = (tp - sma_tp) / (0.015 * mad.replace(0, np.nan))
    pos = np.zeros(n)
    cv = cci.values
    pos[np.nan_to_num(cv, nan=0.0) < -100] = 1.0
    pos[np.nan_to_num(cv, nan=0.0) > 100] = -1.0
    return pos


# ----------------------------------------------------------------------------
# A4 - Donchian(20) breakout (suivi de tendance)
# ----------------------------------------------------------------------------
def signal_A4_donchian() -> np.ndarray:
    upper = high.rolling(20).max().shift(1)  # canal sur les 20 j PRECEDENTES
    lower = low.rolling(20).min().shift(1)
    raw = pd.Series(0.0, index=df.index)
    raw[close > upper] = 1.0
    raw[close < lower] = -1.0
    pos = raw.replace(0.0, np.nan).ffill().fillna(0.0).values  # tenu jusqu'a la casse opposee
    return pos


# ----------------------------------------------------------------------------
# A5 - ATR trend + stop suiveur (Chandelier)
# ----------------------------------------------------------------------------
def signal_A5_atr_trend_stop() -> np.ndarray:
    atr = atr_ind(df, 14).values
    atr_sma50 = pd.Series(atr).rolling(50).mean().values
    ema50 = close.ewm(span=50, adjust=False).mean().values
    c = close.values
    spike_mult, k_atr = 1.2, 3.0

    pos = np.zeros(n)
    state = 0  # 0=flat, +1=long, -1=short
    extreme = np.nan
    for t in range(n):
        if not (np.isfinite(atr[t]) and np.isfinite(atr_sma50[t]) and np.isfinite(ema50[t])):
            pos[t] = state
            continue
        vol_spike = atr[t] > spike_mult * atr_sma50[t]
        if state == 0:
            if vol_spike and c[t] > ema50[t]:
                state, extreme = 1, c[t]
            elif vol_spike and c[t] < ema50[t]:
                state, extreme = -1, c[t]
        elif state == 1:
            extreme = max(extreme, c[t])
            if c[t] < extreme - k_atr * atr[t]:
                state, extreme = 0, np.nan
        elif state == -1:
            extreme = min(extreme, c[t])
            if c[t] > extreme + k_atr * atr[t]:
                state, extreme = 0, np.nan
        pos[t] = state
    return pos


# ----------------------------------------------------------------------------
# A6 - Autocorrelation ACF(1) raffinee (fix du R10 deja teste)
# ----------------------------------------------------------------------------
def signal_A6_acf_refined(window: int = 60) -> np.ndarray:
    pos = np.zeros(n)
    se_thresh = 1.96 / np.sqrt(window)
    for t in range(window, n):
        seg = r_np[t - window + 1:t + 1]
        if not np.all(np.isfinite(seg)):
            continue
        x, y = seg[1:], seg[:-1]
        if x.std() == 0 or y.std() == 0:
            continue
        acf1 = float(np.corrcoef(x, y)[0, 1])
        if not np.isfinite(r_np[t]):
            continue
        sgn = np.sign(r_np[t])
        if acf1 > se_thresh:
            pos[t] = sgn        # regime de tendance -> on suit le dernier rendement
        elif acf1 < -se_thresh:
            pos[t] = -sgn       # regime de retour a la moyenne -> on le fade
        # sinon : ACF non significative -> reste a 0 (plat)
    return pos


# ------------------------------------------------------------------- calculs
pos = {}
pos["BuyHold"] = np.ones(n)
pos["A1_RSI"] = signal_A1_rsi()
a2 = signal_A2_rsi_voltarget(pos["A1_RSI"])
pos["A2_RSI_VolTarget"] = a2["pos"]
pos["A3_CCI"] = signal_A3_cci()
pos["A4_Donchian20"] = signal_A4_donchian()
pos["A5_ATR_TrendStop"] = signal_A5_atr_trend_stop()
pos["A6_ACF_Refined"] = signal_A6_acf_refined()

for k in pos:
    pos[k] = np.nan_to_num(pos[k], nan=0.0)

MODELS = ["BuyHold", "A1_RSI", "A2_RSI_VolTarget", "A3_CCI", "A4_Donchian20",
          "A5_ATR_TrendStop", "A6_ACF_Refined"]
ALT_MODELS = [m for m in MODELS if m != "BuyHold"]

oos = np.arange(T0, n - 1)  # -1: r_fwd[n-1] est NaN (pas de lendemain)

pnl = {m: backtest(pos[m], r_fwd, COST_BPS)[oos] for m in MODELS}
metr = {m: trading_metrics(pnl[m]) for m in MODELS}
turnover = {m: float(np.abs(np.diff(pos[m][oos], prepend=pos[m][oos][0])).mean()) for m in MODELS}

# ------------------------------------------------- Deflated Sharpe Ratio (N=7)
sr_daily = {m: metr[m]["sharpe_daily"] for m in MODELS}
var_trials = float(np.var(list(sr_daily.values()), ddof=1))
T_oos = len(oos)
dsr_out = {}
for m in MODELS:
    dsr_out[m] = dsr(sr_daily[m], T_oos, var_trials, n_trials=len(MODELS),
                     skew=metr[m]["skew"], kurt_excess=metr[m]["excess_kurt"])

# -------------------------------------- test de detection du lookahead (best)
best_alt = max(ALT_MODELS, key=lambda m: metr[m]["sharpe_ann"])
delay_sh = {}
for d in (0, 1, 2, 3):
    delay_sh[d] = trading_metrics(backtest(pos[best_alt], r_fwd, COST_BPS, delay=d)[oos])["sharpe_ann"]

# ------------------------------------------------------------------ verdict
ranked = sorted(MODELS, key=lambda m: metr[m]["sharpe_ann"], reverse=True)
buyhold_sharpe = metr["BuyHold"]["sharpe_ann"]
buyhold_mdd = metr["BuyHold"]["max_drawdown_pct"]
beats_buyhold = [m for m in ALT_MODELS if metr[m]["sharpe_ann"] > buyhold_sharpe]
credible = [m for m in ALT_MODELS if dsr_out[m]["dsr"] > 0.95 and metr[m]["sharpe_ann"] > buyhold_sharpe]
mdd_improvers = [m for m in ALT_MODELS
                 if abs(metr[m]["max_drawdown_pct"]) < 0.7 * abs(buyhold_mdd)
                 and metr[m]["ann_return_pct"] > 0.8 * metr["BuyHold"]["ann_return_pct"]]

n_years = (dates[oos[-1]] - dates[oos[0]]).days / 365.25

# ------------------------------------------------------------------ rapport md
lines = []
w = lines.append
w("# Signaux alternatifs A1-A6 (NDX) — univers ignoré par l'Étape B\n")

w("## 1. Contexte et objectif\n")
w("L'Étape B a figé un univers N=4 (BuyHold, Momentum, LogitL2, HistGB) et "
  "conclu que **Buy & Hold reste la meilleure stratégie testée** (cf. "
  "CLAUDE.md). Ce script teste un **second univers disjoint**, figé avant "
  "évaluation, de 6 signaux à base de règles jamais évalués avec le "
  "protocole walk-forward strict de ce repo (contrairement aux scripts "
  "`run_hypothesis_*.py` antérieurs, qui calculent certains seuils sur "
  "l'échantillon complet — biais corrigé ici).\n")
w(f"Protocole : NDX (`{Path(DATA).name}`), T0={T0}, refit={REFIT_EVERY} j, "
  f"embargo={EMBARGO} j (mécaniquement pertinent seulement pour A2, seul "
  f"signal recalibré en walk-forward), coûts {COST_BPS:.0f} bps "
  f"aller-retour. OOS = {T_oos} jours (~{n_years:.0f} ans, "
  f"{dates[oos[0]]:%m/%Y}→{dates[oos[-1]]:%m/%Y}).\n")

w("## 2. Univers de signaux (FIGÉ avant évaluation — N=6 essais actifs)\n")
w("| # | Signal | Nature | Paramètres (fixés a priori) |")
w("|---|---|---|---|")
w("| A1 | RSI(14) simple | mean-reversion, baseline | seuils 30/70 (textbook) |")
w("| A2 | RSI(14) + vol-targeting | A1 + overlay risque (analogue H12) | "
  "cap 1.5x, coupe 0.5x >p95 vol réalisée (walk-forward) |")
w("| A3 | CCI(20) | mean-reversion, alternative à RSI | seuils ±100 (textbook) |")
w("| A4 | Donchian(20) breakout | suivi de tendance (turtle) | canal 20 j, tenu jusqu'à casse opposée |")
w("| A5 | ATR trend + stop Chandelier | entrée sur expansion de vol + tendance | ATR14>1.2×SMA50(ATR), EMA50, stop 3×ATR |")
w("| A6 | ACF(1) raffinée | régime tendance/retour à la moyenne | fenêtre 60 j, seuil signif. 1.96/√60 |")
w("")
w("*A6 corrige un défaut du signal `R10_ACF` déjà testé dans ce repo "
  f"(`HYPOTHESIS_TESTING_RESULTS.md`, Sharpe {-0.198:.3f}) : R10 posait "
  "position = signe(ACF) seul, indépendamment du sens du dernier rendement "
  "— ici position = signe(ACF₁) × signe(rₜ) si significatif, sinon plat.*\n")

w("## 3. Performance out-of-sample (nette de coûts), classée par Sharpe\n")
w("| Rang | Signal | Sharpe ann. | Sortino ann. | Calmar | Rdt ann. | MDD | Turnover | Profit factor | Hit rate |")
w("|---|---|---|---|---|---|---|---|---|---|")
for i, m in enumerate(ranked, 1):
    x = metr[m]
    tag = " **(BuyHold)**" if m == "BuyHold" else ""
    w(f"| {i} | {m}{tag} | {x['sharpe_ann']:+.2f} | {x['sortino_ann']:+.2f} | "
      f"{x['calmar']:+.2f} | {x['ann_return_pct']:+.1f} % | {x['max_drawdown_pct']:.1f} % | "
      f"{turnover[m]:.3f} | {x['profit_factor']:.2f} | {100*x['hit_rate']:.1f} % |")
w("\n*Le R² est volontairement absent (métrique trompeuse pour le trading, "
  "cf. Étape B). Turnover = variation moyenne absolue de position par jour "
  "OOS (proxy du coût de friction).*\n")

w("## 4. Deflated Sharpe Ratio (Bailey & López de Prado, 2014)\n")
w(f"Univers N={len(MODELS)} essais (BuyHold + A1..A6, même convention que "
  f"`run_etape_b.py`), σ²(SR essais)={var_trials:.4e}. DSR = P(vrai Sharpe > 0 "
  "| sélection sur le max).\n")
w("| Signal | Sharpe quotidien | seuil SR₀ | z | **DSR** |")
w("|---|---|---|---|---|")
for m in ranked:
    d = dsr_out[m]
    w(f"| {m} | {sr_daily[m]:+.4f} | {d['sr0_daily']:.4f} | {d['z']:+.2f} | "
      f"**{d['dsr']:.3f}** |")
w("")

w("## 5. A1 vs A2 — l'overlay vol-targeting aide-t-il le RSI ?\n")
a1, a2m = metr["A1_RSI"], metr["A2_RSI_VolTarget"]
mdd_reduc = 100 * (1 - abs(a2m["max_drawdown_pct"]) / abs(a1["max_drawdown_pct"])) if a1["max_drawdown_pct"] != 0 else float("nan")
w(f"- A1 (RSI brut) : Sharpe {a1['sharpe_ann']:+.2f}, MDD {a1['max_drawdown_pct']:.1f} %, "
  f"Calmar {a1['calmar']:+.2f}.")
w(f"- A2 (RSI + vol-targeting) : Sharpe {a2m['sharpe_ann']:+.2f}, MDD "
  f"{a2m['max_drawdown_pct']:.1f} %, Calmar {a2m['calmar']:+.2f} "
  f"(réduction de MDD vs A1 : {mdd_reduc:+.1f} %).")
verdict_overlay = ("l'overlay améliore le Sharpe ET réduit le MDD : bénéfice net."
                    if a2m["sharpe_ann"] > a1["sharpe_ann"] and abs(a2m["max_drawdown_pct"]) < abs(a1["max_drawdown_pct"])
                    else "l'overlay réduit le risque mais au prix du Sharpe (ou l'inverse) : arbitrage, pas de gain net évident."
                    if abs(a2m["max_drawdown_pct"]) < abs(a1["max_drawdown_pct"]) or a2m["sharpe_ann"] > a1["sharpe_ann"]
                    else "l'overlay n'aide pas ici (ni Sharpe ni MDD améliorés) — cohérent avec Étape D : le vol-targeting "
                         "sert surtout un signal déjà robuste (Buy & Hold), pas un signal RSI faible/bruité.")
w(f"- **Verdict** : {verdict_overlay}\n")

w("## 6. Test de détection du lookahead (délai d'exécution)\n")
w(f"Signal testé : **{best_alt}** (meilleur Sharpe parmi A1-A6). Un vrai edge "
  "se dégrade **graduellement** avec le délai ; un lookahead s'effondre "
  "**verticalement** entre 0 et 1 barre.\n")
w("| Délai (barres) | 0 | 1 | 2 | 3 |")
w("|---|---|---|---|---|")
w(f"| Sharpe ann. | {delay_sh[0]:+.2f} | {delay_sh[1]:+.2f} | "
  f"{delay_sh[2]:+.2f} | {delay_sh[3]:+.2f} |")
collapse = delay_sh[0] - delay_sh[1]
grad = "graduelle → **pas de lookahead détecté**" if abs(collapse) < abs(delay_sh[0]) * 0.6 + 0.3 \
    else "effondrement 0→1 → **lookahead suspecté**"
w(f"\n*Dégradation 0→1 : {collapse:+.2f} de Sharpe — {grad}.*\n")

w("## 7. Verdict honnête\n")
w(f"- Échantillon OOS : {T_oos} jours (~{n_years:.0f} ans). Meilleur signal "
  f"alternatif par Sharpe : **{best_alt}** ({metr[best_alt]['sharpe_ann']:+.2f} "
  f"vs BuyHold {buyhold_sharpe:+.2f}).")
if beats_buyhold:
    w(f"- Signaux battant BuyHold en Sharpe brut (non déflaté) : "
      f"{', '.join(beats_buyhold)}.")
else:
    w("- **Aucun signal alternatif ne bat BuyHold en Sharpe**, même avant "
      "déflation.")
if credible:
    w(f"- **{', '.join(credible)} bat(tent) BuyHold avec un DSR > 0.95** : "
      "edge crédible sur cet échantillon, à confirmer en live.")
else:
    w("- Aucun signal alternatif ne bat BuyHold avec un DSR > 0.95.")
if mdd_improvers:
    w(f"- Réduction de MDD > 30 % sans perte de rendement > 20 % : "
      f"{', '.join(mdd_improvers)}.")
else:
    w("- Aucun signal alternatif ne réduit le MDD de plus de 30 % sans "
      "sacrifier plus de 20 % du rendement annualisé de BuyHold.")
w("- **Conclusion** : " +
  ("des signaux alternatifs ignorés jusqu'ici présentent un edge exploitable "
   "(cf. lignes ci-dessus)." if (beats_buyhold or mdd_improvers) else
   "cette exploration confirme, sur un second univers disjoint de règles "
   "techniques classiques (RSI, CCI, Donchian, ATR/Chandelier, ACF), qu'**on "
   "n'a pas raté de signal évident** : Buy & Hold demeure la référence sur "
   "NDX avec ce protocole. Cohérent avec l'Étape A (efficience) et l'Étape B "
   "(aucun signal directionnel ne bat BuyHold net de coûts et déflaté).") +
  "\n")
w("- **Discipline anti data-snooping** : univers N=6 figé avant évaluation, "
  "DSR compte N=7 essais (BuyHold inclus, même convention que l'Étape B). "
  "Aucun seuil n'a été retouché après avoir vu les résultats OOS.\n")

out = Path(OUT_MD)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text("\n".join(lines))
print("\n".join(lines))

# ------------------------------------------------------------------ json
json_out = {
    "protocol": {
        "data": str(DATA), "T0": T0, "refit_every": REFIT_EVERY, "embargo": EMBARGO,
        "cost_bps": COST_BPS, "oos_start": str(dates[oos[0]]), "oos_end": str(dates[oos[-1]]),
        "oos_n": int(T_oos), "n_trials_dsr": len(MODELS),
        "vol_target_ann_pct_A2": a2["vol_target_ann_pct"],
    },
    "metrics": {m: {**metr[m], "turnover": turnover[m], "dsr": dsr_out[m]} for m in MODELS},
    "ranking_by_sharpe": ranked,
    "lookahead_test": {"signal": best_alt, "sharpe_by_delay": delay_sh},
    "verdict": {
        "beats_buyhold_sharpe": beats_buyhold,
        "dsr_credible_vs_buyhold": credible,
        "mdd_improvers": mdd_improvers,
    },
}
Path(OUT_JSON).write_text(json.dumps(json_out, indent=2, default=str))
print(f"\n[OK] MD  -> {OUT_MD}")
print(f"[OK] JSON -> {OUT_JSON}")
