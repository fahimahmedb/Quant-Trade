"""Etape P4 - fusion bayesienne multi-source. Produit results/etape_P4_fusion.md.

PROTOCOLE FIGE AVANT EXECUTION (anti data-snooping) :
- 4 predicteurs declares : 3 sources seules (fondamentaux, marches, NLP) + leur
  fusion. Aucun ajout a posteriori.
- Fenetre EXPANSIVE, entrainement sur passe strict (cf. src/pp_backtest.py).
- Fiabilites a priori EGALES (1.0) entre sources : la ponderation vient de la
  precision (1/sd^2) declaree par chaque source, PAS d'un poids ajuste sur le
  test (ce qui serait du snooping). La calibration des sd est fixee en amont.
- Metriques : Brier / log-loss / MAE part / taux de bonne issue, OOS.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pp_data import load_registry  # noqa: E402
from pp_backtest import run_oos, markdown_table  # noqa: E402
from pp_fundamentals import FundamentalsSource  # noqa: E402
from pp_markets import MarketsSource  # noqa: E402
from pp_nlp import NlpSource  # noqa: E402
from pp_fusion import FusionSource  # noqa: E402

MIN_TRAIN = 4
examples = load_registry()


def make_fusion() -> FusionSource:
    """Fabrique une fusion neuve avec des sous-sources neuves (aucune fuite)."""
    return FusionSource([FundamentalsSource(), MarketsSource(), NlpSource()])


# --- Backtests OOS : chaque source seule, puis la fusion --------------------- #
runs = {
    "Fondamentaux": run_oos(lambda: FundamentalsSource(), examples, MIN_TRAIN),
    "Marchés": run_oos(lambda: MarketsSource(), examples, MIN_TRAIN),
    "NLP": run_oos(lambda: NlpSource(), examples, MIN_TRAIN),
    "Fusion": run_oos(make_fusion, examples, MIN_TRAIN),
}

# --- Detail par election de la fusion (avec contributions des sources) ------- #
detail = []
for i in range(MIN_TRAIN, len(examples)):
    train, test = examples[:i], examples[i]
    ctx, res = test.context, test.result
    post = make_fusion().fit(train).posterior(ctx)
    actual = res.r2_reference_share(ctx.reference_id)
    won = int(res.winner_id == ctx.reference_id)
    detail.append((ctx, post, actual, won))

# --------------------------------------------------------------------------- #
# Rapport                                                                       #
# --------------------------------------------------------------------------- #
lines = []
w = lines.append
w("# Étape P4 — Fusion bayésienne multi-source (présidentielle FR, deux tours)\n")

w("## 1. Principe\n")
w("On prédit un résultat électoral **sans sondage déclaratif**, en fusionnant "
  "trois familles de sources hétérogènes :\n")
w("- **Fondamentaux** (P1) : régression structurelle économie-politique "
  "(croissance, chômage, approbation, ancienneté) — le *prior*.")
w("- **Marchés de prédiction** (P2) : prix implicites dé-biaisés (favori-outsider).")
w("- **NLP / sentiment** (P3) : proxy comportemental (notoriété, tonalité).\n")
w("La fusion combine leurs estimations gaussiennes de la part 2nd tour par "
  "**pondération de précision en espace logit** (1/σ²), avec un prior diffus et "
  "un plancher d'incertitude anti-sur-confiance (on ne peut être plus certain "
  "que sa meilleure source unique). Voir `src/pp_fusion.py`.\n")

w("## 2. Comparaison OOS — sources seules vs fusion\n")
w("*Fenêtre expansive, entraînement sur le passé strict. Marchés (2017/2022) et "
  "NLP (2007+) ne sont scorés que là où ils existent ; la fusion, elle, exploite "
  "ce qui est disponible à chaque date.*\n")
w("| Prédicteur | n | Brier | Log-loss | MAE part | Bonne issue |")
w("|---|---|---|---|---|---|")
for name, rep in runs.items():
    m = rep.metrics()
    if m.get("n"):
        w(f"| {name} | {m['n']} | {m['brier']:.3f} | {m['log_loss']:.3f} "
          f"| {m['share_mae']:.3f} | {m['hit_rate']:.0%} |")
    else:
        w(f"| {name} | 0 | — | — | — | — |")
w("\n*Brier : 0 = parfait, 0.25 = pile ou face. Comparer à effectif égal : la "
  "fusion et les fondamentaux couvrent les 7 plis ; marchés/NLP moins.*\n")

w("## 3. Détail de la fusion, élection par élection\n")
w("| Année | Référence | Part prévue | P(victoire) | Part réelle | Issue | Poids dominant |")
w("|---|---|---|---|---|---|---|")
for ctx, post, actual, won in detail:
    contribs = {k: v for k, v in post.contributions.items() if k != "prior"}
    dom = max(contribs, key=contribs.get) if contribs else "prior"
    dom_w = post.contributions.get(dom, 0.0)
    issue = "✓ gagne" if won else "✗ perd"
    ok = "✓" if (post.p_reference_wins > 0.5) == bool(won) else "✗"
    w(f"| {ctx.year} | {ctx.reference_id} | {post.r2_share_mean:.3f} "
      f"| {post.p_reference_wins:.2f} | {actual:.3f} | {issue} {ok} "
      f"| {dom} {dom_w:.0%} |")
w("")

w("## 4. Lecture des contributions\n")
for ctx, post, actual, won in detail:
    parts = ", ".join(f"{k} {v:.0%}" for k, v in sorted(
        post.contributions.items(), key=lambda kv: -kv[1]))
    w(f"- **{ctx.year}** : {parts}")
w("")

w("## 5. Audit de provenance des données (lecture critique OBLIGATOIRE)\n")
w("⚠️ **Les scores de cette page surestiment la compétence prédictive réelle.** "
  "Les instantanés marchés (`fr_markets_snapshot.json`) et NLP "
  "(`fr_nlp_snapshot.csv`) ont été rédigés en CONNAISSANT l'issue des élections "
  "(hindsight). Le backtest expansif n'entraîne jamais sur le futur, mais il ne "
  "peut pas laver une donnée qui encode déjà le résultat dans sa valeur.\n")
w("- Marchés (Brier 0.000) et NLP (0.063) mesurent un **ajustement rétrospectif**, "
  "pas une prévision. Les deux calls confiants (2017/2022) sont exactement ceux "
  "où les marchés — donnée rétrospective — dominent la pondération.")
w("- La **seule source exogène** (macro/popularité indépendantes du scrutin) est "
  "les **fondamentaux** : Brier **0.368**, bonne issue **57 %** — non "
  "distinguable du hasard à n=7. C'est le seul chiffre de compétence défendable.")
w("- La thèse (fusion multi-source > source seule) reste plausible avec de VRAIES "
  "données de marché ; ces métriques-ci ne la démontrent simplement pas. "
  "Voir `results/AUDIT.md`.\n")

w("## 6. Limites (honnêteté méthodologique)\n")
w("- **Échantillon minuscule** : 11 présidentielles, 7 plis OOS. Aucun chiffre "
  "n'est significatif au sens statistique ; ce sont des ordres de grandeur.")
w("- **Données approximatives** : macro agrégées, prix de marché et features NLP "
  "illustratifs (2017/2022 pour les marchés, 2007+ pour le NLP). À remplacer par "
  "des séries primaires sourcées avant tout usage réel.")
w("- **2017 = réalignement** : les fondamentaux ratent Macron ; seule la "
  "disponibilité d'autres sources (le cas échéant) corrige le prior.")
w("- **Indépendance supposée** : la fusion suppose des sources non corrélées ; "
  "le plancher d'incertitude en tient compte grossièrement, pas exactement.")
w("- **Anti-snooping** : univers de prédicteurs et calibrations figés AVANT "
  "lecture des scores ; fiabilités a priori égales, non ajustées sur le test.\n")

out = ROOT / "results" / "etape_P4_fusion.md"
out.write_text("\n".join(lines))
print("\n".join(lines))
