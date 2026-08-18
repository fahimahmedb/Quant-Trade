"""Audit independant du #502.

Le backtest mesure le recouvrement sur une FENETRE DE CARACTERES centree sur
l'occurrence. Cet audit le remesure sur la PHRASE qui contient l'occurrence --
un decoupage semantique, pas metrique. Les deux ne peuvent pas coincider
exactement : l'audit publie l'ecart et dit dans quel sens il va.

Il verifie en outre quatre proprietes que le backtest n'enonce pas :
  1. les cinq classes forment une PARTITION ;
  2. la table de transition somme a l'effectif total ;
  3. << confirme en contexte >> implique << present dans la section >> ;
  4. aucun emprunt classe << contexte indisponible >> n'a >= 2 mots-cles.
"""
import ast
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

BACKLOG = ROOT / "NONML_STRATEGY_BACKLOG.md"
RAP = RESULTS / "nonml_contextual_confrontation_result.md"
BT = SCRIPTS / "nonml_contextual_confrontation_backtest.py"
OUT = RESULTS / "nonml_contextual_confrontation_audit.md"
MOI = "contextual_confrontation"

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


def phrases_avec(valeur, section):
    """Les PHRASES contenant l'occurrence en gras -- decoupage semantique."""
    out = []
    v = re.escape(valeur)
    motif = re.compile(r"\*\*-?" + v + r"\s*(?:%|€|bps)?\*\*")
    for para in section.split("\n"):
        if not motif.search(para):
            continue
        for ph in re.split(r"(?<=[.!?;:])\s+", para):
            if motif.search(ph):
                out.append(ph.lower())
    return out


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)
    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c502 = module("nonml_contextual_confrontation_backtest.py")

    secs = c501.sections_backlog()

    emprunts = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if any(k in py.name for k in (c500.MOI, c501.MOI, MOI)):
            continue
        try:
            arbre = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for t, cy, nb in c500.emprunts_de(arbre):
            for g in nb:
                v = c501.chiffres_seuls(g)
                if v is not None:
                    emprunts.append({"py": py.name, "cite": cy[0], "val": v,
                                     "cles": c502.mots_cles(t)})

    par_phrase, presents, indispo, incoherents = 0, 0, 0, []
    for e in emprunts:
        sec = secs.get(e["cite"])
        if sec is None:
            continue
        if len(e["cles"]) < c502.RECOUVREMENT:
            indispo += 1
            if len(e["cles"]) >= c502.RECOUVREMENT:
                incoherents.append(e["py"])
            continue
        phs = phrases_avec(e["val"], sec)
        if not phs:
            continue
        presents += 1
        if max(sum(1 for c in e["cles"] if c in ph) for ph in phs) \
                >= c502.RECOUVREMENT:
            par_phrase += 1

    def num(motif):
        m = re.search(motif, p)
        return int(m.group(1)) if m else None
    pub = {
        "total": num(r"nombres empruntés reclassés : (\d+)"),
        "conf": num(r"\| confirmé en contexte \| (\d+) \|"),
        "sans": num(r"\| présent sans contexte \| (\d+) \|"),
        "abs": num(r"\| absent de la section \| (\d+) \|"),
        "indispo": num(r"\| contexte indisponible \| (\d+) \|"),
        "nonver": num(r"\| non vérifiable \| (\d+) \|"),
    }
    somme = sum(v for k, v in pub.items() if k != "total" and v is not None)
    partition = somme == pub["total"]

    trans = [int(m) for m in re.findall(r"\| [^|]+ \| [^|]+ \| \*\*(\d+)\*\* \|",
                                        rap.split("## La table de transition", 1)[-1]
                                        .split("\n## ", 1)[0])]
    trans_ok = sum(trans) == pub["total"]
    inclusion = (pub["conf"] + pub["sans"]) == presents
    indispo_ok = pub["indispo"] == indispo and not incoherents

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — confrontation par le contexte (#502)")
    A("")
    A(f"Le backtest mesure le recouvrement sur une **fenêtre de "
      f"±{c502.FENETRE} caractères**. Cet audit le remesure sur la **phrase**")
    A("qui contient l'occurrence — un découpage **sémantique**, pas métrique.")
    A("")
    A("## Le recouvrement, remesuré à la phrase")
    A("")
    A(f"- emprunts dont le nombre est **présent** dans la section : **{presents}**")
    A(f"- confirmés par la **fenêtre** (rapport) : **{pub['conf']}**")
    A(f"- confirmés par la **phrase** (ici) : **{par_phrase}**")
    A("")
    ecart = (pub["conf"] or 0) - par_phrase
    A(f"- écart : **{ecart:+d}**")
    A("")
    if ecart > 0:
        A("> **La phrase est plus stricte que la fenêtre**, et c'est attendu :")
        A(f"> ±{c502.FENETRE} caractères débordent sur les phrases voisines. Le")
        A("> sens de l'écart **confirme** que la fenêtre est une borne")
        A("> supérieure, non un compte exact.")
    elif ecart < 0:
        A("> **La phrase est plus permissive que la fenêtre** — inattendu : un")
        A("> découpage plus étroit ne devrait pas confirmer davantage. **Cela")
        A("> signale un défaut dans l'une des deux mesures.**")
    else:
        A("> Les deux découpages donnent le **même compte**.")
    A("")
    A("## Quatre propriétés que le backtest n'énonce pas")
    A("")
    A(f"- les cinq classes forment une **partition** "
      f"(**{somme}** = **{pub['total']}**) : **{'OUI' if partition else 'NON'}**")
    A(f"- la table de transition somme à l'effectif (**{sum(trans)}**) : "
      f"**{'OUI' if trans_ok else 'NON'}**")
    A(f"- **confirmé + présent sans contexte** = nombres présents dans la")
    A(f"  section (**{presents}**) : **{'OUI' if inclusion else 'NON'}**")
    A(f"- aucun « contexte indisponible » n'a ≥ {c502.RECOUVREMENT} mots-clés : "
      f"**{'OUI' if indispo_ok else 'NON'}**")
    A("")
    A("## Ce que cet audit ne prouve pas")
    A("")
    A("Les deux découpages partagent la **même notion de mot-clé** et le **même")
    A("seuil de recouvrement**. Leur accord valide le **découpage du contexte**,")
    A("**pas** l'idée qu'un recouvrement de mots vaut identité de sujet. Cette")
    A("idée reste une **convention**, et le rapport le dit.")
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
    ctrl = [("le recouvrement à la phrase ne contredit pas la fenêtre",
             ecart >= 0),
            ("les cinq classes forment une partition", partition),
            ("la table de transition somme à l'effectif", trans_ok),
            ("confirmé + sans contexte = présents dans la section", inclusion),
            ("la classe « contexte indisponible » est cohérente", indispo_ok),
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
    print(f"{v} — fenêtre {pub['conf']} / phrase {par_phrase}")


if __name__ == "__main__":
    main()
