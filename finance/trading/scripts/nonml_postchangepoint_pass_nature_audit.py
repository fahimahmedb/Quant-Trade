"""Audit indépendant du #516 : recalcule le régime post-basculement par une
route différente (git log --follow par fichier, au lieu de --diff-filter=A
sur l'ensemble du dossier) et revérifie les comptes publiés dans
`nonml_postchangepoint_pass_nature_result.md`, sans réutiliser le code du
backtest.
"""
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RESULT_MD = RESULTS / "nonml_postchangepoint_pass_nature_result.md"
OUT = RESULTS / "nonml_postchangepoint_pass_nature_audit_result.md"

PIVOT_TS = int(datetime(2026, 8, 13, 21, 51, tzinfo=timezone.utc).timestamp())
PHRASE = "porte sur le procédé"


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def premiere_date_fichier(chemin_relatif):
    """Route indépendante : --follow sur le fichier lui-même, plutôt que le
    scan --diff-filter=A du dossier entier fait par le backtest."""
    s = git("log", "--follow", "--diff-filter=A", "--format=%ct", "--",
             chemin_relatif)
    lignes = [int(x) for x in s.splitlines() if x.strip()]
    return min(lignes) if lignes else None


def sans_markdown(t):
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", ""))


def main():
    regime = []
    for py in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        if "postchangepoint_pass_nature" in py.name:
            continue
        rap = RESULTS / f"{py.name[:-len('_backtest.py')]}_result.md"
        if not rap.exists():
            continue
        try:
            txt = rap.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not re.search(r"\bPASS\b|\bFAIL\b", txt):
            continue
        rel = str(py.relative_to(REPO))
        ts = premiere_date_fichier(rel)
        if ts is None or ts < PIVOT_TS:
            continue
        marqueurs = re.findall(r"\*\*(PASS|FAIL)\*\*", txt)
        verdict = marqueurs[-1] if marqueurs else ("PASS" if "PASS" in txt else "FAIL")
        procedural = PHRASE in sans_markdown(txt)
        regime.append({"py": py.name, "ts": ts, "verdict": verdict,
                       "procedural": procedural})

    passes = [r for r in regime if r["verdict"] == "PASS"]
    fails = [r for r in regime if r["verdict"] == "FAIL"]
    procs = [r for r in passes if r["procedural"]]
    subst = [r for r in passes if not r["procedural"]]

    adoption = min((r["ts"] for r in regime if r["procedural"]), default=None)
    avant_conv = [r for r in subst if adoption and r["ts"] < adoption]
    apres_conv = [r for r in subst if not adoption or r["ts"] >= adoption]

    # Comparaison au rapport du backtest (nombres publiés, extraits par regex).
    txt_pub = RESULT_MD.read_text(encoding="utf-8") if RESULT_MD.exists() else ""

    def extrait(motif):
        m = re.search(motif, txt_pub, re.DOTALL)
        return int(m.group(1)) if m else None

    pub_regime = extrait(r"scripts du régime postérieur : \*\*(\d+)\*\*")
    pub_pass = extrait(r"dont \*\*PASS\*\* : \*\*(\d+)\*\*")
    pub_fail = extrait(r"dont \*\*FAIL\*\* : \*\*(\d+)\*\*")
    pub_proc = extrait(r"\*\*PROCÉDURAL\*\* \| \*\*(\d+)\*\*")
    pub_subst = extrait(r"\*\*SUBSTANTIEL\*\* \| \*\*(\d+)\*\*")
    pub_avant = extrait(r"antérieurs.*?: \*\*(\d+)\*\*")
    pub_apres = extrait(r"postérieurs.*?: \*\*(\d+)\*\*")

    checks = [
        ("population régime", len(regime), pub_regime),
        ("PASS", len(passes), pub_pass),
        ("FAIL", len(fails), pub_fail),
        ("PROCÉDURAL", len(procs), pub_proc),
        ("SUBSTANTIEL", len(subst), pub_subst),
        ("substantiels avant adoption", len(avant_conv), pub_avant),
        ("substantiels après adoption", len(apres_conv), pub_apres),
    ]

    L = []
    A = L.append
    A("# Audit indépendant — #516, nature des PASS post-basculement")
    A("")
    A("Route de calcul différente du backtest : `git log --follow` par")
    A("fichier plutôt que le scan `--diff-filter=A` du dossier entier, pour")
    A("dater l'introduction de chaque script sans réutiliser son code.")
    A("")
    A("## Recalcul vs publié")
    A("")
    A("| Grandeur | Recalculée | Publiée | Accord |")
    A("|---|---|---|---|")
    tout_ok = True
    for nom, calc, pub in checks:
        ok = (pub is not None) and (calc == pub)
        tout_ok = tout_ok and ok
        A(f"| {nom} | {calc} | {pub if pub is not None else 'absent'} | "
          f"**{'OUI' if ok else 'NON'}** |")
    A("")
    coherence1 = (len(procs) + len(subst) == len(passes))
    coherence2 = (len(avant_conv) + len(apres_conv) == len(subst))
    A("## Cohérence interne")
    A("")
    A(f"- PROCÉDURAL + SUBSTANTIEL == PASS : **{'OUI' if coherence1 else 'NON'}** "
      f"({len(procs)}+{len(subst)} vs {len(passes)})")
    A(f"- avant_adoption + après_adoption == SUBSTANTIEL : "
      f"**{'OUI' if coherence2 else 'NON'}** "
      f"({len(avant_conv)}+{len(apres_conv)} vs {len(subst)})")
    A("")
    noms_apres = sorted(r["py"] for r in apres_conv)
    liste = ", ".join(f"`{n}`" for n in noms_apres) if noms_apres else "aucun"
    A(f"- scripts identifiés comme vraie exception (post-adoption) par cette "
      f"route indépendante : **{liste}**")
    A("")
    verdict = "PASS" if (tout_ok and coherence1 and coherence2) else "FAIL"
    A(f"**{verdict}** — tous les nombres publiés par le #516 sont reproduits "
      f"par une route de calcul indépendante." if verdict == "PASS" else
      f"**{verdict}** — désaccord entre la route indépendante et le rapport publié.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    n_ok = sum(1 for _, calc, pub in checks if pub is not None and calc == pub)
    print(f"{verdict} — {n_ok}/{len(checks)} grandeurs reproduites")


if __name__ == "__main__":
    main()
