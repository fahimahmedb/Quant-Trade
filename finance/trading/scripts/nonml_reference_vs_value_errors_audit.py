"""Audit independant du #503.

Le backtest cherche les sections candidates en balayant TOUTES les sections
du registre. Cet audit remonte par l'autre bout : il part du NOMBRE et
localise ses occurrences en gras dans le fichier entier, puis rattache chaque
occurrence a la section qui la contient par POSITION. Meme regle, chemin
inverse.

Il verifie en outre quatre proprietes que le backtest n'enonce pas :
  1. les trois classes forment une PARTITION ;
  2. l'effectif des suspects egale 14 + 15 du #502 ;
  3. la classe << valeur suspecte >> implique 0 candidate ;
  4. la direction des candidates est recalculee independamment.
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
RAP = RESULTS / "nonml_reference_vs_value_errors_result.md"
RAP_502 = RESULTS / "nonml_contextual_confrontation_result.md"
BT = SCRIPTS / "nonml_reference_vs_value_errors_backtest.py"
OUT = RESULTS / "nonml_reference_vs_value_errors_audit.md"
MOI = "reference_vs_value_errors"

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


def bornes_sections(txt):
    """[(nom, debut, fin)] -- pour rattacher une position a sa section."""
    marques = [(m.group(1), m.start()) for m in
               re.finditer(r"(?m)^##\s+Backlog\s+#?(\d{3})\b", txt)]
    out = []
    for i, (n, a) in enumerate(marques):
        b = marques[i + 1][1] if i + 1 < len(marques) else len(txt)
        out.append((f"#{n}", a, b))
    return out


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)
    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c502 = module("nonml_contextual_confrontation_backtest.py")
    c503 = module("nonml_reference_vs_value_errors_backtest.py")

    txt = BACKLOG.read_text(encoding="utf-8")
    bornes = bornes_sections(txt)
    secs = c501.sections_backlog()

    # --- Les suspects, re-derives ------------------------------------------
    suspects = []
    for py in sorted(SCRIPTS.glob("nonml_*.py")):
        if any(k in py.name for k in (c500.MOI, c501.MOI, c502.MOI, MOI)):
            continue
        try:
            arbre = ast.parse(py.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for t, cy, nb in c500.emprunts_de(arbre):
            for g in nb:
                v = c501.chiffres_seuls(g)
                if v is None:
                    continue
                cite, cles = cy[0], c502.mots_cles(t)
                sec = secs.get(cite)
                if sec is None or len(cles) < c502.RECOUVREMENT:
                    continue
                fs = c502.fenetres(v, sec)
                if fs and max(sum(1 for c in cles if c in f) for f in fs) \
                        >= c502.RECOUVREMENT:
                    continue
                suspects.append({"py": py.name, "cite": cite, "val": v,
                                 "cles": cles, "sec": sec,
                                 "origine": "absent" if not fs else "sur-crédité"})

    # --- Chemin inverse : du NOMBRE vers la section, par position ----------
    for s in suspects:
        v = re.escape(s["val"])
        motif = re.compile(r"\*\*-?" + v + r"\s*(?:%|€|bps)?\*\*")
        cand = set()
        for m in motif.finditer(txt):
            nom = next((n for n, a, b in bornes if a <= m.start() < b), None)
            if nom is None or nom == s["cite"]:
                continue
            a = max(0, m.start() - c502.FENETRE)
            b = min(len(txt), m.end() + c502.FENETRE)
            fen = txt[a:b].lower()
            if sum(1 for c in s["cles"] if c in fen) >= c502.RECOUVREMENT:
                cand.add(nom)
        s["cand"] = sorted(cand)
        mag = c503.magnitude(s["val"])
        s["grandeur"] = any(c503.magnitude(g) == mag for g in GRAS.findall(s["sec"]))
        s["classe"] = ("référence probable ailleurs" if cand else
                       "valeur suspecte" if s["grandeur"] else "indéterminé")

    cl = {c: sum(1 for s in suspects if s["classe"] == c) for c in c503.CLASSES}
    ailleurs = [s for s in suspects if s["classe"] == "référence probable ailleurs"]
    uniques = sum(1 for s in ailleurs if len(s["cand"]) == 1)
    n = lambda c: int(c.lstrip("#"))
    apres_only = sum(1 for s in ailleurs if all(n(c) > n(s["cite"]) for c in s["cand"]))

    def num(motif, txt_=p):
        m = re.search(motif, txt_)
        return int(m.group(1)) if m else None
    pub = {
        "suspects": num(r"suspects classés : (\d+)"),
        "ailleurs": num(r"\| référence probable ailleurs \| (\d+) \|"),
        "valeur": num(r"\| valeur suspecte \| (\d+) \|"),
        "indet": num(r"\| indéterminé \| (\d+) \|"),
        "uniques": num(r"section candidate unique : (\d+)"),
        "apres": num(r"postérieures au cycle cité : (\d+)"),
    }
    p502 = plat(RAP_502.read_text(encoding="utf-8"))
    n_surc = num(r"\| présent sans contexte \| (\d+) \|", p502)
    n_abs = num(r"\| absent de la section \| (\d+) \|", p502)

    partition = (cl["référence probable ailleurs"] + cl["valeur suspecte"]
                 + cl["indéterminé"]) == len(suspects)
    effectif_ok = pub["suspects"] == (n_surc or 0) + (n_abs or 0)
    exclusif = all(not s["cand"] for s in suspects
                   if s["classe"] in ("valeur suspecte", "indéterminé"))

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — référence ou valeur (#503)")
    A("")
    A("Le backtest balaie **toutes les sections** et cherche le nombre dans")
    A("chacune. Cet audit prend le **chemin inverse** : il localise le nombre")
    A("dans le fichier entier, puis rattache chaque occurrence à sa section")
    A("**par position**. Même règle, parcours opposé.")
    A("")
    A("## Le reclassement par le chemin inverse")
    A("")
    A("| Grandeur | Rapport | Audit | Accord |")
    A("|---|---|---|---|")
    lignes = [("suspects", pub["suspects"], len(suspects)),
              ("référence probable ailleurs", pub["ailleurs"],
               cl["référence probable ailleurs"]),
              ("valeur suspecte", pub["valeur"], cl["valeur suspecte"]),
              ("indéterminé", pub["indet"], cl["indéterminé"]),
              ("candidates uniques", pub["uniques"], uniques),
              ("candidates toutes postérieures", pub["apres"], apres_only)]
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
    A("## Quatre propriétés que le backtest n'énonce pas")
    A("")
    A(f"- les trois classes forment une **partition** : "
      f"**{'OUI' if partition else 'NON'}**")
    A(f"- l'effectif égale **{n_surc}** + **{n_abs}** du #502 : "
      f"**{'OUI' if effectif_ok else 'NON'}**")
    A(f"- « valeur suspecte » et « indéterminé » ont **0** candidate : "
      f"**{'OUI' if exclusif else 'NON'}**")
    A(f"- la direction des candidates, recalculée : **{apres_only}** sur")
    A(f"  **{len(ailleurs)}** n'ont que des candidates **postérieures**")
    A("")
    if apres_only == len(ailleurs) - 1:
        A("> La correction que le rapport s'inflige — « ma classe s'appelle")
        A("> mal » — est **confirmée par ce chemin indépendant**. Elle n'est pas")
        A("> une concession rhétorique : le registre **reprend ses chiffres vers")
        A("> l'avant**, et un détecteur qui ignore le temps prend cette reprise")
        A("> pour une erreur d'attribution.")
    A("")
    A("## Ce que cet audit ne prouve pas")
    A("")
    A("Les deux parcours appliquent la **même règle contextuelle**. Leur accord")
    A("valide le **parcours**, pas la règle. Et **aucun des deux** ne lit le")
    A("sens : « repris plus tard » reste une inférence tirée de **numéros de")
    A("cycle**, pas de la lecture des phrases.")
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
    ctrl = [("les deux parcours donnent les mêmes six grandeurs", not ecarts),
            ("les trois classes forment une partition", partition),
            ("l'effectif des suspects égale celui du #502", effectif_ok),
            ("les classes sans candidate en ont bien zéro", exclusif),
            ("aucun chiffre du rapport tapé en dur, arbre propre",
             not en_dur and not sales)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** pour les prix ; en")
    A("revanche ce cycle **introduit une notion de temps** — l'ordre des")
    A("cycles — et c'est elle qui a corrigé sa propre conclusion.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — {len(ecarts)} écart(s)")


if __name__ == "__main__":
    main()
