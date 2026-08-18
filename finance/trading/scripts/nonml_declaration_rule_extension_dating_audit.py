"""Audit independant du #498 -- recalcul par une AUTRE route.

Le backtest date chaque PREREG par `git log --diff-filter=A` fichier par
fichier. Cet audit reconstruit les dates d'introduction en UN SEUL parcours de
l'historique (`git log --name-status`), une route qui ne partage pas la
commande du backtest, puis recompte tout par-dessus.

Il verifie en outre une propriete structurelle que le backtest n'enonce pas :
la regle tolerante doit etre un SUR-ENSEMBLE strict de la litterale. Si un
PREREG etait detecte par la litterale seule, l'une des deux regles serait mal
transcrite.
"""
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_declaration_rule_extension_dating_result.md"
BT = Path(__file__).resolve().parent / "nonml_declaration_rule_extension_dating_backtest.py"
RAP_483 = RESULTS / "nonml_declaration_convention_dating_result.md"
RAP_492 = RESULTS / "nonml_declaration_convention_decay_result.md"
OUT = RESULTS / "nonml_declaration_rule_extension_dating_audit.md"
MOI = "declaration_rule_extension_dating"

LITTERALE = re.compile(r"Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)
TOLERANTE = re.compile(
    r"\*\*Cycle d[e'’]\s*([^*]+)\*\*|Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)
GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")
N_RECENTS, SEUIL_A, SEUIL_B = 40, 50.0, 20.0


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def plat(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def dates_en_un_parcours():
    """{nom -> ts du PREMIER ajout}, par un seul `git log --name-status`."""
    s = git("log", "--reverse", "--date-order", "--format=@%ct",
            "--name-status", "--diff-filter=A", "--", "finance/trading/")
    out, ts = {}, None
    for l in s.splitlines():
        if l.startswith("@"):
            ts = int(l[1:])
        elif l.startswith("A\t") and ts is not None:
            nom = l.split("\t", 1)[1].strip().split("/")[-1]
            if nom.startswith("PREREG_") and nom.endswith(".md") \
                    and nom not in out:
                out[nom] = ts
    return out


def jour(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%d/%m/%Y")


def mediane(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def lecture(m_d, m_n, p):
    if m_d is None or m_n is None:
        return "C"
    if m_d > m_n and p >= SEUIL_A:
        return "A"
    if m_d < m_n and p < SEUIL_B:
        return "B"
    return "C"


def n(motif, txt):
    m = re.search(motif, txt)
    return m.group(1) if m else None


def main():
    rap = RAP.read_text(encoding="utf-8")
    p = plat(rap)
    dates = dates_en_un_parcours()

    pop = []
    manquants = []
    for f in sorted(ROOT.glob("PREREG_*.md")):
        if MOI in f.name:
            continue
        if f.name not in dates:
            manquants.append(f.name)
            continue
        t = f.read_text(encoding="utf-8")
        pop.append({"nom": f.name, "ts": dates[f.name],
                    "lit": bool(LITTERALE.search(t)),
                    "tol": bool(TOLERANTE.search(t))})
    pop.sort(key=lambda d: d["ts"])
    recents = pop[-N_RECENTS:]

    calc = {}
    for k in ("lit", "tol"):
        dec = [d for d in pop if d[k]]
        non = [d for d in pop if not d[k]]
        m_d, m_n = mediane([d["ts"] for d in dec]), mediane([d["ts"] for d in non])
        pr = 100.0 * sum(1 for d in recents if d[k]) / len(recents)
        calc[k] = {"dec": len(dec), "m_d": m_d, "m_n": m_n, "p": pr,
                   "v": lecture(m_d, m_n, pr)}

    # --- Propriete structurelle : tolerante ⊇ litterale --------------------
    lit_seuls = [d["nom"] for d in pop if d["lit"] and not d["tol"]]

    # --- Le << 380 / 0 >> ---------------------------------------------------
    prem = min((d["ts"] for d in pop if d["lit"]), default=None)
    av = [d for d in pop if prem is not None and d["ts"] < prem]
    tol_av = [d for d in av if d["tol"]]

    # --- Ce que le rapport publie ------------------------------------------
    pub = {
        "n": int(n(r"PREREG_ datés \(hors celui-ci\) : (\d+)", p)),
        "lit_dec": int(n(r"\| littérale \| (\d+) \|", p)),
        "tol_dec": int(n(r"\| tolérante \| (\d+) \|", p)),
        "lit_v": n(r"\| littérale \|(?:[^|]*\|){5} ([ABC]) \|", p),
        "tol_v": n(r"\| tolérante \|(?:[^|]*\|){5} ([ABC]) \|", p),
        "av": int(n(r"antérieurs à cette date : (\d+)", p)),
        "tol_av": int(n(r"déclarés au sens tolérant : (\d+)", p)),
    }

    # --- Le critere du #483 est-il bien celui du #483 ? --------------------
    p483 = plat(RAP_483.read_text(encoding="utf-8"))
    critere_483 = "A si m_d > m_n et p ≥ 50 % ;" in p483 \
        and "B si m_d < m_n et p < 20 % ;" in p483
    # --- Les regles sont-elles bien celles du #492 ? -----------------------
    p492 = RAP_492.read_text(encoding="utf-8")
    regles_492 = LITTERALE.pattern.replace("\\", "") in p492.replace("\\", "") \
        and TOLERANTE.pattern.replace("\\", "") in p492.replace("\\", "")

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — extension de la règle tolérante au #483 (#498)")
    A("")
    A("Le backtest date **fichier par fichier** (`git log --diff-filter=A` par")
    A("`PREREG_`). Cet audit reconstruit les dates en **un seul parcours** de")
    A("l'historique (`git log --name-status`), puis recompte tout par-dessus.")
    A("")
    A("## La datation, par une autre commande")
    A("")
    A(f"- `PREREG_` datés par le parcours unique : **{len(pop)}**")
    A(f"- `PREREG_` que ce parcours **ne date pas** : **{len(manquants)}**")
    A(f"- population publiée par le rapport : **{pub['n']}**")
    A(f"- accord sur la taille : **{'OUI' if len(pop) == pub['n'] else 'NON'}**")
    if manquants:
        A("")
        for m in manquants[:10]:
            A(f"  - non daté : `{m}`")
    A("")
    A("## Les comptes et les verdicts, recalculés")
    A("")
    A("| Grandeur | Rapport | Audit | Accord |")
    A("|---|---|---|---|")
    lignes = [("déclarés — littérale", pub["lit_dec"], calc["lit"]["dec"]),
              ("déclarés — tolérante", pub["tol_dec"], calc["tol"]["dec"]),
              ("verdict — littérale", pub["lit_v"], calc["lit"]["v"]),
              ("verdict — tolérante", pub["tol_v"], calc["tol"]["v"]),
              ("antérieurs au 1ᵉʳ déclaré", pub["av"], len(av)),
              ("dont tolérants", pub["tol_av"], len(tol_av))]
    for nom, a, b in lignes:
        A(f"| {nom} | **{a}** | **{b}** | "
          f"{'**oui**' if str(a) == str(b) else '**NON**'} |")
    A("")
    ecarts = [x for x in lignes if str(x[1]) != str(x[2])]
    A(f"- grandeurs en désaccord : **{len(ecarts)}**")
    A("")
    A("## Une propriété que le backtest n'énonce pas")
    A("")
    A("La tolérante doit être un **sur-ensemble** de la littérale : elle accepte")
    A("les deux typographies, la littérale une seule. Un `PREREG_` détecté par")
    A("la **littérale seule** signalerait une transcription fautive.")
    A("")
    A(f"- détectés par la littérale **seule** : **{len(lit_seuls)}**")
    if lit_seuls:
        A("")
        for x in lit_seuls[:10]:
            A(f"  - `{x}`")
        A("")
        A("> **La propriété est violée** : les deux règles ne sont pas dans le")
        A("> rapport d'inclusion annoncé.")
    else:
        A("")
        gain = calc["tol"]["dec"] - calc["lit"]["dec"]
        A(f"> **Inclusion vérifiée.** L'écart de **{gain:+d}** annoncé par le")
        A("> rapport est donc un **gain net**, jamais un échange.")
    A("")
    A("## Les emprunts sont-ils fidèles ?")
    A("")
    A("Le #497 a montré qu'un chiffre repris d'un cycle antérieur **sans être")
    A("relu** est un canal d'erreur. Ici, ce ne sont pas des chiffres qui sont")
    A("empruntés mais un **critère** et deux **règles** :")
    A("")
    A(f"- le critère A/B/C se retrouve mot pour mot dans le #483 : "
      f"**{'OUI' if critere_483 else 'NON'}**")
    A(f"- les deux regex se retrouvent dans le #492 : "
      f"**{'OUI' if regles_492 else 'NON'}**")
    A("")
    A("## Inertie et chiffres calculés")
    A("")
    A(f"- fichiers de l'arbre git modifiés hors ce cycle : **{len(sales)}**")
    A(f"- nombres en gras : **{len(GRAS.findall(rap))}** ; dont **tapés en "
      f"dur** : **{len(en_dur)}**")
    if en_dur:
        A("")
        A(f"> En dur : {', '.join('`'+v+'`' for v in sorted(set(en_dur)))}")
    A("")
    A("## Verdict")
    A("")
    ctrl = [("la datation par un autre parcours donne la même population",
             len(pop) == pub["n"] and not manquants),
            ("comptes et verdicts recalculés concordent", not ecarts),
            ("la tolérante inclut bien la littérale", not lit_seuls),
            ("critère et règles retrouvés dans leurs cycles d'origine",
             critere_483 and regles_492),
            ("aucun chiffre tapé en dur, arbre propre",
             not en_dur and not sales)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** : aucune série de prix.")
    A("La datation, elle, est **strictement rétrospective** — chaque `PREREG_`")
    A("est daté par son **premier** commit d'ajout, jamais par l'état courant.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — {len(ecarts)} écart(s), littérale seule = {len(lit_seuls)}")


if __name__ == "__main__":
    main()
