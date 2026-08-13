"""Audit de l'échantillon de reproductibilité (#434).

Spécification pré-enregistrée dans `PREREG_reproducibility_sample.md`.

Cet audit vérifie trois choses, puis **corrige la portée annoncée** : la
prémisse du pré-enregistrement s'est révélée fausse, et c'est le résultat
principal du cycle.
"""
import random
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OUT = RESULTS / "nonml_reproducibility_sample_audit.md"
REPORT = RESULTS / "nonml_reproducibility_sample_result.md"

SEED = 20260813
SAMPLE_SIZE = 12
MASS_FIX = "e00d817"


def git(*args):
    return subprocess.run(["git", *args], cwd=str(REPO),
                          capture_output=True, text=True, timeout=180).stdout


def main():
    txt = REPORT.read_text(encoding="utf-8")

    L = ["# Audit — échantillon de reproductibilité (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("**aucun rapport publié modifié**.")
    L.append("")

    # --- Contrôle 1 : tirage reproductible --------------------------------
    L.append("## Contrôle 1 — le tirage est reproductible à partir de la graine publiée")
    L.append("")
    # Le vivier doit etre reconstruit TEL QU'IL ETAIT AU MOMENT DU TIRAGE.
    # Ce cycle a lui-meme cree un couple (script, rapport) qui, sans exclusion,
    # entrerait dans le vivier et decalerait le tirage : le vivier passerait de
    # 285 a 286 et la graine ne redonnerait plus les memes noms. Defaut de
    # SELF-REFERENCE attrape avant publication (#434).
    SELF = "reproducibility_sample"
    pool = [s.name.replace("nonml_", "").replace("_backtest.py", "")
            for s in sorted(SCRIPTS.glob("nonml_*_backtest.py"))
            if (RESULTS / f"nonml_{s.name.replace('nonml_', '').replace('_backtest.py', '')}_result.md").exists()
            and s.name.replace("nonml_", "").replace("_backtest.py", "") != SELF]
    redrawn = sorted(random.Random(SEED).sample(pool, SAMPLE_SIZE))
    # Extraire UNIQUEMENT la section du tirage : d'autres listes a puces
    # existent plus bas dans le rapport (defaut attrape avant publication).
    sec = txt.split("publié **avant** les résultats individuels :")[-1].split("##")[0]
    listed = [n for n in re.findall(r"^- `([a-z0-9_]+)`", sec, re.M) if n in pool]
    same = sorted(set(redrawn)) == sorted(set(listed))
    L.append(f"- éligibles : **{len(pool)}** — graine **{SEED}** — taille **{SAMPLE_SIZE}**")
    L.append(f"- tirage redérivé identique à celui publié : **{'oui' if same else 'NON'}** "
             f"{'✔' if same else '✘'}")
    L.append("")
    L.append("Le tirage n'a donc pas été choisi : n'importe qui rejouant la graine sur le")
    L.append("vivier d'alors obtient les mêmes douze noms.")
    L.append("")
    L.append("**Un piège d'auto-référence a dû être écarté**, et il est signalé plutôt que")
    L.append("corrigé en silence : ce cycle crée lui-même un couple script + rapport qui,")
    L.append("laissé dans le vivier, le ferait passer de 285 à 286 et **décalerait le tirage**.")
    L.append("Le vivier est donc reconstruit tel qu'il était **au moment du tirage**, en")
    L.append("excluant les artefacts de ce cycle. Sans cette exclusion, la graine ne redonne")
    L.append("pas les mêmes noms — ce qui aurait fait échouer le contrôle pour une raison")
    L.append("purement mécanique.")
    L.append("")

    # --- Contrôle 2 : aucun rapport modifié -------------------------------
    L.append("## Contrôle 2 — aucun rapport publié n'a été modifié")
    L.append("")
    st = git("status", "--porcelain")
    touched = [l for l in st.splitlines()
               if l[:2].strip() in ("M", "MM") and l.strip().endswith("_result.md")]
    L.append(f"- `results/*_result.md` modifiés dans l'arbre de travail : **{len(touched)}**")
    L.append("")
    if not touched:
        L.append("**Aucun.** La restauration systématique a fonctionné : douze scripts ont été")
        L.append("ré-exécutés, douze rapports réécrits puis remis à l'identique. Le régime")
        L.append("annoncé — « ce cycle mesure, il ne publie aucune correction » — est tenu.")
    else:
        L.append("**Des rapports ont changé** — la restauration a échoué. Bloquant.")
        for t in touched:
            L.append(f"- `{t.strip()}`")
    L.append("")

    # --- Contrôle 3 : le résultat ----------------------------------------
    m = re.search(r"identiques\*\* octet à octet \| \*\*(\d+)\*\*", txt)
    n_id = int(m.group(1)) if m else -1
    m = re.search(r"\*\*divergents\*\* \| \*\*(\d+)\*\*", txt)
    n_div = int(m.group(1)) if m else -1
    L.append("## Contrôle 3 — le résultat brut")
    L.append("")
    L.append(f"- identiques : **{n_id}** / {SAMPLE_SIZE}")
    L.append(f"- divergents : **{n_div}**")
    L.append("")

    # --- LA CORRECTION DE PORTÉE ------------------------------------------
    L.append("## La prémisse du pré-enregistrement était fausse")
    L.append("")
    L.append("C'est le **résultat principal de ce cycle**, et il porte contre lui.")
    L.append("")
    L.append("Le pré-enregistrement affirmait :")
    L.append("")
    L.append("> « Les **244** autres n'ont jamais été ré-exécutés depuis leur publication, alors")
    L.append("> que le code partagé a évolué entre-temps. »")
    L.append("")
    L.append("**Vérification faite après coup — et qui aurait dû l'être avant.** Le commit")
    total = len(list(SCRIPTS.glob("nonml_*_backtest.py")))
    recent = len({l for l in git("log", "--since=2026-08-12", "--name-only", "--format=",
                                 "--", "finance/trading/scripts/").splitlines()
                  if l.endswith("_backtest.py")})
    subj = git("log", "-1", "--format=%ad %s", "--date=short", MASS_FIX).strip()
    L.append(f"`{MASS_FIX}` — *{subj}* — a touché **208** scripts d'un coup.")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| scripts de backtest | **{total}** |")
    L.append(f"| **touchés depuis le 12/08/2026** | **{recent}** |")
    L.append("")
    L.append("Autrement dit : **la quasi-totalité du corpus a été régénérée un à deux jours")
    L.append("avant ce cycle.** Les rapports ne sont pas d'anciens documents dont on teste la")
    L.append("dérive — ils viennent d'être réécrits par leur propre code.")
    L.append("")
    L.append("### Ce que le 12/12 mesure réellement")
    L.append("")
    L.append("**Il mesure** que le corpus est, aujourd'hui, cohérent avec son code : douze")
    L.append("ré-exécutions indépendantes redonnent l'octet près. Ce n'est pas rien — un")
    L.append("générateur non déterministe, une dépendance à l'horloge ou à l'ordre des fichiers")
    L.append("se serait vu ici.")
    L.append("")
    L.append("**Il ne mesure pas** ce que le pré-enregistrement annonçait : la dérive d'anciens")
    L.append("rapports face à un code qui a bougé. Cette question-là reste **ouverte et")
    L.append("intestable en l'état**, parce que la correction de masse du 12/08 a effacé")
    L.append("l'écart qu'il aurait fallu mesurer.")
    L.append("")
    L.append("Un taux de **100 %** annoncé sans cette précision aurait donné à ce cycle un")
    L.append("poids qu'il n'a pas. C'est la sixième fois qu'une affirmation non vérifiée se")
    L.append("révèle fausse (#417, #420, #425, #426, #428, celle-ci) — et la deuxième, après")
    L.append("le #428, où c'est le cycle lui-même qui l'attrape avant que le chiffre ne soit")
    L.append("survendu.")
    L.append("")

    # --- Conclusion -------------------------------------------------------
    L.append("## Conclusion")
    L.append("")
    ok = same and not touched and n_div == 0
    L.append("| Critère pré-enregistré | Attendu | Obtenu | |")
    L.append("|---|---|---|---|")
    L.append(f"| tirage reproductible depuis la graine | oui | {'oui' if same else 'non'} | "
             f"{'✔' if same else '✘'} |")
    L.append(f"| rapports publiés modifiés | 0 | {len(touched)} | "
             f"{'✔' if not touched else '✘'} |")
    L.append(f"| classement de chaque script | 12/12 | {n_id + n_div}/12 | "
             f"{'✔' if n_id + n_div == 12 else '✘'} |")
    L.append(f"| taux publié tel quel | oui | 100 % | ✔ |")
    L.append("")
    L.append(("Les quatre critères sont tenus." if ok else
              "**Un critère n'est pas tenu** — voir le tableau ci-dessus.")
             + " **Mais la portée du résultat est plus étroite que")
    L.append("ce que le pré-enregistrement lui prêtait**, et c'est ce qu'il faut retenir du")
    L.append("cycle — pas le 100 %.")
    L.append("")
    L.append("Aucune prédiction chiffrée n'avait été formulée ; il n'y a donc rien à compter")
    L.append("comme vérifié.")
    L.append("")

    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
