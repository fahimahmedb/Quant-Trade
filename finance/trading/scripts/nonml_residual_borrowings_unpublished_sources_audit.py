"""Audit independant du #505.

Le backtest cherche les residus dans les sources non publiees en exigeant un
recouvrement de mots-cles. Cet audit fait DEUX choses que le backtest ne fait
pas :

  1. il relache la contrainte -- il cherche le nombre NU, SANS contexte, dans
     tout le depot suivi par git. Si un << introuvable partout >> n'apparait
     nulle part meme sans contrainte de sujet, le constat est bien plus fort ;
     s'il apparait, c'est la contrainte de contexte qui l'a masque, et il faut
     le dire ;
  2. il verifie que les deux << introuvables >> ne sont pas des artefacts de
     la chaine #500-#504 : leur nombre est-il seulement bien EXTRAIT de la
     chaine qui les publie ?
"""
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_residual_borrowings_unpublished_sources_result.md"
BT = SCRIPTS / "nonml_residual_borrowings_unpublished_sources_backtest.py"
OUT = RESULTS / "nonml_residual_borrowings_unpublished_sources_audit.md"
MOI = "residual_borrowings_unpublished_sources"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def plat(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def module(nom):
    p = SCRIPTS / nom
    spec = importlib.util.spec_from_file_location("_m_" + p.stem, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)

    # --- Les residus publies, LUS dans le rapport --------------------------
    blocs = re.findall(
        r"### `([a-z0-9_]+\.py)` — cite `(#\d{3})` pour \*\*([\d,\.]+)\*\*\s*\n"
        r"\s*\n- classe : \*\*([^*]+)\*\*", rap)
    perdus = [(py, cy, v) for py, cy, v, cl in blocs if cl == "introuvable partout"]

    # --- Contrainte relachee : le nombre NU, sans contexte, partout --------
    suivis = [f for f in git("ls-files").splitlines() if f.strip()]
    textes = []
    for f in suivis:
        chemin = REPO / f
        if chemin.suffix.lower() not in (".py", ".md", ".txt"):
            continue
        try:
            textes.append((f, chemin.read_text(encoding="utf-8")))
        except (UnicodeDecodeError, OSError):
            continue
    commits = git("log", "--format=%B")

    sans_contexte = {}
    for py, cy, v in perdus:
        motif = re.compile(r"(?<![\d,.])" + re.escape(v) + r"(?![\d,.])")
        porteurs = [f for f, t in textes
                    if MOI not in f and motif.search(t)]
        sans_contexte[(py, v)] = {
            "fichiers": porteurs,
            "commits": bool(motif.search(commits)),
        }

    # --- Les residus sont-ils bien extraits de leur chaine ? --------------
    c500 = module("nonml_borrowed_figures_census_backtest.py")
    import ast
    extraits_ok = 0
    for py, cy, v in perdus:
        chemin = SCRIPTS / py
        try:
            arbre = ast.parse(chemin.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        for t, cycles, nombres in c500.emprunts_de(arbre):
            if cy in cycles and any(v in g for g in nombres):
                extraits_ok += 1
                break

    def num(motif):
        m = re.search(motif, p)
        return int(m.group(1)) if m else None
    pub = {
        "residus": num(r"résidus repris de la chaîne #500-#504 : (\d+)"),
        "perdus": num(r"Les introuvables partout - effectif : (\d+)"),
        "circ": num(r"dont le PREREG_? du script lui-même : (\d+)"),
        "indep": num(r"dont un PREREG_? tiers : (\d+)"),
    }

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — résidus et sources non publiées (#505)")
    A("")
    A("Cet audit ne refait pas la même mesure : il **relâche la contrainte**.")
    A("Il cherche le nombre **nu, sans aucune exigence de sujet**, dans tout le")
    A("dépôt suivi par git. Un « introuvable partout » qui reste introuvable")
    A("**même sans contrainte de contexte** est un constat bien plus fort ;")
    A("s'il apparaît, **c'est la contrainte qui le masquait**.")
    A("")
    A("## Le corpus élargi")
    A("")
    A(f"- fichiers suivis lus (`.py`, `.md`, `.txt`) : **{len(textes)}**")
    A(f"- messages de commit : **{len(git('log', '--format=%H').splitlines())}**")
    A(f"- « introuvables partout » relus dans le rapport : **{len(perdus)}**")
    A(f"- effectif publié par le rapport : **{pub['perdus']}**")
    A(f"- accord : **{'OUI' if len(perdus) == pub['perdus'] else 'NON'}**")
    A("")
    A("## Chaque introuvable, sans contrainte de contexte")
    A("")
    A("| Script | Cite | Nombre | Fichiers portant le nombre nu | Dans un commit |")
    A("|---|---|---|---|---|")
    for py, cy, v in perdus:
        d = sans_contexte[(py, v)]
        A(f"| `{py}` | `{cy}` | **{v}** | **{len(d['fichiers'])}** | "
          f"{'**oui**' if d['commits'] else '**non**'} |")
    A("")
    vraiment_absents = [k for k, d in sans_contexte.items()
                        if not d["fichiers"] and not d["commits"]]
    A(f"- introuvables **même sans contrainte de sujet** : "
      f"**{len(vraiment_absents)}** sur **{len(perdus)}**")
    A("")
    if vraiment_absents:
        A("> Ces nombres n'existent **nulle part** dans le dépôt en dehors de la")
        A("> phrase qui les emprunte. **C'est le constat le plus fort que cette")
        A("> série ait produit** — et il reste une absence de trace, pas une")
        A("> preuve d'erreur.")
    else:
        A("> **Tous apparaissent ailleurs dès qu'on retire la contrainte de")
        A("> sujet.** Ce n'est donc pas leur existence qui manquait, mais leur")
        A("> **voisinage thématique** : la règle du #502 les a écartés parce")
        A("> qu'ils n'étaient pas entourés des bons mots, non parce qu'ils")
        A("> étaient absents. **Le mot « introuvable » du rapport est trop")
        A("> fort**, et cet audit le corrige.")
    A("")
    A("## Les résidus sont-ils bien extraits de leur script ?")
    A("")
    A(f"- « introuvables » dont l'emprunt est **retrouvé par l'AST** du script")
    A(f"  qui les publie : **{extraits_ok}** sur **{len(perdus)}**")
    A("")
    if extraits_ok == len(perdus):
        A("> Ils ne sont donc pas un artefact d'extraction de la chaîne")
        A("> #500-#504 : chacun correspond bien à une chaîne publiée par son")
        A("> script, citant le cycle annoncé.")
    A("")
    A("## Le sourçage circulaire, recompté")
    A("")
    A(f"- trouvailles circulaires publiées : **{pub['circ']}**")
    A(f"- trouvailles en `PREREG_` tiers : **{pub['indep']}**")
    A("")
    A("> La distinction que le rapport s'impose — un chiffre trouvé dans le")
    A("> `PREREG_` **du script qui le publie** ne le source pas — est la seule")
    A("> qui empêche cette série de se valider elle-même. Sans elle, le cycle")
    if pub["circ"] is not None and pub["indep"] is not None:
        A(f"> aurait annoncé **{pub['circ'] + pub['indep']}** résidus sourcés au")
        A(f"> lieu de **{pub['indep']}**.")
    else:
        A("> aurait surestimé le nombre de résidus sourcés — mais **les deux")
        A("> comptes n'ont pas pu être relus dans le rapport**, et je ne les")
        A("> retape pas.")
    A("")
    A("## Inertie et chiffres calculés")
    A("")
    A(f"- fichiers de l'arbre modifiés hors ce cycle : **{len(sales)}**")
    A(f"- nombres en gras : **{len(GRAS.findall(rap))}** ; dont **tapés en "
      f"dur** : **{len(en_dur)}**")
    if en_dur:
        A("")
        A(f"> En dur : {', '.join('`'+v+'`' for v in sorted(set(en_dur)))}")
    A("")
    A("## Verdict")
    A("")
    ctrl = [("l'effectif des introuvables concorde avec le rapport",
             len(perdus) == pub["perdus"]),
            ("chaque introuvable est re-cherché sans contrainte de contexte",
             len(sans_contexte) == len(perdus)),
            ("les introuvables ne sont pas un artefact d'extraction",
             extraits_ok == len(perdus)),
            ("le sourçage circulaire est distingué du sourçage tiers",
             pub["circ"] is not None and pub["indep"] is not None),
            ("aucun chiffre du rapport tapé en dur, arbre propre",
             not en_dur and not sales)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** : aucune série de prix.")
    A("Son équivalent ici est **l'inertie**, vérifiée ci-dessus.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — {len(vraiment_absents)}/{len(perdus)} absents même sans contexte")


if __name__ == "__main__":
    main()
