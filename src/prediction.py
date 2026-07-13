"""Etape B - Modele de prediction directionnelle (NASDAQ Composite, quotidien).

Choix de conception dictes par la revue de litterature (cf. README) et par les
resultats de l'Etape A (random walk NON rejete, aucune autocorrelation
exploitable du rendement) :

1. On predit une DIRECTION (classification), jamais un prix absolu. Entrainer
   sur des prix produit un R^2 proche de 1 purement artificiel (naive forecast
   decale d'un pas) : erreur classique denoncee par toute la litterature.
2. Labels par TRIPLE BARRIER (Lopez de Prado, 2018) a barrieres dynamiques
   proportionnelles a la volatilite locale, plutot qu'un horizon fixe.
3. Features CAUSALES uniquement (connues a la cloture du jour t), incluant une
   differenciation fractionnaire (Lopez de Prado) qui rend la serie
   stationnaire tout en preservant la memoire.
4. Evaluation walk-forward avec PURGE + EMBARGO (les labels chevauchent H jours,
   sinon fuite d'information train->test).
5. Metriques de TRADING (Sharpe, Sortino, Calmar, drawdown, profit factor) nets
   de couts, jamais le R^2 ; puis DEFLATED SHARPE RATIO (Bailey-Lopez de Prado)
   qui corrige du nombre d'essais et de la non-normalite.
6. Test de detection du lookahead : re-execution avec delai 0/1/2/3 barres ; un
   vrai edge se degrade graduellement, un lookahead s'effondre entre 0 et 1.

L'univers de modeles et le protocole sont FIGES dans scripts/run_etape_b.py
AVANT toute evaluation (discipline anti data-snooping, cf. Etape C).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

TRADING_DAYS = 252


# ----------------------------------------------------------------------------
# 1. Differenciation fractionnaire (Lopez de Prado, AFML ch. 5)
# ----------------------------------------------------------------------------

def _frac_weights(d: float, thresh: float = 1e-4, max_k: int = 512) -> np.ndarray:
    """Poids de la fenetre fixe pour la differenciation fractionnaire d'ordre d.

    w_0 = 1 ; w_k = -w_{k-1} * (d-k+1)/k. Tronque quand |w_k| < thresh.
    """
    w = [1.0]
    for k in range(1, max_k):
        wk = -w[-1] * (d - k + 1) / k
        if abs(wk) < thresh:
            break
        w.append(wk)
    return np.array(w[::-1])  # ordonne du plus ancien au plus recent


def frac_diff(series: np.ndarray, d: float = 0.4, thresh: float = 1e-4) -> np.ndarray:
    """Serie fractionnairement differenciee, alignee (NaN sur l'amorce).

    d in ]0,1[ : compromis stationnarite / memoire. d=0.4 typique pour des
    log-prix d'indice. Convolution causale a fenetre fixe (aucun lookahead).
    """
    w = _frac_weights(d, thresh)
    width = len(w)
    out = np.full(len(series), np.nan)
    for t in range(width - 1, len(series)):
        out[t] = np.dot(w, series[t - width + 1:t + 1])
    return out


# ----------------------------------------------------------------------------
# 2. Indicateurs techniques (tous causaux : n'utilisent que t et le passe)
# ----------------------------------------------------------------------------

def _rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50.0)


def _atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    hl = df["high"] - df["low"]
    hc = (df["high"] - df["close"].shift()).abs()
    lc = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Construit la matrice de features CAUSALES indexee par date.

    Regle d'or : une feature au temps t n'utilise que l'information disponible a
    la cloture du jour t. Aucune normalisation sur l'echantillon complet (le
    z-score global est un lookahead classique) - la standardisation eventuelle
    est faite dans le pipeline, sur la fenetre d'entrainement seulement.
    """
    close = df["close"].astype(float)
    logp = np.log(close)
    r = logp.diff()  # rendement log du jour t (connu a la cloture t)

    f = pd.DataFrame(index=df.index)
    # rendements retardes
    for k in (1, 2, 3, 5, 10):
        f[f"ret_{k}"] = r.shift(0).rolling(k).sum() if k > 1 else r
    # momentum et moyennes
    f["mom_10"] = logp - logp.shift(10)
    f["mom_20"] = logp - logp.shift(20)
    f["ma_ratio_20"] = logp - logp.rolling(20).mean()
    f["ma_ratio_50"] = logp - logp.rolling(50).mean()
    # volatilite realisee rolling (regime)
    f["vol_10"] = r.rolling(10).std()
    f["vol_20"] = r.rolling(20).std()
    f["vol_ratio"] = f["vol_10"] / f["vol_20"]
    # range-based (Parkinson intra-seance)
    hl = np.log(df["high"] / df["low"])
    f["parkinson_5"] = (hl ** 2 / (4 * np.log(2))).rolling(5).mean()
    # drawdown courant depuis un plus-haut glissant
    roll_max = close.rolling(60, min_periods=1).max()
    f["drawdown_60"] = close / roll_max - 1.0
    # indicateurs techniques
    f["rsi_14"] = _rsi(close, 14)
    atr = _atr(df, 14)
    f["atr_rel"] = atr / close
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    f["macd_rel"] = (macd - macd.ewm(span=9, adjust=False).mean()) / close
    ma20 = close.rolling(20).mean()
    sd20 = close.rolling(20).std()
    f["bb_pctb"] = (close - (ma20 - 2 * sd20)) / (4 * sd20)
    low14 = df["low"].rolling(14).min()
    high14 = df["high"].rolling(14).max()
    f["stoch_k"] = (close - low14) / (high14 - low14)
    # differenciation fractionnaire du log-prix (memoire + stationnarite)
    f["fracdiff_04"] = frac_diff(logp.values, d=0.4)
    return f


# ----------------------------------------------------------------------------
# 3. Labeling par Triple Barrier (Lopez de Prado, AFML ch. 3)
# ----------------------------------------------------------------------------

def triple_barrier_labels(df: pd.DataFrame, horizon: int = 5, vol_span: int = 20,
                          mult: float = 1.5) -> pd.Series:
    """Label +1 / -1 / 0 par la methode des trois barrieres.

    Pour chaque jour t (evenement), on regarde le chemin des H jours SUIVANTS :
      - barriere haute (take-profit) a +mult*sigma_t  -> +1 si touchee en premier
      - barriere basse (stop-loss)   a -mult*sigma_t  -> -1 si touchee en premier
      - barriere verticale (H jours)                  -> signe du rendement final
    sigma_t = volatilite locale (ewm) connue en t : les barrieres s'adaptent au
    regime. Aucun lookahead pour les FEATURES (le label est la cible, connu
    seulement H jours plus tard ; c'est precisement ce que la purge protege).
    """
    close = df["close"].astype(float).values
    logp = np.log(close)
    r = np.diff(logp, prepend=logp[0])
    sigma = pd.Series(r).ewm(span=vol_span).std().values
    n = len(close)
    labels = np.full(n, np.nan)
    for t in range(n - 1):
        s = sigma[t]
        if not np.isfinite(s) or s == 0:
            continue
        up, dn = mult * s, -mult * s
        end = min(t + horizon, n - 1)
        lab = 0
        for j in range(t + 1, end + 1):
            cr = logp[j] - logp[t]
            if cr >= up:
                lab = 1
                break
            if cr <= dn:
                lab = -1
                break
        else:
            fr = logp[end] - logp[t]
            lab = 1 if fr > 0 else -1  # signe au toucher de la barriere verticale
        labels[t] = lab
    return pd.Series(labels, index=df.index)


# ----------------------------------------------------------------------------
# 4. Metriques de trading (nettes de couts) + Deflated Sharpe Ratio
# ----------------------------------------------------------------------------

def trading_metrics(strat_ret: np.ndarray, ann: int = TRADING_DAYS) -> dict:
    """Metriques pertinentes pour le trading (jamais le R^2).

    strat_ret : rendements periodiques NETS de couts de la strategie.
    """
    strat_ret = np.asarray(strat_ret, dtype=float)
    strat_ret = strat_ret[np.isfinite(strat_ret)]
    n = len(strat_ret)
    mu, sd = strat_ret.mean(), strat_ret.std(ddof=1)
    sharpe = mu / sd if sd > 0 else 0.0
    downside = strat_ret[strat_ret < 0].std(ddof=1) if (strat_ret < 0).any() else np.nan
    sortino = mu / downside if downside and downside > 0 else np.nan
    eq = np.cumsum(strat_ret)  # equity en log-rendement cumule
    peak = np.maximum.accumulate(eq)
    mdd = float((eq - peak).min())
    ann_ret = mu * ann
    calmar = ann_ret / abs(mdd) if mdd < 0 else np.nan
    gains = strat_ret[strat_ret > 0].sum()
    losses = -strat_ret[strat_ret < 0].sum()
    pf = gains / losses if losses > 0 else np.nan
    return {
        "n": n,
        "sharpe_daily": float(sharpe),
        "sharpe_ann": float(sharpe * np.sqrt(ann)),
        "sortino_ann": float(sortino * np.sqrt(ann)) if np.isfinite(sortino) else np.nan,
        "calmar": float(calmar) if np.isfinite(calmar) else np.nan,
        "ann_return_pct": float(100 * (np.exp(ann_ret) - 1)),
        "max_drawdown_pct": float(100 * (np.exp(mdd) - 1)),
        "profit_factor": float(pf) if np.isfinite(pf) else np.nan,
        "hit_rate": float((strat_ret > 0).mean()),
        "skew": float(stats.skew(strat_ret)) if n > 2 else np.nan,
        "excess_kurt": float(stats.kurtosis(strat_ret)) if n > 3 else np.nan,
    }


def expected_max_sharpe(var_trials: float, n_trials: int) -> float:
    """E[max SR] sous H0 (tous les vrais SR nuls), N essais i.i.d. (Bailey-LdP).

    E[max] ~ sqrt(var) * [(1-g) z_{1-1/N} + g z_{1-1/(N e)}], g = Euler-Mascheroni.
    """
    if n_trials <= 1 or var_trials <= 0:
        return 0.0
    g = 0.5772156649  # constante d'Euler-Mascheroni
    z1 = stats.norm.ppf(1 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1 - 1.0 / (n_trials * np.e))
    return float(np.sqrt(var_trials) * ((1 - g) * z1 + g * z2))


def dsr(sr_hat_daily: float, T: int, var_trials: float, n_trials: int,
        skew: float, kurt_excess: float) -> dict:
    """Deflated Sharpe Ratio complet.

    sr_hat_daily : Sharpe non annualise du modele.
    T            : nombre d'observations (rendements) de la serie evaluee.
    var_trials   : variance des Sharpe (non annualises) des N essais.
    Retourne le seuil de selection SR0 et le DSR = P(SR reel > 0 | selection).
    """
    sr0 = expected_max_sharpe(var_trials, n_trials)
    denom = np.sqrt(max(1e-12, 1 - skew * sr_hat_daily
                        + (kurt_excess) / 4.0 * sr_hat_daily ** 2))
    z = (sr_hat_daily - sr0) * np.sqrt(max(T - 1, 1)) / denom
    return {"sr0_daily": float(sr0), "z": float(z), "dsr": float(stats.norm.cdf(z))}


# ----------------------------------------------------------------------------
# 5. Backtest walk-forward avec purge + embargo
# ----------------------------------------------------------------------------

def walk_forward_signals(X: pd.DataFrame, y: pd.Series, r_fwd: pd.Series,
                         model_factory, t0: int, refit_every: int,
                         embargo: int, standardize: bool) -> np.ndarray:
    """Genere des positions OOS {-1,0,+1} par walk-forward expansif.

    Purge : on retire de l'entrainement les `embargo` derniers evenements (leurs
    labels chevauchent la periode de test). Standardisation eventuelle calee sur
    la fenetre d'entrainement uniquement (jamais l'echantillon complet).
    model_factory() -> estimateur sklearn a chaque re-estimation.
    """
    n = len(X)
    pos = np.zeros(n)
    Xv, yv = X.values, y.values
    for tr in range(t0, n, refit_every):
        tr_end = tr - embargo  # purge des labels chevauchants
        mask = np.isfinite(yv[:tr_end]) & np.all(np.isfinite(Xv[:tr_end]), axis=1)
        if mask.sum() < 100:
            continue
        Xtr, ytr = Xv[:tr_end][mask], yv[:tr_end][mask]
        mu = Xtr.mean(axis=0)
        sd = Xtr.std(axis=0)
        sd[sd == 0] = 1.0
        if standardize:
            Xtr = (Xtr - mu) / sd
        clf = model_factory()
        clf.fit(Xtr, (ytr > 0).astype(int))  # classe binaire : hausse vs baisse
        block = range(tr, min(tr + refit_every, n))
        for t in block:
            xt = Xv[t]
            if not np.all(np.isfinite(xt)):
                continue
            xt = (xt - mu) / sd if standardize else xt
            p_up = clf.predict_proba(xt.reshape(1, -1))[0, 1]
            pos[t] = 1.0 if p_up > 0.5 else -1.0
    return pos


def backtest(pos: np.ndarray, r_fwd: np.ndarray, cost_bps: float,
             delay: int = 0) -> np.ndarray:
    """Rendements nets : position decidee en t, appliquee au rendement t->t+1.

    delay : nombre de barres de retard a l'execution (test de lookahead).
    cost_bps : cout aller-retour en points de base, preleve sur |delta position|.
    """
    pos = np.asarray(pos, dtype=float)
    r_fwd = np.asarray(r_fwd, dtype=float)
    if delay:
        pos = np.concatenate([np.zeros(delay), pos[:-delay]])
    pnl = pos * r_fwd
    turn = np.abs(np.diff(pos, prepend=0.0))
    pnl = pnl - turn * (cost_bps / 1e4)
    return pnl
