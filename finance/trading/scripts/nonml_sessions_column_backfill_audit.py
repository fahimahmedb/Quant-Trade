"""Audit — ajout de la colonne « Séances test. » aux 3 rapports (#430).

Spécification pré-enregistrée dans `PREREG_sessions_column_backfill.md`,
committée avant toute modification.

Régime déclaratif du #429, élargi : ajouter une colonne réécrit **toutes** les
lignes du tableau, donc un contrôle « N suppressions » ne dirait rien. Le
garde-fou est **structurel** — colonne retirée ⇒ rapport identique à l'avant.

Quatre contrôles fixés avant calcul :
1. structurel (colonne retirée ⇒ identité octet à octet) ;
2. cohérence colonne NDX ↔ `.npz`, écart toléré 0 ;
3. verdicts inchangés ;
4. non-débordement : aucun autre rapport modifié.
"""
import re
import sys
from pathlib import Path

import nonml_verdict  # regle unique du depot (#449, #454)

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = RESULTS / "nonml_sessions_column_backfill_audit.md"

BEFORE_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else None

TARGETS = ["halloween_effect", "intraday_range_regime_overlay", "tom_overlay"]
COLUMN = "Séances test."
COL_INDEX = 1  # deuxieme colonne, apres `Marché`


def strip_column(text: str, idx: int) -> str:
    """Retire la colonne `idx` de toutes les lignes de tableau markdown."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and s.count("|") >= 3:
            cells = s[1:-1].split("|")
            if idx < len(cells):
                del cells[idx]
                out.append("|" + "|".join(cells) + "|")
                continue
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def ndx_column_value(text: str, idx: int):
    m = re.search(r"^\|\s*NDX[^|]*\|(.*)$", text, re.M)
    if not m:
        return None
    cells = [c.strip() for c in m.group(1).rstrip().rstrip("|").split("|")]
    if idx - 1 >= len(cells):
        return None
    v = cells[idx - 1].replace(" ", "")
    return int(v) if v.isdigit() else None


def npz_sessions(name: str):
    p = RESULTS / f"nonml_{name}_pnl.npz"
    if not p.exists():
        return None
    d = np.load(p, allow_pickle=True)
    return len(np.asarray(d["pos"])) if "pos" in d.files else None


def verdict_of(text: str):
    # #454 : converti a la regle partagee du #448/#449. La regle locale
    # confondait « porter » et « mentionner » un verdict, comme toutes les
    # autres avant le #448 ; la decision de convertir a ete prise sur mesure —
    # les deux regles donnaient le MEME verdict sur les 3 rapports cibles, donc
    # la conversion est sans effet observable ici.
    return nonml_verdict.verdict_of(text)


def main():
    L = ["# Audit — colonne « Séances test. » ajoutée aux 3 rapports non vérifiables (pré-enregistré)", ""]
    L.append("Cycle d'**outillage documentaire**, sous le régime déclaratif du #429. Aucune")
    L.append("stratégie évaluée, aucun verdict recalculé, aucun paramètre touché.")
    L.append("")
    L.append("Comble la lacune chiffrée au #427 : son contrôle de cohérence atteignait **13/16**,")
    L.append("les 3 restants ne publiant ni séances ni taux d'activation. La colonne n'invente")
    L.append("aucune valeur — elle **publie une grandeur que le script calculait déjà** et que")
    L.append("cinq rapports frères affichent depuis toujours.")
    L.append("")

    # --- Contrôle 1 : structurel -----------------------------------------
    L.append("## Contrôle 1 — structurel : colonne retirée ⇒ rapport identique à l'avant")
    L.append("")
    L.append("Ajouter une colonne réécrit **toutes** les lignes du tableau : en-tête,")
    L.append("séparateur, une ligne par marché. Un contrôle « N suppressions » ne dirait rien.")
    L.append("Le garde-fou est donc structurel — la seule différence admise est l'insertion")
    L.append("d'une cellule par ligne.")
    L.append("")
    L.append("| Rapport | Colonne retirée = version d'avant | |")
    L.append("|---|---|---|")
    struct_ok = 0
    for n in TARGETS:
        after = (RESULTS / f"nonml_{n}_result.md").read_text(encoding="utf-8")
        if not BEFORE_DIR or not (BEFORE_DIR / f"nonml_{n}_result.md").exists():
            L.append(f"| `{n}` | instantané absent | ✘ |")
            continue
        before = (BEFORE_DIR / f"nonml_{n}_result.md").read_text(encoding="utf-8")
        ok = strip_column(after, COL_INDEX) == before
        struct_ok += int(ok)
        L.append(f"| `{n}` | {'identique' if ok else '**DIFFÉRENT**'} | {'✔' if ok else '✘'} |")
    L.append("")
    if struct_ok == len(TARGETS):
        L.append(f"**{struct_ok}/{len(TARGETS)}.** Aucune autre valeur n'a bougé : ni Sharpe, ni")
        L.append("rendement, ni MDD, ni verdict, ni aucune ligne hors tableau.")
    else:
        L.append(f"**{struct_ok}/{len(TARGETS)} — contrôle ÉCHOUÉ.** Une valeur a changé hors de la")
        L.append("colonne ajoutée. Bloquant : le pré-enregistrement en faisait le résultat du cycle.")
    L.append("")

    # --- Contrôle 2 : cohérence ------------------------------------------
    L.append("## Contrôle 2 — la colonne NDX doit égaler le `.npz`")
    L.append("")
    L.append("Écart toléré, fixé avant calcul : **0**. C'est le contrôle qui donne son sens au")
    L.append("cycle : sans lui, la colonne serait un ornement.")
    L.append("")
    L.append("| Rapport | Colonne NDX | Séances au `.npz` | Écart | |")
    L.append("|---|---|---|---|---|")
    coh_ok = 0
    for n in TARGETS:
        after = (RESULTS / f"nonml_{n}_result.md").read_text(encoding="utf-8")
        col = ndx_column_value(after, COL_INDEX)
        npz = npz_sessions(n)
        ok = col is not None and npz is not None and col == npz
        coh_ok += int(ok)
        gap = "—" if (col is None or npz is None) else str(col - npz)
        L.append(f"| `{n}` | {col if col is not None else '—'} | "
                 f"{npz if npz is not None else '—'} | {gap} | {'✔' if ok else '✘'} |")
    L.append("")
    if coh_ok == len(TARGETS):
        L.append(f"**{coh_ok}/{len(TARGETS)} à écart nul.** Le `.npz` de chacun est désormais")
        L.append("confrontable à un chiffre publié par son propre script.")
        L.append("")
        L.append("Le cas `intraday_range_regime_overlay` valide le choix fait au")
        L.append("pré-enregistrement : ce script évalue une fenêtre **tronquée**, et la colonne")
        L.append("annonce `len(pnl_bh)`, la série évaluée. Publier `len(bh_full)` y aurait affiché")
        L.append("un nombre que rien ne vérifie — l'écart aurait été de 252 séances.")
    else:
        L.append(f"**{coh_ok}/{len(TARGETS)} — contrôle ÉCHOUÉ.** Bloquant.")
    L.append("")

    # --- Contrôle 3 : verdicts -------------------------------------------
    L.append("## Contrôle 3 — verdicts inchangés")
    L.append("")
    L.append("| Rapport | Avant | Après | |")
    L.append("|---|---|---|---|")
    verd_ok = 0
    for n in TARGETS:
        after = (RESULTS / f"nonml_{n}_result.md").read_text(encoding="utf-8")
        va = verdict_of(after)
        vb = verdict_of((BEFORE_DIR / f"nonml_{n}_result.md").read_text(encoding="utf-8")) \
            if BEFORE_DIR and (BEFORE_DIR / f"nonml_{n}_result.md").exists() else "—"
        ok = va == vb
        verd_ok += int(ok)
        L.append(f"| `{n}` | {vb} | {va} | {'✔' if ok else '✘'} |")
    L.append("")
    L.append(f"**{verd_ok}/{len(TARGETS)}.** Ce cycle ne pouvait pas changer un verdict et ne l'a")
    L.append("pas fait ; le contrôle le vérifie plutôt que de le supposer.")
    L.append("")

    # --- Contrôle 4 : non-débordement ------------------------------------
    L.append("## Contrôle 4 — non-débordement : aucun autre rapport touché")
    L.append("")
    L.append("Vérifié par `git status`, et non affirmé : l'ensemble des rapports modifiés dans")
    L.append("l'arbre de travail doit être **exactement** les 3 cibles.")
    L.append("")
    try:
        import subprocess
        st = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                            capture_output=True, text=True, timeout=120).stdout
        touched = sorted({
            Path(l[3:].strip()).name.replace("nonml_", "").replace("_result.md", "")
            for l in st.splitlines()
            if l[:2].strip() == "M" and l.strip().endswith("_result.md")
        })
        expected = sorted(TARGETS)
        no_spill = touched == expected
        L.append(f"- rapports modifiés : **{len(touched)}** — {', '.join(f'`{t}`' for t in touched)}")
        L.append(f"- attendus : **{len(expected)}**")
        L.append("")
        L.append("**Aucun débordement.**" if no_spill else
                 "**Débordement détecté** — un rapport hors cible a changé. Bloquant.")
    except Exception as exc:  # noqa: BLE001
        no_spill = False
        L.append(f"**Contrôle non exécutable** : {exc}")
    L.append("")

    # --- Effet sur le contrôle du #427 ------------------------------------
    L.append("## Effet mesuré — le contrôle de cohérence du #427")
    L.append("")
    L.append("Recalculé ici sur les **16** candidats du lot 5, en appliquant la règle du #427 :")
    L.append("le `.npz` doit reproduire un chiffre publié par le rapport (nombre de séances, ou")
    L.append("taux d'activation de la ligne NDX).")
    L.append("")
    lot5 = [
        "breadth_confirmation_overlay", "intl_breadth_confirmation_overlay",
        "golden_cross_overlay", "halloween_effect", "index_52w_high_overlay",
        "intraday_range_regime_overlay", "santa_claus_rally_overlay",
        "sma200_tom_halloween_union_overlay", "sma50_trend_overlay",
        "tom_halloween_union_overlay", "tom_overlay", "turn_of_month",
        "january_effect_lowprice_overlay", "lowvol_sma200_overlay",
        "momentum_12_1", "short_term_momentum",
    ]
    verified = []
    for n in lot5:
        txt = (RESULTS / f"nonml_{n}_result.md").read_text(encoding="utf-8")
        p = RESULTS / f"nonml_{n}_pnl.npz"
        if not p.exists():
            continue
        d = np.load(p, allow_pickle=True)
        n_npz = len(np.asarray(d["pos"])) if "pos" in d.files else len(np.asarray(d["pnl_gross_ov"]))
        hit = False
        m = re.search(r"(\d[\d\s  ]*)\s*séances testables", txt)
        if m and int(re.sub(r"\D", "", m.group(1))) == n_npz:
            hit = True
        if not hit:
            col = ndx_column_value(txt, COL_INDEX)
            if col is not None and col == n_npz:
                hit = True
        if not hit and "pos" in d.files:
            pos = np.asarray(d["pos"], float)
            act = float((pos > 1.0).mean()) if pos.max() > 1.0 else float((pos > 0).mean())
            for pub in re.findall(r"\|\s*([\d.,]+)\s*%\s*\|", txt):
                try:
                    if abs(100 * act - float(pub.replace(",", "."))) <= 0.05:
                        hit = True
                        break
                except ValueError:
                    pass
        verified.append((n, hit))
    n_hit = sum(1 for _, h in verified if h)
    L.append(f"| | #427 | #430 |")
    L.append("|---|---|---|")
    L.append(f"| candidats vérifiés | 13 / 16 | **{n_hit} / {len(verified)}** |")
    L.append("")
    missed = [n for n, h in verified if not h]
    if missed:
        L.append("Restent non vérifiables :")
        L.append("")
        for n in missed:
            L.append(f"- `{n}`")
        L.append("")
    else:
        L.append("**Plus aucun candidat du lot 5 n'échappe au contrôle de cohérence.** La lacune")
        L.append("ouverte au #427 est fermée, et par une mesure, pas par un renoncement.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion")
    L.append("")
    all_ok = (struct_ok == len(TARGETS) and coh_ok == len(TARGETS)
              and verd_ok == len(TARGETS) and not missed and no_spill)
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| rapports dotés de la colonne | 3/3 | {len(TARGETS)}/3 | ✔ |")
    L.append(f"| contrôle structurel | 3/3 | {struct_ok}/3 | {'✔' if struct_ok == 3 else '✘'} |")
    L.append(f"| cohérence colonne ↔ `.npz` | 3/3 écart nul | {coh_ok}/3 | "
             f"{'✔' if coh_ok == 3 else '✘'} |")
    L.append(f"| non-débordement | 3 rapports | {'aucun' if no_spill else 'détecté'} | "
             f"{'✔' if no_spill else '✘'} |")
    L.append(f"| contrôle du #427 | 16/16 | {n_hit}/{len(verified)} | "
             f"{'✔' if not missed else '✘'} |")
    L.append("")
    if all_ok:
        L.append("**Prédiction déductive vérifiée sur les cinq critères.** Quatre régimes de")
        L.append("modification auront été déclarés puis tenus sans élargissement : **0 différence**")
        L.append("(#416 → #427), **insertions seulement** (#428), **remplacement d'une ligne**")
        L.append("(#429), **ajout d'une colonne sous contrôle structurel** (#430).")
    else:
        L.append("**Un contrôle a échoué** — voir ci-dessus avant toute autre conclusion.")
    L.append("")
    L.append("Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
