"""Audit independant du #513.

Le backtest conclut qu'AUCUN detecteur ne passe. Une conclusion negative a
une faiblesse propre : elle peut venir d'un detecteur mal ecrit plutot que
d'une impossibilite. Cet audit la teste par un TEMOIN POSITIF -- l'inverse de
celui du #512.

Il fabrique un corpus ou la reponse est CONNUE : des sections synthetiques
contenant des rectifications explicites, et des sections n'en contenant
aucune. Si les detecteurs S1 et S2 ne retrouvent pas ce qu'on y a mis, ils
sont casses ; s'ils le retrouvent, alors leur echec sur le vrai registre
vient bien du REGISTRE, pas du code.
"""
import importlib.util
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_structured_rectification_result.md"
BT = SCRIPTS / "nonml_structured_rectification_backtest.py"
OUT = RESULTS / "nonml_structured_rectification_audit.md"
MOI = "structured_rectification"

GRAS = re.compile(r"\*\*(-?\d[\d  ]*(?:[,.]\d+)?)\s*(?:%|€|bps)?\*\*")

# Corpus synthetique : la reponse est CONNUE d'avance.
POSITIFS = {
    "#900": "## Backlog #900\n\nRien de particulier ici.\n",
    "#901": "### La justification du #900 est **fausse**\n\nCorps.\n",
    "#902": "Corps.\n\n> **Le verdict du #900 est réfuté par la mesure.**\n",
    "#903": "## Backlog #903\n\nAucune référence, aucun marqueur.\n",
}
ATTENDU_S1 = {900}       # rectifie par #901 (titre)
ATTENDU_S2 = {900}       # rectifie par #902 (span en gras)


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
    bt = module("nonml_structured_rectification_backtest.py")
    c512 = module("nonml_rectification_rate_backtest.py")
    a512 = module("nonml_rectification_rate_audit.py")
    c501 = module("nonml_borrowed_figures_confrontation_backtest.py")

    nums = sorted(int(k.lstrip("#")) for k in POSITIFS)
    r1 = bt.applique(POSITIFS, nums, bt.s1_titres, c512.MARQUEURS)
    r2 = bt.applique(POSITIFS, nums, bt.s2_gras, c512.MARQUEURS)
    trouve1 = {n for n in nums if r1[n]}
    trouve2 = {n for n in nums if r2[n]}
    ok1 = trouve1 == ATTENDU_S1
    ok2 = trouve2 == ATTENDU_S2

    # --- Faux positifs sur une section sans marqueur ---------------------
    fp1 = 903 in trouve1
    fp2 = 903 in trouve2

    # --- Recalcul des quatre taux sur le vrai registre -------------------
    secs = c501.sections_backlog()
    numeros = sorted(int(k.lstrip("#")) for k in secs)
    n = len(numeros)
    taux = {}
    for nom, det in (("S1", bt.s1_titres), ("S2", bt.s2_gras)):
        for etiq, mots in (("réel", c512.MARQUEURS), ("témoin", a512.NEUTRES)):
            r = bt.applique(secs, numeros, det, mots)
            taux[(nom, etiq)] = 100.0 * sum(1 for x in numeros if r[x]) / n

    def num(motif):
        m = re.search(motif, p)
        return m.group(1) if m else None
    pub = {}
    for nom in ("S1", "S2"):
        for etiq in ("réel", "témoin"):
            pub[(nom, etiq)] = num(rf"\| {nom} \| {etiq} \| \d+ \| ([\d,]+) %")
    ecarts_pub = [x for (nom, etiq), v in pub.items()
                  if v is None
                  or abs(float(v.replace(",", ".")) - taux[(nom, etiq)]) > 0.05]

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [g.group(1) for g in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(g.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — détecteur structurel de rectification (#513)")
    A("")
    A("Le #513 conclut qu'**aucun détecteur ne passe**. Une conclusion négative")
    A("a une faiblesse propre : elle peut venir d'un **détecteur cassé** plutôt")
    A("que d'une impossibilité. Cet audit monte donc le **témoin positif** —")
    A("l'inverse de celui du #512.")
    A("")
    A("## Le corpus synthétique, où la réponse est connue")
    A("")
    A("Quatre sections fabriquées :")
    A("")
    A("- `#900` — cible, sans rien de particulier ;")
    A("- `#901` — **titre** : « La justification du #900 est **fausse** » ;")
    A("- `#902` — **span en gras** : « Le verdict du #900 est réfuté… » ;")
    A("- `#903` — **aucune** référence, **aucun** marqueur *(piège à faux")
    A("  positifs)*.")
    A("")
    A("| Détecteur | Attendu | Trouvé | Correct |")
    A("|---|---|---|---|")
    A(f"| **S1** (titres) | `{sorted(ATTENDU_S1)}` | `{sorted(trouve1)}` | "
      f"**{'OUI' if ok1 else 'NON'}** |")
    A(f"| **S2** (gras) | `{sorted(ATTENDU_S2)}` | `{sorted(trouve2)}` | "
      f"**{'OUI' if ok2 else 'NON'}** |")
    A("")
    A(f"- faux positif sur `#903` : **S1 {'oui' if fp1 else 'non'}**, "
      f"**S2 {'oui' if fp2 else 'non'}**")
    A("")
    if ok1 and ok2 and not fp1 and not fp2:
        A("> **Les deux détecteurs fonctionnent.** Ils retrouvent exactement ce")
        A("> qu'on a mis dans le corpus et n'inventent rien sur la section")
        A("> piège. **Leur échec sur le vrai registre vient donc du registre,")
        A("> pas du code** — la conclusion négative du #513 tient.")
    else:
        A("> **Au moins un détecteur est cassé.** La conclusion négative du")
        A("> #513 ne peut pas être attribuée au registre tant que ce défaut")
        A("> n'est pas corrigé.")
    A("")
    A("## Les quatre taux, recalculés sur le vrai registre")
    A("")
    A("| Détecteur | Liste | Rapport | Audit |")
    A("|---|---|---|---|")
    for nom in ("S1", "S2"):
        for etiq in ("réel", "témoin"):
            A(f"| **{nom}** | {etiq} | **{pub[(nom, etiq)] or '—'} %** | "
              + f"**{taux[(nom, etiq)]:.1f} %**".replace(".", ",") + " |")
    A("")
    A(f"- grandeurs en désaccord : **{len(ecarts_pub)}**")
    A("")
    A("## Ce que cet audit ne prouve pas")
    A("")
    A("Le témoin positif montre que les détecteurs **savent voir** une")
    A("rectification écrite sous les deux formes prévues. Il ne montre **pas**")
    A("qu'une rectification s'écrive toujours ainsi : si le registre les")
    A("exprime le plus souvent **en prose ordinaire**, aucun des deux ne les")
    A("verra — et c'est précisément ce que le #513 conclut.")
    A("")
    A("**Les deux cycles se rejoignent donc sur un point qu'aucun n'a prouvé")
    A("seul** : ce n'est pas que la rectification soit rare, c'est qu'elle")
    A("n'est pas **formatée**.")
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
    ctrl = [("le témoin positif est monté et publié", True),
            ("S1 retrouve exactement la rectification attendue", ok1),
            ("S2 retrouve exactement la rectification attendue", ok2),
            ("aucun faux positif sur la section piège", not fp1 and not fp2),
            ("les quatre taux du rapport sont recalculés à l'identique",
             not ecarts_pub),
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
    print(f"{v} — S1 {ok1}, S2 {ok2}, faux positifs {fp1}/{fp2}, "
          f"écarts {len(ecarts_pub)}")


if __name__ == "__main__":
    main()
