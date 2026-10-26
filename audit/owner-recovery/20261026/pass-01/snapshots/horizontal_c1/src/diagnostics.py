"""Etape A - Diagnostics preliminaires sur les rendements NASDAQ.

- Statistiques descriptives (skew, kurtosis, Jarque-Bera)
- Test de ratio de variance Lo-MacKinlay (1988), stat z homoscedastique
  et z* robuste a l'heteroscedasticite
- Ljung-Box sur rendements et rendements au carre
- Test ARCH-LM d'Engle
- Ajustement Student-t sur rendements standardises (non conditionnel)
"""
from __future__ import annotations

import numpy as np
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch


def summary_stats(r: np.ndarray) -> dict:
    jb, jb_p = stats.jarque_bera(r)[:2]
    return {
        "n": len(r),
        "mean_daily_pct": float(np.mean(r)),
        "ann_mean_pct": float(252 * np.mean(r)),
        "ann_vol_pct": float(np.sqrt(252) * np.std(r, ddof=1)),
        "skew": float(stats.skew(r)),
        "excess_kurtosis": float(stats.kurtosis(r)),
        "min_pct": float(np.min(r)),
        "max_pct": float(np.max(r)),
        "jarque_bera": float(jb),
        "jb_pvalue": float(jb_p),
    }


def lo_mackinlay_vr(r: np.ndarray, q: int) -> dict:
    """Test de ratio de variance de Lo & MacKinlay (1988, RFS 1:41-66).

    VR(q) = variance des rendements agreges sur q periodes (chevauchants,
    corriges du biais) / (q x variance 1 periode). Sous H0 random walk,
    VR(q) = 1.  z : stat homoscedastique ; z* : robuste a l'heteroscedasticite
    (RW3), la seule interpretable sur des donnees a clustering de volatilite.
    """
    r = np.asarray(r, dtype=float)
    T = len(r)  # nq dans les notations de Lo-MacKinlay
    mu = r.mean()
    # variance 1 periode (estimateur non biaise)
    var1 = np.sum((r - mu) ** 2) / (T - 1)
    # somme q-periodes chevauchantes des rendements
    csum = np.cumsum(np.insert(r, 0, 0.0))
    rq = csum[q:] - csum[:-q]  # T-q+1 sommes chevauchantes
    # correction de biais L&M ; le facteur q est DEJA inclus dans m,
    # donc VR = varq/var1 (ne pas rediviser par q).
    m = q * (T - q + 1) * (1 - q / T)
    varq = np.sum((rq - q * mu) ** 2) / m
    vr = varq / var1
    # garde-fou : VR(q) doit etre coherent avec 1 + 2*sum_j (1-j/q) rho_j
    dm0 = r - mu
    den0 = np.sum(dm0**2)
    vr_acf = 1 + 2 * sum(
        (1 - j / q) * np.sum(dm0[j:] * dm0[:-j]) / den0 for j in range(1, q)
    )
    assert abs(vr - vr_acf) < 0.05, f"VR incoherent: {vr:.4f} vs ACF {vr_acf:.4f}"
    # stat homoscedastique
    phi = 2 * (2 * q - 1) * (q - 1) / (3 * q * T)
    z = (vr - 1) / np.sqrt(phi)
    # stat robuste heteroscedasticite
    dm = r - mu
    denom = (np.sum(dm**2)) ** 2
    phi_star = 0.0
    for j in range(1, q):
        delta_j = T * np.sum(dm[j:] ** 2 * dm[:-j] ** 2) / denom
        phi_star += (2 * (q - j) / q) ** 2 * delta_j
    z_star = (vr - 1) / np.sqrt(phi_star / T)
    return {
        "q": q,
        "VR": float(vr),
        "z_homo": float(z),
        "p_homo": float(2 * stats.norm.sf(abs(z))),
        "z_robust": float(z_star),
        "p_robust": float(2 * stats.norm.sf(abs(z_star))),
    }


def ljung_box(r: np.ndarray, lags=(5, 10, 22)) -> dict:
    out = {}
    for series, name in ((r, "returns"), ((r - r.mean()) ** 2, "squared")):
        lb = acorr_ljungbox(series, lags=list(lags), return_df=True)
        out[name] = {
            int(l): {"Q": float(lb.loc[l, "lb_stat"]), "p": float(lb.loc[l, "lb_pvalue"])}
            for l in lags
        }
    return out


def acf(r: np.ndarray, nlags: int = 10) -> list[float]:
    r = np.asarray(r, dtype=float)
    dm = r - r.mean()
    denom = np.sum(dm**2)
    return [float(np.sum(dm[k:] * dm[:-k]) / denom) for k in range(1, nlags + 1)]


def engle_arch_lm(r: np.ndarray, nlags: int = 10) -> dict:
    lm, lm_p, f, f_p = het_arch(r - r.mean(), nlags=nlags)
    return {"nlags": nlags, "LM": float(lm), "p_LM": float(lm_p), "F": float(f), "p_F": float(f_p)}


def fit_student_t(r: np.ndarray) -> dict:
    """Ajuste une Student-t (loc, scale, nu) par MV sur les rendements bruts.

    NB : c'est la queue NON CONDITIONNELLE. Le nu conditionnel (residus GARCH)
    est plus eleve car le clustering de volatilite explique une partie des
    queues epaisses. Les deux sont rapportes (cf. Etape C).
    """
    nu, loc, scale = stats.t.fit(r)
    ll_t = np.sum(stats.t.logpdf(r, nu, loc, scale))
    mu_n, sd_n = stats.norm.fit(r)
    ll_n = np.sum(stats.norm.logpdf(r, mu_n, sd_n))
    return {
        "nu": float(nu),
        "loc": float(loc),
        "scale": float(scale),
        "loglik_t": float(ll_t),
        "loglik_normal": float(ll_n),
        "lr_stat_t_vs_normal": float(2 * (ll_t - ll_n)),
    }
