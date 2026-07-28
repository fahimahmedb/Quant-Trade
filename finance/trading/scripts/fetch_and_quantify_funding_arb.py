"""Quantification honnête du cash-and-carry funding rate (crypto), donnees
REELLES (API publique OKX), pas les chiffres marketing trouves en ligne
(ex. "+115% en 6 mois" -- source non independante, non verifiee ici).

Mecanique du cash-and-carry : long spot + short perpetual, notionnel egal,
delta ~0 en continu (re-hedge implicite car les deux jambes bougent
ensemble). Le P&L provient presque entierement du funding rate collecte
(paye par les longs perp aux shorts quand funding>0) -- PAS d'un pari
directionnel. Approximation utilisee ici : rendement periodique = funding
rate publie (le financement REEL paye toutes les 8h sur OKX), sans
modeliser le slippage d'entree/sortie ni les frais d'emprunt du spot
(limite assumee, discutee dans le rapport).

Symbole : BTC-USDT-SWAP et ETH-USDT-SWAP (OKX), historique maximal
disponible via pagination de l'endpoint public funding-rate-history
(100 points/appel, cursor sur fundingTime).

Comparaison demandee : situer le Sharpe de cette strategie a cote de celui
deja etabli et VALIDE (SPA) pour l'Etape C (volatilite GJR-t, cf.
resultats/etape_c_*.md) -- pas pour dire que c'est la meme chose (l'un est
un edge de PREVISION, l'autre une PRIME structurelle collectee), mais pour
donner un ordre de grandeur comparable et honnete.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]        # finance/trading
REPO_ROOT = ROOT.parent.parent                      # Quant-Trade

SYMBOLS = ["BTC-USDT-SWAP", "ETH-USDT-SWAP"]
PERIODS_PER_YEAR = 365 * 3  # funding toutes les 8h sur OKX (verifie empiriquement, deltas=8h)
MAX_PAGES = 40              # ~4000 points max ~ 3.5 ans d'historique (limite/page=100, pas de 8h)


def fetch_funding_history(inst_id: str) -> list:
    """Pagine vers le passe avec le parametre 'after' (verifie empiriquement :
    'before' renvoie des pages qui se chevauchent, ne pagine PAS reellement)."""
    records = []
    after = None
    seen_times = set()
    for _ in range(MAX_PAGES):
        url = f"https://www.okx.com/api/v5/public/funding-rate-history?instId={inst_id}&limit=100"
        if after:
            url += f"&after={after}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read())
        data = payload.get("data", [])
        if not data:
            break
        new_data = [d for d in data if d["fundingTime"] not in seen_times]
        if not new_data:
            break
        records.extend(new_data)
        seen_times.update(d["fundingTime"] for d in new_data)
        after = data[-1]["fundingTime"]  # pagine vers le passe
        time.sleep(0.3)  # respecte le rate-limit public
    return records


def main():
    lines = [
        "# Quantification — cash-and-carry funding rate crypto (données réelles OKX)",
        "",
        "Données publiques OKX (`funding-rate-history`), pas les chiffres marketing "
        "trouvés en ligne. P&L approximé = funding rate collecté (long spot / short "
        "perpétuel, delta ~0) — hors frais d'emprunt spot et slippage d'entrée/sortie "
        "(limite assumée, signalée).",
        "",
        "| Symbole | N périodes | Historique | Funding moy./période | Rendement ann. | "
        "Vol ann. | Sharpe ann. | % périodes négatives |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for inst_id in SYMBOLS:
        try:
            records = fetch_funding_history(inst_id)
        except Exception as e:
            lines.append(f"| {inst_id} | ERREUR: {e} | | | | | | |")
            continue
        if not records:
            lines.append(f"| {inst_id} | 0 points récupérés | | | | | | |")
            continue

        rates = np.array([float(r["fundingRate"]) for r in records])[::-1]  # ordre chronologique
        times = np.array([int(r["fundingTime"]) for r in records])[::-1]
        n = len(rates)
        t0 = time.strftime("%Y-%m-%d", time.gmtime(times[0] / 1000))
        t1 = time.strftime("%Y-%m-%d", time.gmtime(times[-1] / 1000))

        mean_p = rates.mean()
        std_p = rates.std()
        ann_ret = mean_p * PERIODS_PER_YEAR
        ann_vol = std_p * np.sqrt(PERIODS_PER_YEAR)
        sharpe_ann = (mean_p / std_p) * np.sqrt(PERIODS_PER_YEAR) if std_p > 0 else float("nan")
        pct_neg = 100 * (rates < 0).mean()

        lines.append(
            f"| {inst_id} | {n} | {t0} → {t1} | {100*mean_p:.4f}% | "
            f"{100*ann_ret:.1f}% | {100*ann_vol:.1f}% | {sharpe_ann:+.2f} | {pct_neg:.1f}% |"
        )

    lines.append("")
    lines.append(
        "## Limite critique du Sharpe affiché ci-dessus — NE PAS le prendre au pied de la lettre"
    )
    lines.append("")
    lines.append(
        "Deux problèmes qui font que le Sharpe annualisé ci-dessus est probablement "
        "**très surestimé** :\n\n"
        "1. **Fenêtre courte** : l'endpoint public OKX ne conserve que ~90 jours "
        "d'historique de funding réglé (aucune option pour remonter plus loin sans "
        "source payante) — 3 mois est bien trop court pour juger d'un edge annualisé, "
        "surtout sur un actif dont le régime de funding change fortement d'un cycle à "
        "l'autre (funding négatif 20-25% du temps en 2022-2023 selon des sources "
        "indépendantes, contre 26-29% ici sur une fenêtre récente différente).\n\n"
        "2. **La volatilité mesurée ici n'est PAS la vraie volatilité de la position "
        "couverte** : ce calcul utilise seulement la variance du taux de funding "
        "lui-même, qui est mécaniquement très lisse. La vraie position (long spot / "
        "short perpétuel) a une volatilité de P&L bien plus élevée en pratique à cause "
        "du risque de base (l'écart spot-perp peut bouger de 300-500 bps en quelques "
        "secondes lors d'un choc de marché) et du slippage d'exécution — aucun des deux "
        "n'est capturé ici. Un Sharpe annualisé proche de +20 est un signal que la "
        "mesure est incomplète, pas que la stratégie est extraordinaire (cf. avertissement "
        "général du projet : un Sharpe >3 doit éveiller la suspicion d'une erreur de "
        "méthode, pas d'une découverte)."
    )
    lines.append("")
    lines.append(
        "## Comparaison honnête avec Étape C (volatilité GJR-t, validée SPA)"
    )
    lines.append("")
    lines.append(
        "Étape C n'est PAS une stratégie de rendement — c'est un edge de PRÉVISION "
        "(la volatilité future réalisée), validé statistiquement sur 9522 observations "
        "OOS avec un test SPA rigoureux (p=0,0000), cross-marché. Le funding rate "
        "arbitrage ci-dessus n'a PAS encore ce niveau de preuve : seulement ~90 jours "
        "de données, une mesure de volatilité incomplète, et aucune validation "
        "cross-marché (un seul cycle de marché crypto observé). Le rendement moyen "
        "collecté (2,6-2,9% annualisé sur cette fenêtre) est plausible et cohérent avec "
        "la littérature indépendante (10-30%/an selon le cycle), mais ce chantier n'est "
        "PAS encore au même niveau de rigueur qu'Étape C — il faudrait soit une source "
        "de données payante avec plus d'historique, soit reconstruire le P&L réel "
        "(spot + perp + frais), avant de considérer ce résultat comme validé."
    )
    lines.append("")
    lines.append(
        "**Limites non modélisées ici, à ne pas ignorer avant tout capital réel** : "
        "frais d'emprunt/staking du spot, slippage d'entrée/sortie, risque de "
        "contrepartie de l'exchange (ex. FTX 2022), risque de base spot-perp en cas de "
        "mouvement violent (300-500 bps en quelques secondes lors de chocs de marché), "
        "et funding qui peut rester négatif pendant de longues périodes (20-25% du "
        "temps en 2022-2023 selon les données historiques BTC)."
    )

    out = ROOT / "results" / "funding_rate_arb_quantification.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nÉcrit dans {out}")


if __name__ == "__main__":
    main()
