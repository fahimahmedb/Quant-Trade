#!/usr/bin/env python3
"""Garde-fou d'equipe A2 : detecte ce que personne ne regarde. Deterministe, sans modele.

Lit les commentaires de la PR #22 et la file de travail ; applique des regles fixes ; imprime des lignes `ACTION: ...`.
Usage : python3 a2_watchdog.py [PR=22] [repo=fahimahmedb/Quant-Trade]
Codes de sortie : 0 = rien a faire (OK) ; 10 = au moins une ACTION ; 2 = lecture impossible (aucun verdict).
Formats lus (voir A2_OPERATING_LOOP.md point 11) :
  entete `[A2-TEAM] DE: <builder|orchestrateur> -> A: <builder|orchestrateur|Owner...>`
  ligne   `ATTENTE: <objet> avant 2026-10-08T08:30Z`   (UTC, forme ISO complete)
Une attente est close par tout commentaire ulterieur dont l'entete DE: est le destinataire.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

HEADER = re.compile(r"\[A2-TEAM\]\s+DE:\s*(\w+)\s*(?:→|->)\s*(?:À|A|Á):\s*([^\n]+)")
WAIT = re.compile(r"^ATTENTE:\s*(.+?)\s+avant\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})Z", re.M)
SILENCE_PING = timedelta(hours=3)      # un agent muet depuis 3 h alors qu'on l'attend
SILENCE_ALERT = timedelta(hours=6)     # equipe entiere muette depuis 6 h avec du travail ouvert
AGENTS = {"builder", "orchestrateur"}


def parse_time(text):
    return datetime.strptime(text.replace("Z", ""), "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)


def messages(comments):
    """Liste ordonnee de (id, instant, expediteur, destinataires, [(objet, echeance)], demande_reelle)."""
    out = []
    for c in sorted(comments, key=lambda c: c["id"]):
        m = HEADER.search(c.get("body", ""))
        if not m:
            continue
        sender = m.group(1).lower()
        if sender not in AGENTS:
            continue
        targets = {t.strip().lower() for t in re.split(r"[,/]", m.group(2).split("\n")[0])}
        waits = [(o, parse_time(d + "Z")) for o, d in WAIT.findall(c["body"])]
        asks = re.search(r"^DEMANDE:\s*(?!aucune\b)\S", c["body"], re.M | re.I) is not None
        out.append((c["id"], parse_time(c["created_at"][:16]), sender, targets, waits, asks))
    return out


def evaluate(comments, now, open_work):
    msgs = messages(comments)
    actions = []
    last_seen = {a: None for a in AGENTS}
    for _, when, sender, _, _, _ in msgs:
        last_seen[sender] = when
    for i, (cid, when, sender, targets, waits, _) in enumerate(msgs):
        for objet, deadline in waits:
            answered = any(m[2] in targets and m[1] >= when and m[0] != cid for m in msgs[i + 1:])
            if answered or now <= deadline:
                continue
            for target in sorted(targets & AGENTS):
                if target == "orchestrateur":
                    actions.append(f"ACTION: PING_CODEX attente de {sender} sans reponse (commentaire {cid}, '{objet}', echeance {deadline:%Y-%m-%dT%H:%MZ})")
                else:
                    actions.append(f"ACTION: WAKE_BUILDER attente de {sender} sans reponse (commentaire {cid}, '{objet}', echeance {deadline:%Y-%m-%dT%H:%MZ})")
    # Agent attendu mais muet depuis longtemps, sans echeance explicite.
    for agent in sorted(AGENTS):
        seen = last_seen[agent]
        asked = [m for m in msgs if agent in m[3] and m[2] != agent and m[5]]
        if asked and (seen is None or seen < asked[-1][1]) and now - asked[-1][1] > SILENCE_PING:
            tag = "PING_CODEX" if agent == "orchestrateur" else "WAKE_BUILDER"
            line = f"ACTION: {tag} {agent} sollicite par {asked[-1][2]} (commentaire {asked[-1][0]}) sans reponse depuis plus de 3 h"
            if line not in actions and not any(a.startswith(f"ACTION: {tag}") for a in actions):
                actions.append(line)
    newest = max((m[1] for m in msgs), default=None)
    if open_work and newest is not None and now - newest > SILENCE_ALERT:
        actions.append("ACTION: ALERT_OWNER equipe muette depuis plus de 6 h avec du travail ouvert")
    return actions


def gh_json(path):
    r = subprocess.run(["gh", "api", path, "--paginate"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ECHEC lecture GitHub : {r.stderr.strip()[:160]}", file=sys.stderr)
        sys.exit(2)
    text = r.stdout.replace("][", ",")
    return json.loads(text)


def open_work_in(queue_text):
    for line in queue_text.splitlines():
        if line.startswith("| Q") and not any(s in line for s in ("| DONE", "OWNER_GATED", "| BLOCKED")):
            return True
    return False


def main():
    pr = sys.argv[1] if len(sys.argv) > 1 else "22"
    repo = sys.argv[2] if len(sys.argv) > 2 else "fahimahmedb/Quant-Trade"
    comments = gh_json(f"repos/{repo}/issues/{pr}/comments?per_page=100")
    r = subprocess.run(["gh", "api", f"repos/{repo}/contents/research/weather_forward/v4/team/A2_WORK_QUEUE.md?ref=team/weather-v4-a2-coordination-2026-10-08",
                        "-H", "Accept: application/vnd.github.raw+json"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ECHEC lecture de la file : {r.stderr.strip()[:160]}", file=sys.stderr)
        sys.exit(2)
    now = datetime.now(timezone.utc)
    actions = evaluate(comments, now, open_work_in(r.stdout))
    for a in actions:
        print(a)
    print("OK" if not actions else f"{len(actions)} action(s)")
    sys.exit(10 if actions else 0)


if __name__ == "__main__":
    main()
