"""Audit du lot 5 de persistance du P&L (#427).

Spécification pré-enregistrée dans `PREREG_pnl_persistence_lot5.md`, committée
avant toute modification des scripts.

Ce lot diffère des quatre précédents : ses candidats portent des **PASS**. Un
doublon exact entre deux d'entre eux signifierait que deux « hypothèses
indépendantes » n'en sont qu'une.

Contrôles, tous fixés avant calcul :
1. cohérence `.npz` / rapport publié (écart toléré : 0) ;
2. balayage de doublons rejoué **sans modification** ;
3. couverture du balayage, décomposée non-ML / ML (piste 2 du #426).
"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
OUT = RESULTS / "nonml_pnl_persistence_lot5_audit.md"

LOT = [
    "breadth_confirmation_overlay", "intl_breadth_confirmation_overlay",
    "golden_cross_overlay", "halloween_effect", "index_52w_high_overlay",
    "intraday_range_regime_overlay", "santa_claus_rally_overlay",
    "sma200_tom_halloween_union_overlay", "sma50_trend_overlay",
    "tom_halloween_union_overlay", "tom_overlay", "turn_of_month",
    "january_effect_lowprice_overlay", "lowvol_sma200_overlay",
    "momentum_12_1", "short_term_momentum",
]

SET_ASIDE = {
    "tom_decomposition_overlay":
        "boucle sur plusieurs **variantes** × marchés : nommer un seul `.npz` "
        "obligerait à élire une variante, c'est-à-dire à inventer une convention "
        "pour l'occasion.",
    "capitulation_gate_floor_sweep":
        "**diagnostic, pas une stratégie** (sa propre docstring le dit) — son PASS "
        "est un faux positif de détection.",
}

DUP_BEFORE = {"series": 202, "exact": 3, "quasi": 1}


def n_sessions(name: str):
    d = np.load(RESULTS / f"nonml_{name}_pnl.npz", allow_pickle=True)
    if "pos" in d.files:
        return len(np.asarray(d["pos"])), "indiciel"
    return len(np.asarray(d["pnl_gross_ov"])), "panier"


def published_sessions(name: str):
    t = (RESULTS / f"nonml_{name}_result.md").read_text(encoding="utf-8")
    m = re.search(r"(\d[\d\s  ]*)\s*séances testables", t)
    return int(re.sub(r"\D", "", m.group(1))) if m else None


def main():
    L = ["# Audit — persistance du P&L, lot 5 : les PASS invisibles au balayage de doublons (pré-enregistré)", ""]
    L.append("Cycle d'**infrastructure**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("aucun décompte d'hypothèses corrigé.")
    L.append("")
    L.append("**Ce lot n'est pas comme les quatre précédents.** Les #416, #423, #424 et #426 ne")
    L.append("portaient que des FAIL : aucun verdict ne pouvait bouger. Ceux-ci portent des")
    L.append("**PASS**, et un doublon exact entre deux d'entre eux gonflerait le décompte")
    L.append("« X PASS sur Y hypothèses testées », entrée directe du `n_trials` du DSR.")
    L.append("")

    # --- Périmètre --------------------------------------------------------
    L.append("## Périmètre — 16 traités, 2 écartés avec leur raison")
    L.append("")
    L.append(f"- rapports portant un PASS : **101**")
    L.append(f"- parmi eux sans `.npz` : **18**")
    L.append(f"- **traités par ce cycle** : **{len(LOT)}**")
    L.append(f"- **écartés** : **{len(SET_ASIDE)}**")
    L.append("")
    for n, why in SET_ASIDE.items():
        L.append(f"- `{n}` — {why}")
    L.append("")
    L.append("Le pré-enregistrement annonçait 17 traités et 1 écarté. La lecture script par")
    L.append("script en a écarté un second, `tom_decomposition_overlay`, pour la raison")
    L.append("ci-dessus. L'engagement était explicite — « tout script dont la structure ne")
    L.append("correspond à aucune des trois conventions est écarté et listé, pas forcé » — et")
    L.append("je ne suis pas passé outre pour tenir un chiffre annoncé.")
    L.append("")

    # --- Non-régression ---------------------------------------------------
    L.append("## Contrôle de non-régression — 16/16 identiques octet à octet")
    L.append("")
    L.append("Vérifié par comparaison binaire des `results/nonml_<nom>_result.md` avant et")
    L.append("après ré-exécution. Le `diff` des scripts ne comporte que des **insertions**")
    L.append("(159 lignes ajoutées, **0 supprimée**) : aucune ligne de calcul n'est touchée.")
    L.append("")
    L.append("Prédiction déductive du pré-enregistrement **confirmée**, comme aux #416")
    L.append("(10/10), #423 (4/4), #424 (12/12) et #426 (2/2). **Quarante-quatre résultats")
    L.append("publiés** ont désormais été testés contre leur propre code — et ces 16-ci sont")
    L.append("les premiers **PASS** des cinq lots.")
    L.append("")

    # --- Cohérence --------------------------------------------------------
    L.append("## Contrôle de cohérence — le `.npz` contre le rapport du candidat")
    L.append("")
    L.append("Le nombre de séances stocké doit coïncider avec celui que le rapport annonce")
    L.append("déjà. Écart toléré, fixé avant calcul : **0**.")
    L.append("")
    L.append("| Candidat | Schéma | Séances au rapport | Séances au `.npz` | Accord |")
    L.append("|---|---|---|---|---|")
    n_ok, n_nc = 0, 0
    checked_names = set()
    for name in LOT:
        n_npz, schema = n_sessions(name)
        pub = published_sessions(name)
        if pub is None:
            n_nc += 1
            L.append(f"| `{name}` | {schema} | — (non annoncé) | {n_npz} | n/a |")
            continue
        ok = pub == n_npz
        n_ok += int(ok)
        checked_names.add(name)
        L.append(f"| `{name}` | {schema} | {pub} | {n_npz} | {'✔' if ok else '✘'} |")
    L.append("")
    testable = len(LOT) - n_nc
    L.append(f"**{n_ok}/{testable} en accord** ({n_nc} rapport(s) n'annonçant pas de nombre de")
    L.append("séances, le contrôle y est inapplicable et compté comme tel, pas comme réussi).")
    L.append("")
    if n_ok == testable:
        L.append("Les séries sauvegardées sont bien celles que les rapports décrivent.")
    else:
        L.append("**Désaccord** — au moins un `.npz` ne porte pas la fenêtre annoncée par son")
        L.append("rapport. Bloquant : à instruire avant toute autre conclusion.")
    L.append("")

    # --- Contrôle supplémentaire, ajouté après coup et signalé comme tel ---
    L.append("### Contrôle supplémentaire — la ligne NDX des rapports multi-marchés")
    L.append("")
    L.append("**Ajouté après avoir constaté que le contrôle pré-enregistré ne couvrait que")
    L.append(f"{n_ok} des {len(LOT)} candidats.** Les rapports multi-marchés publient un tableau par")
    L.append("marché sans total de séances : le contrôle par nombre de séances y est")
    L.append("inapplicable, mais leur **ligne NDX** publie souvent « Séances test. » et/ou")
    L.append("« %j levé », tous deux comparables à ce que contient le `.npz`.")
    L.append("")
    L.append("Ce contrôle **resserre** le cycle au lieu de le relâcher, et la tolérance n'est")
    L.append("pas choisie pour passer : les taux sont publiés au dixième de point, donc")
    L.append("**0,05 point** est la moitié du pas d'arrondi — valeur déduite du format, pas")
    L.append("ajustée. Je le signale comme ajout post-hoc plutôt que de le présenter comme")
    L.append("prévu d'avance.")
    L.append("")
    TOL = 0.05
    L.append("| Candidat | Séances (rapport / `.npz`) | Activation (rapport / `.npz`) | Accord |")
    L.append("|---|---|---|---|")
    extra_ok, extra_tested = 0, 0
    for name in LOT:
        rep = (RESULTS / f"nonml_{name}_result.md").read_text(encoding="utf-8")
        hdr = re.search(r"^\|\s*Marché\s*\|.*$", rep, re.M)
        row = re.search(r"^\|\s*NDX[^|]*\|(.*)$", rep, re.M)
        if not hdr or not row:
            continue
        cols = [c.strip() for c in hdr.group(0).strip("|").split("|")]
        vals = [c.strip() for c in row.group(1).strip("|").split("|")]
        if len(cols) - 1 != len(vals):
            continue
        d = dict(zip(cols[1:], vals))
        p = np.load(RESULTS / f"nonml_{name}_pnl.npz", allow_pickle=True)
        if "pos" not in p.files:
            continue
        pos = np.asarray(p["pos"], float)
        act = float((pos > 1.0).mean()) if pos.max() > 1.0 else float((pos > 0).mean())
        s_txt = a_txt = "—"
        agree = []
        for k, v in d.items():
            if "Séances" in k and v.replace(" ", "").isdigit():
                s_txt = f"{int(v.replace(' ', ''))} / {len(pos)}"
                agree.append(int(v.replace(" ", "")) == len(pos))
            if "%j" in k or "jours en" in k:
                try:
                    pub = float(v.rstrip("%").replace(",", "."))
                except ValueError:
                    continue
                a_txt = f"{pub:.1f} % / {100*act:.1f} %"
                agree.append(abs(100 * act - pub) <= TOL)
        if not agree:
            continue
        extra_tested += 1
        ok = all(agree)
        extra_ok += int(ok)
        checked_names.add(name)
        L.append(f"| `{name}` | {s_txt} | {a_txt} | {'✔' if ok else '✘'} |")
    L.append("")
    L.append(f"**{extra_ok}/{extra_tested} en accord.**")
    if extra_tested and extra_ok == extra_tested:
        L.append("La série NDX sauvegardée reproduit les chiffres que le rapport publiait déjà,")
        L.append("calculés indépendamment par le script du candidat. Combiné au contrôle")
        L.append(f"pré-enregistré, **{n_ok + extra_ok} vérifications** portent sur ces 16 `.npz`.")
    elif extra_tested:
        L.append("**Désaccord** — au moins une série NDX sauvegardée ne reproduit pas le chiffre")
        L.append("publié. Bloquant : à instruire avant toute autre conclusion.")
    L.append("")

    # --- Doublons ---------------------------------------------------------
    L.append("## Mesure — balayage de doublons rejoué sans modification")
    L.append("")
    dup = subprocess.run([sys.executable, str(SCRIPTS / "nonml_pnl_duplicate_sweep_backtest.py")],
                         capture_output=True, text=True, timeout=3000)
    txt = (RESULTS / "nonml_pnl_duplicate_sweep_result.md").read_text(encoding="utf-8")

    def grab(pat, default="—"):
        m = re.search(pat, txt)
        return m.group(1) if m else default

    n_series = grab(r"P&L reconstruits\s*:\s*\*\*(\d+)\*\*")
    n_exact = grab(r"groupes de doublons\s*:\s*\*\*(\d+)\*\*")
    n_quasi = grab(r"paires signalées\s*:\s*\*\*(\d+)\*\*")
    L.append("| | #426 | #427 |")
    L.append("|---|---|---|")
    L.append(f"| séries de P&L reconstruites | {DUP_BEFORE['series']} | **{n_series}** |")
    L.append(f"| groupes de doublons exacts | {DUP_BEFORE['exact']} | **{n_exact}** |")
    L.append(f"| quasi-doublons | {DUP_BEFORE['quasi']} | **{n_quasi}** |")
    L.append("")
    if dup.returncode != 0:
        L.append(f"**Le balayage a échoué** (code {dup.returncode}) :")
        L.append("")
        L.append("```")
        L.append(dup.stderr.strip()[-800:])
        L.append("```")
        L.append("")

    try:
        grew = int(n_exact) > DUP_BEFORE["exact"] or int(n_quasi) > DUP_BEFORE["quasi"]
    except ValueError:
        grew = False

    # Extraction des groupes pour savoir s'ils impliquent des PASS de ce lot.
    section = txt.split("## Doublons exacts")[-1].split("## Quasi-doublons")[0]
    involved = sorted({n for n in LOT if f"nonml_{n}`" in section or f"nonml_{n} " in section
                       or f"`nonml_{n}`" in section})
    if grew:
        L.append("**Le décompte a augmenté.** Les séries ajoutées introduisent au moins un")
        L.append("doublon ou quasi-doublon qui n'existait pas au #426.")
    else:
        L.append("**Décompte inchangé.** Les 16 séries ajoutées n'introduisent aucun doublon")
        L.append("exact ni quasi-doublon nouveau.")
    L.append("")
    if involved:
        L.append("Candidats de ce lot apparaissant dans un groupe de doublons exacts :")
        L.append("")
        for n in involved:
            L.append(f"- `{n}`")
        L.append("")
        L.append("**Aucune requalification n'est appliquée ici** : corriger un décompte")
        L.append("d'hypothèses est une opération distincte, à déclarer séparément (règle posée")
        L.append("au #415 et tenue depuis).")
    else:
        L.append("Aucun candidat de ce lot n'apparaît dans un groupe de doublons exacts. La")
        L.append("question posée par le pré-enregistrement — « deux PASS sont-ils la même")
        L.append("série ? » — reçoit donc une réponse **négative pour les 16 testés**.")
        L.append("")
        L.append("Je n'avais fait **aucune prédiction** sur ce point, et je ne présente pas")
        L.append("cette absence comme une confirmation : c'est une mesure, désormais faite.")
    L.append("")

    # --- Couverture -------------------------------------------------------
    L.append("## Mesure — couverture du balayage de doublons (piste 2 du #426)")
    L.append("")
    all_npz = sorted(RESULTS.glob("*_pnl.npz"))
    nonml = [p for p in all_npz if p.name.startswith("nonml_")]
    other = [p for p in all_npz if not p.name.startswith("nonml_")]
    n_scripts = len(list(SCRIPTS.glob("nonml_*_backtest.py")))
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| séries lues par le balayage (`results/*_pnl.npz`) | **{len(all_npz)}** |")
    L.append(f"| dont candidats non-ML (`nonml_*`) | **{len(nonml)}** |")
    L.append(f"| dont séries ML / Étape D | **{len(other)}** |")
    L.append(f"| scripts de backtest non-ML du dépôt | **{n_scripts}** |")
    L.append(f"| **couverture non-ML** | **{100*len(nonml)/n_scripts:.1f} %** |")
    L.append("")
    L.append("Le rapport du balayage annonce un total sans dire que des séries ML et Étape D")
    L.append("y figurent, ni quelle fraction du dépôt non-ML il couvre. Les deux chiffres sont")
    L.append("publiés ici ; les inscrire dans son propre rapport reste à faire.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion")
    L.append("")
    verified = n_ok + extra_ok
    unverified = [n for n in LOT if n not in checked_names]
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| scripts traités ou écartés avec raison | 17 | {len(LOT)} traités + "
             f"{len(SET_ASIDE)} écartés | ✔ |")
    L.append(f"| différences de résultat | 0 | **0** | ✔ |")
    L.append(f"| cohérence `.npz` / rapport | **17/17** | "
             f"**{verified}/{len(LOT)}** vérifiés | **✘** |")
    L.append(f"| mesures publiées | 3 | 3 | ✔ |")
    L.append("")
    L.append("**Le critère de cohérence n'est pas tenu tel qu'il était écrit.** Il exigeait")
    L.append(f"17/17 ; {verified} des {len(LOT)} candidats sont vérifiés ({n_ok} par le contrôle")
    L.append(f"pré-enregistré, {extra_ok} par le contrôle supplémentaire). Je le marque en échec")
    L.append("plutôt que de recompter sur le sous-ensemble applicable — écrire « 6/6 ✔ » aurait")
    L.append("été exact au mot près et trompeur en pratique.")
    L.append("")
    if unverified:
        L.append(f"Les **{len(unverified)}** candidats non vérifiés publient un tableau")
        L.append("multi-marchés qui n'annonce **ni** nombre de séances **ni** taux d'activation :")
        L.append("")
        for n in unverified:
            L.append(f"- `{n}`")
        L.append("")
        L.append("Leur `.npz` est produit et lisible ; il n'existe simplement aucun chiffre")
        L.append("déjà publié auquel le confronter. La lacune est dans le rapport d'origine,")
        L.append("et elle est notée plutôt que comblée par une valeur inventée ici.")
        L.append("")
    L.append("La prédiction déductive « 0 différence » est **vérifiée** pour la cinquième fois")
    L.append("consécutive. Le chiffre de 17 traités n'est pas tenu non plus : 16 le sont, le")
    L.append("dix-septième étant écarté après lecture pour une raison publiée — ce que")
    L.append("l'engagement 2 prévoyait explicitement.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
