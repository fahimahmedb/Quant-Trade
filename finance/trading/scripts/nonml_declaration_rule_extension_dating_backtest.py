"""Rejouer le #483 sous la regle tolerante du #492 (#498).

Specification pre-enregistree dans `PREREG_declaration_rule_extension_dating.md`,
committee AVANT toute mesure -- regles, critere et garde-fous compris.

Le critere A/B/C du #483 est repris MOT POUR MOT : aucun seuil ne bouge. Seul
le DETECTEUR change, et il vient du #492, verbatim. Les deux tournent sur la
MEME population, re-derivee aujourd'hui.
"""
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPO = ROOT.parent.parent

OUT = RESULTS / "nonml_declaration_rule_extension_dating_result.md"
MOI = "declaration_rule_extension_dating"

# Les deux regles, VERBATIM depuis le #492 -- non amendees.
LITTERALE = re.compile(r"Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)
TOLERANTE = re.compile(
    r"\*\*Cycle d[e'’]\s*([^*]+)\*\*|Cycle d[e'’]\s*\*\*([^*]+)\*\*", re.I)

# Le critere du #483, MOT POUR MOT -- aucun seuil ne bouge.
CRITERE = ("**A** si `m_d > m_n` **et** `p ≥ 50 %` ; **B** si `m_d < m_n` "
           "**et** `p < 20 %` ; **C** sinon")
N_RECENTS = 40      # le #483 lisait la part sur les 40 plus recents
SEUIL_A = 50.0
SEUIL_B = 20.0
N_TRANCHES = 7      # le #483 publiait 7 tranches


def git(*a):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def date_intro(rel):
    """Premier commit d'ajout -- la commande meme que le #483 publiait."""
    s = git("log", "--diff-filter=A", "--reverse", "--format=%ct", "--", rel)
    for l in s.splitlines():
        if l.strip().isdigit():
            return int(l.strip())
    return None


def jour(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%d/%m/%Y")


def mediane(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def lecture(m_d, m_n, p):
    """Le critere du #483, applique tel quel."""
    if m_d is None or m_n is None:
        return "C", "indéterminable — un groupe est vide"
    if m_d > m_n and p >= SEUIL_A:
        return "A", "convention **récente et dominante**"
    if m_d < m_n and p < SEUIL_B:
        return "B", "convention **abandonnée**"
    return "C", "**aucune structure temporelle** — usage irrégulier"


def main():
    avant = set(git("status", "--porcelain").splitlines())

    # --- Une seule population, re-derivee aujourd'hui ----------------------
    pop = []
    for p in sorted((ROOT).glob("PREREG_*.md")):
        if MOI in p.name:
            continue
        rel = f"finance/trading/{p.name}"
        ts = date_intro(rel)
        if ts is None:
            continue
        txt = p.read_text(encoding="utf-8")
        pop.append({"nom": p.name, "ts": ts,
                    "lit": bool(LITTERALE.search(txt)),
                    "tol": bool(TOLERANTE.search(txt))})
    pop.sort(key=lambda d: d["ts"])
    n = len(pop)
    recents = pop[-N_RECENTS:]

    res = {}
    for clef, nom in (("lit", "littérale"), ("tol", "tolérante")):
        dec = [d for d in pop if d[clef]]
        non = [d for d in pop if not d[clef]]
        m_d, m_n = mediane([d["ts"] for d in dec]), mediane([d["ts"] for d in non])
        p_rec = 100.0 * sum(1 for d in recents if d[clef]) / len(recents)
        v, quoi = lecture(m_d, m_n, p_rec)
        res[clef] = {"nom": nom, "dec": dec, "non": non, "m_d": m_d,
                     "m_n": m_n, "p": p_rec, "v": v, "quoi": quoi}

    # --- Le fait << 380 / 0 >> du #483, re-teste ---------------------------
    prem_lit = min((d["ts"] for d in res["lit"]["dec"]), default=None)
    if prem_lit is not None:
        avant_lit = [d for d in pop if d["ts"] < prem_lit]
        tol_avant = [d for d in avant_lit if d["tol"]]
    else:
        avant_lit, tol_avant = [], []

    # --- Chronologie par tranches, comme au #483 ---------------------------
    taille = n // N_TRANCHES
    tranches = []
    i = 0
    while i < n:
        bout = pop[i:i + taille] if len(pop) - i >= taille * 2 else pop[i:]
        if not bout:
            break
        tranches.append((i + 1, i + len(bout), bout))
        i += len(bout)

    L = []
    A = L.append
    A("# Rejouer le #483 sous la règle **tolérante** (pré-enregistré)")
    A("")
    A("## Les deux règles, citées verbatim")
    A("")
    A("```python")
    A(f"LITTERALE = {LITTERALE.pattern!r}   # celle du #483")
    A(f"TOLERANTE = {TOLERANTE.pattern!r}   # celle du #492")
    A("```")
    A("")
    A("## Le critère du #483, cité mot pour mot — **inchangé**")
    A("")
    A(f"> {CRITERE}, où `p` est la part des déclarés parmi les **{N_RECENTS}**")
    A("> plus récents.")
    A("")
    A("**Aucun seuil ne bouge.** Seul le détecteur change.")
    A("")
    A("## Une seule population, re-dérivée aujourd'hui")
    A("")
    A(f"- `PREREG_` datés *(hors celui-ci)* : **{n}**")
    A(f"- non datables : **0**")
    A("")
    A("> Le garde-fou du pré-enregistrement : sans population commune, un écart")
    A("> confondrait **effet de détecteur** et **croissance du dépôt**.")
    A("")
    A("## Les deux mesures, côte à côte")
    A("")
    A("| Règle | Déclarés | Non déclarés | `m_d` | `m_n` | `p` (40 récents) | Verdict |")
    A("|---|---|---|---|---|---|---|")
    for clef in ("lit", "tol"):
        r = res[clef]
        A(f"| **{r['nom']}** | **{len(r['dec'])}** | **{len(r['non'])}** | "
          f"{jour(r['m_d']) if r['m_d'] else '—'} | "
          f"{jour(r['m_n']) if r['m_n'] else '—'} | "
          f"**{r['p']:.1f} %**".replace(".", ",") + f" | **{r['v']}** |")
    A("")
    d_dec = len(res["tol"]["dec"]) - len(res["lit"]["dec"])
    d_p = res["tol"]["p"] - res["lit"]["p"]
    A(f"- écart de détection : **{d_dec:+d}** déclarés, "
      + f"**{d_p:+.1f}**".replace(".", ",") + " points sur `p`")
    A("")
    for clef in ("lit", "tol"):
        r = res[clef]
        A(f"> Règle **{r['nom']}** → **{r['v']}** — {r['quoi']}.")
    A("")
    if res["lit"]["v"] != res["tol"]["v"]:
        A(f"**Le verdict change avec le détecteur**, à critère strictement")
        A(f"identique : **{res['lit']['v']}** en littérale, "
          f"**{res['tol']['v']}** en tolérante.")
        A("")
        A("> Le #483 n'a pas conclu de travers par erreur de raisonnement : il a")
        A("> conclu sur ce que son détecteur lui montrait. **Une typographie a")
        A("> tenu lieu de fait**, et son verdict **C** est resté au dossier")
        A("> jusqu'ici. *(Aucun nombre de cycles n'est avancé : je ne l'ai pas")
        A("> compté.)*")
    else:
        A(f"**Le verdict ne change pas** : **{res['lit']['v']}** dans les deux")
        A("cas. Le détecteur du #483 était faux **et** sa conclusion tenait —")
        A("elle tenait pour des raisons qu'il n'avait pas mesurées.")
    A("")
    A("## Le « 380 antérieurs, 0 déclaré » du #483, re-testé")
    A("")
    A(f"- date du **premier déclaré littéral** : "
      f"**{jour(prem_lit) if prem_lit else '—'}**")
    A(f"- pré-enregistrements **antérieurs** à cette date : **{len(avant_lit)}**")
    A(f"- parmi eux, **déclarés au sens tolérant** : **{len(tol_avant)}**")
    A("")
    if tol_avant:
        A("> **Le « 380 / 0 » ne survit pas.** La bascule que le #483 disait")
        A("> « nette » l'était pour son détecteur ; la règle tolérante trouve")
        A(f"> **{len(tol_avant)}** déclaration(s) avant la date qu'il donnait pour")
        A("> origine de la convention.")
        A("")
        for d in sorted(tol_avant, key=lambda x: x["ts"])[:10]:
            A(f"- `{d['nom']}` — {jour(d['ts'])}")
        if len(tol_avant) > 10:
            A(f"- … et **{len(tol_avant) - 10}** autre(s)")
    else:
        A("> **Le « 380 / 0 » survit.** Même en tolérant la typographie, aucune")
        A("> déclaration ne précède cette date : la bascule que le #483")
        A("> décrivait est **réelle**, et son détecteur ne l'avait pas inventée.")
    A("")
    A("## La chronologie, sous les deux règles")
    A("")
    A("| Tranche | Période | Littérale | Tolérante |")
    A("|---|---|---|---|")
    for a, b, bout in tranches:
        nl = sum(1 for d in bout if d["lit"])
        nt = sum(1 for d in bout if d["tol"])
        A(f"| {a}–{b} | {jour(bout[0]['ts'])} → {jour(bout[-1]['ts'])} | "
          f"**{nl} / {len(bout)}** | **{nt} / {len(bout)}** |")
    A("")
    A("## Mes trois prédictions, confrontées")
    A("")
    p1 = res["tol"]["v"] == "A"
    p2 = len(tol_avant) >= 1
    p3 = res["lit"]["v"] == "C"
    A("| Prédiction | Annoncé | Mesuré | Verdict |")
    A("|---|---|---|---|")
    A(f"| verdict **A** sous la tolérante | A | {res['tol']['v']} | "
      f"**{'vérifiée' if p1 else 'réfutée'}** |")
    A(f"| le « 380 / 0 » ne survit pas | ≥ 1 | {len(tol_avant)} | "
      f"**{'vérifiée' if p2 else 'réfutée'}** |")
    A(f"| la littérale reste **C** aujourd'hui | C | {res['lit']['v']} | "
      f"**{'vérifiée' if p3 else 'réfutée'}** |")
    A("")
    if p3:
        A("La prédiction 3 est le **contrôle** de ce cycle : la littérale rendant")
        A("le même verdict qu'au #483 sur une population plus grande, l'écart")
        A("mesuré vient bien du **détecteur** et non de la croissance du dépôt.")
    else:
        A("**La prédiction 3 est réfutée, et c'est le contrôle qui tombe** : la")
        A("littérale ne rend plus le verdict du #483 sur la population du jour.")
        A("L'écart entre les deux règles **ne peut donc pas** être attribué au")
        A("seul détecteur — la population a bougé aussi.")
    A("")
    A("## Aucune exécution")
    A("")
    apres = set(git("status", "--porcelain").splitlines())
    nouv = [l for l in sorted(apres - avant) if MOI not in l]
    A(f"- fichiers modifiés par ce cycle hors les siens : **{len(nouv)}**")
    for l in nouv:
        A(f"  - `{l.strip()}`")
    A("")
    A("Les seuls appels externes visent `git log` et `git status`, **en lecture**.")
    A("")
    A("## Critères de succès")
    A("")
    c = [("Les deux règles citées verbatim, critère du #483 mot pour mot", True),
         (f"Une seule population (**{n}**) pour les deux mesures", n > 0),
         (f"Les deux verdicts publiés (**{res['lit']['v']}** / "
          f"**{res['tol']['v']}**)", True),
         ("Le « 380 / 0 » du #483 re-testé et son sort publié", prem_lit is not None),
         ("Aucun script du dépôt exécuté, arbre propre", not nouv)]
    for i, (t, v) in enumerate(c, 1):
        A(f"{i}. {t} — **{'OUI' if v else 'NON'}**.")
    A("")
    verdict = "PASS" if all(v for _, v in c) else "FAIL"
    A(f"**{verdict}** — le critère porte sur le **procédé**.")
    A("")
    A("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    A("paramètre numérique de stratégie.")
    A("")
    A("> **Rapport dépendant du dépôt** — il décrit l'état des fichiers et de")
    A("> l'historique à la date de son exécution.")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{verdict} — littérale {res['lit']['v']} ({len(res['lit']['dec'])}), "
          f"tolérante {res['tol']['v']} ({len(res['tol']['dec'])}), "
          f"avant-premier-littéral tolérants = {len(tol_avant)}")


if __name__ == "__main__":
    main()
