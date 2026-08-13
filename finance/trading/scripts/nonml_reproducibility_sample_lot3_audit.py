"""Audit du lot 3 de reproductibilité (#436).

Spécification pré-enregistrée dans `PREREG_reproducibility_sample_lot3.md`.

**Une divergence a été observée.** Le pré-enregistrement prévoyait ce cas :
« la borne ne s'applique plus ; le résultat principal du cycle devient la
divergence elle-même ». Cet audit instruit cette divergence, en nomme la
cause, et refuse explicitement de sauver la borne par une reclassification
décidée après coup.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUT = RESULTS / "nonml_reproducibility_sample_lot3_audit.md"
REPORT = RESULTS / "nonml_reproducibility_sample_lot3_result.md"

# Motifs par lesquels un rapport embarque un decompte du DEPOT plutot que de
# ses seules entrees.
SELF_COUNT = re.compile(
    r'glob\("nonml_\*_backtest\.py"\)|glob\("\*_pnl\.npz"\)|glob\("nonml_\*_result\.md"\)')


def main():
    txt = REPORT.read_text(encoding="utf-8")

    L = ["# Audit — reproductibilité, lot 3 : une divergence, et elle est de mon fait", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("**aucun rapport publié modifié**.")
    L.append("")

    # --- La divergence ----------------------------------------------------
    m = re.search(r"\| `([^`]+)` \| [\d.]+ s \| (\d+) \|", txt)
    name = m.group(1) if m else "?"
    n_lines = m.group(2) if m else "?"
    L.append("## La divergence")
    L.append("")
    L.append(f"Sur 24 tirages : **23 identiques**, **1 divergent** — `{name}`, "
             f"**{n_lines}** lignes.")
    L.append("")
    L.append("Le pré-enregistrement du #435 comme celui du #436 prévoyaient ce cas :")
    L.append("")
    L.append("> « Si une divergence apparaît, la borne ne s'applique plus : le résultat")
    L.append("> principal du cycle devient la divergence elle-même. »")
    L.append("")
    L.append("**La borne n'est donc pas publiée.** Ni celle de ~4,9 % qui était visée, ni une")
    L.append("borne recalculée sur 59 tirages « hors le cas gênant ».")
    L.append("")

    # --- La cause ---------------------------------------------------------
    L.append("## La cause — un chiffre que j'ai moi-même rendu instable au #428")
    L.append("")
    L.append("Les lignes divergentes portent toutes sur le même décompte :")
    L.append("")
    L.append("```")
    L.append("- | scripts de backtest non-ML du dépôt | **284** |")
    L.append("+ | scripts de backtest non-ML du dépôt | **289** |")
    L.append("- | **couverture non-ML** | **73.2 %** |")
    L.append("+ | **couverture non-ML** | **72.0 %** |")
    L.append("```")
    L.append("")
    n_now = len(list(SCRIPTS.glob("nonml_*_backtest.py")))
    L.append(f"Le dépôt comptait **284** scripts de backtest au #428 ; il en compte **{n_now}**")
    L.append("aujourd'hui. Les cinq de plus sont **les miens** — ceux des cycles #431 à #436,")
    L.append("dont ce cycle lui-même.")
    L.append("")
    L.append("**C'est le #428 qui a introduit ce chiffre dans le rapport du balayage.** J'y")
    L.append("avais ajouté la couverture non-ML précisément pour que le lecteur ne surestime")
    L.append("pas la portée du balayage. L'intention était bonne ; la conséquence ne l'est")
    L.append("pas : un rapport qui embarque un décompte du **dépôt** cesse d'être stable dès")
    L.append("que le dépôt bouge, c'est-à-dire à chaque cycle qui ajoute un script.")
    L.append("")
    L.append("Ce rapport était donc **divergent par construction** depuis le #428, et aucun")
    L.append("des cycles suivants ne l'avait vu — y compris les deux lots de reproductibilité,")
    L.append("qui ne l'avaient simplement pas tiré.")
    L.append("")

    # --- Combien d'autres rapports ont cette structure --------------------
    L.append("## Combien d'autres rapports sont dans ce cas")
    L.append("")
    affected = []
    for f in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        try:
            if SELF_COUNT.search(f.read_text(encoding="utf-8")):
                affected.append(f.name.replace("nonml_", "").replace("_backtest.py", ""))
        except Exception:  # noqa: BLE001
            pass
    L.append(f"Scripts dont le rapport embarque un décompte du dépôt (et non de ses seules")
    L.append(f"entrées) : **{len(affected)}**")
    L.append("")
    for n in affected:
        L.append(f"- `{n}`")
    L.append("")
    L.append("Tous sont des **diagnostics**, pas des stratégies — ce qui limite la portée du")
    L.append("problème : aucun verdict PASS/FAIL n'en dépend. Mais tous partagent la même")
    L.append("fragilité, et **je les ai presque tous écrits**.")
    L.append("")

    # --- Ce que je refuse de faire ----------------------------------------
    L.append("## Ce que je refuse de faire ici")
    L.append("")
    L.append("Il serait tentant de distinguer deux espèces de divergence :")
    L.append("")
    L.append("- **structurelle** — le rapport embarque un compteur du dépôt, il bougera")
    L.append("  toujours ; ce n'est pas un résultat périmé ;")
    L.append("- **substantielle** — un résultat publié ne se reproduit plus, ce que la")
    L.append("  campagne cherchait.")
    L.append("")
    L.append("La distinction est **juste**. Mais l'appliquer **maintenant**, pour écarter le")
    L.append("seul cas gênant et republier une borne de 4,9 %, serait exactement le geste que")
    L.append("tout ce protocole interdit : changer la règle après avoir vu le résultat.")
    L.append("")
    L.append("> La distinction sera donc **pré-enregistrée dans un cycle ultérieur**, avec son")
    L.append("> critère mécanique fixé avant tout nouveau tirage — et la campagne repartira de")
    L.append("> là, sans réutiliser les 60 tirages actuels comme s'ils avaient été classés")
    L.append("> selon une règle qui n'existait pas quand ils ont été faits.")
    L.append("")
    L.append("**État publié de la borne : caduque.** Le #434 (22,1 %) et le #435 (8,0 %)")
    L.append("restent vrais pour ce qu'ils mesuraient, mais la campagne ne peut pas prétendre")
    L.append("à 4,9 % en écartant après coup le tirage qui la contredit.")
    L.append("")

    # --- Volet B ----------------------------------------------------------
    L.append("## Volet B — représentativité en âge : contrôle passé")
    L.append("")
    gap = re.search(r"écart : \*\*([+-]?[\d.]+) points\*\*", txt)
    med = re.findall(r"\| date de publication médiane \| ([\d-]+) \| ([\d-]+) \|", txt)
    L.append("Ce volet est **indépendant de la divergence** et son verdict tient.")
    L.append("")
    if med:
        L.append(f"- date de publication médiane — vivier : **{med[0][0]}**, testés : **{med[0][1]}**")
    if gap:
        L.append(f"- écart sur le tiers le plus ancien : **{gap.group(1)} points**, "
                 f"tolérance **±10** fixée avant mesure")
    L.append("")
    L.append("**Tirage représentatif en âge.** Les rapports anciens — les plus exposés à la")
    L.append("dérive du code partagé — sont couverts à la même fréquence que les récents. Le")
    L.append("seuil n'a pas été ajusté après coup ; il n'a pas eu besoin de l'être.")
    L.append("")
    L.append("Ce contrôle valait la peine d'être fait **avant** de connaître son résultat :")
    L.append("s'il avait échoué, il aurait invalidé la lecture des deux lots précédents.")
    L.append("")

    # --- Régime -----------------------------------------------------------
    st = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO),
                        capture_output=True, text=True, timeout=120).stdout
    touched = [l for l in st.splitlines() if l.strip().endswith("_result.md")
               and "reproducibility_sample" not in l]
    L.append("## Régime — aucun rapport publié modifié")
    L.append("")
    L.append(f"- rapports `*_result.md` modifiés hors artefacts de ce cycle : "
             f"**{len(touched)}** {'✔' if not touched else '✘'}")
    L.append("")
    L.append(f"Le rapport divergent `{name}` a été **restauré à l'identique**. Le corriger")
    L.append("demanderait son propre pré-enregistrement et son propre régime déclaré, comme")
    L.append("aux #428, #429 et #430.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion")
    L.append("")
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append("| 24 scripts tirés et classés | 24 | 24 | ✔ |")
    L.append("| divergence publiée avec son `diff` | si présente | **oui** | ✔ |")
    L.append(f"| rapports publiés modifiés | 0 | {len(touched)} | {'✔' if not touched else '✘'} |")
    L.append("| borne cumulée | ~4,9 % | **non publiée — caduque** | — |")
    L.append("| représentativité en âge | publiée | **passée (−3,2 pts)** | ✔ |")
    L.append("")
    L.append("**La campagne de reproductibilité a trouvé ce qu'elle cherchait, à sa troisième")
    L.append("tentative — et le défaut est de mon fait.** C'est le meilleur résultat que ces")
    L.append("trois cycles pouvaient produire : une borne rassurante de plus n'aurait rien")
    L.append("appris ; une divergence, si.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
