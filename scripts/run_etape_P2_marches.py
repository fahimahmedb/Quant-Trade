"""Étape P2 — Marchés de prédiction.

Génère results/etape_P2_marches.md :
  1. Description de la source (loader hybride live -> snapshot offline)
  2. Calibration du biais favori-outsider (avant/après sur les prix connus)
  3. Backtest OOS (évaluation hors-échantillon)
  4. Limitations et mises en garde
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pp_data import load_registry, registry_quality_report  # noqa: E402
from pp_markets import (  # noqa: E402
    FAVORITE_LONGSHOT_K,
    LIVE_TIMEOUT_S,
    SHARE_SLOPE_K,
    MARKET_SD,
    MarketsSource,
    debias_favorite_longshot,
    load_market_prob,
    prob_to_share,
)
from pp_backtest import run_oos, markdown_table  # noqa: E402


def main():
    """Génère le rapport complet."""

    examples = load_registry()
    qr = registry_quality_report(examples)

    lines = []
    w = lines.append

    w("# Étape P2 — Marchés de prédiction\n")

    w("## 1. Description de la source\n")
    w("Les **marchés de prédiction** (Polymarket, PredictIt, Betfair Exchange...) publient un")
    w("prix qui s'interprète comme une probabilité implicite de victoire : des agents engagent")
    w("de l'argent réel (ou virtuel liquide) sur l'issue du 2nd tour, ce qui agrège en principe")
    w("l'information disponible plus vite et plus largement qu'un sondage ponctuel.\n")

    w("**Loader hybride** (`pp_markets.load_market_prob`) :\n")
    w("1. Tentative **live** (`_fetch_live`, timeout court de "
      f"{LIVE_TIMEOUT_S:.0f} s) — non câblée vers un endpoint précis dans")
    w("   ce dépôt (les URLs des marchés électoraux changent au fil des campagnes) ; lève")
    w("   `NotImplementedError` par construction, capturée silencieusement.")
    w("2. **Fallback** systématique sur `data/fr_markets_snapshot.json` (instantané offline).")
    w("3. Si l'élection n'a ni prix live ni entrée snapshot → aucune tentative de deviner :")
    w("   `SourceSignal(available=False)`.\n")

    w("**Couverture réelle** : les marchés de prédiction grand public sur la présidentielle")
    w("française n'existent avec un volume significatif que depuis 2017 (essor Polymarket /")
    w("PredictIt / Betfair sur les élections). Le snapshot ne couvre donc que **FR_pres_2017** et")
    w("**FR_pres_2022**, plus une entrée d'exemple `FR_pres_2027` illustrant l'usage live pour une")
    w("élection à venir. Les prix du snapshot sont **approximatifs/illustratifs** (ordre de")
    w("grandeur des cotes de fin de campagne d'entre-deux-tours), pas un relevé tick-by-tick")
    w("audité — voir `_meta.avertissement` dans le fichier.\n")

    w("## 2. Calibration du biais favori-outsider (favorite-longshot bias)\n")
    w("La littérature empirique sur les marchés de paris et de prédiction (Wolfers & Zitzewitz")
    w("2004 ; Snowberg & Wolfers 2010) documente un biais systématique : les prix **sous-estiment**")
    w("les favoris et **sur-estiment** les outsiders (prime payée pour le gain \"loterie\" improbable")
    w("de l'outsider). Le marché compresse donc les probabilités vers 0.5 par rapport à la vérité.\n")

    w("**Correction retenue** — extrémisation en espace logit, prior FIXE (jamais ajusté sur le")
    w("jeu de test, donc sans fuite d'information) :\n")
    w("```")
    w("p_debiaisee = sigmoid(k * logit(p_marche)),   k = FAVORITE_LONGSHOT_K > 1")
    w("```")
    w(f"avec **k = {FAVORITE_LONGSHOT_K}** : k > 1 repousse la probabilité plus loin de 0.5 (favori")
    w("poussé vers 1, outsider poussé vers 0), ce qui compense la compression du marché vers le")
    w("centre.\n")

    w("Conversion en part de vote 2nd tour, mapping monotone amorti (une quasi-certitude de")
    w("marché ne se traduit pas en score plébiscitaire improbable) :\n")
    w("```")
    w("r2_share_mean = clamp_share(0.5 + K * (p_debiaisee - 0.5)),   K = SHARE_SLOPE_K")
    w("```")
    w(f"avec **K = {SHARE_SLOPE_K}**, et un écart-type fixe **sd = {MARKET_SD}** (marché jugé plutôt")
    w("fiable, moins incertain que le prior \"sans information\" à 0.08 des fondamentaux).\n")

    w("### Avant / après sur les deux élections où un prix de marché est connu\n")
    w("| Élection | Référence | p marché brut | p débiaisé (k="
      f"{FAVORITE_LONGSHOT_K}) | Part prévue | Part réelle |")
    w("|---|---|---|---|---|---|")
    for eid in ("FR_pres_2017", "FR_pres_2022"):
        data = load_market_prob(eid)
        ctx_match = next(ex for ex in examples if ex.context.election_id == eid)
        p_raw = data["p_reference_wins"]
        p_deb = debias_favorite_longshot(p_raw)
        share = prob_to_share(p_deb)
        actual = ctx_match.result.r2_reference_share(ctx_match.context.reference_id)
        w(f"| {eid} | {ctx_match.context.reference_id} | {p_raw:.2f} | {p_deb:.2f} | "
          f"{share:.3f} | {actual:.3f} |")
    w("")
    w("Le débiaisage accentue l'écart à 0.5 : par exemple un prix brut de 0.87 devient ≈"
      f" {debias_favorite_longshot(0.87):.2f} avant conversion en part de vote.\n")

    w("## 3. Backtest hors-échantillon (OOS)\n")
    w("**Protocole anti-data-snooping** (fenêtre expansive, identique aux autres sources) :\n")
    w("- Pour prédire l'élection T, `fit()` reçoit l'historique < T — mais c'est un **no-op** pour")
    w("  cette source (un prix de marché ne s'entraîne pas sur le passé électoral ; le facteur de")
    w("  débiaisage `k` et la pente `K` sont des priors fixes, choisis avant de lire les scores,")
    w("  pas ajustés élection par élection).")
    w("- Seules **FR_pres_2017** et **FR_pres_2022** ont un prix de marché disponible : toutes les")
    w("  élections antérieures sont marquées **indisponibles** par construction (pas de marché")
    w("  électoral liquide avant l'essor de ces plateformes). C'est le comportement attendu du")
    w("  contrat (`SourceSignal(available=False)`), pas un défaut du modèle — le tableau ci-dessous")
    w("  l'illustre par la colonne « (source indispo.) ».\n")

    report = run_oos(
        make_source=lambda: MarketsSource(),
        examples=examples,
        min_train=4,
        source_name="markets",
    )

    w(markdown_table(report))
    w("")

    w("## 4. Limitations honnêtes\n")
    w("⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :\n")
    w("")
    w("1. **Couverture minimale (n=2)** : le backtest OOS ne score que 2017 et 2022 — bien trop peu")
    w("   pour valider statistiquement le facteur de débiaisage `k` ou la pente `K`. Ils restent des")
    w("   priors motivés par la littérature, pas des paramètres estimés sur ce dépôt.")
    w("")
    w("2. **Snapshot illustratif** : les prix de `data/fr_markets_snapshot.json` reconstituent un")
    w("   ordre de grandeur plausible de fin de campagne, pas un relevé horodaté et audité d'un")
    w("   flux réel. À remplacer par des données primaires (archives Polymarket/PredictIt/Betfair)")
    w("   avant toute publication.")
    w("")
    w("3. **Live non câblé** : `_fetch_live` est un point d'extension qui lève systématiquement")
    w("   `NotImplementedError` — le fallback snapshot est donc la voie d'exécution normale de ce")
    w("   dépôt, pas un filet de sécurité occasionnel.")
    w("")
    w("4. **Biais favori-outsider potentiellement variable dans le temps/plateforme** : le facteur")
    w("   `k` unique appliqué ici ne distingue pas Polymarket de PredictIt, ni les régimes de forte")
    w("   vs faible liquidité, alors que l'intensité du biais en dépend empiriquement.")
    w("")
    w("**Conclusion** : ce modèle est un **composant d'un ensemble** (fusion avec fondamentaux,")
    w("NLP). Sa faible couverture historique en fait un signal complémentaire tardif (utile")
    w("surtout à partir de 2017), pas un substitut aux autres sources.\n")

    out = ROOT / "results" / "etape_P2_marches.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))

    print("\n".join(lines))
    print(f"\n✓ Rapport écrit : {out}")


if __name__ == "__main__":
    main()
