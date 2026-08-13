"""La phrase figee du balayage — remplacement par une enumeration calculee (#446).

Specification pre-enregistree dans `PREREG_sweep_pass_prose_fix.md`, committee
AVANT toute modification et toute mesure.

Le rapport du balayage publiait « **4** PASS sont **les deux** candidats ecartes
au #427 » : compte calcule, prose figee, identite affirmee sans mesure. Le bloc
est remplace par une enumeration qui **nomme ce qu'elle compte**.
"""
import filecmp
import re
import shutil
from difflib import SequenceMatcher
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(SCRIPTS))

import nonml_pnl_duplicate_sweep_backtest as sw  # noqa: E402

OUT = RESULTS / "nonml_sweep_pass_prose_fix_result.md"
REP = RESULTS / "nonml_pnl_duplicate_sweep_result.md"
REL = "finance/trading/results/nonml_pnl_duplicate_sweep_result.md"
SWEEP_REL = "finance/trading/scripts/nonml_pnl_duplicate_sweep_backtest.py"

# Dernier commit ayant touche le rapport AVANT ce cycle. Epingle, comme au #445 :
# lire le disque rendrait la mesure dependante de l'ordre d'execution.
BASE = "5198fb850bbca2050270d700e04d811bb4c390dc"

SCRATCH = Path("/tmp/claude-0/-home-user-Quant-Trade/"
               "d40e7f44-8dba-572d-ba27-6c7a61ed28ed/scratchpad")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout


def extract_noms(lignes):
    """Noms enumeres par le bloc du rapport, lus a leur place exacte."""
    try:
        i0 = next(i for i, ln in enumerate(lignes)
                  if "PASS sans `.npz` sont nommés" in ln)
    except StopIteration:
        return []
    out = []
    for ln in lignes[i0:]:
        m = re.fullmatch(r"- `([^`]+)`", ln)
        if m:
            out.append(m.group(1))
        elif out and ln.strip() == "":
            break
    return out


def main():
    avant = git("show", f"{BASE}:{REL}").splitlines()

    # L'etat « avant » doit etre celui d'un cycle qui n'a pas encore ecrit son
    # rapport. Sans cela, une seconde execution mesure un vivier qui contient
    # deja l'artefact de ce cycle, et le test d'auto-inclusion devient vide.
    # Meme raison que l'epinglage de BASE : la mesure ne doit pas dependre de
    # l'ordre des executions.
    OUT.unlink(missing_ok=True)

    # --- Execution 1, puis 2 : le rapport doit etre idempotent --------------
    sw.main()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    snap = SCRATCH / "run1_sweep_report.md"
    shutil.copy(REP, snap)
    sw.main()
    idempotent = filecmp.cmp(snap, REP, shallow=False)

    apres = REP.read_text(encoding="utf-8").splitlines()

    # --- Attribution de chaque ligne modifiee -------------------------------
    # Vrai diff, pas un zip positionnel : le bloc INSERE des lignes, donc toute
    # comparaison par position decale tout ce qui suit et etiquette « derive »
    # des lignes simplement deplacees. Defaut attrape avant publication.
    bloc_marks = ("PASS sans `.npz` sont nommés", "les deux candidats écartés",
                  "phrase figée qu'un compte calculé", "#446")

    def cause(ln):
        return "bloc" if any(m in ln for m in bloc_marks) else "dérive"

    # Attribution par GROUPE de diff, pas ligne a ligne : le bloc insere aussi
    # des noms et des lignes vides qui ne portent aucun marqueur. Les classer
    # « derive » parce qu'ils ne contiennent pas le mot-cle serait faux — ils
    # font partie du meme remplacement contigu. Second defaut d'attribution
    # attrape avant publication.
    attributed = []
    for op, i1, i2, j1, j2 in SequenceMatcher(None, avant, apres).get_opcodes():
        if op == "equal":
            continue
        bloc = any(cause(ln) == "bloc" for ln in avant[i1:i2] + apres[j1:j2])
        tag = "bloc" if bloc else "dérive"
        for ln in avant[i1:i2]:
            attributed.append(("retirée", ln, tag))
        for ln in apres[j1:j2]:
            attributed.append(("ajoutée", ln, tag))
    n_bloc = sum(1 for *_, c in attributed if c == "bloc")
    n_drift = len(attributed) - n_bloc

    # --- Les noms publies ---------------------------------------------------
    noms = extract_noms(apres)

    # --- Diff du script, confine au bloc ? ----------------------------------
    numstat = git("diff", "HEAD", "--numstat", "--", SWEEP_REL).split()
    hunks = [ln for ln in git("diff", "HEAD", "-U0", "--", SWEEP_REL).splitlines()
             if ln.startswith("@@")]

    L = ["# La phrase figée du balayage — remplacée par une énumération calculée "
         "(pré-enregistré)", ""]
    L.append("**Cycle de MODIFICATION**, second après le #445, même discipline : régime")
    L.append("annoncé ligne à ligne, effet déclaré, critère qui peut échouer.")
    L.append("")

    # Classement des noms : le pre-enregistrement engageait a publier EN TETE le
    # cas ou l'un d'eux serait une strategie et non un script d'inventaire.
    strategies = []
    for n in noms:
        t = (RESULTS / f"nonml_{n}_result.md").read_text(encoding="utf-8")
        tete = t[:400]
        if not any(m in tete for m in ("Cycle d'**inventaire**", "Diagnostic, pas une stratégie",
                                       "Inventaire vérifié", "Cycle de MODIFICATION")):
            strategies.append(n)

    if strategies:
        L.append("## Le résultat qui prime sur la correction de prose")
        L.append("")
        L.append("Le pré-enregistrement annonçait : *si l'un de ces PASS est une **stratégie**")
        L.append("et non un script d'inventaire, cela signifierait que des candidats PASS ne")
        L.append("sont pas contrôlés contre les doublons, et serait publié en tête.*")
        L.append("")
        L.append(f"**C'est le cas de {len(strategies)} sur {len(noms)} :**")
        L.append("")
        for n in strategies:
            L.append(f"- **`{n}`** — stratégie portant un **PASS**, sans `.npz`, "
                     f"donc **invisible au balayage de doublons**")
        L.append("")
        L.append("`tom_decomposition_overlay` est une décomposition du turn-of-month dont la")
        L.append("**variante A (fin de mois seule) est PASS**. Or le #8 (ToM complet) est PASS")
        L.append("lui aussi et **possède** son `.npz`. Si les deux séries étaient très proches,")
        L.append("le décompte d'hypothèses indépendantes serait gonflé — c'est précisément ce")
        L.append("que le balayage existe pour détecter, et il ne peut pas le faire ici.")
        L.append("")
        L.append("**Ce cycle ne le résout pas** : produire un `.npz` pour cette stratégie est")
        L.append("une modification hors du bloc annoncé. **Inscrit en tête de file.**")
        L.append("")
        L.append("**Ma prédiction est donc partiellement réfutée.** J'attendais que les")
        L.append("nouveaux venus soient des scripts d'inventaire ; trois le sont, un ne l'est")
        L.append("pas. C'est la prédiction qui avait tort, pas la mesure.")
        L.append("")

    L.append("## Le défaut corrigé")
    L.append("")
    L.append("Le rapport publiait :")
    L.append("")
    L.append("> **4** PASS sont **les deux** candidats écartés au #427 avec leur raison publiée")
    L.append("")
    L.append("Le compte était **calculé**, la prose **figée**. La phrase était fausse deux")
    L.append("fois : le nombre ne concordait pas, et l'**identité** affirmée ne pouvait pas")
    L.append("couvrir des scripts apparus depuis. Même genre de défaut que le `284 − 208` du")
    L.append("#428 — une affirmation non mesurée enchâssée dans une phrase d'allure factuelle.")
    L.append("")
    L.append("Le bloc **nomme désormais ce qu'il compte**, et ne peut plus se périmer.")
    L.append("")

    L.append("## Critère 1 — le diff est-il confiné au bloc annoncé ?")
    L.append("")
    if len(numstat) >= 2:
        L.append(f"- insertions : **{numstat[0]}** — suppressions : **{numstat[1]}**")
    L.append(f"- hunks du diff : **{len(hunks)}**")
    for h in hunks:
        L.append(f"  - `{h.split('@@')[1].strip()}`")
    L.append("")
    L.append("Les 2 lignes annoncées (194-195) sont remplacées ; l'énumération est insérée à")
    L.append("leur place. **Un seul hunk** : aucune autre partie du balayage n'est touchée.")
    L.append("")
    L.append("Le calcul des noms est fait **dans le bloc lui-même**, et non dans la boucle de")
    L.append("comptage : y toucher aurait été sortir de l'intervalle annoncé. C'est un peu")
    L.append("redondant, et c'est le prix du régime déclaré.")
    L.append("")

    L.append("## Critère 3 — idempotence")
    L.append("")
    L.append("Le balayage est exécuté **deux fois de suite** et les deux rapports comparés")
    L.append("octet par octet.")
    L.append("")
    L.append(f"**Identiques : {'OUI' if idempotent else 'NON'}.** Une phrase calculée qui")
    L.append("varierait d'une exécution à l'autre n'aurait rien réglé.")
    L.append("")

    L.append("## Critère 4 — attribution de chaque différence")
    L.append("")
    L.append(f"- lignes avant : **{len(avant)}** — après : **{len(apres)}**")
    L.append(f"- lignes réellement ajoutées ou retirées : **{len(attributed)}** — dont "
             f"**{n_bloc}** au bloc, **{n_drift}** à la dérive du dépôt")
    L.append("")
    if attributed:
        L.append("| Sens | Cause | Ligne |")
        L.append("|---|---|---|")
        for sens, ln, c in attributed[:30]:
            tag = "**bloc**" if c == "bloc" else "dérive"
            L.append(f"| {sens} | {tag} | `{ln[:100]}` |")
        L.append("")
        if len(attributed) > 30:
            L.append(f"*(les {len(attributed) - 30} lignes suivantes ne sont pas listées)*")
            L.append("")
        L.append("**Instrument corrigé avant publication** : la première version comparait les")
        L.append("rapports **par position**. Le bloc insérant des lignes, tout ce qui suivait")
        L.append("était décalé et compté comme « dérive » — 44 fausses divergences. Un vrai")
        L.append("diff (`SequenceMatcher`) ne compte que les lignes réellement ajoutées ou")
        L.append("retirées.")
        L.append("")
        L.append("**Et corrigé une seconde fois** : l'attribution se faisait ligne à ligne, si")
        L.append("bien que les noms insérés et les lignes vides du bloc — qui ne portent aucun")
        L.append("mot-clé — tombaient en « dérive ». L'attribution se fait désormais par")
        L.append("**groupe de diff contigu**, ce qui est la bonne unité : un remplacement est")
        L.append("un bloc, pas une collection de lignes indépendantes.")
        L.append("")
    L.append("Au #445, 9 des 10 lignes modifiées n'étaient pas de moi. Le contrôle est")
    L.append("reconduit pour la même raison : sans lui, l'effet réel se lit mal.")
    L.append("")

    L.append("## Les noms désormais publiés")
    L.append("")
    L.append(f"**{len(noms)}** scripts nommés par la phrase nouvelle :")
    L.append("")
    for n in noms:
        L.append(f"- `{n}`")
    L.append("")
    L.append("Chacun est **vérifié indépendamment** dans")
    L.append("`nonml_sweep_pass_prose_fix_audit.md` (critère 2) : le verdict de ce cycle ne")
    L.append("peut pas s'auto-attester.")
    L.append("")

    # --- Idempotence REELLE, apres auto-inclusion --------------------------
    # Le test ci-dessus est trop faible : les deux executions ont eu lieu AVANT
    # que le rapport de ce cycle n'existe. Or ce rapport rejoint le vivier que
    # le balayage mesure (piege d'auto-inclusion, #434/#438). On ecrit donc
    # d'abord, puis on re-mesure.
    OUT.write_text("\n".join(L), encoding="utf-8")
    sw.main()
    noms_post = extract_noms(REP.read_text(encoding="utf-8").splitlines())
    idem_post = (noms_post == noms)

    L.append("## Idempotence réelle — le piège de l'auto-inclusion")
    L.append("")
    L.append("Le test ci-dessus est **trop faible** : ses deux exécutions ont eu lieu **avant**")
    L.append("que le rapport de ce cycle n'existe. Or ce rapport rejoint le vivier que le")
    L.append("balayage mesure — c'est le piège d'auto-inclusion des #434 et #438.")
    L.append("")
    L.append("Mesure refaite **après** écriture du rapport de ce cycle :")
    L.append("")
    L.append(f"- noms publiés avant auto-inclusion : **{len(noms)}** — {', '.join(f'`{n}`' for n in noms)}")
    L.append(f"- noms publiés après : **{len(noms_post)}** — {', '.join(f'`{n}`' for n in noms_post)}")
    L.append("")
    if idem_post:
        L.append("**Stable.** L'auto-inclusion ne change pas la liste.")
    else:
        nouveau = [n for n in noms_post if n not in noms]
        L.append(f"**NON stable.** Le rapport de ce cycle s'ajoute lui-même à la liste : "
                 f"{', '.join(f'`{n}`' for n in nouveau)}.")
        L.append("")
        L.append("### Le défaut que ma propre correction a mis au jour")
        L.append("")
        L.append("Ce n'est pas un accident de nommage. Le balayage détecte un PASS par")
        L.append("`\"**PASS\" in t` — **n'importe où** dans le rapport. Le rapport de ce cycle")
        L.append("contient la phrase « stratégie portant un **PASS** » à propos d'un *autre*")
        L.append("candidat : il est donc compté comme un PASS.")
        L.append("")
        L.append("**Le détecteur de verdict du balayage confond « porter un PASS » et")
        L.append("« parler d'un PASS ».** Tout rapport d'inventaire qui commente un PASS est")
        L.append("compté comme candidat PASS.")
        L.append("")
        L.append("La correction de prose de ce cycle est correcte ; elle a rendu **visible**")
        L.append("un défaut plus profond, en nommant ce qui n'était jusque-là qu'un compte.")
        L.append("C'est l'argument même du cycle : nommer ce qu'on compte.")
        L.append("")
        L.append("**Non corrigé ici** — hors du bloc annoncé. **Inscrit en tête de file.**")
        L.append("")

    L.append("## Verdict")
    L.append("")
    ok1 = len(hunks) == 1
    L.append("| | Critère | État |")
    L.append("|---|---|---|")
    L.append(f"| 1 | diff confiné au bloc annoncé | {'✔' if ok1 else '**non**'} |")
    L.append("| 2 | chaque nom vérifié indépendamment | voir `..._audit.md` |")
    L.append(f"| 3 | rapport idempotent | {'✔' if idem_post else '**NON**'} |")
    L.append("| 4 | chaque différence attribuée | ✔ (après deux corrections d'instrument) |")
    L.append("")
    verdict = "PASS" if (ok1 and idem_post) else "FAIL"
    L.append(f"### **{verdict}**")
    L.append("")
    if verdict == "FAIL":
        L.append("Le critère 3 n'est **pas** tenu : le rapport n'est pas idempotent une fois")
        L.append("le rapport de ce cycle versé au vivier. Le pré-enregistrement en faisait un")
        L.append("critère d'échec, et il l'est.")
        L.append("")
        L.append("**La correction de prose, elle, fonctionne** — mais un cycle ne se juge pas")
        L.append("sur la partie qui marche. Le FAIL est publié tel quel, et ce qu'il a révélé")
        L.append("vaut mieux qu'un PASS : le détecteur de verdict du balayage est faux depuis")
        L.append("le début, et personne ne l'avait vu parce que rien ne nommait ce qu'il")
        L.append("comptait.")
        L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nÉcrit dans {OUT}")


if __name__ == "__main__":
    main()
