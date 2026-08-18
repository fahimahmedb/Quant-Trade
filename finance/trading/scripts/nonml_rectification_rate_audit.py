"""Audit independant du #512.

Le backtest cherche des MARQUEURS LEXICAUX autour d'une reference. Cet audit
teste la mesure autrement : par un TEMOIN NEGATIF. Il rejoue exactement la
meme regle avec une liste de marqueurs NEUTRES -- des mots frequents du
registre qui n'ont rien a voir avec une rectification. Si le taux obtenu avec
des mots neutres est proche du taux publie, alors le detecteur ne mesure pas
la rectification mais la simple COOCCURRENCE, et le chiffre ne vaut rien.

Il verifie en outre :
  1. l'antisymetrie -- aucun cycle ne peut rectifier un predecesseur ET etre
     rectifie par lui ;
  2. l'auto-exclusion -- aucun cycle ne se rectifie lui-meme ;
  3. la coherence du delai median annonce.
"""
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_rectification_rate_result.md"
BT = SCRIPTS / "nonml_rectification_rate_backtest.py"
OUT = RESULTS / "nonml_rectification_rate_audit.md"
MOI = "rectification_rate"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")
# Temoins NEUTRES : frequents dans ce registre, etrangers a la rectification.
NEUTRES = ["cycle", "rapport", "mesure", "script", "publie", "critère",
           "verdict", "audit", "population", "chiffre", "règle", "dépôt"]


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


def applique(secs, numeros, mots, fenetre):
    """La regle du #512, avec une liste de mots quelconque."""
    rect = {n: [] for n in numeros}
    auto, retro = 0, 0
    for mmm in numeros:
        txt = secs[f"#{mmm}"].lower()
        for m in re.finditer(r"#(\d{3})", txt):
            nnn = int(m.group(1))
            if nnn not in rect:
                continue
            a = max(0, m.start() - fenetre)
            b = min(len(txt), m.end() + fenetre)
            fen = txt[a:b]
            if not any(k in fen for k in mots):
                continue
            if nnn == mmm:
                auto += 1
            elif nnn > mmm:
                retro += 1
            elif mmm not in rect[nnn]:
                rect[nnn].append(mmm)
    return rect, auto, retro


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)
    bt = module("nonml_rectification_rate_backtest.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
    secs = c501.sections_backlog()
    numeros = sorted(int(k.lstrip("#")) for k in secs)

    reel, auto_r, retro_r = applique(secs, numeros, bt.MARQUEURS, bt.FENETRE)
    neut, auto_n, _ = applique(secs, numeros, NEUTRES, bt.FENETRE)

    n_reel = sum(1 for n in numeros if reel[n])
    n_neut = sum(1 for n in numeros if neut[n])
    t_reel = 100.0 * n_reel / len(numeros) if numeros else 0.0
    t_neut = 100.0 * n_neut / len(numeros) if numeros else 0.0

    # antisymetrie : A rectifie B et B rectifie A
    paires = set()
    for n in numeros:
        for m in reel[n]:
            if n in reel.get(m, []):
                paires.add(tuple(sorted((n, m))))

    delais = sorted(min(reel[n]) - n for n in numeros if reel[n])
    med = (delais[len(delais) // 2] if len(delais) % 2
           else (delais[len(delais) // 2 - 1] + delais[len(delais) // 2]) / 2) \
        if delais else None

    def num(motif):
        m = re.search(motif, p)
        return m.group(1) if m else None
    pub_n = num(r"rectifiés par au moins un successeur : (\d+)")
    pub_t = num(r"taux global : ([\d,]+) %")
    pub_med = num(r"délai médian avant première rectification : (\d+)")

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [g.group(1) for g in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(g.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — taux de rectification (#512)")
    A("")
    A("Cet audit ne refait pas la même mesure : il monte un **témoin négatif**.")
    A("Il rejoue **exactement la même règle** avec des marqueurs **neutres** —")
    A("des mots fréquents du registre étrangers à toute rectification. Si le")
    A("taux obtenu avec des mots neutres approche le taux publié, **le")
    A("détecteur ne mesure pas la rectification mais la cooccurrence**.")
    A("")
    A("## Le témoin négatif")
    A("")
    A("> mots neutres employés : " + ", ".join(f"`{m}`" for m in NEUTRES))
    A("")
    A("| Liste de marqueurs | Cycles « rectifiés » | Taux |")
    A("|---|---|---|")
    A(f"| **réels** (#512) | **{n_reel}** | "
      + f"**{t_reel:.1f} %**".replace(".", ",") + " |")
    A(f"| **neutres** (témoin) | **{n_neut}** | "
      + f"**{t_neut:.1f} %**".replace(".", ",") + " |")
    A("")
    ecart = t_reel - t_neut
    A(f"- écart : " + f"**{ecart:+.1f}** points".replace(".", ","))
    A("")
    if t_neut > t_reel:
        A("> **Le témoin négatif fait MIEUX que les marqueurs réels.** Des mots")
        A("> quelconques du registre — `cycle`, `rapport`, `mesure` — désignent")
        A(f"> **plus** de cycles « rectifiés » (" + f"{t_neut:.1f} %".replace(".", ",")
          + ") que les marqueurs de")
        A(f"> rectification (" + f"{t_reel:.1f} %".replace(".", ",") + ").")
        A(">")
        A("> **Le détecteur ne discrimine rien.** Il réagit à la présence d'une")
        A("> référence `#NNN` dans un texte dense, pas au fait qu'une")
        A("> rectification soit écrite. **Le taux publié par le #512 ne mesure")
        A("> pas ce qu'il annonce**, et sa « borne supérieure » comme sa")
        A("> « lecture stricte » héritent du même défaut.")
    elif t_neut >= t_reel - 10:
        A("> **Le témoin négatif obtient presque le même taux.** Le détecteur")
        A("> réagit donc surtout à la **présence d'une référence `#NNN` dans un")
        A("> texte dense**, pas au fait qu'une rectification soit écrite.")
        A("> **Le chiffre du #512 ne mesure pas ce qu'il annonce.**")
    else:
        A("> **Le témoin négatif reste nettement en retrait.** Les marqueurs de")
        A("> rectification apportent une information que des mots fréquents")
        A("> quelconques n'apportent pas : le détecteur discrimine réellement.")
    A("")
    A("## Trois propriétés que le backtest n'énonce pas")
    A("")
    A(f"- **auto-rectifications** captées (un cycle se citant lui-même avec un")
    A(f"  marqueur) : **{auto_r}** — elles sont **exclues** par la règle ;")
    A(f"- **références rétrospectives** (un cycle citant un successeur) : "
      f"**{retro_r}** — exclues elles aussi ;")
    A(f"- **paires symétriques** (A rectifie B **et** B rectifie A) : "
      f"**{len(paires)}** *(doit valoir 0 : seul un successeur rectifie)*")
    A("")
    A("## Le recalcul des grandeurs publiées")
    A("")
    A("| Grandeur | Rapport | Audit | Accord |")
    A("|---|---|---|---|")
    lignes = [("cycles rectifiés", pub_n, str(n_reel)),
              ("taux global", pub_t, f"{t_reel:.1f}".replace(".", ",")),
              ("délai médian", pub_med, str(int(med)) if med is not None else "—")]
    for nom, a, b in lignes:
        A(f"| {nom} | **{a}** | **{b}** | "
          f"{'**oui**' if str(a) == str(b) else '**NON**'} |")
    A("")
    ecarts = [x for x in lignes if str(x[1]) != str(x[2])]
    A(f"- grandeurs en désaccord : **{len(ecarts)}**")
    A("")
    A("## Ce que cet audit ne prouve pas")
    A("")
    A("Le témoin négatif teste la **spécificité** du détecteur, pas la")
    A("**justesse** de chaque appariement. Et il partage la fenêtre de")
    A(f"**±{bt.FENETRE} caractères** : si cette fenêtre est trop large, les deux")
    A("listes en souffrent également — c'est justement ce que l'écart mesure.")
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
    ctrl = [("le témoin négatif est monté et publié", True),
            ("le détecteur discrimine mieux que des mots neutres",
             t_neut < t_reel - 10),
            ("aucune paire symétrique", not paires),
            ("les grandeurs publiées sont recalculées à l'identique",
             not ecarts),
            ("aucun chiffre du rapport tapé en dur, arbre propre",
             not en_dur and not sales)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** : aucune série de prix.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — réel {t_reel:.1f} % vs neutre {t_neut:.1f} %, "
          f"paires {len(paires)}, écarts {len(ecarts)}")


if __name__ == "__main__":
    main()
