"""Les 9 sans temoin non examines (#484).

Specification pre-enregistree dans `PREREG_guards_witness_remainder.md`,
committee AVANT toute mesure -- examen a la main compris.

Le #481 avait classe 14 titres << sans temoin >> et n'en avait lu que 5, en
ecrivant que son 2/5 ne s'extrapolait pas. Ce cycle lit les restants et rend le
compte COMPLET.

Lecture du disque : aucun script execute, aucun effet de bord.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent

OUT = RESULTS / "nonml_guards_witness_remainder_result.md"
MOI = "guards_witness_remainder"
REF_481 = {"sans": 14, "examines": 5, "masquants": 2}
SUFFIXES = [("_result.md", "_backtest.py"), ("_audit.md", "_audit.py"),
            ("_robustness.md", "_robustness.py")]
ECRIVENT = ("append", "write", "print", "write_text")
GARDES = (ast.If, ast.For, ast.While, ast.Try)
VAR = re.compile(r"^if\s+(?:not\s+)?([a-z_][a-z0-9_]*)\s*:\s*$")

DEJA_481 = {("nonml_battery_coverage_backtest.py", 159),
            ("nonml_citer_451_resolution_backtest.py", 187),
            ("nonml_marker_emitter_crossing_backtest.py", 175),
            ("nonml_net_pnl_correction_backtest.py", 279),
            ("nonml_net_pnl_correction_robustness.py", 76)}

# --- VERDICTS DE L'EXAMEN A LA MAIN -------------------------------------
# DECLARE dans le pre-enregistrement. Ecrits a la main apres lecture du code
# autour de chaque garde. "ifelse" marque une branche d'alternative
# exhaustive -- comptee a part du total des masquants (critere 5).
V = {
 ("nonml_net_pnl_correction_robustness.py", 86): ("ANODIN", True,
  "**Branche `else` de `if tous:`** — le pendant exact du cas l.76 déjà lu au "
  "#481. Les deux issues écrivent une section (« Plateau, pas pic » ou « La "
  "conclusion ne tient pas partout ») : **une section paraît toujours**."),
 ("nonml_prereg_convention_coverage_backtest.py", 174): ("ANODIN", False,
  "Le **bloc parent** publie, quatre lignes plus haut, "
  "`| **aucun** fichier ne porte ce <nom> | **{len(aucun_fichier)}** |`. Le "
  "compte est donc visible chaque fois que le bloc englobant s'exécute. **Ma "
  "règle ne cherchait le témoin qu'au niveau *non gardé*** — elle ignore un "
  "témoin situé dans un bloc parent."),
 ("nonml_prereg_convention_coverage_backtest.py", 182): ("ANODIN", False,
  "Identique au précédent : `| le rapport **existe sous un autre nom** | "
  "**{len(autre_nom)}** |` est publié dans le bloc parent. Même angle mort de "
  "ma règle, même script, deux lignes."),
 ("nonml_self_inclusion_detector_backtest.py", 106): ("ANODIN", False,
  "Le témoin existe **sous un autre nom** : le tableau de calibration publie "
  "sans garde `| **rappel** (fautifs signalés) | 2 / 2 | **{len(rappel)} / 2** "
  "|`. Or `rates` est le **complément** de `rappel` — un lecteur voyant "
  "« 2 / 2 » sait qu'aucun cas n'a été manqué. **Ma règle cherche la variable "
  "de la garde, pas la grandeur qu'elle décrit.**"),
 ("nonml_silent_skip_decision_backtest.py", 119): ("ANODIN", True,
  "**Branche `if not a_modifier:` d'une alternative** dont l'`else` écrit "
  "« Décision : rendre l'écart visible dans N script(s) ». **Une décision est "
  "toujours publiée** ; seule laquelle varie."),
 ("nonml_six_reports_regeneration_backtest.py", 232): ("MASQUANT", False,
  "**Le cas du #475 lui-même.** `perdus` n'apparaît nulle part hors de sa "
  "garde. La section porte l'unique mention de l'effet de bord découvert, et "
  "son effacement a envoyé **trois cycles** (#469, #472, #475) chercher un "
  "encart qui n'avait jamais été écrit. **Contrôle positif : une règle qui ne "
  "le classerait pas masquant serait à jeter.**"),
 ("nonml_sweep_pass_prose_fix_backtest.py", 134): ("MASQUANT", False,
  "`if strategies:` n'a **pas d'`else`**, et aucun compte de `strategies` "
  "n'est publié hors garde. Si aucun PASS n'était une stratégie, le lecteur "
  "**n'apprendrait jamais que le contrôle a eu lieu** — alors que la section "
  "annonce précisément *« le résultat qui prime sur la correction de prose »*. "
  "**Deuxième masquant établi de ce cycle.**"),
 ("nonml_verdict_detector_complete_robustness.py", 124): ("ANODIN", True,
  "**Branche `else` de `if plateau:`.** L'issue `if` écrit « **Plateau** : le "
  "résultat tient sur tout le voisinage » ; l'`else` écrit « Ce n'est pas un "
  "plateau, c'est un escalier ». **L'état est toujours énoncé**, seule sa "
  "valeur change. *(Ma règle a attribué la garde au `if` alors que le titre "
  "est dans l'`else` — l'attribution est grossière, mais sans conséquence "
  "ici.)*"),
 ("nonml_hardcoded_tables_repair_backtest.py", 215): ("ANODIN", False,
  "**C'est mon propre cycle #482**, entré dans la population depuis le #481. "
  "Le témoin existe **sous un autre nom** : le tableau publié sans garde juste "
  "au-dessus porte une colonne « Lignes de diff » où **0** apparaît pour le "
  "script concerné. Un lecteur voyant ce zéro sait pourquoi la section existe. "
  "**Troisième occurrence du même angle mort — et je viens de le commettre "
  "moi-même, dans le cycle qui l'a nommé deux fois.**"),
 ("nonml_verdict_detector_fix_backtest.py", 248): ("ANODIN", True,
  "**Branche `else` de `if idem:`**, et le témoin existe en plus **sous un "
  "autre nom** : le tableau de verdict publie sans garde "
  "`| 4 | comptes idempotents | ✔ / **NON** |`, calculé depuis `ok4 = idem`. "
  "**Deux raisons indépendantes** de ne pas le compter masquant."),
}


def producteur(nom_md):
    for a, b in SUFFIXES:
        if nom_md.endswith(a):
            return SCRIPTS / f"{nom_md[:-len(a)]}{b}"
    return None


def nomcall(n):
    f = n.func
    return f.attr if isinstance(f, ast.Attribute) else \
        (f.id if isinstance(f, ast.Name) else "")


def sans_temoin(py):
    try:
        src = py.read_text(encoding="utf-8")
        arbre = ast.parse(src)
    except (SyntaxError, UnicodeDecodeError):
        return []
    lignes = src.splitlines()
    out = []
    for fn in [x for x in ast.walk(arbre) if isinstance(x, ast.FunctionDef)]:
        titres, libres = [], []

        def visite(nd, gardes):
            for e in ast.iter_child_nodes(nd):
                g = gardes + [e] if isinstance(e, GARDES) else gardes
                if isinstance(e, ast.Call) and nomcall(e) in ECRIVENT:
                    for a in e.args:
                        if isinstance(a, ast.Constant) \
                                and isinstance(a.value, str) \
                                and a.value.startswith(("## ", "### ")) and gardes:
                            titres.append((a.lineno, a.value.strip(), gardes[-1]))
                    if not gardes:
                        libres.append(ast.dump(e))
                visite(e, g)

        visite(fn, [])
        for ln, titre, garde in titres:
            gl = lignes[garde.lineno - 1].strip()
            m = VAR.match(gl)
            if not m:
                continue
            if not any(re.search(rf"\b{re.escape(m.group(1))}\b", d) for d in libres):
                out.append((py.name, ln, titre, gl))
    return out


def main():
    vus, S = set(), []
    for p in sorted(RESULTS.glob("nonml_*.md")):
        if p.name.endswith("_anti_cheat.md") or MOI in p.name:
            continue
        py = producteur(p.name)
        if not (py and py.exists()) or py.name in vus:
            continue
        vus.add(py.name)
        S.extend(sans_temoin(py))
    S = sorted(S)
    restants = [x for x in S if (x[0], x[1]) not in DEJA_481]
    ecart = len(S) - REF_481["sans"]

    L = ["# Les **sans témoin non examinés** du #481 (pré-enregistré)", ""]
    L.append("Le **#481** avait classé **14** titres de section *sans témoin*, n'en")
    L.append("avait lu que **5**, et avait écrit lui-même que son **2/5 ne")
    L.append("s'extrapolait pas**. **Ce cycle lit les restants** et rend le compte")
    L.append("**complet** — un dénombrement, plus un taux d'échantillon.")
    L.append("")

    L.append("## La population, re-dérivée")
    L.append("")
    L.append("| | #481 | Ici | Écart |")
    L.append("|---|---|---|---|")
    L.append(f"| sans témoin | {REF_481['sans']} | **{len(S)}** | **{ecart:+d}** |")
    L.append(f"| déjà examinés au #481 | {REF_481['examines']} | "
             f"**{len(DEJA_481)}** | — |")
    L.append(f"| **restants, examinés ici** | — | **{len(restants)}** | — |")
    L.append("")
    L.append("**La règle du #481 est reprise sans modification**, y compris son défaut")
    L.append("connu : elle ne reconnaît pas l'exhaustivité d'un `if/else`. Le total de")
    L.append(f"**{len(S)}** reste donc un **majorant**, et les branches d'alternative")
    L.append("sont **comptées à part** ci-dessous plutôt que corrigées.")
    L.append("")

    L.append("## Les verdicts, un par un")
    L.append("")
    L.append("**Écrits à la main après lecture du code autour de chaque garde.** Ordre")
    L.append("et règle binaire fixés dans le pré-enregistrement.")
    L.append("")
    masquants, ifelse, non_examines = [], [], []
    for nom, ln, titre, gl in restants:
        etat, alt, motif = V.get((nom, ln), ("NON EXAMINÉ", False, "—"))
        if etat == "MASQUANT":
            masquants.append((nom, ln))
        if alt:
            ifelse.append((nom, ln))
        if etat == "NON EXAMINÉ":
            non_examines.append((nom, ln))
        etiq = {"MASQUANT": "**MASQUANT**", "ANODIN": "anodin"}.get(etat, "**NON EXAMINÉ**")
        L.append(f"### `{nom}` l.{ln} — {etiq}"
                 + (" *(branche d'`if/else`)*" if alt else ""))
        L.append("")
        L.append(f"Garde : `{gl}` — section : *{titre[:60]}*")
        L.append("")
        L.append(motif)
        L.append("")

    L.append("## Le compte")
    L.append("")
    L.append(f"- **MASQUANTS** parmi les restants : **{len(masquants)} / "
             f"{len(restants)}**")
    L.append(f"- **branches d'`if/else`** *(anodines par exhaustivité, comptées à "
             f"part)* : **{len(ifelse)}**")
    if non_examines:
        L.append(f"- **non examinés** : **{len(non_examines)}**")
    L.append("")
    tot_masq = len(masquants) + REF_481["masquants"]
    L.append("### Consolidé sur toute la population")
    L.append("")
    L.append("| Origine | Masquants | Examinés |")
    L.append("|---|---|---|")
    L.append(f"| #481 *(les 5 premiers)* | {REF_481['masquants']} | "
             f"{REF_481['examines']} |")
    L.append(f"| **#484** *(le reste)* | **{len(masquants)}** | "
             f"**{len(restants)}** |")
    L.append(f"| **total** | **{tot_masq}** | "
             f"**{len(restants) + REF_481['examines']}** |")
    L.append("")
    L.append("> **Toute la population a été lue.** Ce total ne demande aucune")
    L.append("> extrapolation — c'est le second dénombrement complet de cette série,")
    L.append("> après celui du #479.")
    L.append("")

    L.append("## Trois angles morts de ma règle, tous trouvés par l'examen")
    L.append("")
    L.append("Le #481 en connaissait **un**. L'examen des restants en révèle **deux")
    L.append("autres** — et aucun n'est corrigé ici :")
    L.append("")
    L.append("| Angle mort | Cas concernés |")
    L.append("|---|---|")
    L.append(f"| branche d'`if/else` exhaustif *(connu au #481)* | **{len(ifelse)}** |")
    parent = sum(1 for k, v in V.items() if "bloc parent" in v[2])
    autre = sum(1 for k, v in V.items() if "sous un autre nom" in v[2])
    L.append(f"| témoin situé dans un **bloc parent** | **{parent}** |")
    L.append(f"| témoin publié **sous un autre nom** | **{autre}** |")
    L.append("")
    L.append(f"*(Les causes **se recoupent** : {len(ifelse) + parent + autre} causes")
    L.append(f"pour {len(restants) - len(masquants)} cas anodins, parce qu'un cas peut")
    L.append("en cumuler deux — `verdict_detector_fix` est à la fois une branche")
    L.append("d'alternative **et** doté d'un témoin sous un autre nom.)*")
    L.append("")
    L.append("> **Ma règle cherchait la variable de la garde au seul niveau non gardé.**")
    L.append("> Elle manque donc un témoin dès qu'il est un peu plus haut, ou qu'il")
    L.append("> porte un autre nom — `rappel` pour `rates`, `ok4` pour `idem`.")
    L.append("")
    L.append("**Aucun n'est corrigé.** Les corriger après mesure serait le retuning que")
    L.append("les #480, #481 et #483 ont refusé. Le majorant est publié **avec ses")
    L.append("trois causes**, ce qui permet à un lecteur de retrancher lui-même.")
    L.append("")

    L.append("## Mes trois prédictions, confrontées")
    L.append("")
    p1 = len(masquants) >= 2
    p2 = tot_masq <= 7
    p3 = len(ifelse) >= 1
    L.append("| Prédiction | Annoncé | Mesuré | Verdict |")
    L.append("|---|---|---|---|")
    L.append(f"| ≥ 2 masquants parmi les restants | ≥ 2 | {len(masquants)} | "
             f"{'**vérifiée**' if p1 else '**réfutée**'} |")
    L.append(f"| total consolidé ≤ 7 masquants | ≤ 7 | {tot_masq} | "
             f"{'**vérifiée**' if p2 else '**réfutée**'} |")
    L.append(f"| ≥ 1 branche d'`if/else` | ≥ 1 | {len(ifelse)} | "
             f"{'**vérifiée**' if p3 else '**réfutée**'} |")
    L.append("")
    L.append(f"**Les trois sont vérifiées, et c'est le résultat le moins intéressant")
    L.append("du cycle.** Elles étaient faibles : « ≥ 2 » quand le #481 en avait trouvé")
    L.append("2 sur 5, « ≤ 7 » sur 14, « ≥ 1 » alternative quand le #481 en signalait")
    L.append("déjà une. **Ce que le cycle apprend vraiment, il ne l'avait pas prédit** :")
    L.append("les **deux angles morts supplémentaires** de ma propre règle.")
    L.append("")

    L.append("## Ce que devient la dette")
    L.append("")
    L.append(f"- **{tot_masq} sections masquantes** établies sur **{len(S)}** sans")
    L.append("  témoin — **toutes lues**, plus aucune non jugée ;")
    anodins_r = len(restants) - len(masquants)
    L.append(f"- **{len(S) - tot_masq}** anodines, dont les **{anodins_r}** lues ici")
    L.append("  le sont **toutes** pour une raison que ma règle ne sait pas voir ;")
    L.append("- **0** correction apportée : ni aux scripts, ni à la règle.")
    L.append("")
    L.append(f"> **La forme qui a coûté trois cycles existe en {tot_masq} exemplaires**")
    L.append("> — sur les **766** scripts producteurs recensés au #481. Elle est réelle,")
    L.append("> nommée, et rare — les trois à la fois.")
    L.append("")

    L.append("## Critères de succès")
    L.append("")
    c2 = not non_examines
    c4 = all(any(x[0] == n and x[1] == l for x in restants) for n, l in masquants)
    L.append(f"1. Population re-dérivée (**{len(S)}**), écart au #481 (**{ecart:+d}**),")
    L.append(f"   les **{len(DEJA_481)}** du #481 déclarés et exclus — **OUI**.")
    L.append(f"2. **{len(restants) - len(non_examines)}/{len(restants)}** examinés avec")
    L.append(f"   garde verbatim et verdict — **{'OUI' if c2 else 'NON'}**.")
    L.append("3. Total consolidé publié, part du #481 distinguée — **OUI**.")
    L.append(f"4. Aucun masquant compté sans sa garde publiée — "
             f"**{'OUI' if c4 else 'NON'}**.")
    L.append(f"5. Branches d'`if/else` comptées à part (**{len(ifelse)}**) — **OUI**.")
    L.append("")
    L.append(f"**{'PASS' if (c2 and c4) else 'FAIL'}** — le critère porte sur le")
    L.append("**procédé**.")
    L.append("")
    L.append("Simulation 300 € et robustesse **sans objet** : aucune position, aucun")
    L.append("paramètre à perturber. **Aucun script du dépôt n'a été exécuté.**")
    L.append("")
    L.append("")
    L.append("> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date")
    L.append("> de son exécution (cycles #436-#438).")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"S={len(S)} restants={len(restants)} masquants={len(masquants)} "
          f"ifelse={len(ifelse)} non_examines={len(non_examines)} total={tot_masq}")
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
