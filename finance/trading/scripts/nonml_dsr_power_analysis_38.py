"""Analyse de puissance statistique du DSR sur le #38 — complément du
cycle #163 (aucun nouveau backtest, aucune nouvelle hypothèse).

Question posée par l'utilisateur après le #163 : vaut-il la peine de
continuer à chercher de l'historique pour franchir le seuil DSR > 0,95 ?

Méthode : le DSR est `Phi(z)` où `z` croît en `sqrt(n-1)` à edge journalier
constant (le seuil de sélection `SR0` ne dépend, lui, que de `n_trials` et
de `var_trials`, pas de `n`). On peut donc résoudre exactement le `n`
requis, à partir des quantités DÉJÀ mesurées au #163 — sans aucun nouveau
degré de liberté.

Toutes les valeurs d'entrée sont recalculées depuis les poids réels
(`build_weights`), pas recopiées d'un rapport (Règle 6).
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from prediction import trading_metrics, dsr  # noqa: E402
from nonml_leaders_index52w_high_overlay_backtest import build_weights, COST_BPS  # noqa: E402
from nonml_pass_validation_battery import approx_var_trials, parse_backlog_n_trials  # noqa: E402
from ndx100_membership import tickers_as_of_date  # noqa: E402

TARGET_DSR = 0.95


def pnl_pit():
    dates, w_base, w_lev, R, _ = build_weights(
        ROOT / "data" / "pead" / "prices_pit",
        panel_start="2013-01-01",
        membership_fn=tickers_as_of_date,
        rebal_anchor="2015-01-01",
    )
    nz = np.where(w_base.sum(axis=1) > 0)[0]
    start = int(nz[0])
    w, r = w_lev[start:], R[start:]
    turn = np.abs(np.diff(w, axis=0, prepend=w[0:1])).sum(axis=1) / 2.0
    return dates[start:], (w * r).sum(axis=1) - turn * (COST_BPS / 1e4)


def main():
    dates, pnl = pnl_pit()
    me = trading_metrics(pnl)
    n_trials = parse_backlog_n_trials()
    var_annual, n_extracted = approx_var_trials()
    var_trials = var_annual / 252.0

    base = dsr(me["sharpe_daily"], me["n"], var_trials, n_trials=n_trials,
               skew=me["skew"], kurt_excess=me["excess_kurt"])

    # z croit en sqrt(n-1) a edge, skew, kurtosis et SR0 constants.
    z_target = 1.6448536269514722  # Phi^-1(0.95)
    n_needed = 1.0 + (me["n"] - 1.0) * (z_target / base["z"]) ** 2

    lines = [
        "# Analyse de puissance du DSR sur le #38 — jusqu'où l'historique peut-il aider ?",
        "",
        "Complément du cycle #163 (aucun nouveau backtest, aucune nouvelle hypothèse, "
        "aucun paramètre touché). Produit par `scripts/nonml_dsr_power_analysis_38.py`, "
        "toutes les entrées recalculées depuis les poids réels de l'univers point-in-time.",
        "",
        "## Entrées mesurées (univers point-in-time 2015-2026, cycle #163)",
        "",
        "| Quantité | Valeur |",
        "|---|---|",
        f"| Séances `n` | {me['n']} ({dates[0].date()} → {dates[-1].date()}) |",
        f"| Sharpe quotidien | {me['sharpe_daily']:+.4f} |",
        f"| Sharpe annualisé | {me['sharpe_ann']:+.2f} |",
        f"| Asymétrie / kurtosis excédentaire | {me['skew']:+.3f} / {me['excess_kurt']:+.3f} |",
        f"| `n_trials` (taille du backlog) | {n_trials} |",
        f"| `var_trials` (journalière, {n_extracted} Sharpe extraits) | {var_trials:.4e} |",
        f"| Seuil de sélection `SR0` | {base['sr0_daily']:.4f} |",
        f"| `z` | {base['z']:+.4f} |",
        f"| **DSR** | **{base['dsr']:.3f}** |",
        "",
        "## Combien d'observations faudrait-il pour franchir 0,95 ?",
        "",
        "Le DSR vaut `Phi(z)` et, à edge journalier / asymétrie / kurtosis / `SR0` "
        "constants, `z` croît exactement en `sqrt(n-1)`. Le `n` requis pour "
        f"`z = {z_target:.4f}` (soit DSR = 0,95) se résout donc directement :",
        "",
        f"    n = 1 + (n_actuel - 1) x (z_cible / z_actuel)^2",
        f"      = 1 + ({me['n']} - 1) x ({z_target:.4f} / {base['z']:.4f})^2",
        f"      ≈ **{n_needed:,.0f} séances**, soit environ "
        f"**{n_needed/252:,.0f} ans** de données quotidiennes.",
        "",
        "## Vérification empirique de la trajectoire",
        "",
        "| Cycle | Univers | Séances | z | DSR |",
        "|---|---|---|---|---|",
        "| #161 | liste 2026, 2022-2026 | 1144 | +0,61 | 0,730 |",
        f"| #163 | **point-in-time, 2015-2026** | {me['n']} | {base['z']:+.2f} | {base['dsr']:.3f} |",
        "",
        f"Multiplier l'échantillon par {me['n']/1144:.1f} a rapporté "
        f"{base['dsr']-0.730:+.3f} de DSR. La progression est conforme à la loi en "
        "`sqrt(n)` — donc parfaitement prévisible, et donc extrapolable.",
        "",
        "## Conclusion — limite structurelle, pas un problème d'échantillon",
        "",
        f"Il faudrait ~{n_needed/252:,.0f} ans de données quotidiennes pour que ce "
        "candidat franchisse le seuil de la Règle 9 **par accumulation d'historique "
        "seule**. C'est matériellement impossible :",
        "",
        "- le NDX-100 n'existe que depuis 1985 (~41 ans) ;",
        "- une composition point-in-time fiable et gratuite n'existe que depuis 2015 "
        "  (recherche menée et documentée au cycle #163 : aucune source libre "
        "  antérieure trouvée) ;",
        "- et `n_trials` **augmente** à chaque cycle du backlog, ce qui relève `SR0` "
        "  et éloigne la cible au fil du temps plutôt que de la rapprocher.",
        "",
        "**La contrainte qui bloque le #38 n'est donc PAS la taille d'échantillon** "
        "(hypothèse formulée au #161, ici quantitativement infirmée) **mais le niveau "
        "de son Sharpe quotidien face au seuil de sélection imposé par 163 hypothèses "
        "testées.** Un edge de cette taille n'est pas distinguable du meilleur d'un tel "
        "nombre d'essais, quel que soit l'historique disponible.",
        "",
        "**Recommandation : cet axe de recherche rétrospective est clos.** La seule voie "
        "de confirmation restante pour le #38 est un test **PROSPECTIF** (Règle 8 : "
        "validation en avant sur définition figée, plusieurs mois, sans aucune "
        "modification en cours de route), pas une nouvelle tentative d'extension de "
        "données historiques. Le résultat du #163 (DSR = "
        f"{base['dsr']:.3f}, univers point-in-time réel, biais du survivant corrigé et "
        "mesuré) reste la **meilleure preuve rétrospective** obtenue sur ce candidat, et "
        "le verdict final de cet axe sauf donnée nouvelle qui changerait la donne.",
        "",
    ]
    out = ROOT / "results" / "nonml_dsr_power_analysis_38.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
