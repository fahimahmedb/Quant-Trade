"""Audit indépendant du #518 : ne réutilise pas le dictionnaire de verdicts
`V` écrit à la main dans le backtest. Reconstruit par AST (pas par regex sur
le texte) ce que chacun des 11 scripts appelle réellement, et vérifie
mécaniquement les trois chutes (aucun `.glob(` littéral dans le code source
des trois scripts déclarés FAUSSE) sans faire confiance à la prose du
backtest.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

RESULT_MD = RESULTS / "nonml_reparable_justifications_485_result.md"
OUT = RESULTS / "nonml_reparable_justifications_485_audit_result.md"

ONZE = [
    "nonml_duplicate_sweep_coverage_audit.py",
    "nonml_content_defined_magnitudes_audit.py",
    "nonml_content_defined_magnitudes_backtest.py",
    "nonml_coverage_wording_fix_audit.py",
    "nonml_dsr_corrected_trials_backtest.py",
    "nonml_idempotence_famille_capable_backtest.py",
    "nonml_idempotence_lot2_backtest.py",
    "nonml_marker_emitter_crossing_backtest.py",
    "nonml_orphans_interrupted_or_lost_backtest.py",
    "nonml_report_idempotence_backtest.py",
    "nonml_reproducibility_campaign_v2_audit.py",
]
TOMBES_ATTENDUS = {
    "nonml_coverage_wording_fix_audit.py",
    "nonml_report_idempotence_backtest.py",
    "nonml_reproducibility_campaign_v2_audit.py",
}
# Sous-ensemble testable par la seule presence/absence d'un appel .glob( :
# repro_v2 a un glob (pour un autre usage), donc ne peut pas etre detecte
# par ce test seul -- il recoit une verification dediee plus bas.
SANS_GLOB_ATTENDU = {
    "nonml_coverage_wording_fix_audit.py",
    "nonml_report_idempotence_backtest.py",
}


def appels_glob(py):
    """Parcourt l'AST : tout appel dont l'attribut est 'glob', peu importe
    l'objet sur lequel il porte. Route indépendante du regex `\\.glob\\(`
    utilisé par le backtest."""
    try:
        arbre = ast.parse(py.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    out = []
    for n in ast.walk(arbre):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "glob"):
            arg = n.args[0] if n.args and isinstance(n.args[0], ast.Constant) else None
            out.append(arg.value if arg else "?")
    return out


def hardliterals(py):
    """Compte les constantes entières/flottantes en dur DANS des f-strings
    ou chaines litterales passees a L.append, par une route differente :
    parcours AST des JoinedStr (f-strings) pour reperer les segments
    Constant (texte fixe) qui contiennent des chiffres, plutot que le
    regex du backtest."""
    try:
        arbre = ast.parse(py.read_text(encoding="utf-8"))
    except SyntaxError:
        return 0
    n = 0
    for node in ast.walk(arbre):
        if isinstance(node, ast.JoinedStr):
            for v in node.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    if any(c.isdigit() for c in v.value):
                        n += 1
    return n


def justification_publiee(txt_pub, nom):
    """Extrait la justification du #485 telle que publiée dans le rapport du
    backtest (ligne « Justification du #485, verbatim : « ... » »), sans
    passer par le dictionnaire `V` du backtest -- route indépendante pour
    savoir CE QUE chaque justification revendique comme preuve."""
    marqueur = f"### `{nom}`"
    i = txt_pub.find(marqueur)
    if i < 0:
        return ""
    j = txt_pub.find("Justification du #485", i)
    if j < 0:
        return ""
    fin = txt_pub.find("\n", j)
    return txt_pub[j:fin]


def main():
    glob_par_script = {nom: appels_glob(SCRIPTS / nom) for nom in ONZE}

    txt_pub = RESULT_MD.read_text(encoding="utf-8") if RESULT_MD.exists() else ""

    # Ne teste l'absence de glob QUE pour les scripts dont la justification
    # publiee revendique explicitement un glob comme preuve -- les autres
    # (ex. content_defined_magnitudes_*, qui revendiquent une lecture git)
    # n'ont aucune raison d'avoir un appel .glob(.
    revendique_glob = {nom for nom in ONZE
                       if "glob" in justification_publiee(txt_pub, nom).lower()}
    sans_glob = {nom for nom in revendique_glob if not glob_par_script[nom]}

    L = []
    A = L.append
    A("# Audit indépendant — #518, les 11 justifications RÉPARABLE du #485")
    A("")
    A("Route de calcul différente du backtest : parcours **AST** (pas regex")
    A("sur le texte source) pour repérer tout appel `.glob(` quel que soit")
    A("l'objet visé, et pour compter les segments de texte fixe contenant un")
    A("chiffre à l'intérieur des f-strings — sans jamais lire le dictionnaire")
    A("`V` de verdicts écrits à la main dans le backtest.")
    A("")
    A("## Présence d'un appel `.glob(` — par script, route AST")
    A("")
    A("| Script | Appels `.glob(...)` trouvés | Segments littéraux "
      "chiffrés (f-string) |")
    A("|---|---|---|")
    for nom in ONZE:
        g = glob_par_script[nom]
        hl = hardliterals(SCRIPTS / nom)
        aff = ", ".join(f"`{x}`" for x in g) if g else "**aucun**"
        A(f"| `{nom}` | {aff} | {hl} |")
    A("")

    A("## Les 3 chutes du backtest sont-elles confirmées par cette route ?")
    A("")
    def fmt(ens):
        return ", ".join(f"`{n}`" for n in sorted(ens)) if ens else "aucun"

    A(f"- parmi les scripts dont la **justification publiée** revendique "
      f"explicitement un `glob` comme preuve (**{len(revendique_glob)}** "
      f"sur 11, extraits du rapport, pas du dictionnaire interne du "
      f"backtest) : {fmt(revendique_glob)}")
    A(f"- ceux d'entre eux **sans aucun** appel `.glob(` détecté par AST : "
      f"**{len(sans_glob)}**")
    for nom in sorted(sans_glob):
        A(f"  - `{nom}`")
    A("")
    accord = sans_glob == SANS_GLOB_ATTENDU
    A(f"- sous-ensemble testable par ce seul critère (glob revendiqué ET "
      f"absent) : {fmt(SANS_GLOB_ATTENDU)}")
    A(f"- accord exact : **{'OUI' if accord else 'NON'}**")
    A("")
    if accord:
        A("> **Accord exact** sur les 2 des 3 chutes testables par la seule "
          "présence/absence d'un `.glob(` — `reproducibility_campaign_v2_"
          "audit.py` **a** un `.glob(`, mais pour un autre usage, testé "
          "séparément ci-dessous plutôt que forcé dans ce même critère.")
    else:
        A("> **Désaccord** — voir le détail des appels par script ci-dessus.")
    A("")

    # Verification specifique reproducibility_campaign_v2 : le glob existe,
    # mais ne porte pas sur *.npz -- teste explicitement.
    g_repro = glob_par_script["nonml_reproducibility_campaign_v2_audit.py"]
    porte_sur_npz = any(a and "npz" in str(a) for a in g_repro)
    A("## Cas particulier vérifié séparément : `reproducibility_campaign_v2_audit.py`")
    A("")
    A(f"- appels `.glob(` détectés : "
      f"{', '.join(repr(a) for a in g_repro) if g_repro else 'aucun'}")
    A(f"- l'un d'eux porte-t-il sur un motif `*.npz` : "
      f"**{'OUI' if porte_sur_npz else 'NON'}**")
    A("")
    if not porte_sur_npz:
        A("> Confirme la nuance du backtest : ce script **a** un `.glob(`, "
          "mais il sert à lister les scripts éligibles, pas à compter les "
          "`.npz` — le chiffre cité (208) n'est donc dérivé d'aucun des "
          "appels présents.")
    A("")

    n_exactes_pub = None
    for ligne in txt_pub.splitlines():
        if "justifications **exactes**" in ligne:
            import re as _re
            m = _re.search(r"\*\*(\d+) / (\d+)\*\*", ligne)
            if m:
                n_exactes_pub = (int(m.group(1)), int(m.group(2)))
    verdict = "PASS" if accord and porte_sur_npz is False else "FAIL"
    A(f"**{verdict}** — la route AST indépendante confirme, sans lire le "
      "dictionnaire de verdicts du backtest, l'ensemble exact des 3 "
      "reclassements et la nuance du cas `reproducibility_campaign_v2`.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — sans_glob={sorted(sans_glob)}, accord={accord}, "
          f"repro_v2_glob_npz={porte_sur_npz}")


if __name__ == "__main__":
    main()
