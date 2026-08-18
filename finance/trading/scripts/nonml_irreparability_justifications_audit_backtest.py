"""Les 4 autres justifications d'irreparabilite (#493).

Specification pre-enregistree dans
`PREREG_irreparability_justifications_audit.md`, committee AVANT toute mesure
-- examen a la main DECLARE compris.

Le #488 a montre qu'une justification d'irreparabilite du #485 etait fausse.
Les 4 autres n'avaient jamais ete relues. Ce cycle les relit.

Lecture du disque : aucun script execute, aucun effet de bord.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_irreparability_justifications_audit_result.md"
DEJA_488 = "nonml_pnl_duplicate_sweep_audit.py"

QUATRE = [
    ("nonml_protocol_inventory_audit.py",
     "colonne « Après inspection » = **lecture manuelle**"),
    ("nonml_marker_emitted_by_scripts_backtest.py",
     "classification **jamais effectuée** par le script"),
    ("nonml_pnl_persistence_exposed_pass_audit.py",
     "univers du balayage #415, **disparu**"),
    ("nonml_reproducibility_campaign_v3_lot2_audit.py",
     "projection contrefactuelle, **aucun univers**"),
]

# --- VERDICTS DE L'EXAMEN A LA MAIN -------------------------------------
# DECLARE dans le pre-enregistrement. Chacun adosse a une ligne de code.
V = {
 "nonml_protocol_inventory_audit.py": ("EXACTE",
  "Le script **n'énumère rien** — ni `glob`, ni `iterdir`, ni `read_text` — et "
  "n'importe aucun module du dépôt. Ses **4** seules interpolations sont "
  "`len(names)` et `total` dans une boucle de listage. **Les valeurs de la "
  "colonne « Après inspection » (1, 0, 6, 0, 0) ne sont dérivables de rien "
  "dans ce fichier.** L'assertion négative tient."),
 "nonml_marker_emitted_by_scripts_backtest.py": ("EXACTE",
  "`CIBLES` est une liste de **5 entrées codées en dur** (l.25), et le script "
  "ne lit que ces fichiers-là. Il **n'énumère jamais** `results/`. **Le #473 "
  "l'avait établi sur pièce** ; la relecture le confirme."),
 "nonml_pnl_persistence_exposed_pass_audit.py": ("EXACTE",
  "`TARGETS` est une liste de **10 entrées codées en dur** (l.31). Les seuls "
  "accès disque sont des tests d'existence **par cible** — "
  "`(RESULTS / f\"nonml_{n}_pnl.npz\").exists()` (l.123) — jamais un `glob`. "
  "**L'univers du balayage #415 n'est ni construit ni atteignable.**"),
 "nonml_reproducibility_campaign_v3_lot2_audit.py": ("FAUSSE_VERDICT_TOMBE",
  "**L'assertion est fausse, et le verdict tombe avec elle.** Le script "
  "définit `def bound(n)` **au niveau module** (l.29), lie `cum` dans `main()` "
  "(l.59), et publie **déjà** `{100*bound(cum):.1f} %` aux lignes **126, 145 "
  "et 176**. Le « **6,2 %** » écrit en dur l.159 est **exactement cette "
  "valeur**, et le « **~4,1 %** » est `100*bound(cum + 24)`. "
  "**Les deux sont dérivables d'une fonction que le script possède.**"),
}


def enumere(py):
    """Ce que le script parcourt, par lecture de motifs structurels."""
    src = py.read_text(encoding="utf-8")
    out = []
    for motif, lab in ((r"\.glob\(", "`glob`"),
                       (r"\.iterdir\(", "`iterdir`"),
                       (r"\.read_text\(", "`read_text`"),
                       (r"^import nonml_|^from nonml_", "import du dépôt")):
        if re.search(motif, src, re.M):
            out.append(lab)
    cst = re.findall(r"^([A-Z_]{3,})\s*=\s*\[", src, re.M)
    return out, cst


def interpolations(py):
    return len(re.findall(r"\.append\(f[\"']", py.read_text(encoding="utf-8")))


def fonctions(py):
    try:
        arbre = ast.parse(py.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    return [n.name for n in ast.walk(arbre) if isinstance(n, ast.FunctionDef)]


def main():
    L = ["# Les **4 autres justifications** d'irréparabilité (pré-enregistré)", ""]
    L.append("Le **#488** a repris **une** des cinq raisons d'irréparabilité du #485 et")
    L.append("l'a trouvée **fausse** — le verdict survivant. **Les 4 autres n'avaient")
    L.append("jamais été relues.**")
    L.append("")
    L.append(f"> `{DEJA_488[:-3]}`, tranché au #488, est **exclu** de ce cycle : il")
    L.append("> n'est pas rejugé.")
    L.append("")

    L.append("## Ce que chacun énumère — mécanique, avant toute lecture")
    L.append("")
    L.append("| Script | Énumère | Constantes en dur | Interpolations | Fonctions |")
    L.append("|---|---|---|---|---|")
    infos = {}
    for nom, _j in QUATRE:
        py = SCRIPTS / nom
        en, cst = enumere(py)
        it, fn = interpolations(py), fonctions(py)
        infos[nom] = (en, cst, it, fn)
        L.append(f"| `{nom}` | {', '.join(en) if en else '**rien**'} | "
                 f"{', '.join('`' + c + '`' for c in cst) if cst else '—'} | "
                 f"**{it}** | {len(fn)} |")
    L.append("")

    L.append("## Les verdicts, un par un")
    L.append("")
    L.append("**Écrits à la main après lecture, chacun adossé à une ligne de code.**")
    L.append("")
    tombes, fausses = [], []
    for nom, just in QUATRE:
        etat, motif = V.get(nom, ("NON EXAMINÉ", "—"))
        etiq = {"EXACTE": "**JUSTIFICATION EXACTE**",
                "FAUSSE_VERDICT_SURVIT": "**JUSTIFICATION FAUSSE, verdict survivant**",
                "FAUSSE_VERDICT_TOMBE": "**JUSTIFICATION FAUSSE, VERDICT À REVOIR**"
                }.get(etat, "**NON EXAMINÉ**")
        if etat.startswith("FAUSSE"):
            fausses.append(nom)
        if etat == "FAUSSE_VERDICT_TOMBE":
            tombes.append(nom)
        L.append(f"### `{nom}` — {etiq}")
        L.append("")
        L.append(f"Justification du #485, **verbatim** : « {just} »")
        L.append("")
        L.append(motif)
        L.append("")

    L.append("## Le compte")
    L.append("")
    L.append(f"- justifications **exactes** : **{len(QUATRE) - len(fausses)} / "
             f"{len(QUATRE)}**")
    L.append(f"- justifications **fausses** : **{len(fausses)}**")
    L.append(f"- **verdicts d'irréparabilité qui tombent** : **{len(tombes)}**")
    for n in tombes:
        L.append(f"  - `{n}`")
    L.append("")
    if tombes:
        L.append("### Le compte du #485 est corrigé")
        L.append("")
        L.append("| | #485 | Ici |")
        L.append("|---|---|---|")
        L.append(f"| irréparables | 5 | **{5 - len(tombes)}** |")
        L.append(f"| réparables | 12 | **{12 + len(tombes)}** |")
        L.append("")
        L.append("> **Ma prédiction 2 annonçait qu'aucun verdict ne tomberait. Elle est")
        L.append("> réfutée**, et c'est un verdict que **j'ai signé au #485**.")
        L.append("")
        L.append("**Le cas est aggravant, pas anodin** : le même rapport publie")
        L.append("`6,2 %` **comme valeur interpolée** aux lignes 126, 145 et 176, **et**")
        L.append("**comme littéral** à la ligne 159. **Deux sources pour un même chiffre")
        L.append("dans un même document** — exactement la famille de défauts que les")
        L.append("#479 à #488 ont passé dix cycles à dénombrer, et qui a échappé au")
        L.append("recensement parce que j'ai cru une phrase au lieu de lire le code.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(fausses) >= 1
    p2 = not tombes
    p3 = V.get("nonml_marker_emitted_by_scripts_backtest.py", ("",))[0] == "EXACTE"
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 1 justification fausse | ≥ 1 | {len(fausses)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| aucun verdict ne tombe | 0 | {len(tombes)} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| `marker_emitted_by_scripts` exacte | exacte | "
             f"{'exacte' if p3 else 'non'} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    if not p2:
        L.append("**La prédiction 2 est réfutée, et c'est le résultat qui compte.**")
        L.append("J'annonçais que les 4 tiendraient ; l'un tombe. **Le #485 avait donc")
        L.append("un irréparable de trop**, et il aurait suffi de lire son code plutôt")
        L.append("que de relire ma propre phrase.")
        L.append("")
        L.append("> **Deux cycles sur cinq justifications relues, deux justifications")
        L.append("> fausses** (#488 et celui-ci). **Le taux ne se généralise pas** — il")
        L.append("> ne reste plus rien à relire, les 5 le sont toutes.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c3 = all(V.get(n, ("NON EXAMINÉ",))[0] != "NON EXAMINÉ" for n, _j in QUATRE)
    L.append(f"1. Les **{len(QUATRE)}** nommés, ce qu'ils énumèrent publié — **OUI**.")
    L.append("2. Justifications citées verbatim — **OUI**.")
    L.append(f"3. **{len(QUATRE)}/{len(QUATRE)}** examinés, chacun adossé à une ligne "
             f"de code — **{'OUI' if c3 else 'NON'}**.")
    L.append(f"4. Verdict renversé publié et compte du #485 corrigé — "
             + ("**OUI**" if tombes else "**sans objet**") + ".")
    L.append(f"5. `{DEJA_488[:-3]}` exclu explicitement — **OUI**.")
    L.append("")
    L.append(f"**{'PASS' if c3 else 'FAIL'}** — le critère porte sur le **procédé** :")
    L.append("un cycle qui fait tomber un de ses propres verdicts et le publie réussit.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre de stratégie. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"exactes={len(QUATRE)-len(fausses)} fausses={len(fausses)} "
          f"tombes={len(tombes)} -> irreparables 5 -> {5-len(tombes)}")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
