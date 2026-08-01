"""Décomposition chiffrée du DSR du #38 (univers point-in-time, cycle #163).

ANALYSE DIAGNOSTIQUE sur des résultats DÉJÀ COMMITTÉS -- pas un nouveau
backtest, pas une nouvelle hypothèse, aucun paramètre touché. Réutilise
`build_weights()` du backtest d'origine (Règle 7 : pas de réimplémentation
divergente) et `prediction.dsr()` tel quel.

Question posée : pourquoi le #38 plafonne-t-il à DSR = 0,754 plutôt que 0,95 ?
Réponse chiffrée par contrefactuels, pas qualitative :
  (a) skew = 0
  (b) kurtosis excédentaire = 0
  (c) n_trials 10x plus petit
  (d) échantillon 2x / 5x plus grand à edge journalier constant
  + le Sharpe qu'il FAUDRAIT, et l'effet de la convention de kurtosis.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics, dsr, expected_max_sharpe  # noqa: E402
from nonml_leaders_index52w_high_overlay_backtest import (  # noqa: E402
    build_weights, COST_BPS,
)
from nonml_leaders_index52w_high_overlay_pass_validation_battery import (  # noqa: E402
    portfolio_pnl,
)
from nonml_pass_validation_battery import (  # noqa: E402
    approx_var_trials, parse_backlog_n_trials,
)
from ndx100_membership import tickers_as_of_date  # noqa: E402


def dsr_z(sr, sr0, T, skew, kurt_excess):
    denom = np.sqrt(max(1e-12, 1 - skew * sr + kurt_excess / 4.0 * sr ** 2))
    return (sr - sr0) * np.sqrt(max(T - 1, 1)) / denom


def main():
    # ---------------------------------------------------------- 1. entrees
    mlog = []
    dates_full, w_base_f, w_lev_f, R, _ = build_weights(
        ROOT / "data" / "pead" / "prices_pit",
        panel_start="2013-01-01",
        membership_fn=tickers_as_of_date,
        rebal_anchor="2015-01-01",
        membership_log=mlog,
    )
    nz = np.where(w_base_f.sum(axis=1) > 0)[0]
    start = int(nz[0])
    w_base, w_lev, R_s = w_base_f[start:], w_lev_f[start:], R[start:]
    dates = pd.to_datetime(dates_full[start:])

    pnl_cand = portfolio_pnl(w_lev, R_s, COST_BPS)
    pnl_ref = portfolio_pnl(w_base, R_s, COST_BPS)
    me = trading_metrics(pnl_cand)
    me_ref = trading_metrics(pnl_ref)

    T = me["n"]
    sr = me["sharpe_daily"]
    sk = me["skew"]
    ku = me["excess_kurt"]

    n_trials = parse_backlog_n_trials()
    var_trials_annual, n_extracted = approx_var_trials()
    var_trials = var_trials_annual / 252.0
    sr0 = expected_max_sharpe(var_trials, n_trials)

    base = dsr(sr, T, var_trials, n_trials, sk, ku)

    L = []
    A = L.append
    A("# Décomposition chiffrée du DSR du #38 — pourquoi 0,754 et pas 0,95 ?")
    A("")
    A("**Analyse diagnostique, pas un nouveau backtest.** Aucune nouvelle hypothèse, "
      "aucun paramètre du #38 touché, aucun nouveau pré-enregistrement : tous les "
      "chiffres ci-dessous sont recalculés à partir des poids déjà committés du cycle "
      "#163 (`build_weights()` du backtest d'origine, univers point-in-time réel "
      "2015-2026) et de `finance/src/prediction.py::dsr` tel quel. Produit par "
      "`scripts/nonml_dsr_decomposition_38.py` (Règle 6).")
    A("")
    A("Question : le #38 est le meilleur candidat du backlog (DSR = 0,754, record). "
      "Qu'est-ce qui pèse le plus sur son DSR — l'asymétrie de sa distribution, le "
      "nombre d'essais, ou la taille d'échantillon ? La réponse est chiffrée par "
      "contrefactuels, pas devinée.")
    A("")

    # ---------------------------------------------------------- 2. mesures
    A("## 1. Entrées mesurées (recalculées, non recopiées)")
    A("")
    A("| Quantité | Valeur |")
    A("|---|---|")
    A(f"| Séances `T` | {T} ({dates[0].date()} → {dates[-1].date()}) |")
    A(f"| Sharpe quotidien candidat `SR_j` | {sr:+.6f} |")
    A(f"| Sharpe annualisé candidat | {me['sharpe_ann']:+.4f} |")
    A(f"| Sharpe annualisé référence (Leaders 1.0x) | {me_ref['sharpe_ann']:+.4f} |")
    A(f"| **Asymétrie (skew) du PnL candidat** | **{sk:+.4f}** |")
    A(f"| **Kurtosis excédentaire du PnL candidat** | **{ku:+.4f}** |")
    A(f"| Asymétrie / kurtosis exc. de la référence | {me_ref['skew']:+.4f} / {me_ref['excess_kurt']:+.4f} |")
    A(f"| `n_trials` (backlog, lu automatiquement) | {n_trials} |")
    A(f"| `var_trials` journalière ({n_extracted} Sharpe extraits) | {var_trials:.6e} |")
    A(f"| écart-type des Sharpe d'essai (annualisé) | {np.sqrt(var_trials_annual):.4f} |")
    A(f"| Seuil de sélection `SR0` (journalier) | {sr0:.6f} |")
    A(f"| `SR0` équivalent annualisé | {sr0*np.sqrt(252):.4f} |")
    A(f"| `z` | {base['z']:+.6f} |")
    A(f"| **DSR** | **{base['dsr']:.4f}** |")
    A("")
    A(f"*Traçabilité du DSR de référence.* Le rapport du cycle #163 affiche **0,754** "
      f"(calculé avec `n_trials = 162`, la taille du backlog AVANT ce cycle, comme "
      f"l'impose la Règle 9e) ; l'analyse de puissance du #164 affiche 0,753 "
      f"(`n_trials = 163`) ; ce document affiche **{base['dsr']:.4f}** "
      f"(`n_trials = {n_trials}`, valeur courante lue automatiquement dans le backlog). "
      f"L'écart est **entièrement** dû à l'incrémentation du compteur d'essais, pas à un "
      f"recalcul divergent — et il illustre déjà, à lui seul, le point n°2 de la "
      f"conclusion : chaque cycle supplémentaire dégrade mécaniquement le DSR de tous "
      f"les candidats du backlog.")
    A("")
    A(f"Lecture immédiate : le candidat doit franchir un seuil de sélection de "
      f"**{sr0*np.sqrt(252):.2f} de Sharpe annualisé** avant même de commencer à "
      f"compter. Il en affiche {me['sharpe_ann']:+.2f}. L'excédent réel n'est donc que de "
      f"**{(sr-sr0)*np.sqrt(252):+.2f}** de Sharpe annualisé — c'est CE chiffre, et non "
      f"le {me['sharpe_ann']:+.2f} affiché partout, qui est testé.")
    A("")

    # ------------------------------------------------- 3. contrefactuels
    A("## 2. Contrefactuels — qu'est-ce qui pèse le plus ?")
    A("")
    A("Chaque ligne ne change QU'UNE quantité, toutes choses égales par ailleurs.")
    A("")
    A("| Contrefactuel | `SR0` | `z` | **DSR** | Δ DSR |")
    A("|---|---|---|---|---|")
    A(f"| **Référence (#163 tel quel)** | {sr0:.4f} | {base['z']:+.4f} | **{base['dsr']:.4f}** | — |")

    rows = []

    # (a) skew nul
    d_a = dsr(sr, T, var_trials, n_trials, 0.0, ku)
    rows.append(("(a) asymétrie neutralisée (`skew = 0`)", sr0, d_a))

    # (b) kurtosis excedentaire nulle
    d_b = dsr(sr, T, var_trials, n_trials, sk, 0.0)
    rows.append(("(b) kurtosis excédentaire neutralisée (`kurt_ex = 0`)", sr0, d_b))

    # (a+b) gaussien
    d_ab = dsr(sr, T, var_trials, n_trials, 0.0, 0.0)
    rows.append(("(a+b) distribution parfaitement gaussienne", sr0, d_ab))

    # (c) n_trials / 10
    n10 = max(2, int(round(n_trials / 10)))
    sr0_10 = expected_max_sharpe(var_trials, n10)
    d_c = dsr(sr, T, var_trials, n10, sk, ku)
    rows.append((f"(c) `n_trials` 10× plus petit ({n_trials} → {n10})", sr0_10, d_c))

    # (c') n_trials = 1 (interdit, montre pour reference)
    d_c1 = dsr(sr, T, var_trials, 1, sk, ku)
    rows.append(("(c′) `n_trials = 1` — **INTERDIT (Règle 2)**, montré pour référence seule",
                 0.0, d_c1))

    # (d) echantillon 2x / 5x
    for mult in (2, 5):
        d_d = dsr(sr, int(round(T * mult)), var_trials, n_trials, sk, ku)
        rows.append((f"(d) échantillon ×{mult} à edge journalier constant "
                     f"(T = {int(round(T*mult))})", sr0, d_d))

    for label, s0, d in rows:
        A(f"| {label} | {s0:.4f} | {d['z']:+.4f} | **{d['dsr']:.4f}** | "
          f"{d['dsr']-base['dsr']:+.4f} |")
    A("")

    # ------------------------------------------- 4. verdict de sensibilite
    ordered = sorted(
        [("asymétrie (a)", d_a["dsr"] - base["dsr"]),
         ("kurtosis (b)", d_b["dsr"] - base["dsr"]),
         ("distribution gaussienne (a+b)", d_ab["dsr"] - base["dsr"]),
         ("n_trials ÷10 (c)", d_c["dsr"] - base["dsr"]),
         ("échantillon ×5 (d)", dsr(sr, T * 5, var_trials, n_trials, sk, ku)["dsr"] - base["dsr"])],
        key=lambda kv: -abs(kv[1]))
    A("### Hiérarchie des leviers (par |Δ DSR| décroissant)")
    A("")
    for k, (lab, delta) in enumerate(ordered, 1):
        A(f"{k}. **{lab}** : {delta:+.4f}")
    A("")

    # ------------------------------------ 5. Sharpe requis / n requis
    A("## 3. Combien faudrait-il, exactement ?")
    A("")
    z_target = float(stats.norm.ppf(0.95))
    # SR requis a T et n_trials constants : resout z(sr)=z_target par bissection
    lo, hi = sr0, sr0 + 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if dsr_z(mid, sr0, T, sk, ku) < z_target:
            lo = mid
        else:
            hi = mid
    sr_req = 0.5 * (lo + hi)
    A(f"- **Sharpe requis à échantillon et `n_trials` inchangés** : "
      f"`SR_j = {sr_req:.6f}` soit **{sr_req*np.sqrt(252):.2f} de Sharpe annualisé** "
      f"(contre {me['sharpe_ann']:+.2f} observé, soit **×{sr_req/sr:.2f}**).")
    n_req = 1 + (T - 1) * (z_target / base["z"]) ** 2
    A(f"- **Échantillon requis à edge constant** : `T = {n_req:,.0f}` séances, soit "
      f"**~{n_req/252:.0f} ans** (confirme `results/nonml_dsr_power_analysis_38.md`).")
    # n_trials requis
    n_req_trials = None
    for nt in range(2, n_trials + 1):
        s0 = expected_max_sharpe(var_trials, nt)
        if dsr_z(sr, s0, T, sk, ku) >= z_target:
            n_req_trials = nt
    A(f"- **`n_trials` maximal compatible avec DSR > 0,95**, à edge et échantillon "
      f"inchangés : **{n_req_trials}** (contre {n_trials} réellement testés). "
      f"*Information de diagnostic uniquement — la Règle 2 interdit de choisir "
      f"`n_trials` pour obtenir un résultat.*")
    A("")

    # ------------------------------------ 6. convention de kurtosis
    A("## 4. Contrôle de la convention de kurtosis (Règle 6)")
    A("")
    A("La formule canonique de Bailey & López de Prado (« The Sharpe Ratio Efficient "
      "Frontier », 2012) écrit le dénominateur `sqrt(1 − γ3·SR + ((γ4−1)/4)·SR²)` où "
      "**γ4 est la kurtosis NON excédentaire** (γ4 = 3 pour une gaussienne). "
      "`finance/src/prediction.py::dsr` utilise `kurt_excess/4 = (γ4−3)/4`, soit un "
      "écart de `0,5·SR²` sur le carré du dénominateur.")
    A("")
    denom_repo = np.sqrt(1 - sk * sr + ku / 4.0 * sr ** 2)
    denom_canon = np.sqrt(1 - sk * sr + (ku + 3 - 1) / 4.0 * sr ** 2)
    z_canon = (sr - sr0) * np.sqrt(T - 1) / denom_canon
    dsr_canon = float(stats.norm.cdf(z_canon))
    A(f"| Convention | dénominateur | `z` | DSR |")
    A(f"|---|---|---|---|")
    A(f"| repo (`kurt_excess/4`) | {denom_repo:.6f} | {base['z']:+.6f} | {base['dsr']:.4f} |")
    A(f"| canonique (`(γ4−1)/4`) | {denom_canon:.6f} | {z_canon:+.6f} | {dsr_canon:.4f} |")
    A("")
    A(f"**Écart : {dsr_canon-base['dsr']:+.5f} de DSR.** L'implémentation du repo est "
      f"donc marginalement OPTIMISTE (elle sous-estime le dénominateur, donc surestime "
      f"`z`). Aucun verdict déjà rendu ne change — tous les FAIL du backlog sont très "
      f"loin du seuil, et cet écart les enfoncerait plutôt. Signalé pour traçabilité, "
      f"pas corrigé ici (corriger `dsr()` modifierait rétroactivement 20 rapports "
      f"déjà committés ; ce serait une décision de protocole, pas une décision "
      f"d'analyse).")
    A("")

    # ------------------------------------ 7. conclusion
    A("## 5. Conclusion — quel levier est le plus prometteur, à partir de CE diagnostic")
    A("")
    A(f"**1. Les leviers distributionnels sont morts.** Neutraliser l'asymétrie rapporte "
      f"{d_a['dsr']-base['dsr']:+.4f} de DSR, neutraliser la kurtosis "
      f"{d_b['dsr']-base['dsr']:+.4f}, et rendre la distribution parfaitement gaussienne "
      f"{d_ab['dsr']-base['dsr']:+.4f}. La raison est structurelle et vaudra pour TOUTE "
      f"stratégie évaluée en quotidien dans ce repo : le terme d'asymétrie vaut "
      f"`skew × SR_j` ≈ {abs(sk*sr):.4f} et celui de kurtosis `kurt_ex/4 × SR_j²` ≈ "
      f"{ku/4*sr**2:.4f}, face à un 1 au dénominateur. **L'intuition « chercher une "
      f"famille à asymétrie positive pour aider le DSR » est donc quantitativement "
      f"réfutée à cette fréquence** — c'est une bonne idée pour le contrôle de crise "
      f"(Règle 9b, précisément celui que le #38 vient de perdre), pas pour le DSR.")
    A("")
    A(f"**2. Le levier dominant est le rapport `SR_j / SR0`, de très loin.** Diviser "
      f"`n_trials` par 10 ferait passer le DSR de {base['dsr']:.3f} à {d_c['dsr']:.3f} "
      f"({d_c['dsr']-base['dsr']:+.3f}) — c'est-à-dire que **le nombre d'hypothèses "
      f"testées dans ce programme de recherche pèse plus lourd sur le verdict du #38 "
      f"que toutes ses propriétés statistiques réunies.** C'est un constat désagréable "
      f"mais central : ce n'est pas la stratégie qui échoue, c'est la stratégie *dans "
      f"ce contexte de recherche*. Et ce levier n'est **pas actionnable honnêtement** : "
      f"`n_trials` ne peut que croître (Règle 2), il vaudra {n_trials+1}, {n_trials+2}… "
      f"au prochain cycle. Chaque cycle supplémentaire relève `SR0` et éloigne la cible.")
    A("")
    A(f"**3. La taille d'échantillon est un levier réel mais insuffisant.** ×2 donne "
      f"{dsr(sr, 2*T, var_trials, n_trials, sk, ku)['dsr']:.3f}, ×5 donne "
      f"{dsr(sr, 5*T, var_trials, n_trials, sk, ku)['dsr']:.3f} — toujours sous 0,95. "
      f"Déjà tranché au #164 (~67 ans requis) ; ce diagnostic le confirme par un autre "
      f"chemin.")
    A("")
    A(f"**4. Le seul levier honnête et suffisant est donc le niveau du Sharpe "
      f"quotidien.** Il faudrait **{sr_req*np.sqrt(252):.2f} de Sharpe annualisé** "
      f"(×{sr_req/sr:.2f} l'actuel) sur le même échantillon. **Aucun réglage du #38 ne "
      f"peut produire ça** : sa robustesse est déjà un plateau parfait, son SPA passe "
      f"déjà à p=0,0000, et un Sharpe de 1,7 n'est pas atteignable par un portefeuille "
      f"long-only levé dont la volatilité est dominée par celle du marché.")
    A("")
    A(f"**5. Conséquence de conception, tirée de CE diagnostic et pas d'une intuition "
      f"générale.** Puisque (i) la forme de la distribution ne compte pas, (ii) "
      f"`n_trials` ne peut que grandir, (iii) l'historique est borné, alors la seule "
      f"voie est un mécanisme dont le Sharpe quotidien est structurellement plus élevé "
      f"— pas parce qu'il gagne plus, mais parce que **son dénominateur est plus "
      f"petit**. Le #38 a une volatilité annualisée de "
      f"{100*np.std(pnl_cand, ddof=1)*np.sqrt(252):.1f} %, presque entièrement du "
      f"risque de marché : il porte une exposition de 1,0x à 2,0x en permanence. Une "
      f"construction **dollar-neutre** retire ce terme du dénominateur sans retirer "
      f"l'alpha, et une construction à **grande ampleur** (au sens de Grinold, "
      f"`IR ≈ IC·sqrt(BR)`) est le seul moyen documenté d'obtenir un IC modeste × un "
      f"grand nombre de paris indépendants. C'est la conclusion qui motive la Phase 3 "
      f"(voir `RECHERCHE_dsr_par_construction.md`, §7 piste A).")
    A("")
    A(f"**6. Ce que ce diagnostic NE dit pas.** Il ne dit pas qu'un mécanisme "
      f"dollar-neutre atteindra 1,7 de Sharpe sur cet univers — la littérature "
      f"(Do & Faff 2010) documente au contraire une érosion forte des stratégies "
      f"relative-value après 2003, et notre échantillon commence en 2015. Il dit "
      f"seulement que c'est la **seule famille dont le profil statistique rend la "
      f"barre atteignable en principe**. Si elle échoue aussi, la conclusion honnête "
      f"sera qu'aucune stratégie testable avec ces données ne peut franchir la Règle 9e "
      f"— ce qui serait une information de premier ordre pour la suite du projet.")
    A("")

    out = ROOT / "results" / "nonml_dsr_decomposition_38.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
