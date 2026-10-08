#!/usr/bin/env python3
"""Etat d'equipe A2 en une commande : file de travail + tetes de branches + changements depuis le dernier passage.

Lecture seule (git fetch + git rev-parse/log). Aucune ecriture dans le depot, aucun reseau hors `git fetch`.
Usage : python3 research/weather_forward/v4/team/a2_team_status.py [chemin_marqueur]
Le marqueur memorise les tetes vues au dernier passage (defaut : $TMPDIR/a2_team_seen.json).
"""
import json
import os
import subprocess
import sys
import tempfile

QUEUE_BRANCH = "team/weather-v4-a2-coordination-2026-10-08"
QUEUE_PATH = "research/weather_forward/v4/team/A2_WORK_QUEUE.md"
BRANCHES = [
    QUEUE_BRANCH,
    "builder/weather-v4-a2-lot2-tooling-2026-10-07",
    "builder/weather-v4-a2-doc-integration-root-candidate-2026-10-08",
    "builder/weather-v4-a2-lot2-l2i-verification-2026-10-08",
    "builder/weather-v4-a2-lot2-l2j-dossier-2026-10-08",
    "astra/weather-v4-a2-lot3-independent-review-2026-10-08",
]


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def main():
    marker = sys.argv[1] if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "a2_team_seen.json")
    git("fetch", "-q", "origin", *BRANCHES)
    try:
        seen = json.load(open(marker, encoding="utf-8"))
    except (OSError, ValueError):
        seen = {}
    now = {}
    print("== Branches (NOUVEAU = tete differente du dernier passage) ==")
    for b in BRANCHES:
        rc, sha = git("rev-parse", "--verify", "-q", f"origin/{b}")
        if rc != 0:
            print(f"  absente      {b}")
            continue
        now[b] = sha
        _, subj = git("log", "-1", "--format=%an | %s", sha)
        flag = "NOUVEAU" if seen.get(b) != sha else "inchange"
        print(f"  {flag:9} {sha[:8]} {b}\n            {subj[:110]}")
    print("\n== File de travail : taches non DONE ==")
    rc, q = git("show", f"origin/{QUEUE_BRANCH}:{QUEUE_PATH}")
    ready = []
    for line in q.splitlines():
        if line.startswith("| Q") and "| DONE" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            status = cells[-1][:90]
            print(f"  {cells[0]:4} {status}")
            if status.startswith("READY"):
                ready.append(cells[0])
    print("\n== Verdict ==")
    if ready:
        print("TACHES READY :", ", ".join(ready), "-> a prendre maintenant, ne pas finir le tour.")
    else:
        print("Aucune tache READY. Si une session enfant est en cours, verifier get_session.")
    json.dump(now, open(marker, "w", encoding="utf-8"))


if __name__ == "__main__":
    main()
