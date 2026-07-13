"""Etape C - Moteur de volatilite : fits, previsions walk-forward, evaluation.

Univers de modeles DECLARE AVANT toute evaluation out-of-sample (fige, aucun
ajout a posteriori - discipline anti data-snooping) :

  1. EWMA RiskMetrics (lambda=0.94)      - benchmark naif, zero parametre estime
  2. GARCH(1,1) normal                   - LE benchmark Hansen-Lunde (2005)
  3. GARCH(1,1) Student-t
  4. GJR-GARCH(1,1) Student-t            - spec recommandee (effet de levier)
  5. GJR-GARCH(1,1) skew-t               - spec du document
  6. HAR sur RV Parkinson (log, OLS)     - Corsi (2009), re-echelle close-to-close

Evaluation : QLIKE (primaire, robuste au proxy - Patton 2011) et MSE sur la
variance, proxy primaire = rendement demeane au carre (non biaise), proxy
secondaire = variance Parkinson re-echelonnee. Tests de Diebold-Mariano (HAC)
contre le benchmark GARCH(1,1)-normal.
"""
from __future__ import annotations

import numpy as np
from arch import arch_model
from scipy import stats

ANNUALIZE = np.sqrt(252)

# ----------------------------------------------------------------------------
# Fits
# ----------------------------------------------------------------------------

ARCH_SPECS = {
    "GARCH-n": dict(vol="GARCH", p=1, o=0, q=1, dist="normal"),
    "GARCH-t": dict(vol="GARCH", p=1, o=0, q=1, dist="t"),
    "GJR-t": dict(vol="GARCH", p=1, o=1, q=1, dist="t"),
    "GJR-skewt": dict(vol="GARCH", p=1, o=1, q=1, dist="skewt"),
}


def fit_arch(r: np.ndarray, name: str):
    spec = ARCH_SPECS[name]
    am = arch_model(r, mean="Constant", **spec)
    res = am.fit(disp="off", show_warning=False)
    return res


def params_dict(res) -> dict:
    return {k: float(v) for k, v in res.params.items()}


# ----------------------------------------------------------------------------
# Recursions de variance (1 pas et h pas), parametres fixes
# ----------------------------------------------------------------------------

def garch_path(r: np.ndarray, p: dict, gjr: bool) -> np.ndarray:
    """sigma2[t] = variance conditionnelle du rendement r[t] (information t-1).

    Retourne un tableau de taille len(r)+1 ; le dernier element est la
    prevision 1 pas hors echantillon.
    """
    eps = r - p["mu"]
    omega, alpha, beta = p["omega"], p["alpha[1]"], p["beta[1]"]
    gamma = p.get("gamma[1]", 0.0) if gjr else 0.0
    s2 = np.empty(len(r) + 1)
    s2[0] = eps.var()  # initialisation ; sans effet asymptotiquement
    for t in range(len(r)):
        e2 = eps[t] ** 2
        s2[t + 1] = omega + (alpha + gamma * (eps[t] < 0)) * e2 + beta * s2[t]
    return s2


def garch_multistep(s2_next: float, p: dict, gjr: bool, h: int, p_neg: float = 0.5) -> np.ndarray:
    """E[sigma2_{t+1..t+h}] ; pour GJR, E[1(eps<0)eps^2] = p_neg * sigma2.

    p_neg=0.5 exact sous innovations symetriques (normal, t) ; approximation
    pour skew-t (asymetrie estimee faible, biais negligeable vs bruit du proxy).
    """
    omega, alpha, beta = p["omega"], p["alpha[1]"], p["beta[1]"]
    gamma = p.get("gamma[1]", 0.0) if gjr else 0.0
    persist = alpha + gamma * p_neg + beta
    out = np.empty(h)
    out[0] = s2_next
    for i in range(1, h):
        out[i] = omega + persist * out[i - 1]
    return out


def ewma_path(r: np.ndarray, lam: float = 0.94) -> np.ndarray:
    eps = r - r.mean()
    s2 = np.empty(len(r) + 1)
    s2[0] = eps.var()
    for t in range(len(r)):
        s2[t + 1] = lam * s2[t] + (1 - lam) * eps[t] ** 2
    return s2


# ----------------------------------------------------------------------------
# HAR sur RV Parkinson (spec log, correction lognormale, re-echelle c2c)
# ----------------------------------------------------------------------------

def har_design(rv: np.ndarray):
    """Matrice HAR : lags journalier / hebdo (5) / mensuel (22) de log(rv)."""
    lrv = np.log(np.maximum(rv, 1e-12))
    T = len(lrv)
    rows, y = [], []
    for t in range(22, T):
        d = lrv[t - 1]
        w = lrv[t - 5:t].mean()
        m = lrv[t - 22:t].mean()
        rows.append((1.0, d, w, m))
        y.append(lrv[t])
    return np.array(rows), np.array(y)


def fit_har(rv_train: np.ndarray, r_train: np.ndarray) -> dict:
    X, y = har_design(rv_train)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    s2_resid = resid.var(ddof=4)
    # re-echelle vers la variance close-to-close (Parkinson ignore le gap
    # overnight) : ratio des moyennes SUR LA FENETRE D'ENTRAINEMENT uniquement
    eps2 = (r_train - r_train.mean()) ** 2
    c2c_scale = eps2.mean() / rv_train.mean()
    return {"beta": beta, "s2_resid": float(s2_resid), "c2c_scale": float(c2c_scale)}


def har_forecast(rv_hist: np.ndarray, mod: dict, h: int) -> np.ndarray:
    """Previsions 1..h pas, iteration sur les lags avec les valeurs predites."""
    buf = list(np.log(np.maximum(rv_hist[-22:], 1e-12)))
    beta, s2r, scale = mod["beta"], mod["s2_resid"], mod["c2c_scale"]
    out = np.empty(h)
    for i in range(h):
        d = buf[-1]
        w = np.mean(buf[-5:])
        m = np.mean(buf[-22:])
        lf = beta[0] + beta[1] * d + beta[2] * w + beta[3] * m
        out[i] = np.exp(lf + s2r / 2) * scale  # correction lognormale + c2c
        buf.append(lf)
        buf.pop(0)
    return out


# ----------------------------------------------------------------------------
# Pertes et test de Diebold-Mariano
# ----------------------------------------------------------------------------

def qlike(proxy: np.ndarray, fcst: np.ndarray) -> np.ndarray:
    """QLIKE >= 0, nulle si fcst == proxy (Patton 2011, version normalisee)."""
    ratio = np.maximum(proxy, 1e-12) / fcst
    return ratio - np.log(ratio) - 1.0


def mse(proxy: np.ndarray, fcst: np.ndarray) -> np.ndarray:
    return (proxy - fcst) ** 2


def _stationary_bootstrap_idx(T: int, mean_block: float, rng) -> np.ndarray:
    """Indices d'un bootstrap stationnaire de Politis-Romano (1994).

    Blocs de longueur geometrique (moyenne mean_block), enchaines circulairement.
    """
    p = 1.0 / mean_block
    idx = np.empty(T, dtype=int)
    t = 0
    while t < T:
        start = rng.integers(0, T)
        L = rng.geometric(p)
        for j in range(min(L, T - t)):
            idx[t] = (start + j) % T
            t += 1
    return idx


def spa_test(losses: dict, bench: str, B: int = 5000, mean_block: float = 20.0,
             seed: int = 42) -> dict:
    """Test SPA de Hansen (2005, JBES), version consistante (SPA_c).

    H0 : le benchmark n'est battu par AUCUN modele de l'univers.
    d_k,t = L_bench,t - L_k,t (>0 <=> k meilleur). Statistique studentisee
    max_k sqrt(T) dbar_k / omega_k ; distribution sous H0 par bootstrap
    stationnaire avec recentrage de Hansen (les modeles nettement inferieurs
    ne gonflent pas la valeur critique, contrairement au Reality Check).
    """
    models = [m for m in losses if m != bench]
    D = np.column_stack([losses[bench] - losses[m] for m in models])
    T, K = D.shape
    dbar = D.mean(axis=0)
    rng = np.random.default_rng(seed)
    boot_means = np.empty((B, K))
    for b in range(B):
        boot_means[b] = D[_stationary_bootstrap_idx(T, mean_block, rng)].mean(axis=0)
    omega = np.sqrt(T) * boot_means.std(axis=0, ddof=1)  # ecart-type long terme
    tstats = np.sqrt(T) * dbar / omega
    t_spa = max(float(tstats.max()), 0.0)
    # recentrage consistant : ne recentre que les modeles non "nettement mauvais"
    a_n = np.sqrt(2 * np.log(np.log(T)))
    g = np.where(tstats >= -a_n, dbar, 0.0)
    z = np.sqrt(T) * (boot_means - g) / omega
    t_boot = np.maximum(z.max(axis=1), 0.0)
    return {
        "t_spa": t_spa,
        "p_value": float((t_boot >= t_spa).mean()),
        "best_model": models[int(np.argmax(tstats))],
        "t_by_model": {m: float(t) for m, t in zip(models, tstats)},
    }


def dm_test(loss_bench: np.ndarray, loss_model: np.ndarray, hac_lags: int) -> dict:
    """H0 : egalite de perte attendue. d>0 <=> le modele bat le benchmark.

    Variance HAC (Newey-West, noyau de Bartlett).
    """
    d = loss_bench - loss_model
    T = len(d)
    dbar = d.mean()
    dc = d - dbar
    lrv = np.sum(dc**2) / T
    for j in range(1, hac_lags + 1):
        w = 1 - j / (hac_lags + 1)
        lrv += 2 * w * np.sum(dc[j:] * dc[:-j]) / T
    se = np.sqrt(lrv / T)
    t_stat = dbar / se if se > 0 else np.nan
    return {
        "mean_diff": float(dbar),
        "t": float(t_stat),
        "p_two_sided": float(2 * stats.norm.sf(abs(t_stat))),
        "p_one_sided_model_better": float(stats.norm.sf(t_stat)),
    }
