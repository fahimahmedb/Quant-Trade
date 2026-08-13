"""Audit adversarial — Leaders + overlay vol-targeting 20 %, univers point-in-time.

Six contrôles indépendants du backtest :

1. **Recalcul du P&L par simulation en NOMBRE DE PARTS** (+ diagnostic 1b : cet
   écart de niveau peut-il retourner le verdict ?).
2. **Recalcul indépendant de la sélection Leaders** par un chemin de code
   disjoint (`pandas.rolling` au lieu de la boucle NumPy du backtest).
3. **Anti-lookahead par perturbation du futur** sur les prix.
4. **Respect de l'appartenance point-in-time** à la date de décision.
5. **Causalité du décalage des poids** (un jour, exactement).
6. **Causalité de l'exposition** : la volatilité qui dimensionne la position du
   jour t doit être entièrement connue en t−1. Contrôle propre à ce candidat,
   dont l'overlay est piloté par le portefeuille lui-même et non par un signal
   externe — c'est là que se logerait une fuite circulaire.

Usage : python3 scripts/nonml_leaders_vol_targeting_20_overlay_pit_universe_audit.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics  # noqa: E402
import nonml_leaders_vol_targeting_20_overlay_pit_universe_backtest as bt  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

OUT = ROOT / "results" / "nonml_leaders_vol_targeting_20_overlay_pit_universe_audit.md"


def rebuild_weights_pandas():
    """Reconstruction INDEPENDANTE des poids Leaders.

    Le backtest calcule le plus-haut 252j par une boucle NumPy explicite ; ici on
    passe par `pandas.rolling(...).max()`, dont le `min_periods` par defaut exige
    252 observations valides -- equivalent logique du masque `has_full` du
    backtest, mais code entierement disjoint.
    """
    series = bt.load_prices_pit()
    tickers = sorted(series.keys())
    ref_idx = None
    for t in tickers:
        ref_idx = series[t].index if ref_idx is None else ref_idx.union(series[t].index)
    ref_idx = ref_idx.sort_values()
    P = pd.DataFrame({t: series[t].reindex(ref_idx) for t in tickers})
    T, n = P.shape
    tickers = list(P.columns)

    ratio = (P / P.rolling(bt.LOOKBACK).max()).values
    n_top = max(1, int(round(n * bt.TERCILE)))
    W = np.zeros((T, n))
    investable = np.zeros(T, dtype=bool)

    rebal = list(range(bt.LOOKBACK, T, bt.REBAL_EVERY))
    for k, t in enumerate(rebal):
        end = rebal[k + 1] if k + 1 < len(rebal) else T
        if P.index[t] < bt.COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[t])
        if not members:
            continue
        mc = np.array([tickers[j] in members for j in range(n)])
        r = ratio[t]
        elig = np.where(np.isfinite(r) & mc)[0]
        k_t = min(n_top, len(elig))
        if k_t > 0:
            top = elig[np.argsort(-r[elig])[:k_t]]
            w = np.zeros(n)
            w[top] = 1.0 / k_t
            W[t:end] = w
            investable[t:end] = True
    return P, tickers, W, investable


def equity_by_shares(P, W_lagged, start_eff):
    """Simulation en NOMBRE DE PARTS — aucune formule de rendement.

    Retourne la valeur finale ET le chemin d'equite complet.
    """
    close = P.values
    value = 1.0
    shares = None
    prev_w = None
    path = np.empty(len(P) - start_eff)
    for t in range(start_eff, len(P)):
        if shares is not None:
            px = np.nan_to_num(close[t], nan=0.0)
            held = np.nan_to_num(shares, nan=0.0)
            value = float((held * px).sum())
        path[t - start_eff] = value
        w = W_lagged[t]
        if prev_w is None or not np.array_equal(w, prev_w):
            px = close[t]
            with np.errstate(divide="ignore", invalid="ignore"):
                shares = np.where((w > 0) & np.isfinite(px) & (px > 0), value * w / px, 0.0)
            prev_w = w.copy()
    return value, path


def main():
    L = ["# Audit adversarial — Leaders + overlay vol-targeting 20 %, univers point-in-time", ""]
    L.append("Le backtest conclut **FAIL** ; l'audit vérifie que ce FAIL est le produit d'un")
    L.append("calcul correct et non d'un bug — un verdict négatif mérite le même contrôle")
    L.append("qu'un verdict positif, sans quoi on ne filtrerait que dans un sens.")
    L.append("")

    P_bt, tickers_bt, W_bt, inv_bt, _cov = bt.build_weights()
    P, tickers, W, investable = rebuild_weights_pandas()

    R = np.nan_to_num((P_bt / P_bt.shift(1) - 1.0).values, nan=0.0)
    R[0, :] = 0.0
    pnl_raw = (W_bt * R).sum(axis=1)
    exposure = bt.vol_target_exposure(pnl_raw)

    W_lag = bt.lag_one_day(W_bt)
    W_lev_lag = bt.lag_one_day(W_bt * exposure[:, None])
    inv_lag = np.concatenate(([False], inv_bt[:-1]))
    first = int(np.argmax(inv_lag)) if inv_lag.any() else len(P_bt)
    start_eff = max(bt.LOOKBACK + bt.VOL_WINDOW, first + bt.VOL_WINDOW)

    # --- 1. recalcul par parts (sans couts, on isole la mecanique) ---
    val_shares, eq_shares = equity_by_shares(P_bt, W_lag, start_eff)
    pnl_formula = (W_lag[start_eff:] * R[start_eff:]).sum(axis=1)
    val_formula = float(np.cumprod(1.0 + pnl_formula)[-1])
    rel = abs(val_formula - val_shares) / val_shares

    L.append("## 1. Recalcul du P&L par simulation en nombre de parts")
    L.append("")
    L.append("Chemin comptable pur : capital réparti, parts détenues, portefeuille")
    L.append("revalorisé aux prix. Aucune formule de rendement n'intervient — ce contrôle")
    L.append("ne partage aucune ligne de calcul avec le backtest. Sans coûts, sur la jambe")
    L.append("de référence (1,0×), pour isoler la mécanique d'agrégation.")
    L.append("")
    L.append(f"- capital final, formule `Σ wᵢ·r_simple,ᵢ` : **{val_formula:.4f}**")
    L.append(f"- capital final, simulation en parts : **{val_shares:.4f}**")
    L.append(f"- écart relatif : **{100*rel:.2f} %**")
    L.append("")
    ok1 = rel < 0.05
    L.append(f"**{'CONFORME' if ok1 else 'ÉCART SIGNIFICATIF'}** — l'écart résiduel provient de la")
    L.append("dérive des poids entre deux rebalancements, que la formule suppose constants.")
    L.append("")
    if not ok1:
        L.append("Le seuil de 5 % vient du gabarit d'audit des cycles précédents ; il est")
        L.append("**conservé tel quel**, pas relâché après lecture du résultat. Il est franchi")
        L.append("pour la même raison qu'au #401 : 11,5 ans et un panier de momentum dispersé,")
        L.append("là où la formule rééquilibre implicitement tous les jours.")
        L.append("")

    # --- 1b. diagnostic : le verdict tient-il par le chemin en parts ? ---
    # pnl_lev[t] = exposure[t-1] * pnl_base[t] exactement (l'exposition est un
    # scalaire par date), on peut donc rejouer les deux jambes a partir des
    # rendements du chemin en parts. Ce diagnostic ne MODIFIE PAS le verdict.
    turn_b = np.abs(np.diff(W_lag[start_eff:], axis=0,
                            prepend=W_lag[start_eff:start_eff + 1])).sum(axis=1) / 2.0
    turn_l = np.abs(np.diff(W_lev_lag[start_eff:], axis=0,
                            prepend=W_lev_lag[start_eff:start_eff + 1])).sum(axis=1) / 2.0
    r_sh = np.concatenate(([0.0], eq_shares[1:] / eq_shares[:-1] - 1.0))
    exp_lag = np.concatenate(([1.0], exposure[start_eff:-1]))
    c = bt.COST_BPS / 1e4
    pnl_b_sh = r_sh - turn_b * c
    pnl_l_sh = exp_lag * r_sh - turn_l * c
    me_b_sh = trading_metrics(np.log1p(pnl_b_sh))
    me_l_sh = trading_metrics(np.log1p(pnl_l_sh))
    ret_b_sh = float(np.cumprod(1.0 + pnl_b_sh)[-1] - 1.0)
    ret_l_sh = float(np.cumprod(1.0 + pnl_l_sh)[-1] - 1.0)
    sh_ok = me_l_sh["sharpe_ann"] > me_b_sh["sharpe_ann"]
    rt_ok = ret_l_sh > ret_b_sh

    L.append("### 1b. L'écart de niveau peut-il retourner le verdict ?")
    L.append("")
    L.append("Le contrôle 1 mesure un écart de **niveau**. Question distincte : suffit-il à")
    L.append("changer le **verdict** ? Le P&L de la jambe levier vaut exactement")
    L.append("`exposure[t−1] × P&L de la jambe base` (l'exposition est un scalaire par date),")
    L.append("on peut donc rejouer les deux jambes à partir des rendements du chemin en parts.")
    L.append("")
    L.append("**Ce diagnostic ne modifie pas le verdict pré-enregistré**, quel qu'en soit le")
    L.append("résultat : le protocole fige la formule d'agrégation du backtest.")
    L.append("")
    L.append("| Chemin en parts | Sharpe ann. | Rendement total net |")
    L.append("|---|---|---|")
    L.append(f"| Leaders 1.0x | {me_b_sh['sharpe_ann']:+.2f} | {100*ret_b_sh:+.1f}% |")
    L.append(f"| Leaders + vol-targeting 20 % | {me_l_sh['sharpe_ann']:+.2f} | {100*ret_l_sh:+.1f}% |")
    L.append("")
    L.append(f"- Sharpe overlay > référence : **{'OUI' if sh_ok else 'non'}**")
    L.append(f"- Rendement overlay > référence : **{'OUI' if rt_ok else 'non'}**")
    L.append("")
    L.append(f"Conclusion du diagnostic : par ce second chemin le critère renforcé serait "
             f"**{'ATTEINT' if (sh_ok and rt_ok) else 'MANQUÉ'}** — "
             + ("il concorde donc avec le FAIL du backtest."
                if not (sh_ok and rt_ok) else
                "il **diverge** du FAIL du backtest, ce qui est consigné tel quel."))
    L.append("")

    # --- 2. recalcul independant de la selection ---
    same_w = bool(np.allclose(W, W_bt, atol=1e-12))
    n_diff = int((np.abs(W - W_bt) > 1e-12).any(axis=1).sum())
    L.append("## 2. Recalcul indépendant de la sélection Leaders")
    L.append("")
    L.append("Le backtest calcule le plus-haut 252 jours par une boucle NumPy sur fenêtres")
    L.append("glissantes ; l'audit le recalcule par `pandas.rolling(252).max()`. Les deux")
    L.append("chemins ne partagent aucune ligne.")
    L.append("")
    L.append(f"- matrices de poids identiques : **{'OUI' if same_w else 'NON'}**")
    L.append(f"- séances où les poids diffèrent : **{n_diff}** / {len(P)}")
    L.append("")
    L.append(f"**{'CONFORME — la sélection est reproductible par un second chemin.' if same_w else 'DIVERGENCE — les deux implémentations ne concordent pas.'}**")
    L.append("")

    # --- 3. anti-lookahead sur les prix ---
    cut = len(P) // 2
    P_pert = P.copy()
    P_pert.iloc[cut:] = P_pert.iloc[cut:] * 5.0
    saved = bt.load_prices_pit
    bt.load_prices_pit = lambda: {c_: P_pert[c_].dropna() for c_ in P_pert.columns}  # noqa: E731
    try:
        _, _, W_pert, _ = rebuild_weights_pandas()
    finally:
        bt.load_prices_pit = saved
    same_before = bool(np.array_equal(W[:cut], W_pert[:cut]))

    L.append("## 3. Anti-lookahead — perturbation du futur")
    L.append("")
    L.append(f"Les prix après l'indice {cut} sont multipliés par 5. Les poids AVANT cette")
    L.append("date doivent être **strictement** identiques.")
    L.append("")
    L.append(f"- poids identiques avant la coupure : **{'OUI' if same_before else 'NON'}**")
    L.append("")
    L.append(f"**{'CONFORME — aucune fuite du futur.' if same_before else 'FUITE DÉTECTÉE — résultat invalide.'}**")
    L.append("")

    # --- 4. appartenance PIT ---
    rebal_dates = list(range(bt.LOOKBACK, len(P), bt.REBAL_EVERY))
    viol_decision = checked_decision = 0
    for t in rebal_dates:
        if P.index[t] < bt.COMPOSITION_START:
            continue
        members = tickers_as_of_date(P.index[t])
        if not members:
            continue
        checked_decision += 1
        for j in np.where(W_bt[t] > 0)[0]:
            if tickers[j] not in members:
                viol_decision += 1

    held_through_exit = checked_hold = 0
    for t in range(start_eff, len(P), 200):
        members = tickers_as_of_date(P.index[t])
        if not members:
            continue
        checked_hold += 1
        for j in np.where(W_bt[t] > 0)[0]:
            if tickers[j] not in members:
                held_through_exit += 1

    L.append("## 4. Respect de l'appartenance point-in-time")
    L.append("")
    L.append("**Ce qui constituerait une fuite** : sélectionner à la date de DÉCISION un")
    L.append("titre pas encore membre de l'indice.")
    L.append("")
    L.append(f"- dates de rebalancement vérifiées : **{checked_decision}**")
    L.append(f"- sélections d'un non-membre à la décision : **{viol_decision}**")
    L.append("")
    L.append(f"**{'CONFORME' if viol_decision == 0 else 'FUITE DÉTECTÉE'}** — aucun titre n'est "
             f"sélectionné avant son entrée dans l'indice.")
    L.append("")
    L.append("**Ce qui n'en est pas une, mais mérite d'être documenté** : un titre sorti de")
    L.append("l'indice entre deux rebalancements reste détenu jusqu'au suivant — comportement")
    L.append("réaliste d'un portefeuille rebalancé tous les 21 jours.")
    L.append("")
    L.append(f"- dates échantillonnées hors rebalancement : **{checked_hold}**")
    L.append(f"- positions détenues sur un titre sorti de l'indice : **{held_through_exit}**")
    L.append("")

    # --- 5. causalite du decalage des poids ---
    ok5 = bool(np.array_equal(W_lag[1:], W_bt[:-1])) and bool((W_lag[0] == 0).all())
    L.append("## 5. Causalité du décalage des poids")
    L.append("")
    L.append("Le poids appliqué au rendement du jour t doit avoir été décidé en t−1.")
    L.append("")
    L.append(f"- décalage d'exactement un jour vérifié : **{'OUI' if ok5 else 'NON'}**")
    L.append("")
    L.append(f"**{'CONFORME' if ok5 else 'ANOMALIE'}**")
    L.append("")

    # --- 6. causalite de l'EXPOSITION (propre a ce candidat) ---
    # L'overlay est pilote par le portefeuille lui-meme : si l'exposition du jour
    # t utilisait le P&L du jour t, la position serait dimensionnee par un
    # rendement pas encore realise. Test : on perturbe le P&L a partir d'un
    # indice k ; l'exposition jusqu'a k INCLUS doit rester inchangee.
    k = len(pnl_raw) // 2
    pnl_pert = pnl_raw.copy()
    pnl_pert[k:] = pnl_pert[k:] * 10.0 + 0.05
    exp_pert = bt.vol_target_exposure(pnl_pert)
    exp_causal = bool(np.allclose(exposure[:k + 1], exp_pert[:k + 1], equal_nan=True))
    first_diff = int(np.argmax(~np.isclose(exposure, exp_pert, equal_nan=True)))

    L.append("## 6. Causalité de l'exposition — contrôle propre à ce candidat")
    L.append("")
    L.append("L'overlay n'est pas piloté par un signal externe mais par la volatilité du")
    L.append("portefeuille **lui-même** : c'est là que se logerait une fuite circulaire, si")
    L.append("l'exposition du jour t utilisait le P&L du jour t. Test : le P&L est perturbé à")
    L.append(f"partir de l'indice {k} ; l'exposition jusqu'à cet indice **inclus** doit rester")
    L.append("inchangée.")
    L.append("")
    L.append(f"- exposition inchangée jusqu'à l'indice {k} inclus : **{'OUI' if exp_causal else 'NON'}**")
    L.append(f"- premier indice où l'exposition diffère : **{first_diff}** (attendu : ≥ {k + 1})")
    L.append("")
    L.append(f"**{'CONFORME — la volatilité qui dimensionne la position du jour t est entièrement connue en t−1.' if exp_causal else 'FUITE CIRCULAIRE — le dimensionnement utilise le rendement du jour même.'}**")
    L.append("")

    verdict = ok1 and same_w and same_before and (viol_decision == 0) and ok5 and exp_causal
    hard_ok = same_w and same_before and (viol_decision == 0) and ok5 and exp_causal
    L.append("## Verdict de l'audit")
    L.append("")
    if verdict:
        L.append("**CONFORME — les six contrôles passent.**")
        L.append("")
        L.append("Le **FAIL** du backtest est donc un résultat calculé correctement, pas un")
        L.append("artefact d'implémentation.")
    elif hard_ok:
        L.append("**RÉSERVE — seul le contrôle 1 dépasse sa tolérance de 5 %.**")
        L.append("")
        L.append("Les contrôles 2 à 6 passent : sélection reproductible par un chemin de code")
        L.append("disjoint, aucune fuite du futur, aucune sélection hors appartenance, décalage")
        L.append("causal exact, et dimensionnement de position sans fuite circulaire. La seule")
        L.append("réserve porte sur l'écart de niveau du contrôle 1, dont le diagnostic 1b")
        L.append("montre " + ("qu'il ne retourne pas le verdict." if not (sh_ok and rt_ok)
                              else "qu'il **retournerait** le verdict par ce second chemin."))
        L.append("")
        L.append("Le verdict pré-enregistré reste **FAIL** : le protocole fige la formule")
        L.append("d'agrégation, et on ne rejuge pas un résultat après l'avoir lu.")
    else:
        L.append("**NON CONFORME — au moins un contrôle structurel échoue.**")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
