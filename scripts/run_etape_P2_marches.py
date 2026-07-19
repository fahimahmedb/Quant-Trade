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

    w("**Correction d'audit — source forward-only** : un premier jet backtestait cette source sur")
    w("des prix 2017/2022 **rédigés en connaissant l'issue** (hindsight), ce qui gonflait")
    w("artificiellement les scores (cf. `results/AUDIT.md`). Ces prix ont été **supprimés**. Un prix")
    w("de marché ne peut être honnêtement backtesté que s'il a été **horodaté avant le scrutin** par")
    w("une source vérifiable. Faute d'archives fiables hors-ligne, la source marchés est désormais")
    w("**réservée à la prévision d'élections à venir** (2027) : sur tout l'historique 1965-2022 elle")
    w("se déclare indisponible. Seule reste une entrée `FR_pres_2027` **vide** (`p=null`), à remplir")
    w("par un vrai relevé daté (ou via `_fetch_live`) le moment venu.\n")

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

    w("### Démonstration de la transformation (grille HYPOTHÉTIQUE, pas des élections réelles)\n")
    w("Pour illustrer la mécanique sans aucune donnée rétrospective, on applique la calibration à")
    w("une grille de prix de marché fictifs :\n")
    w(f"| p marché brut | p débiaisé (k={FAVORITE_LONGSHOT_K}) | Part 2nd tour prévue (K={SHARE_SLOPE_K}) |")
    w("|---|---|---|")
    for p_raw in (0.55, 0.65, 0.75, 0.85, 0.95):
        p_deb = debias_favorite_longshot(p_raw)
        share = prob_to_share(p_deb)
        w(f"| {p_raw:.2f} | {p_deb:.2f} | {share:.3f} |")
    w("")
    w("Le débiaisage accentue l'écart à 0.5 (favori renforcé) ; la conversion en part reste amortie")
    w("(une quasi-certitude de marché ne devient pas un score plébiscitaire). Ces lignes sont de la")
    w("**pure arithmétique de démonstration**, sans lien avec un scrutin passé.\n")

    w("## 3. Backtest hors-échantillon (OOS)\n")
    w("**Protocole anti-data-snooping** (fenêtre expansive, identique aux autres sources) :\n")
    w("- Pour prédire l'élection T, `fit()` reçoit l'historique < T — mais c'est un **no-op** pour")
    w("  cette source (un prix de marché ne s'entraîne pas sur le passé électoral ; le facteur de")
    w("  débiaisage `k` et la pente `K` sont des priors fixes, choisis avant de lire les scores,")
    w("  pas ajustés élection par élection).")
    w("- **Aucune** élection historique n'a de prix de marché honnête (données rétrospectives")
    w("  supprimées) : toutes sont marquées **indisponibles** (`available=False`). Le backtest ne")
    w("  score donc **0 pli** — c'est voulu. Cette source n'apportera de valeur mesurable que sur")
    w("  un scrutin futur (2027), où un prix live est capté sans hindsight possible.\n")

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
    w("1. **Couverture historique nulle (n=0)** : après suppression des prix rétrospectifs, aucun")
    w("   pli n'est scoré. Le facteur de débiaisage `k` et la pente `K` restent des priors motivés")
    w("   par la littérature, **non validés** sur données réelles dans ce dépôt.")
    w("")
    w("2. **Validation reportée au futur** : la seule façon honnête de mesurer cette source est de")
    w("   capter un prix live **avant** un scrutin à venir (2027) et de comparer après coup. Tout")
    w("   prix historique reconstitué a posteriori serait du hindsight — précisément l'erreur")
    w("   corrigée ici (cf. `results/AUDIT.md`).")
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
