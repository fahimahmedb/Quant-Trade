#!/usr/bin/env python3
"""Etat d'equipe A2 en une commande : file de travail + tetes de branches + changements depuis le dernier passage.

Aucune ecriture dans le depot. Il fait un `git fetch` (reseau) et ecrit un petit fichier marqueur HORS depot (defaut : $TMPDIR/a2_team_seen.json).
Usage : python3 research/weather_forward/v4/team/a2_team_status.py [chemin_marqueur]
Le marqueur memorise les tetes vues au dernier passage (defaut : $TMPDIR/a2_team_seen.json).
"""
import json
import os
import re
import subprocess
import sys
import tempfile

QUEUE_BRANCH = "team/weather-v4-a2-coordination-2026-10-08"
QUEUE_PATH = "research/weather_forward/v4/team/A2_WORK_QUEUE.md"
CORE_BRANCHES = [
    QUEUE_BRANCH,
    "builder/weather-v4-a2-lot2-tooling-2026-10-07",
    "builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08",
]
TASK_ROW = re.compile(r"^\|\s*[A-Z]+\d+[\w-]*\s*\|")
BRANCH_RE = re.compile(r"`((?:builder|astra|team|owner|blue)/weather-v4-a2-[A-Za-z0-9._-]+)`")


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def git_fetch(branch):
    """(ok, absent) : absent = la branche n'existe pas (normal) ; tout autre echec (reseau, authentification) reste fatal."""
    r = subprocess.run(["git", "fetch", "-q", "origin", branch], capture_output=True, text=True)
    return r.returncode == 0, "couldn't find remote ref" in r.stderr


def main():
    marker = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "a2_team_seen.json")
    rc, _ = git("fetch", "-q", "origin", QUEUE_BRANCH)
    if rc != 0:
        print(f"ECHEC git fetch de {QUEUE_BRANCH} : verdict impossible, marqueur non modifie", file=sys.stderr)
        sys.exit(2)
    rc, q = git("show", f"origin/{QUEUE_BRANCH}:{QUEUE_PATH}")
    if rc != 0 or not q:
        print("ECHEC lecture de la file de travail : verdict impossible, marqueur non modifie", file=sys.stderr)
        sys.exit(2)
    # Branches surveillees = noyau + toute branche nommee dans la file. L'absence d'une branche (jamais creee, ou supprimee
    # apres sa tache) n'est pas un echec ; une erreur reseau ou d'authentification l'est (aucun verdict).
    branches = list(dict.fromkeys(CORE_BRANCHES + BRANCH_RE.findall(q)))
    for b in branches:
        ok, absent = git_fetch(b)
        if not ok and not absent:
            print(f"ECHEC git fetch de {b} : verdict impossible, marqueur non modifie", file=sys.stderr)
            sys.exit(2)
    try:
        seen = json.load(open(marker, encoding="utf-8"))
    except (OSError, ValueError):
        seen = {}
    now = {}
    print("== Branches (NOUVEAU = tete differente du dernier passage) ==")
    for b in branches:
        rc, sha = git("rev-parse", "--verify", "-q", f"origin/{b}")
        if rc != 0:
            print(f"  absente      {b}")
            continue
        now[b] = sha
        _, subj = git("log", "-1", "--format=%an | %s", sha)
        flag = "NOUVEAU" if seen.get(b) != sha else "inchange"
        print(f"  {flag:9} {sha[:8]} {b}\n            {subj[:110]}")
    print("\n== File de travail : taches non DONE ==")
    ready = []
    for line in q.splitlines():
        if TASK_ROW.match(line) and "| DONE" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            status = cells[-1][:90]
            print(f"  {cells[0]:4} {status}")
            if status.startswith("READY"):
                ready.append(cells[0])
    print("\n== Verdict ==")
    if ready:
        print("TACHES READY :", ", ".join(ready), "-> lire la colonne agent : ne prendre que les tiennes, ne pas finir le tour.")
    else:
        print("Aucune tache READY : IDLE est un etat legitime si aucune tache utile n'est due (regle 14). "
              "Si une session enfant est en cours, verifier get_session.")
    json.dump(now, open(marker, "w", encoding="utf-8"))


if __name__ == "__main__":
    main()
