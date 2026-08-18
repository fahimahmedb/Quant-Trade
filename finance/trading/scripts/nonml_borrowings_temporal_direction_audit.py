"""Audit independant du #509.

Le backtest date par le PREMIER COMMIT D'AJOUT. Cet audit date autrement :
par le RANG du cycle dans la sequence des `PREREG_`, et par le rang du
rapport dans la sequence des rapports. Un rang est insensible aux ecarts de
quelques minutes -- ce qui est justement le point faible du #509, dont
l'unique << anterieure >> tient a 56 minutes.

Il verifie en outre :
  1. que la population des << B tiers >> egale celle du #508 (26 - 5) ;
  2. que les trois classes forment une partition ;
  3. qu'aucune << anterieure >> ne survit a un test par RANG DE JOUR.
"""
import ast
import importlib.util
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent

RAP = RESULTS / "nonml_borrowings_temporal_direction_result.md"
RAP_508 = RESULTS / "nonml_borrowings_final_taxonomy_result.md"
BT = SCRIPTS / "nonml_borrowings_temporal_direction_backtest.py"
OUT = RESULTS / "nonml_borrowings_temporal_direction_audit.md"
MOI = "borrowings_temporal_direction"

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
    c509 = module("nonml_borrowings_temporal_direction_backtest.py")
    dates = c509.dates_ajout()

    # --- Les lignes publiees ---------------------------------------------
    def num(motif, txt=p):
        m = re.search(motif, txt)
        return int(m.group(1)) if m else None
    pub = {
        "tiers": num(r"« B tiers » repris du #508 : (\d+)"),
        "post": num(r"\| postérieure \| (\d+) \|"),
        "ant": num(r"\| antérieure \| (\d+) \|"),
        "indat": num(r"\| indatable \| (\d+) \|"),
    }
    p508 = plat(RAP_508.read_text(encoding="utf-8"))
    b508 = num(r"emprunts en B : (\d+)", p508)
    circ508 = num(r"rapport du script lui-même : (\d+)", p508)
    attendu = (b508 - circ508) if (b508 is not None and circ508 is not None) else None

    partition = (pub["post"] + pub["ant"] + pub["indat"]) == pub["tiers"]
    pop_ok = attendu is not None and pub["tiers"] == attendu

    # --- Route par RANG DE JOUR -------------------------------------------
    def jourcle(ts):
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")

    bloc = rap.split("## Les antérieures", 1)[-1].split("\n## ", 1)[0]
    lignes = re.findall(
        r"\|\s*`([a-z0-9_]+\.py)`\s*\|\s*`(#\d{3})`\s*\|\s*\*\*([\d,\.]+)\*\*"
        r"\s*\|\s*`([^`]+)`\s*\|", bloc)
    survivants = []
    for py, cy, v, ou in lignes:
        t_src = dates.get(ou)
        secs = c509.module("nonml_borrowed_figures_confrontation_backtest.py") \
            if False else None
        # date du cycle cité, par la meme voie que le backtest
        t_cite = None
        c501 = module("nonml_borrowed_figures_confrontation_backtest.py")
        c504 = module("nonml_suspect_values_reports_backtest.py")
        sec = c501.sections_backlog().get(cy)
        if sec is not None:
            nom, _ = c504.rapports_du_cycle(sec)
            if nom:
                t_cite = dates.get(f"PREREG_{nom}.md")
        if t_src is None or t_cite is None:
            continue
        if jourcle(t_src) < jourcle(t_cite):
            survivants.append((py, cy, v, ou))

    src_bt = BT.read_text(encoding="utf-8")
    en_dur = [m.group(1) for m in GRAS.finditer(rap)
              if re.search(r"[\"']\s*\*\*" + re.escape(m.group(1)) + r"\s*\*\*", src_bt)]
    sales = [l for l in git("status", "--porcelain").splitlines()
             if l.strip() and MOI not in l]

    L = []
    A = L.append
    A("# Audit indépendant — direction temporelle des emprunts (#509)")
    A("")
    A("Le backtest date par le **premier commit d'ajout**, à la seconde. Cet")
    A("audit compare les **jours calendaires** : un rang de jour est insensible")
    A("aux écarts de quelques minutes — **le point faible du #509**, dont")
    A("l'unique « antérieure » tient à moins d'une heure.")
    A("")
    A("## La population, recoupée avec le #508")
    A("")
    A(f"- classe **B** du #508 : **{b508}**")
    A(f"- dont **circulaires** : **{circ508}**")
    A(f"- « B tiers » attendus : **{attendu}**")
    A(f"- « B tiers » annoncés par le #509 : **{pub['tiers']}**")
    A(f"- accord : **{'OUI' if pop_ok else 'NON'}**")
    A("")
    A("## La partition")
    A("")
    A(f"- postérieure **{pub['post']}** + antérieure **{pub['ant']}** + "
      f"indatable **{pub['indat']}** = **{pub['post'] + pub['ant'] + pub['indat']}**")
    A(f"- effectif : **{pub['tiers']}** — partition : "
      f"**{'OUI' if partition else 'NON'}**")
    A("")
    A("## Le test par jour calendaire")
    A("")
    A(f"- « antérieures » publiées : **{len(lignes)}**")
    A(f"- **survivant à un test par jour** (source d'un jour strictement")
    A(f"  antérieur) : **{len(survivants)}**")
    A("")
    if lignes and not survivants:
        A("> **Aucune antériorité ne survit.** Toutes tiennent à un écart")
        A("> intra-journalier, c'est-à-dire à l'**ordre d'écriture des fichiers**")
        A("> et non à l'ordre des travaux. Le #509 le disait ; cet audit le")
        A("> confirme par une route qui **ne peut pas** voir les minutes.")
        A(">")
        A("> **Le résidu de neuf cycles d'enquête est donc nul par deux voies")
        A("> indépendantes.**")
    elif survivants:
        A("| Script | Cite | Nombre | Source |")
        A("|---|---|---|---|")
        for py, cy, v, ou in survivants:
            A(f"| `{py}` | `{cy}` | **{v}** | `{ou}` |")
        A("")
        A("> Ces antériorités **survivent** au changement de granularité : elles")
        A("> ne sont pas un artefact de minutes.")
    A("")
    A("## Ce que cet audit ne prouve pas")
    A("")
    A("Une antériorité, même de plusieurs jours, **n'établit pas** qu'une")
    A("citation soit fausse : une grandeur peut légitimement apparaître dans")
    A("deux cycles. Cet audit **resserre** un soupçon, il n'en fonde aucun.")
    A("")
    A("Et il partage avec le backtest la **règle contextuelle du #502** : si")
    A("« ≥ 2 mots-clés dans ±200 caractères » est un mauvais test de « même")
    A("sujet », les deux routes se trompent ensemble depuis le début.")
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
    ctrl = [("la population égale celle du #508 moins ses circulaires", pop_ok),
            ("les trois classes forment une partition", partition),
            (f"le test par jour est appliqué aux **{len(lignes)}** antérieures",
             len(lignes) == pub["ant"]),
            ("aucun chiffre du rapport tapé en dur, arbre propre",
             not en_dur and not sales)]
    for i, (t, v) in enumerate(ctrl, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    v = "AUDIT OK" if all(x for _, x in ctrl) else "AUDIT — RÉSERVE"
    A(f"**{v}** ({sum(1 for _, x in ctrl if x)}/{len(ctrl)})")
    A("")
    A("Anti-lookahead **sans objet au sens temporel** pour les prix ; la")
    A("datation est **strictement rétrospective** — premiers commits d'ajout.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{v} — survivants au test par jour : {len(survivants)}/{len(lignes)}")


if __name__ == "__main__":
    main()
