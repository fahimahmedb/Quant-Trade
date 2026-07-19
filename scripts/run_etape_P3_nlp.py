"""Étape P3 — Source NLP / sentiment (proxy comportemental).

Génère results/etape_P3_nlp.md :
  1. Nature du proxy (comportemental vs déclaratif) et limites de principe
  2. Features utilisées et mapping vers la part 2nd tour
  3. Backtest OOS (évaluation hors-échantillon, fenêtre expansive)
  4. Limitations honnêtes
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pp_data import load_registry  # noqa: E402
from pp_nlp import NlpSource, NLP_DATA_START_YEAR  # noqa: E402
from pp_backtest import run_oos, markdown_table  # noqa: E402


def main():
    """Génère le rapport complet."""

    examples = load_registry()

    lines = []
    w = lines.append

    w("# Étape P3 — Source NLP / sentiment (proxy comportemental)\n")

    w("## 1. Nature du proxy : comportemental, pas déclaratif\n")
    w("Contrairement à un sondage (déclaratif : « pour qui comptez-vous voter ? »), cette")
    w("source mesure des traces **comportementales** et une **tonalité agrégée** :\n")
    w("")
    w("- **Volume de recherche Google Trends** : révèle un *intérêt* ou une *inquiétude* pour")
    w("  un candidat, pas une intention de vote. Un pic de recherche peut venir d'un scandale")
    w("  (intérêt négatif) autant que d'un engouement (intérêt positif).")
    w("- **Tonalité de mentions** (presse + réseaux) : sentiment moyen agrégé sur la période,")
    w("  lui-même dépendant de la ligne éditoriale et de la composition du corpus -- pas une")
    w("  mesure calibrée d'opinion publique.")
    w("")
    w("Ce double proxy est donc **structurellement plus bruyant et plus manipulable** qu'un")
    w("sondage : volume gonflable par du buzz négatif coordonné, tonalité sensible au choix des")
    w("sources. Il est traité comme tel dans le mapping (voir §2) et dans l'incertitude renvoyée")
    w("(`r2_share_sd` volontairement large).\n")

    w(f"**Couverture temporelle** : Google Trends n'existe (au sens exploitable) que depuis")
    w(f"~{NLP_DATA_START_YEAR}. Les présidentielles antérieures (1965 → 2002) sont donc")
    w("**structurellement indisponibles** pour cette source -> `SourceSignal(available=False)`,")
    w("traitées comme un pli non scorable par le backtest OOS (attendu, pas une anomalie).\n")

    w("## 2. Features et mapping vers la part 2nd tour\n")
    w("Snapshot `data/fr_nlp_snapshot.csv` (valeurs illustratives, voir en-tête du fichier) :\n")
    w("")
    w("| Colonne | Sens |")
    w("|---|---|")
    w("| `ref_trends_share` / `opp_trends_share` | Part du volume Google Trends entre référence et principal adversaire (somme = 1) |")
    w("| `ref_mention_volume` | Indice de volume de mentions du candidat de référence (base 100) |")
    w("| `ref_tonality` / `opp_tonality` | Tonalité moyenne des mentions, dans [-1, 1] |")
    w("")
    w("**Mapping** (monotone, pas de boîte noire) :\n")
    w("")
    w("```")
    w("raw   = w1 * (ref_trends_share - opp_trends_share)")
    w("      + w2 * (ref_tonality      - opp_tonality)")
    w("share = clamp( 0.5 + 0.5 * tanh(scale * raw) )")
    w("```")
    w("")
    w(f"avec `w1 = {NlpSource.W1_TRENDS}` (différentiel de notoriété), "
      f"`w2 = {NlpSource.W2_TONALITY}` (différentiel de tonalité) fixés a priori -- non ré-estimés,")
    w("n trop petit pour régresser deux poids sans surapprendre. Seul `scale` peut être recalibré")
    w("par `fit()` (régression 1D sans intercept, bornée), à partir de l'historique strictement")
    w("antérieur. `r2_share_sd` reste dans "
      f"[{NlpSource.SD_MIN}, {NlpSource.SD_MAX}] -- large par construction : dans la fusion")
    w("bayésienne (pondération 1/variance), cette source pèse volontairement peu face aux")
    w("fondamentaux ou aux marchés.\n")

    w("### Chargeur hybride\n")
    w("`load_nlp_features(election_id)` tente d'abord une collecte **live** (`_fetch_live`,")
    w("Google Trends via `pytrends`), protégée par `try/except` et un timeout court ; dans cet")
    w("environnement `pytrends` n'est pas une dépendance du projet, l'import échoue donc")
    w("immédiatement et **aucune requête réseau n'est jamais émise** -- repli systématique et")
    w("instantané sur le snapshot offline `data/fr_nlp_snapshot.csv`.\n")

    w("## 3. Backtest hors-échantillon (OOS)\n")
    w("**Protocole anti-data-snooping** (fenêtre expansive, identique aux autres sources) :\n")
    w("- Pour prédire l'élection T, `NlpSource` est entraînée UNIQUEMENT sur les élections")
    w("  d'année < T (recalibration de `scale` seulement, voir §2)")
    w("- Les élections 1965 → 2002 n'ont pas de donnée NLP : plis marqués « indisponible »,")
    w("  seules 2007 → 2022 sont effectivement scorées (n=4 au maximum)\n")

    report = run_oos(
        make_source=lambda: NlpSource(),
        examples=examples,
        min_train=4,
        source_name="nlp",
    )

    w(markdown_table(report))
    w("")

    n_available = sum(1 for f in report.folds if f.available)
    n_total = len(report.folds)
    w(f"*{n_available}/{n_total} plis disponibles (les autres sont antérieurs à "
      f"~{NLP_DATA_START_YEAR}, indisponibilité attendue, pas un échec).*\n")

    w("## 4. Limitations honnêtes\n")
    w("⚠️ Cet exercice est à vocation **méthodologique**. Avant toute application réelle :\n")
    w("")
    w("1. **Snapshot illustratif** : les valeurs de `data/fr_nlp_snapshot.csv` sont construites")
    w("   à dire d'expert (ordre de grandeur plausible), PAS extraites d'un export réel Google")
    w("   Trends ni d'un moteur de sentiment calibré. À remplacer avant toute publication.")
    w("")
    w("2. **Échantillon minuscule** : au mieux 4 élections avec donnée NLP (2007-2022), dont 2")
    w("   seulement disponibles pour la calibration du dernier pli testé. Aucune conclusion")
    w("   statistique robuste ne peut être tirée d'un backtest à si peu de points ; les")
    w("   métriques OOS ci-dessus sont indicatives, pas une preuve de valeur ajoutée.")
    w("")
    w("3. **Proxy bruité et manipulable** : volume de recherche et tonalité agrégée peuvent être")
    w("   gonflés ou orientés par des campagnes coordonnées (bots, brigading), un scandale")
    w("   médiatique sans lien avec l'issue du vote, ou un biais de couverture éditoriale. Le")
    w("   signal n'a de sens qu'agrégé avec d'autres sources, jamais utilisé seul.")
    w("")
    w("4. **Mapping simple par construction** : poids `w1`/`w2` fixés a priori, pas appris --")
    w("   choix délibéré anti-surapprentissage vu la taille de l'échantillon, mais qui laisse de")
    w("   côté d'éventuelles non-linéarités (ex. effet de seuil au-delà d'un certain volume).")
    w("")
    w("5. **Causalité non établie** : notoriété/tonalité et vote peuvent être co-déterminés par")
    w("   un troisième facteur (actualité, contexte macro) sans lien causal direct entre les")
    w("   deux -- cette source capture une corrélation contemporaine, pas un mécanisme causal.")
    w("")
    w("**Conclusion** : ce module est un **composant bruité d'un ensemble** (fusion avec")
    w("fondamentaux, marchés). Sa valeur attendue est de capter des signaux de dernière minute")
    w("(dynamique de campagne) que les fondamentaux structurels ne voient pas -- pas de remplacer")
    w("un sondage, et certainement pas de faire une prévision autonome.\n")

    out = ROOT / "results" / "etape_P3_nlp.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))

    print("\n".join(lines))
    print(f"\n✓ Rapport écrit : {out}")


if __name__ == "__main__":
    main()
