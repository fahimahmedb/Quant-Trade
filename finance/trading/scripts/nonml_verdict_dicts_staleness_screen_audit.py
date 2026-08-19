"""Audit indépendant du #522 : recompte les entrées des 4 dictionnaires V
et les candidats trouvés, par une route distincte (regex sur texte brut
pour l'extraction des clés, découpage du backlog par `grep -n` plutôt que
par un scan regex en mémoire) sans réutiliser le code du backtest.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"
REPO = ROOT.parent.parent

RESULT_MD = RESULTS / "nonml_verdict_dicts_staleness_screen_result.md"
OUT = RESULTS / "nonml_verdict_dicts_staleness_screen_audit_result.md"

DICOS = [
    ("nonml_hardcoded_figures_remainder_backtest.py", 479),
    ("nonml_guards_witness_remainder_backtest.py", 484),
    ("nonml_guards_without_witness_backtest.py", 481),
    ("nonml_orphan_audits_declared_reading_backtest.py", 483),
]
MARQUEURS = ("corrigé au #", "verdict tombe", "périmé", "FAUSSE",
             "contredit", "réfuté")


def cles_par_regex(chemin):
    """Extrait les cles de V par regex sur texte brut -- route differente
    de l'AST du backtest. Ne cherche que les cles en debut de ligne du
    bloc V, entre '^V = {' et la '}' de fermeture au meme niveau."""
    src = chemin.read_text(encoding="utf-8")
    m = re.search(r"^V = \{\n(.*?)\n\}\n", src, re.M | re.S)
    if not m:
        return []
    bloc = m.group(1)
    # Une cle commence toujours en debut de ligne (colonne 1, pas indentee
    # comme le texte de justification qui suit toujours une cle).
    cles = re.findall(r'^\s?\(?"([a-z0-9_.]+)"', bloc, re.M)
    return cles


def grep_ligne(motif, chemin):
    r = subprocess.run(["grep", "-n", motif, str(chemin)],
                       capture_output=True, text=True)
    return [int(l.split(":", 1)[0]) for l in r.stdout.splitlines()]


def main():
    lignes_entetes = grep_ligne("^## Backlog #", BACKLOG)
    toutes_lignes = BACKLOG.read_text(encoding="utf-8").splitlines()
    cycles_par_ligne = {}
    for ln in lignes_entetes:
        m = re.match(r"## Backlog #(\d+)", toutes_lignes[ln - 1])
        if m:
            cycles_par_ligne[ln] = int(m.group(1))

    def plage(n):
        cand = [ln for ln, c in cycles_par_ligne.items() if c == n]
        if not cand:
            return None
        debut = cand[0]
        suivants = sorted(ln for ln in cycles_par_ligne if ln > debut)
        fin = suivants[0] if suivants else len(toutes_lignes) + 1
        return debut, fin

    def bloc(n):
        pl = plage(n)
        if pl is None:
            return ""
        return "\n".join(toutes_lignes[pl[0] - 1:pl[1] - 1])

    total_noms = 0
    total_candidats = 0
    par_dico_n = {}
    for nom_fichier, cycle_origine in DICOS:
        noms = cles_par_regex(SCRIPTS / nom_fichier)
        par_dico_n[nom_fichier] = len(noms)
        total_noms += len(noms)
        n_candidats = 0
        for nom_cible in noms:
            court = re.sub(r"^nonml_|_backtest\.py$|_audit\.py$|\.py$", "",
                           nom_cible)
            for n_sec in set(cycles_par_ligne.values()):
                if n_sec <= cycle_origine:
                    continue
                sec_txt = bloc(n_sec)
                if nom_cible not in sec_txt and court not in sec_txt:
                    continue
                if any(m in sec_txt for m in MARQUEURS):
                    n_candidats += 1
                    break
        total_candidats += n_candidats

    txt_pub = RESULT_MD.read_text(encoding="utf-8") if RESULT_MD.exists() else ""

    def extrait(motif):
        m = re.search(motif, txt_pub)
        return int(m.group(1)) if m else None

    pub_total = extrait(r"\*\*(\d+)\*\* entrées passées à l'écran")
    pub_candidats = extrait(r"candidats trouvés \(tous dictionnaires "
                            r"confondus\) : \*\*(\d+)\*\*")

    L = []
    A = L.append
    A("# Audit indépendant — #522, écran de staleness sur 4 dictionnaires V")
    A("")
    A("Route distincte du backtest : extraction des clés par regex sur")
    A("texte brut (pas AST), découpage du backlog par bornes de ligne")
    A("issues de `grep -n` (pas un scan regex unique en mémoire).")
    A("")
    A("## Effectifs par dictionnaire, recomptés")
    A("")
    A("| Script | Effectif (regex) | Effectif (backtest, AST) | Accord |")
    A("|---|---|---|---|")
    attendu_ast = {"nonml_hardcoded_figures_remainder_backtest.py": 32,
                   "nonml_guards_witness_remainder_backtest.py": 10,
                   "nonml_guards_without_witness_backtest.py": 5,
                   "nonml_orphan_audits_declared_reading_backtest.py": 4}
    tout_ok = True
    for nom_fichier, _ in DICOS:
        n_regex = par_dico_n[nom_fichier]
        n_ast = attendu_ast[nom_fichier]
        ok = n_regex == n_ast
        tout_ok = tout_ok and ok
        A(f"| `{nom_fichier}` | {n_regex} | {n_ast} | "
          f"**{'OUI' if ok else 'NON'}** |")
    A("")
    A(f"- total recompté : **{total_noms}**")
    A(f"- total publié par le backtest : **{pub_total}**")
    accord_total = total_noms == pub_total
    A(f"- accord : **{'OUI' if accord_total else 'NON'}**")
    A("")

    A("## Candidats, recomptés")
    A("")
    A(f"- candidats trouvés par cette route : **{total_candidats}**")
    A(f"- candidats publiés par le backtest : **{pub_candidats}**")
    accord_candidats = total_candidats == pub_candidats
    A(f"- accord : **{'OUI' if accord_candidats else 'NON'}**")
    A("")

    verdict = "PASS" if (tout_ok and accord_total and accord_candidats) else "FAIL"
    A(f"**{verdict}** — " + (
        "la route indépendante (regex + grep -n) reproduit les effectifs "
        "et le compte de candidats publiés par le backtest."
        if verdict == "PASS" else
        "désaccord entre la route indépendante et le rapport publié."))
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — total={total_noms}/{pub_total}, "
          f"candidats={total_candidats}/{pub_candidats}")


if __name__ == "__main__":
    main()
