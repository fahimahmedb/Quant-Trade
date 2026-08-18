"""Audit independant du #508.

Le backtest teste les sources dans un ORDRE de priorite (cycle cite, puis
ailleurs, puis existence). Un ordre peut cacher une erreur : si le test A est
trop permissif, B et C ne sont jamais atteints. Cet audit calcule les QUATRE
appartenances INDEPENDAMMENT, sans ordre, puis verifie que la classe rendue
est bien celle que l'ordre declare produit.

Il verifie en outre :
  1. l'exclusivite reelle -- un emprunt en A doit aussi satisfaire << existe >> ;
  2. la monotonie -- tout emprunt en A ou B doit satisfaire << existe >> ;
  3. que la classe D vide ne resulte pas d'un test d'existence trop large.
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

RAP = RESULTS / "nonml_borrowings_final_taxonomy_result.md"
BT = SCRIPTS / "nonml_borrowings_final_taxonomy_backtest.py"
OUT = RESULTS / "nonml_borrowings_final_taxonomy_audit.md"
MOI = "borrowings_final_taxonomy"

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
    c500 = module("nonml_borrowed_figures_census_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    c502 = module("nonml_contextual_confrontation_backtest.py")
    c504 = module("nonml_suspect_values_reports_backtest.py")
    c508 = module("nonml_borrowings_final_taxonomy_backtest.py")
    secs = c501.sections_backlog()

    rapports = {}
    for f in sorted(RESULTS.glob("*.md")):
        if MOI in f.name:
            continue
        try:
            rapports[f.name] = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
    pregs = {}
    for f in sorted(ROOT.glob("PREREG_*.md")):
        if MOI in f.name:
            continue
        try:
            pregs[f.name] = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

    def au_sujet(v, cles, textes, nus=False):
        for nom, txt in textes.items():
            fens = (c508.nu(v, txt.lower(), c502.FENETRE) if nus
                    else c502.fenetres(v, txt))
            if fens and max(sum(1 for c in cles if c in f) for f in fens) \
                    >= c502.RECOUVREMENT:
                return nom
        return None

    tous = list(rapports.values()) + list(pregs.values()) + list(secs.values())

    emprunts = []
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
                cles = c502.mots_cles(t)
                cite = cy[0]
                sec = secs.get(cite)
                # --- les quatre appartenances, INDEPENDAMMENT ------------
                a_sec = bool(sec) and bool(au_sujet(v, cles, {cite: sec}))
                a_rap = False
                if sec is not None:
                    _, fichiers = c504.rapports_du_cycle(sec)
                    a_rap = bool(au_sujet(
                        v, cles, {f.name: rapports.get(f.name, "") for f in fichiers}))
                b_ok = bool(au_sujet(v, cles,
                                     {k: t2 for k, t2 in secs.items() if k != cite})
                            or au_sujet(v, cles, rapports)
                            or au_sujet(v, cles, pregs, nus=True))
                ex = any(re.search(r"(?<![\d,.])" + re.escape(v) + r"(?![\d,.])", t2)
                         for t2 in tous)
                emprunts.append({"py": py.name, "cite": cite, "val": v,
                                 "A": a_sec or a_rap, "B": b_ok, "ex": ex})

    # --- La classe que l'ordre declare doit produire ----------------------
    for e in emprunts:
        e["cl"] = ("A" if e["A"] else "B" if e["B"] else "C" if e["ex"] else "D")
    cl = {k: sum(1 for e in emprunts if e["cl"] == k) for k in "ABCD"}

    mono = all(e["ex"] for e in emprunts if e["A"] or e["B"])
    a_sans_ex = [e for e in emprunts if e["A"] and not e["ex"]]
    d_vide_legitime = all(e["ex"] for e in emprunts)

    def num(motif):
        m = re.search(motif, p)
        return int(m.group(1)) if m else None
    pub = {k: num(rf"\| {k} \| (\d+) \|") for k in "ABCD"}
    pub["n"] = num(r"nombres empruntés : (\d+)")

    ecarts = [(k, pub[k], cl[k]) for k in "ABCD" if pub[k] != cl[k]]

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — taxonomie des emprunts (#508)")
    A("")
    A("Le backtest teste les sources **dans un ordre de priorité**. Un ordre")
    A("peut masquer une erreur : si le test **A** est trop permissif, **B** et")
    A("**C** ne sont jamais atteints. Cet audit calcule les **quatre")
    A("appartenances indépendamment**, sans ordre, puis reconstruit la classe.")
    A("")
    A("## Le reclassement sans ordre")
    A("")
    A("| Classe | Rapport | Audit | Accord |")
    A("|---|---|---|---|")
    for k in "ABCD":
        A(f"| **{k}** | **{pub[k]}** | **{cl[k]}** | "
          f"{'**oui**' if pub[k] == cl[k] else '**NON**'} |")
    A("")
    A(f"- classes en désaccord : **{len(ecarts)}**")
    A(f"- effectif recalculé : **{len(emprunts)}** ; annoncé : **{pub['n']}**")
    A("")
    A("## Trois propriétés que le backtest n'énonce pas")
    A("")
    A(f"- **monotonie** : tout emprunt en **A** ou **B** satisfait aussi")
    A(f"  « existe » — **{'OUI' if mono else 'NON'}**")
    A(f"- emprunts en **A** dont le nombre n'existe nulle part : "
      f"**{len(a_sans_ex)}** *(doit valoir 0 : être au sujet implique exister)*")
    A(f"- la classe **D** vide est-elle légitime ? tous les nombres existent : "
      f"**{'OUI' if d_vide_legitime else 'NON'}**")
    A("")
    if d_vide_legitime:
        A("> **D vide n'est pas un artefact de test trop large** : chaque nombre")
        A("> emprunté est réellement présent quelque part dans le dépôt. Le")
        A("> test d'existence est **nu** — donc permissif — mais son résultat")
        A("> est cohérent avec la monotonie ci-dessus.")
    A("")
    A("## Ce que cet audit ne prouve pas")
    A("")
    A("Il valide l'**ordre** de la taxonomie, pas ses **définitions**. Les deux")
    A("routes partagent la règle contextuelle du #502 : si « ≥ 2 mots-clés dans")
    A("±200 caractères » est un mauvais test de « même sujet », **les deux se")
    A("trompent ensemble**. Le rapport le dit déjà ; l'audit ne le contredit")
    A("pas.")
    A("")
    A("Il ne se prononce pas non plus sur le **contrôle échoué** : que les deux")
    A("résidus du #505 tombent en **B** est un **fait**, et le pré-enregistrement")
    A("en faisait un **FAIL**. Rien ici ne le rattrape.")
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
    ctrl = [("les deux routes donnent les mêmes quatre comptes", not ecarts),
            ("l'effectif recalculé égale l'effectif annoncé",
             len(emprunts) == pub["n"]),
            ("la monotonie A/B ⊂ existe est vérifiée", mono and not a_sans_ex),
            ("la classe D vide n'est pas un artefact", d_vide_legitime),
            ("aucun chiffre du rapport tapé en dur, arbre propre",
             not en_dur and not sales)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("> **Un audit qui passe sur un cycle qui échoue n'est pas une")
    A("> contradiction** : le cycle échoue son **contrôle pré-enregistré**,")
    A("> l'audit vérifie que son **classement** est cohérent. Les deux peuvent")
    A("> être vrais en même temps, et le backlog doit porter les deux.")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** : aucune série de prix.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — {len(ecarts)} écart(s)")


if __name__ == "__main__":
    main()
