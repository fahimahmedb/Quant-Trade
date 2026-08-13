"""Reproductibilité des rapports publiés — échantillon tiré au sort (#434).

Spécification pré-enregistrée dans `PREREG_reproducibility_sample.md`,
committée avant tout tirage.

Question jamais posée : un rapport publié se reproduit-il encore à partir de
son propre code ? Les lots #416-#427 ont vérifié 44 rapports, mais seulement
ceux dont le script venait d'être modifié.

Régime FIXÉ AVANT EXÉCUTION : chaque rapport est sauvegardé, le script
ré-exécuté, le rapport comparé puis **restauré à l'identique**. Ce cycle ne
publie aucune correction — il mesure.
"""
import random
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SCRIPTS = Path(__file__).resolve().parent
OUT = RESULTS / "nonml_reproducibility_sample_result.md"

SEED = 20260813        # fixée dans le pré-enregistrement
SAMPLE_SIZE = 12       # fixée dans le pré-enregistrement
TIMEOUT_S = 300        # fixé dans le pré-enregistrement

# Chronometres avant le pre-enregistrement, pour dimensionner le delai.
# Ils restent dans le tirage ; leur presence eventuelle est signalee.
PRE_KNOWN = {"halloween_effect", "turn_of_month", "sma50_trend_overlay"}


def eligible():
    """Scripts de backtest possédant un rapport de résultat."""
    out = []
    for s in sorted(SCRIPTS.glob("nonml_*_backtest.py")):
        name = s.name.replace("nonml_", "").replace("_backtest.py", "")
        if (RESULTS / f"nonml_{name}_result.md").exists():
            out.append(name)
    return out


def main():
    pool = eligible()
    rng = random.Random(SEED)
    sample = sorted(rng.sample(pool, min(SAMPLE_SIZE, len(pool))))

    L = ["# Reproductibilité des rapports publiés — échantillon tiré au sort (pré-enregistré)", ""]
    L.append("Cycle d'**inventaire**. Aucune stratégie évaluée, aucun verdict recalculé,")
    L.append("aucun paramètre touché, **aucun rapport publié modifié**.")
    L.append("")
    L.append("Question jamais posée : un rapport publié se reproduit-il encore à partir de son")
    L.append("propre code ? Les lots #416-#427 ont vérifié **44** rapports, mais seulement ceux")
    L.append("dont le script venait d'être modifié.")
    L.append("")
    L.append("## Tirage")
    L.append("")
    L.append(f"- scripts éligibles (backtest **et** rapport publié) : **{len(pool)}**")
    L.append(f"- graine, fixée au pré-enregistrement : **{SEED}**")
    L.append(f"- taille de l'échantillon : **{len(sample)}**")
    L.append(f"- délai maximal par script : **{TIMEOUT_S} s**")
    L.append("")
    L.append("Échantillon tiré, publié **avant** les résultats individuels :")
    L.append("")
    for n in sample:
        mark = " — *chronométré avant le pré-enregistrement*" if n in PRE_KNOWN else ""
        L.append(f"- `{n}`{mark}")
    L.append("")
    n_pre = len(set(sample) & PRE_KNOWN)
    if n_pre:
        L.append(f"**{n_pre}** des {len(sample)} avaient été chronométrés avant le")
        L.append("pré-enregistrement pour dimensionner le délai, et s'étaient reproduits. Ils")
        L.append("sont restés dans le tirage — les exclure l'aurait biaisé — mais leur résultat")
        L.append("était **connu d'avance** et ne doit pas compter comme une vérification neuve.")
    else:
        L.append("Aucun des 3 scripts chronométrés avant le pré-enregistrement n'a été tiré :")
        L.append("l'échantillon est intégralement neuf.")
    L.append("")

    # --- Mesure -----------------------------------------------------------
    tmp = Path(tempfile.mkdtemp(prefix="repro_"))
    identical, divergent, inconclusive = [], [], []

    for name in sample:
        rep = RESULTS / f"nonml_{name}_result.md"
        backup = tmp / rep.name
        shutil.copy2(rep, backup)
        t0 = time.time()
        try:
            r = subprocess.run([sys.executable, str(SCRIPTS / f"nonml_{name}_backtest.py")],
                               capture_output=True, text=True, timeout=TIMEOUT_S)
            dt = time.time() - t0
            if r.returncode != 0:
                inconclusive.append((name, f"code {r.returncode}",
                                     (r.stderr.strip().splitlines() or ["—"])[-1][:160]))
            elif rep.read_bytes() == backup.read_bytes():
                identical.append((name, dt))
            else:
                a = backup.read_text(encoding="utf-8").splitlines()
                b = rep.read_text(encoding="utf-8").splitlines()
                n_diff = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
                divergent.append((name, dt, n_diff))
        except subprocess.TimeoutExpired:
            inconclusive.append((name, f"délai > {TIMEOUT_S} s", "—"))
        finally:
            # RESTAURATION systematique : ce cycle ne publie aucune correction.
            shutil.copy2(backup, rep)

    # --- Résultats --------------------------------------------------------
    L.append("## Résultat")
    L.append("")
    L.append("| | Nombre |")
    L.append("|---|---|")
    L.append(f"| rapports **identiques** octet à octet | **{len(identical)}** |")
    L.append(f"| rapports **divergents** | **{len(divergent)}** |")
    L.append(f"| **non concluants** (délai / erreur) | **{len(inconclusive)}** |")
    L.append("")
    tested = len(identical) + len(divergent)
    if tested:
        L.append(f"**Taux de reproductibilité sur les {tested} scripts effectivement testés : "
                 f"{100*len(identical)/tested:.1f} %.**")
    L.append("")
    if identical:
        L.append("### Identiques")
        L.append("")
        L.append("| Script | Durée |")
        L.append("|---|---|")
        for n, dt in sorted(identical):
            mark = " *(connu d'avance)*" if n in PRE_KNOWN else ""
            L.append(f"| `{n}`{mark} | {dt:.1f} s |")
        L.append("")
    if divergent:
        L.append("### Divergents — le rapport publié ne correspond plus à son code")
        L.append("")
        L.append("| Script | Durée | Lignes différentes |")
        L.append("|---|---|---|")
        for n, dt, nd in sorted(divergent):
            L.append(f"| `{n}` | {dt:.1f} s | {nd} |")
        L.append("")
        L.append("**Ces divergences ne sont pas committées.** Le rapport d'origine a été")
        L.append("restauré : corriger un résultat publié est une opération distincte, qui")
        L.append("mériterait son propre pré-enregistrement et son propre régime déclaré.")
        L.append("")
    if inconclusive:
        L.append("### Non concluants")
        L.append("")
        L.append("| Script | Raison | Détail |")
        L.append("|---|---|---|")
        for n, why, det in sorted(inconclusive):
            L.append(f"| `{n}` | {why} | {det} |")
        L.append("")
        L.append("Comptés **ni comme réussite ni comme échec**, conformément au")
        L.append("pré-enregistrement.")
        L.append("")

    L.append("## Portée — ce que 12 tirages disent, et ne disent pas")
    L.append("")
    L.append(f"L'échantillon couvre **{len(sample)}** scripts sur **{len(pool)}** éligibles, soit")
    L.append(f"**{100*len(sample)/len(pool):.1f} %**. Un résultat sur 12 tirages ne prouve rien")
    L.append("sur les 276 autres : il indique seulement s'il existe un problème **massif** ou")
    L.append("**fréquent**. Une divergence rare passerait au travers.")
    L.append("")
    L.append("Le tirage étant aléatoire à graine fixée, il est **reproductible et non choisi**.")
    L.append("")

    shutil.rmtree(tmp, ignore_errors=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"Écrit dans {OUT}")


if __name__ == "__main__":
    main()
