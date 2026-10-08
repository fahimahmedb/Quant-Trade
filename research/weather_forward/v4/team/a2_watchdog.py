#!/usr/bin/env python3
"""Garde-fou d'equipe A2 : detecte ce que personne ne regarde. Deterministe, sans modele, sans etat local.

Lit les commentaires de la PR #22 et la file de travail ; applique des regles fixes ; imprime des lignes `ACTION: ...`.
Usage : python3 a2_watchdog.py [PR=22] [repo=fahimahmedb/Quant-Trade]
Codes de sortie : 0 = rien a faire (OK ou STOP d'Owner actif) ; 10 = au moins une ACTION ; 2 = lecture impossible.

Formats (A2_OPERATING_LOOP.md point 11) :
  entete  `[A2-TEAM] DE: <builder|orchestrateur> → À: <destinataire(s)>`
  attente `ATTENTE[id]: <objet> avant AAAA-MM-JJTHH:MMZ`  (UTC). Avec `[id]`, seule une reponse du destinataire qui contient
          cet id clot l'attente ; sans `[id]` (ancien format), tout message ulterieur du destinataire la clot (plus faible).
  Owner   un commentaire d'Owner SANS entete `[A2-TEAM]` dont la premiere ligne est `STOP` arrete le garde-fou ; `REPRISE` le relance.
Idempotence sans etat local : chaque ACTION porte une cle ; si un commentaire `RAPPEL watchdog <cle>` existe deja, la relance n'est
pas reemise et l'attente non satisfaite passe en `ALERT_OWNER` (une seule fois par cle, `ALERT_OWNER watchdog <cle>`).
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

OWNER_LOGIN = "fahimahmedb"
HEADER = re.compile(r"\[A2-TEAM\]\s+DE:\s*(\w+)\s*(?:→|->)\s*(?:À|A|Á):\s*([^\n]+)")
WAIT = re.compile(r"^ATTENTE(?:\[([\w.-]+)\])?:\s*(.+?)\s+avant\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})Z", re.M)
ASK = re.compile(r"^DEMANDE:\s*(?!aucune\b)\S", re.M | re.I)
STOP = re.compile(r"\A\s*STOP\b")
RESUME = re.compile(r"\A\s*REPRISE\b")
SILENCE_PING = timedelta(hours=3)
SILENCE_ALERT = timedelta(hours=6)
AGENTS = {"builder", "orchestrateur"}


def parse_time(text):
    return datetime.strptime(text.replace("Z", "")[:16], "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)


def owner_stopped(comments):
    state = False
    for c in sorted(comments, key=lambda c: c["id"]):
        body = c.get("body", "")
        if (c.get("user") or {}).get("login") != OWNER_LOGIN or HEADER.search(body):
            continue
        if STOP.search(body):
            state = True
        elif RESUME.search(body):
            state = False
    return state


def messages(comments):
    out = []
    for c in sorted(comments, key=lambda c: c["id"]):
        body = c.get("body", "")
        m = HEADER.search(body)
        if not m or m.group(1).lower() not in AGENTS:
            continue
        targets = {t.strip().lower() for t in re.split(r"[,/]", m.group(2).split("\n")[0])}
        out.append({"id": c["id"], "at": parse_time(c["created_at"]), "sender": m.group(1).lower(), "targets": targets,
                    "body": body, "asks": ASK.search(body) is not None,
                    "waits": [(i, o, parse_time(d)) for i, o, d in WAIT.findall(body)]})
    return out


def done_keys(comments):
    pinged, alerted = set(), set()
    for c in comments:
        body = c.get("body", "")
        pinged.update(re.findall(r"RAPPEL watchdog (\S+)", body))
        alerted.update(re.findall(r"ALERT_OWNER watchdog (\S+)", body))
    return pinged, alerted


def tag_for(agent):
    return "PING_CODEX" if agent == "orchestrateur" else "WAKE_BUILDER"


def evaluate(comments, now, open_work):
    if owner_stopped(comments):
        return []
    msgs = messages(comments)
    pinged, alerted = done_keys(comments)
    raw = []  # (cle, agent_attendu, texte)
    for i, m in enumerate(msgs):
        for wid, objet, deadline in m["waits"]:
            if now <= deadline:
                continue
            for target in sorted(m["targets"] & AGENTS):
                later = [x for x in msgs[i + 1:] if x["sender"] == target]
                answered = any(wid in x["body"] for x in later) if wid else bool(later)
                if not answered:
                    raw.append((f"{target}:{m['id']}:{wid or 'x'}", target,
                                f"attente de {m['sender']} sans reponse (commentaire {m['id']}, '{objet}', echeance {deadline:%Y-%m-%dT%H:%MZ})"))
    for agent in sorted(AGENTS):
        asked = [x for x in msgs if agent in x["targets"] and x["sender"] != agent and x["asks"] and not x["waits"]]
        # Une demande qui porte une ATTENTE est suivie par sa propre echeance (pas de doublon avec la regle des 3 h).
        last_own = max((x["at"] for x in msgs if x["sender"] == agent), default=None)
        if asked and (last_own is None or last_own < asked[-1]["at"]) and now - asked[-1]["at"] > SILENCE_PING:
            raw.append((f"{agent}:{asked[-1]['id']}:silence", agent,
                        f"{agent} sollicite par {asked[-1]['sender']} (commentaire {asked[-1]['id']}) sans reponse depuis plus de 3 h"))
    actions, seen = [], set()
    for key, agent, text in raw:
        if key in seen:
            continue
        seen.add(key)
        if f"PING:{key}" not in pinged:
            actions.append(f"ACTION: {tag_for(agent)} [cle=PING:{key}] {text}")
        elif f"ALERT:{key}" not in alerted:
            actions.append(f"ACTION: ALERT_OWNER [cle=ALERT:{key}] relance deja emise sans effet : {text}")
    newest = max(msgs, key=lambda x: x["at"], default=None)
    if open_work and newest and now - newest["at"] > SILENCE_ALERT and f"ALERT:team:{newest['id']}" not in alerted:
        actions.append(f"ACTION: ALERT_OWNER [cle=ALERT:team:{newest['id']}] equipe muette depuis plus de 6 h avec du travail ouvert")
    return actions


def gh_json(path):
    r = subprocess.run(["gh", "api", path, "--paginate"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ECHEC lecture GitHub : {r.stderr.strip()[:160]}", file=sys.stderr)
        sys.exit(2)
    return json.loads(r.stdout.replace("][", ","))


def open_work_in(queue_text):
    return any(l.startswith("| Q") and not any(s in l for s in ("| DONE", "OWNER_GATED", "| BLOCKED"))
               for l in queue_text.splitlines())


def main():
    pr = sys.argv[1] if len(sys.argv) > 1 else "22"
    repo = sys.argv[2] if len(sys.argv) > 2 else "fahimahmedb/Quant-Trade"
    comments = gh_json(f"repos/{repo}/issues/{pr}/comments?per_page=100")
    r = subprocess.run(["gh", "api", f"repos/{repo}/contents/research/weather_forward/v4/team/A2_WORK_QUEUE.md"
                        "?ref=team/weather-v4-a2-coordination-2026-10-08", "-H", "Accept: application/vnd.github.raw+json"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ECHEC lecture de la file : {r.stderr.strip()[:160]}", file=sys.stderr)
        sys.exit(2)
    if owner_stopped(comments):
        print("STOP_OWNER actif : aucune action")
        sys.exit(0)
    actions = evaluate(comments, datetime.now(timezone.utc), open_work_in(r.stdout))
    for a in actions:
        print(a)
    print("OK" if not actions else f"{len(actions)} action(s)")
    sys.exit(10 if actions else 0)


if __name__ == "__main__":
    main()
