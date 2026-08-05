"""Audit adversarial — Overlay de vol-targeting estimateur HAR-P (Corsi 2009).

Recalcul totalement indépendant : régression HAR par équations normales
explicites (sans `np.linalg.lstsq`, sans réutiliser `volatility.py::fit_har`/
`har_forecast`) et prévision itérative recalculée par boucle manuelle,
plus test anti-lookahead.
"""
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
REPO_ROOT = FINANCE_ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

warnings.filterwarnings("ignore")

from data_loader import load_ohlc, log_returns_pct, parkinson_var_pct, quality_report  # noqa: E402
from nonml_har_vol_targeting_overlay_backtest import (  # noqa: E402
    T0, REFIT_EVERY, TARGET_VOL_ANNUAL_PCT, CAP, MARKETS, har_vol_position,
)

ANNUALIZE = np.sqrt(252)


def manual_har_design(rv: np.ndarray):
    lrv = np.log(np.maximum(rv, 1e-12))
    T = len(lrv)
    rows, y = [], []
    for t in range(22, T):
        d = lrv[t - 1]
        w = sum(lrv[t - 5:t]) / 5.0
        m = sum(lrv[t - 22:t]) / 22.0
        rows.append((1.0, d, w, m))
        y.append(lrv[t])
    return np.array(rows), np.array(y)


def manual_ols_normal_equations(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Beta = (X'X)^-1 X'y par equations normales explicites (independant
    de np.linalg.lstsq, qui utilise une decomposition SVD)."""
    XtX = X.T @ X
    Xty = X.T @ y
    return np.linalg.solve(XtX, Xty)


def manual_fit_har(rv_train: np.ndarray, r_train: np.ndarray) -> dict:
    X, y = manual_har_design(rv_train)
    beta = manual_ols_normal_equations(X, y)
    resid = y - X @ beta
    dof = len(y) - 4
    s2_resid = float(np.sum(resid ** 2) / dof)
    eps2 = (r_train - r_train.mean()) ** 2
    c2c_scale = float(eps2.mean() / rv_train.mean())
    return {"beta": beta, "s2_resid": s2_resid, "c2c_scale": c2c_scale}


def manual_har_forecast_1step(rv_hist: np.ndarray, mod: dict) -> float:
    lrv = np.log(np.maximum(rv_hist[-22:], 1e-12))
    d = lrv[-1]
    w = sum(lrv[-5:]) / 5.0
    m = sum(lrv[-22:]) / 22.0
    beta = mod["beta"]
    lf = beta[0] + beta[1] * d + beta[2] * w + beta[3] * m
    return float(np.exp(lf + mod["s2_resid"] / 2) * mod["c2c_scale"])


def independent_har_position(df) -> np.ndarray:
    r_pct = log_returns_pct(df).values
    rv_pct2 = parkinson_var_pct(df).values
    T = len(r_pct)
    vol_fcst = np.full(T, np.nan)
    for tr in range(T0, T, REFIT_EVERY):
        block = range(tr, min(tr + REFIT_EVERY, T))
        mod = manual_fit_har(rv_pct2[:tr], r_pct[:tr])
        for t in block:
            v1 = manual_har_forecast_1step(rv_pct2[:t], mod)
            vol_fcst[t] = ANNUALIZE * np.sqrt(v1)
    with np.errstate(divide="ignore", invalid="ignore"):
        pos = TARGET_VOL_ANNUAL_PCT / vol_fcst
    pos = np.clip(pos, 0.0, CAP)
    return np.nan_to_num(pos, nan=1.0)


def main():
    lines = ["# Audit adversarial — Overlay de vol-targeting estimateur HAR-P (Corsi 2009)", "",
             "## 1. Recalcul totalement indépendant (équations normales explicites, sans "
             "`np.linalg.lstsq` ni `fit_har`/`har_forecast`)", "",
             "| Marché | Écart position max (hors marge T0) |",
             "|---|---|"]
    all_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        r_pct = log_returns_pct(df).values
        if len(r_pct) <= T0 + REFIT_EVERY:
            continue
        pos_orig = har_vol_position(df)
        pos_indep = independent_har_position(df)
        max_diff = float(np.max(np.abs(pos_orig[T0:] - pos_indep[T0:])))
        all_ok &= (max_diff < 1e-6)
        lines.append(f"| {name} | {max_diff:.2e} |")

    lines.append("")
    lines.append(f"**{'OK — position confirmée par recalcul totalement indépendant.' if all_ok else 'ÉCHEC.'}**")

    lines.append("")
    lines.append("## 2. Test anti-lookahead (perturbation du futur, OHLC)")
    lines.append("")
    lines.append("| Marché | Décisions passées identiques après perturbation future |")
    lines.append("|---|---|")
    anti_leak_ok = True
    for name, fname in MARKETS.items():
        path = REPO_ROOT / "data" / fname
        if not path.exists():
            continue
        df = load_ohlc(str(path))
        quality_report(df)
        r_pct = log_returns_pct(df).values
        if len(r_pct) <= T0 + REFIT_EVERY:
            continue
        pos_before = har_vol_position(df)

        df_pert = df.copy()
        cut = len(df_pert) // 2
        rng = np.random.default_rng(73)
        shock = 1.0 + rng.normal(0, 0.1, len(df_pert) - cut)
        for col in ("open", "high", "low", "close"):
            df_pert.loc[df_pert.index[cut:], col] = df_pert[col].values[cut:] * shock
        pos_after = har_vol_position(df_pert)

        check_end = cut - T0 if cut > T0 else 0
        if check_end < 10:
            lines.append(f"| {name} | (fenêtre trop courte pour tester) |")
            continue
        identical = bool(np.allclose(pos_before[T0:T0 + check_end], pos_after[T0:T0 + check_end]))
        anti_leak_ok &= identical
        lines.append(f"| {name} | {'OUI' if identical else 'NON — FUITE DETECTEE'} |")

    lines.append("")
    lines.append(f"**{'OK — aucune fuite de données futures.' if anti_leak_ok else 'ÉCHEC — fuite détectée.'}**")

    out = ROOT / "results" / "nonml_har_vol_targeting_overlay_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
