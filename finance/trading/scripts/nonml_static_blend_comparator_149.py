"""Comparateur blend statique vs #149 (spécification pré-enregistrée dans
PREREG_static_blend_comparator_149.md, committée avant ce script). PAS un
nouveau cycle du backlog non-ML -- question de déploiement Voie A.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FINANCE_ROOT = ROOT.parent
sys.path.insert(0, str(FINANCE_ROOT / "src"))

from prediction import trading_metrics  # noqa: E402

COST_BPS = 5.0


def pnl_static(weight, r_asset, r_alt, cost_bps):
    pos = np.full_like(r_asset, weight)
    turn = np.abs(np.diff(pos, prepend=1.0))  # meme convention que #149 : position de depart = 1.0 (BH)
    return pos * r_asset + (1.0 - pos) * r_alt - turn * (cost_bps / 1e4)


def pnl_dynamic(pos, r_asset, r_alt, cost_bps):
    turn = np.abs(np.diff(pos, prepend=1.0))
    return pos * r_asset + (1.0 - pos) * r_alt - turn * (cost_bps / 1e4)


def pnl_bh(r_asset, cost_bps):
    pnl = r_asset.copy()
    pnl[0] -= cost_bps / 1e4
    return pnl


def main():
    d = np.load(ROOT / "results" / "nonml_cash_rate_correction_defensive_vol_targeting_44_pnl.npz", allow_pickle=True)
    pos, r_asset, r_alt = d["pos"], d["r_asset"], d["r_alt"]

    static_weight = float(np.mean(pos))

    pnl_dyn = pnl_dynamic(pos, r_asset, r_alt, COST_BPS)
    pnl_stat = pnl_static(static_weight, r_asset, r_alt, COST_BPS)
    pnl_buyhold = pnl_bh(r_asset, COST_BPS)

    m_dyn = trading_metrics(pnl_dyn)
    m_stat = trading_metrics(pnl_stat)
    m_bh = trading_metrics(pnl_buyhold)

    def total_return_pct(pnl):
        # Meme convention que scripts/nonml_pass_validation_battery.py
        # (cumprod(1+r)-1) -- pas exp(cumsum(r))-1, pour rester directement
        # comparable aux tableaux de batterie deja publies (#134/#149).
        # Note methodologique : r etant un rendement LOG, exp(cumsum(r))-1
        # serait la formule exacte ; cumprod(1+r)-1 est une approximation
        # deja utilisee partout ailleurs dans le backlog non-ML. Ecart
        # constate a la construction de ce script (exp(cumsum) donnait ici
        # +25466% de rendement BH contre le chiffre cumprod ci-dessous) --
        # n'affecte aucun verdict PASS/FAIL deja rendu (comparaison
        # relative, meme formule des deux cotes a chaque fois), mais vaut
        # un point de vigilance pour un futur audit du backlog non-ML.
        return 100.0 * (np.cumprod(1.0 + pnl[np.isfinite(pnl)])[-1] - 1.0)

    threshold_ok = m_stat["sharpe_ann"] >= m_dyn["sharpe_ann"] - 0.05

    lines = [
        "# Comparateur blend statique vs #149 (Voie A, spécification pré-enregistrée)",
        "",
        f"Poids statique = exposition moyenne réelle de #149 sur la période : {static_weight:.4f}",
        f"({len(pos)} séances, coût {COST_BPS} bps, rebalancement quotidien vers poids constant).",
        "",
        "| Portefeuille | Sharpe ann. | Rendement total net | MDD | Calmar |",
        "|---|---|---|---|---|",
        f"| Buy&Hold pur | {m_bh['sharpe_ann']:+.2f} | {total_return_pct(pnl_buyhold):+.1f}% | {m_bh['max_drawdown_pct']:.1f}% | {m_bh['calmar']:.3f} |",
        f"| Blend statique (poids={static_weight:.3f}) | {m_stat['sharpe_ann']:+.2f} | {total_return_pct(pnl_stat):+.1f}% | {m_stat['max_drawdown_pct']:.1f}% | {m_stat['calmar']:.3f} |",
        f"| #149 dynamique (vol-targeting + diversification) | {m_dyn['sharpe_ann']:+.2f} | {total_return_pct(pnl_dyn):+.1f}% | {m_dyn['max_drawdown_pct']:.1f}% | {m_dyn['calmar']:.3f} |",
        "",
        f"Critère pré-enregistré : blend statique préféré si Sharpe(statique) >= Sharpe(#149) - 0.05.",
        f"Sharpe(statique) - Sharpe(#149) = {m_stat['sharpe_ann'] - m_dyn['sharpe_ann']:+.3f}",
        "",
        f"**Verdict : {'BLEND STATIQUE PRÉFÉRÉ (déployer le statique, plus simple)' if threshold_ok else 'DYNAMIQUE CONSERVE UNE VALEUR SUFFISANTE (continuer le shadow-trading du dynamique)'}**",
        "",
        "Ne change aucun verdict Règle 9 déjà rendu sur #149 (reste 3/5, SPA et "
        "DSR à n_trials=125 toujours en échec). Cette comparaison porte "
        "uniquement sur le choix opérationnel de déploiement (§2 du document "
        "de déploiement Voie A), pas sur la validité statistique du timing.",
    ]

    out = ROOT / "results" / "nonml_static_blend_comparator_149.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
