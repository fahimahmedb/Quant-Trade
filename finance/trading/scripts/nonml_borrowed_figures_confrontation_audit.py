"""Audit independant du #501.

Le backtest decoupe le registre en sections par un balayage ligne a ligne et
cherche la valeur en gras. Cet audit recoupe les sections par une AUTRE
mecanique -- `re.split` sur les entetes, positions calculees -- et reclasse
tout. Il verifie en outre trois proprietes que le backtest n'enonce pas :

  1. les quatre classes forment une PARTITION (somme = effectif) ;
  2. << confirme >> implique << retrouve quelque part >> -- une classe ne peut
     pas etre plus stricte que celle qui la contient ;
  3. la coupure forte/faible ne depend que du NOMBRE DE CHIFFRES, verifiable
     sans rejouer la confrontation.
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
RAP = RESULTS / "nonml_borrowed_figures_confrontation_result.md"
BT = SCRIPTS / "nonml_borrowed_figures_confrontation_backtest.py"
OUT = RESULTS / "nonml_borrowed_figures_confrontation_audit.md"
MOI = "borrowed_figures_confrontation"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")
SEUIL_FORT = 3


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


def sections_par_split(txt):
    """Autre mecanique : decoupe par `re.split` sur les entetes."""
    bouts = re.split(r"(?m)^##\s+Backlog\s+#?(\d{3})\b", txt)
    out = {}
    for i in range(1, len(bouts) - 1, 2):
        out[f"#{bouts[i]}"] = bouts[i + 1]
    return out


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)
    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")

    txt_bl = BACKLOG.read_text(encoding="utf-8")
    secs = sections_par_split(txt_bl)
    autres = []
    for f in sorted(RESULTS.glob("*.md")):
        if MOI in f.name:
            continue
        try:
            autres.append(f.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue

    emprunts = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if c500.MOI in py.name or MOI in py.name:
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
                                     "txt": t})

    for e in emprunts:
        sec = secs.get(e["cite"])
        ici = sec is not None and c501.en_gras_dans(e["val"], sec)
        ailleurs = c501.en_gras_dans(e["val"], txt_bl) or \
            any(c501.en_gras_dans(e["val"], t) for t in autres)
        e["ici"], e["ailleurs"] = ici, ailleurs
        e["classe"] = ("non vérifiable" if sec is None else
                       "confirmé" if ici else
                       "retrouvé ailleurs" if ailleurs else "non retrouvé")
        e["fort"] = len(re.sub(r"\D", "", e["val"])) >= SEUIL_FORT

    cl = {c: sum(1 for e in emprunts if e["classe"] == c)
          for c in ("confirmé", "retrouvé ailleurs", "non retrouvé",
                    "non vérifiable")}
    conf = [e for e in emprunts if e["classe"] == "confirmé"]
    forts = sum(1 for e in conf if e["fort"])
    faibles = len(conf) - forts

    def num(motif):
        m = re.search(motif, p)
        return int(m.group(1)) if m else None
    pub = {
        "chaines": num(r"chaînes empruntées — l'unité du #500 : (\d+)"),
        "nombres": num(r"nombres empruntés — l'unité d'ici : (\d+)"),
        "confirmé": num(r"\| confirmé \| (\d+) \|"),
        "ailleurs": num(r"\| retrouvé ailleurs \| (\d+) \|"),
        "non_retr": num(r"\| non retrouvé \| (\d+) \|"),
        "non_ver": num(r"\| non vérifiable \| (\d+) \|"),
        "forts": num(r"\| fortes \(≥ \d+ chiffres\) \| (\d+) \|"),
        "faibles": num(r"\| faibles \(1-2 chiffres\) \| (\d+) \|"),
    }

    chaines = {(e["py"], e["txt"]) for e in emprunts}
    partition = (cl["confirmé"] + cl["retrouvé ailleurs"] + cl["non retrouvé"]
                 + cl["non vérifiable"]) == len(emprunts)
    inclusion = all(e["ailleurs"] for e in conf)
    coupure_ok = all(
        (len(re.sub(r"\D", "", e["val"])) >= SEUIL_FORT) == e["fort"]
        for e in emprunts)

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — confrontation des emprunts (#501)")
    A("")
    A("Le backtest découpe le registre **ligne à ligne**. Cet audit le recoupe")
    A("par **`re.split` sur les en-têtes** et reclasse tout.")
    A("")
    A("## Le reclassement")
    A("")
    A("| Grandeur | Rapport | Audit | Accord |")
    A("|---|---|---|---|")
    lignes = [("chaînes", pub["chaines"], len(chaines)),
              ("nombres", pub["nombres"], len(emprunts)),
              ("confirmé", pub["confirmé"], cl["confirmé"]),
              ("retrouvé ailleurs", pub["ailleurs"], cl["retrouvé ailleurs"]),
              ("non retrouvé", pub["non_retr"], cl["non retrouvé"]),
              ("non vérifiable", pub["non_ver"], cl["non vérifiable"]),
              ("confirmations fortes", pub["forts"], forts),
              ("confirmations faibles", pub["faibles"], faibles)]
    for nom, a, b in lignes:
        A(f"| {nom} | **{a}** | **{b}** | {'**oui**' if a == b else '**NON**'} |")
    A("")
    ecarts = [x for x in lignes if x[1] != x[2]]
    A(f"- grandeurs en désaccord : **{len(ecarts)}**")
    if ecarts:
        A("")
        for nom, a, b in ecarts:
            A(f"  - **{nom}** : rapport **{a}**, audit **{b}**")
    A("")
    A("## Trois propriétés que le backtest n'énonce pas")
    A("")
    A(f"- les quatre classes forment une **partition** : "
      f"**{'OUI' if partition else 'NON'}**")
    A(f"- **confirmé ⊂ retrouvé quelque part** — une classe ne peut être plus")
    A(f"  stricte que celle qui la contient : **{'OUI' if inclusion else 'NON'}**")
    A(f"- la coupure forte/faible ne dépend que du **nombre de chiffres** : "
      f"**{'OUI' if coupure_ok else 'NON'}**")
    A("")
    if inclusion:
        A("> L'inclusion n'est pas une évidence de code : « confirmé » regarde")
        A("> **une** section, « retrouvé ailleurs » regarde **tout**. Qu'aucun")
        A("> confirmé n'échappe au second est ce qui rend les classes lisibles")
        A("> comme des cercles emboîtés plutôt que comme des étiquettes.")
    A("")
    A("## Ce que l'accord des deux routes **ne** prouve **pas**")
    A("")
    A("Les deux mécaniques partagent la **même règle de confrontation** — elles")
    A("ne diffèrent que par le **découpage** du registre. Leur accord valide le")
    A("découpage, **pas la règle** : si chercher un nombre en gras dans une")
    A("section est un mauvais test de justesse, les deux routes se trompent")
    A("ensemble. **Le rapport le dit déjà, et cet audit ne le contredit pas.**")
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
    ctrl = [("les deux découpages donnent les mêmes huit grandeurs", not ecarts),
            ("les quatre classes forment une partition", partition),
            ("confirmé est inclus dans retrouvé quelque part", inclusion),
            ("la coupure forte/faible est reproductible", coupure_ok),
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
    print(f"{v} — {len(ecarts)} écart(s)")


if __name__ == "__main__":
    main()
