"""Audit adversarial indépendant — portefeuille volatility-managed GJR-t
(cycle #165, `PREREG_volatility_managed_portfolio_gjr.md`).

Six vérifications, toutes destinées à casser le résultat plutôt qu'à le
confirmer :

1. **Réconciliation avec un artefact DÉJÀ COMMITTÉ** : les prévisions de
   volatilité utilisées ici doivent être exactement celles publiées par
   l'Étape C sur NDX (`results/etape_C_ndx_40ans.md`, produit par un autre
   script, avant ce cycle) — nombre de ré-estimations, nombre de prévisions
   OOS, min/médiane/max de la vol annualisée prévue.
2. **Recalcul par la boucle de l'Étape C** (fit_arch + garch_path_fold_only
   appelés directement ici, sans passer par le wrapper
   `overlay.walk_forward_vol_forecast` utilisé par le backtest).
3. **Recalcul par la librairie `arch` elle-même** (`fix()` + `forecast()`) —
   implémentation tierce, initialisation différente de la récursion maison.
4. **Alignement calendaire explicite** : pour un échantillon de dates t, la
   prévision servant à la position appliquée à r[t] est reconstruite en
   Python pur à partir de **r[:t] UNIQUEMENT** (aucune donnée d'indice ≥ t
   n'entre dans le calcul), puis comparée à celle du backtest.
5. **Test anti-lookahead par mutation du futur** : les 20 % de rendements les
   plus récents sont bruités, tout le walk-forward est relancé, les positions
   antérieures doivent être *strictement* inchangées.
6. **Recalcul manuel du verdict** (Sharpe et rendement composé par boucles
   explicites, sans `trading_metrics` ni `np.cumprod`).
"""
import re
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

from arch import arch_model  # noqa: E402
from data_loader import load_ohlc, log_returns_pct, quality_report  # noqa: E402
from volatility import ANNUALIZE, fit_arch, garch_path_fold_only, params_dict  # noqa: E402
from nonml_volatility_managed_portfolio_gjr_backtest import (  # noqa: E402
    CAP, COST_BPS, MARKET_FILE, REFIT_EVERY, T0, TARGET_VOL_ANNUAL_PCT,
    build_positions,
)

ETAPE_C_REPORT = ROOT / "results" / "etape_C_ndx_40ans.md"


def refit_start(t: int) -> int:
    """Indice de la dernière ré-estimation <= t (grille figée T0 + k*REFIT_EVERY)."""
    return T0 + ((t - T0) // REFIT_EVERY) * REFIT_EVERY


def pure_python_forecast(r_list, t: int, params: dict) -> float:
    """Récursion GJR écrite de zéro (boucles Python, aucun numpy, aucune
    fonction du repo) sur r[:t] SEULEMENT. Retourne la vol annualisée prévue
    pour r[t]. Sert à la fois de recalcul indépendant et de preuve
    d'alignement calendaire : aucun élément d'indice >= t n'est lu — y compris
    pour l'initialisation de la récursion (le backtest, lui, initialise sur la
    variance plein échantillon ; si cette initialisation avait la moindre
    influence matérielle, ce recalcul divergerait)."""
    mu = params["mu"]
    omega, alpha, beta = params["omega"], params["alpha[1]"], params["beta[1]"]
    gamma = params["gamma[1]"]
    hist = r_list[:t]                      # <-- borne stricte : rien après t-1
    eps = [x - mu for x in hist]
    n = len(eps)
    mean_eps = sum(eps) / n
    s2 = sum((e - mean_eps) ** 2 for e in eps) / n   # convention numpy .var() (ddof=0)
    for i in range(n):
        e2 = eps[i] * eps[i]
        neg = 1.0 if eps[i] < 0 else 0.0
        s2 = omega + (alpha + gamma * neg) * e2 + beta * s2
    return (252 ** 0.5) * (s2 ** 0.5)


def main():
    df = load_ohlc(str(REPO_ROOT / "data" / MARKET_FILE))
    quality_report(df)
    ser = log_returns_pct(df)
    r = ser.values
    T = len(r)

    built = build_positions(r)
    pos_full, vol_fcst = built["pos"], built["vol_fcst"]
    pos = pos_full[T0:]
    r_t = r[T0:] / 100.0

    lines = ["# Audit adversarial — portefeuille volatility-managed GJR-t (cycle #165)", ""]
    verdicts = []

    # ---------------------------------------------------------------- 1.
    lines += ["## 1. Réconciliation avec l'artefact déjà committé de l'Étape C", "",
              "Les prévisions de volatilité de ce cycle doivent être *les mêmes objets* que "
              "celles publiées par l'Étape C sur NDX (script différent, committé avant ce "
              "cycle) — sinon le moteur validé au SPA de Hansen n'est pas celui qui est "
              "réellement utilisé ici.", ""]
    txt = ETAPE_C_REPORT.read_text()
    m_refit = re.search(r"ré-estimation tous les (\d+) j \((\d+) ré-estimations\)", txt)
    m_oos = re.search(r"\*\*(\d+) prévisions 1 pas\*\*", txt)
    m_vol = re.search(r"Vol\. annualisée prédite \(GJR-t\) sur l'OOS : min ([\d.]+) % / "
                      r"méd\. ([\d.]+) % / max ([\d.]+) %", txt)
    vol_oos = vol_fcst[T0:]
    mine = {
        "refit_every": REFIT_EVERY,
        "n_refits": int(np.ceil((T - T0) / REFIT_EVERY)),
        "n_oos": len(vol_oos),
        "vmin": round(float(np.min(vol_oos)), 1),
        "vmed": round(float(np.median(vol_oos)), 1),
        "vmax": round(float(np.max(vol_oos)), 1),
    }
    ref = {
        "refit_every": int(m_refit.group(1)),
        "n_refits": int(m_refit.group(2)),
        "n_oos": int(m_oos.group(1)),
        "vmin": float(m_vol.group(1)),
        "vmed": float(m_vol.group(2)),
        "vmax": float(m_vol.group(3)),
    }
    lines += ["| Grandeur | Étape C (committé) | Ce cycle | Identique |", "|---|---|---|---|"]
    ok1 = True
    for k, label in (("refit_every", "cadence de ré-estimation (j)"),
                     ("n_refits", "nombre de ré-estimations"),
                     ("n_oos", "nombre de prévisions OOS 1 pas"),
                     ("vmin", "vol prévue min (%)"), ("vmed", "vol prévue médiane (%)"),
                     ("vmax", "vol prévue max (%)")):
        same = ref[k] == mine[k]
        ok1 &= same
        lines.append(f"| {label} | {ref[k]} | {mine[k]} | {'OUI' if same else 'NON'} |")
    lines += ["", f"**{'OK — le moteur de prévision est bien celui validé au SPA à l Étape C.' if ok1 else 'ÉCART — le moteur utilisé ne coïncide PAS avec celui de l Étape C.'}**", ""]
    verdicts.append(("Réconciliation Étape C", ok1))

    # ---------------------------------------------------------------- 2.
    lines += ["## 2. Recalcul par la boucle de l'Étape C (sans le wrapper `overlay`)", ""]
    vol_indep = np.full(T, np.nan)
    for tr in range(T0, T, REFIT_EVERY):
        res = fit_arch(r[:tr], "GJR-t")
        p = params_dict(res)
        path = garch_path_fold_only(r, p, tr, gjr=True)
        for t in range(tr, min(tr + REFIT_EVERY, T)):
            vol_indep[t] = ANNUALIZE * np.sqrt(path[t])
    d2 = float(np.nanmax(np.abs(vol_indep[T0:] - vol_fcst[T0:])))
    ok2 = d2 < 1e-10
    lines += [f"Écart absolu maximal sur les {len(vol_oos)} prévisions OOS : **{d2:.2e}**",
              "", f"**{'OK — recalcul identique à la précision machine.' if ok2 else 'ÉCART DÉTECTÉ.'}**", ""]
    verdicts.append(("Recalcul boucle Étape C", ok2))

    # ---------------------------------------------------------------- 3.
    lines += ["## 3. Recalcul par la librairie `arch` (implémentation tierce)", "",
              "`arch_model(...).fix(params).forecast(horizon=1)` sur `r[:t]` — code, "
              "initialisation et récursion écrits par les auteurs de la librairie, pas par "
              "ce projet.", "",
              "| t | Vol prévue backtest | Vol prévue `arch` | Écart relatif |", "|---|---|---|---|"]
    sample_t = list(range(T0, T, 1200))
    ok3 = True
    for t in sample_t:
        tr = refit_start(t)
        res = fit_arch(r[:tr], "GJR-t")
        am = arch_model(r[:t], mean="Constant", vol="GARCH", p=1, o=1, q=1, dist="t")
        fx = am.fix(res.params)
        v_arch = ANNUALIZE * np.sqrt(float(fx.forecast(horizon=1, reindex=False).variance.values[0, 0]))
        rel = abs(v_arch - vol_fcst[t]) / v_arch
        ok3 &= rel < 1e-3
        lines.append(f"| {t} | {vol_fcst[t]:.4f} % | {v_arch:.4f} % | {rel:.2e} |")
    lines += ["", f"**{'OK — implémentation tierce concordante (tolérance 1e-3, même seuil que la validation de l Étape C).' if ok3 else 'ÉCART DÉTECTÉ.'}**", ""]
    verdicts.append(("Recalcul librairie arch", ok3))

    # ---------------------------------------------------------------- 4.
    lines += ["## 4. Alignement calendaire — la prévision pour r[t] ne lit que r[:t]", "",
              "Récursion GJR réécrite de zéro en Python pur, alimentée par une tranche "
              "**strictement bornée à `r[:t]`** : si le backtest contenait la moindre fuite "
              "d'un jour, ce recalcul divergerait.", "",
              "| t | Date | Position backtest | Position recalculée (r[:t] seulement) | Écart |",
              "|---|---|---|---|---|"]
    r_list = [float(x) for x in r]
    ok4 = True
    for t in sample_t:
        tr = refit_start(t)
        res = fit_arch(r[:tr], "GJR-t")
        p = params_dict(res)
        v_pure = pure_python_forecast(r_list, t, p)
        pos_pure = min(CAP, max(0.0, TARGET_VOL_ANNUAL_PCT / v_pure))
        d = abs(pos_pure - float(pos_full[t]))
        ok4 &= d < 1e-9
        lines.append(f"| {t} | {ser.index[t]:%d/%m/%Y} | {pos_full[t]:.6f} | {pos_pure:.6f} | {d:.2e} |")
    lines += ["", f"**{'OK — aucune donnée postérieure à t-1 n intervient dans la position appliquée à r[t].' if ok4 else 'FUITE CALENDAIRE DÉTECTÉE.'}**", ""]
    verdicts.append(("Alignement calendaire", ok4))

    # ---------------------------------------------------------------- 5.
    lines += ["## 5. Test anti-lookahead par mutation des 20 % de rendements les plus récents", ""]
    cut = int(T * 0.8)
    rng = np.random.default_rng(165)
    r_mut = r.copy()
    r_mut[cut:] = r_mut[cut:] + rng.normal(0.0, 2.0, T - cut)
    pos_mut = build_positions(r_mut)["pos"]
    d5 = float(np.nanmax(np.abs(pos_full[T0:cut] - pos_mut[T0:cut])))
    ok5 = d5 < 1e-12
    beta_ref = params_dict(fit_arch(r[:T0], "GJR-t"))["beta[1]"]
    lines += [f"Bruit gaussien σ=2 points de % ajouté sur les {T - cut} derniers rendements "
              f"(indices ≥ {cut}). Écart maximal sur les positions **antérieures** : **{d5:.2e}**",
              "",
              "*Point de vigilance identifié et quantifié, pas passé sous silence* : "
              "`garch_path_fold_only` (code de l'Étape C, réutilisé tel quel) initialise la "
              "récursion avec la variance de l'échantillon **complet** passé en argument — "
              "donc techniquement avec une information postérieure. L'influence de cette "
              f"initialisation décroît en β^t avec β ≈ {beta_ref:.4f} (fit sur la fenêtre "
              f"initiale) : à la première observation OOS (t = {T0}) elle vaut déjà "
              f"β^{T0} ≈ {beta_ref ** T0:.1e}, très en dessous de la précision machine. La "
              "mesure ci-dessus le confirme empiriquement, et le contrôle 4 (récursion "
              "initialisée sur `r[:t]` uniquement) le confirme indépendamment.",
              "", f"**{'OK — le passé est inchangé, aucune information future exploitable.' if ok5 else 'ÉCHEC — fuite détectée.'}**", ""]
    verdicts.append(("Anti-lookahead (mutation)", ok5))

    # ---------------------------------------------------------------- 6.
    lines += ["## 6. Recalcul manuel du verdict (boucles explicites, sans `trading_metrics`)", ""]
    pnl_ov, pnl_bh = [], []
    prev = 1.0
    for i in range(len(pos)):
        turn = abs(float(pos[i]) - prev)
        pnl_ov.append(float(pos[i]) * float(r_t[i]) - turn * (COST_BPS / 1e4))
        prev = float(pos[i])
        pnl_bh.append(float(r_t[i]) - (COST_BPS / 1e4 if i == 0 else 0.0))

    def sharpe(x):
        n = len(x)
        mu = sum(x) / n
        sd = (sum((v - mu) ** 2 for v in x) / (n - 1)) ** 0.5
        return mu / sd * (252 ** 0.5)

    def compounded(x):
        eq = 1.0
        for v in x:
            eq *= (1.0 + v)
        return eq - 1.0

    s_ov, s_bh = sharpe(pnl_ov), sharpe(pnl_bh)
    c_ov, c_bh = compounded(pnl_ov), compounded(pnl_bh)
    ok6 = (s_ov > s_bh) and (c_ov > c_bh)
    lines += ["| Grandeur | Volatility-managed | Buy & Hold | Candidat > BH |", "|---|---|---|---|",
              f"| Sharpe annualisé (recalcul manuel) | {s_ov:+.4f} | {s_bh:+.4f} | {'OUI' if s_ov > s_bh else 'non'} |",
              f"| Rendement total composé (recalcul manuel) | {100 * c_ov:+.1f}% | {100 * c_bh:+.1f}% | {'OUI' if c_ov > c_bh else 'non'} |",
              "", f"**{'OK — le verdict PASS de niveau 1 est confirmé par un recalcul totalement indépendant.' if ok6 else 'ÉCART — le verdict ne se reproduit pas.'}**", ""]
    verdicts.append(("Recalcul manuel du verdict", ok6))

    # ---------------------------------------------------------------- synthèse
    n_fail = sum(1 for _, ok in verdicts if not ok)
    lines += ["## Synthèse", "", "| Vérification | Statut |", "|---|---|"]
    for label, ok in verdicts:
        lines.append(f"| {label} | {'OK' if ok else 'ÉCHEC'} |")
    lines += ["", f"**Verdict de l'audit : {'CONFORME — aucun bug ni fuite détecté sur les 6 contrôles.' if n_fail == 0 else f'{n_fail} contrôle(s) en échec — résultat à ne pas utiliser en l état.'}**",
              "",
              "*Limite honnête de cet audit* : il vérifie l'absence de fuite et l'exactitude "
              "du calcul, PAS la validité économique du mécanisme. La question « un meilleur "
              "prédicteur de variance donne-t-il un meilleur ratio rendement/risque ? » "
              "relève des contrôles statistiques de la Règle 9 (SPA, DSR, stabilité), pas "
              "d'un audit de code."]

    out = ROOT / "results" / "nonml_volatility_managed_portfolio_gjr_audit.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
