"""Derived Owner view, V3 live telemetry and local pause/resume; this server is not a scheduler."""
import html
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .engine import Lab, question_due
from .seed import BRANCH, REPO
from .store import Refused


def clean(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def _session_time(session):
    return (session.get("finished_at") or session.get("recovered_at") or
            session.get("heartbeat_at") or session.get("started_at") or "")


def live_state(state, control, now=None, discovery=None):
    """Small machine-readable contract for the room/site; derived, never authority."""
    now = now or datetime.now(timezone.utc)
    from .worker import queue
    from .planning import project
    work = queue(state, control, now)
    plan = project(state, control, now)
    if control["paused"]:
        operational = "PAUSED"
    elif work["counts"]["recovery"]:
        operational = "RECOVERY_NEEDED"
    elif work["counts"]["in_progress"]:
        operational = "WORKING"
    elif work["counts"]["ready"] or plan["status"] == "READY_TO_QUALIFY":
        operational = "READY"
    elif work["counts"]["scheduled"]:
        operational = "WAITING_FOR_DATE"
    else:
        operational = "IDLE_NO_ADMISSIBLE_WORK"
    active = next(iter(work["groups"]["recovery"] or work["groups"]["in_progress"]), None)
    sessions = list(state.get("worker_sessions", {}).values())
    completed = [s for s in sessions if s.get("status") == "COMPLETED"]
    last_completed = max(completed, key=_session_time, default=None)
    scheduled = [s for s in sessions if s.get("context") == "scheduled-automation"]
    last_scheduled = max(scheduled, key=_session_time, default=None)
    passes = len(scheduled)
    proof = ("MULTIPLE_SCHEDULED_PASSES_OBSERVED" if passes >= 2 else
             "SINGLE_SCHEDULED_PASS_OBSERVED" if passes == 1 else "NO_SCHEDULED_PASS_OBSERVED")
    if active:
        next_action = active.get("next") or active.get("question")
    elif work["groups"]["ready"]:
        next_action = work["groups"]["ready"][0].get("next") or work["groups"]["ready"][0].get("question")
    elif plan.get("next_option"):
        next_action = plan["next_option"]["question"]
    else:
        next_action = None
    tick = state["scheduler"].get("last_tick") or {}
    value = {"schema": 3, "generated_at": now.isoformat(), "state_updated_at": state.get("updated_at"),
        "operational_status": operational, "paused": control["paused"],
        "scheduler": {"enabled": state["scheduler"].get("enabled"), "last_tick_at": tick.get("at"),
            "last_tick_actor": tick.get("actor"), "last_tick_status": tick.get("status"),
            "configured_at": state["scheduler"].get("enabled_confirmed_at")},
        "autonomy": {"proof": proof, "scheduled_passes_recorded": passes,
            "last_scheduled_session_at": _session_time(last_scheduled) if last_scheduled else None,
            "last_scheduled_session_id": last_scheduled.get("id") if last_scheduled else None,
            "delivery_verified": bool(last_scheduled and last_scheduled.get("delivery_verified")),
            "meaning": "Observed scheduled sessions prove passages, not permanent daemon uptime."},
        "active_task": ({"id": active["id"], "status": active["status"], "claim_id": active.get("claim_id"),
            "question": active.get("question"), "next": active.get("next")} if active else None),
        "last_completed": ({"session_id": last_completed.get("id"), "question_id": last_completed.get("question_id"),
            "finished_at": last_completed.get("finished_at"), "decision_status": last_completed.get("decision_status")}
            if last_completed else None),
        "queue": work["counts"], "planning_status": plan["status"],
        "research_options_pending": len(plan["pending"]), "research_options_consumed": len(plan["consumed"]),
        "next_action": next_action, "next_due_at": plan.get("next_due_at"),
        "real_capital_authorized": False, "live_trading_authorized": False}
    value["validation"] = {"status": operational, "counts": work["counts"], "active_task": value["active_task"]}
    if discovery is not None:
        from .discovery import project as discovery_project
        view = discovery_project(discovery, control, now)
        value["discovery"] = view
        value["operational_status"] = view["status"]
    return value


def markdown(directory):
    lab = Lab(directory)
    state, control = lab.snapshot()
    return markdown_state(state, control)


def markdown_state(state, control, discovery=None):
    """Pure projection, also usable while the writer holds the state lock."""
    tick = state["scheduler"]["last_tick"] or {}
    from .worker import queue
    from .planning import project
    work = queue(state, control)
    plan = project(state, control)
    live = live_state(state, control)
    due = [(k, v) for k, v in state["decisions"].items() if question_due(v)]
    decision = None if control["paused"] else min(due, key=lambda x: (x[1]["priority"], x[1]["created_at"], x[0]), default=None)
    active = live["active_task"]
    lines = ["# Quant — labo de recherche V3", "",
             "**État opérationnel V3 : " + live["operational_status"] + "**",
             "", "Le statut opérationnel combine file, lease worker et planificateur ; le dernier tick seul ne pilote plus l'affichage.",
             "", f"Dernier cycle attesté : `{tick.get('at', 'NON OBSERVÉ')}` ; acteur `{tick.get('actor', 'aucun')}` ; statut tick `{tick.get('status', 'aucun')}`.",
             (f"Rappels désactivés (confirmation outil) : `{state['scheduler'].get('disabled_confirmed_at')}`."
              if state['scheduler'].get('enabled') is False else
              f"Worker de recherche programmé : configuration observée `{state['scheduler']['enabled_confirmed_at'] or 'NON CONFIRMÉ'}`."),
             "", "## Autonomie observable V3", "",
             f"Preuve : `{live['autonomy']['proof']}` ; passages scheduled enregistrés : **{live['autonomy']['scheduled_passes_recorded']}**.",
             f"Dernière session scheduled : `{live['autonomy']['last_scheduled_session_at'] or 'NON OBSERVÉE'}` ; delivery_verified=`{str(live['autonomy']['delivery_verified']).lower()}`.",
             "Une session scheduled enregistrée prouve un passage ; elle ne prouve pas à elle seule un daemon permanent. La salle doit afficher cette nuance.",
             f"Flux machine de salle : [`LIVE.json`]({REPO}/blob/{BRANCH}/research/edge_lab/LIVE.json).",
             "", f"[Pause/reprise persistante : modifier `paused` dans CONTROL.json]({REPO}/edit/{BRANCH}/research/edge_lab/CONTROL.json)",
             "La pause empêche tout nouveau travail.",
             "", "## Travail courant", "",
             (f"`{active['id']}` — **{active['status']}** — claim `{active.get('claim_id')}` — {clean(active.get('next') or active.get('question'))}" if active else
              "Aucun travail actif."),
             "", "## Prochaine décision utile", "",
             (("Construction : " if decision[1].get("reason") == "CONSTRUCTION_ADMISSION" else "")
              + decision[1]["question"] + " (`" + decision[0] + "`)") if decision else
             (plan["next_option"]["question"] + " — à prendre avec worker-start/CAS." if plan["next_option"] else
              "Aucune question admissible due maintenant ; prochaine échéance : " + str(plan["next_due_at"] or "preuve nouvelle requise")),
             "", "## File V3", "",
             f"Prêtes : {work['counts']['ready']} ; différées : {work['counts']['scheduled']} ; en cours : {work['counts']['in_progress']} ; récupération : {work['counts']['recovery']} ; WAIT : {work['counts']['waiting']}.",
             f"Sessions CLI conservées : {len(state.get('worker_sessions', {}))}.",
             f"Investigations documentaires en réserve : {len(plan['pending'])} ; déjà traitées/prélevées : {len(plan['consumed'])}. Pilotage plan : `{plan['status']}`.",
             "", "## Programme et preuves", "", "| Voie | État | Preuve figée | Prochain travail |", "|---|---|---|---|"]
    for identity, family in sorted(state["families"].items(), key=lambda x: x[1]["priority"]):
        sha = family.get("sha")
        proof = f"[{sha[:8]}]({REPO}/tree/{sha})" if sha else "Hypothèse, aucun edge établi"
        lines.append(f"| {clean(family['label'])} | `{family['status']}` | {proof} | {clean(family['next'])} |")
    lines += ["", "## N, essais et fenêtres", "",
              f"Nouveaux looks réservés/consommés par le labo : **{len(state['looks'])}**.",
              "Les jours/instruments/routes corrélés ne sont pas convertis en observations indépendantes.",
              "M effectif et expositions privées : UNKNOWN. Aucun seuil historique ni Sharpe cible modifié.",
              "", "| Jeu de données | Essais historiques déclarés | Nouveaux chemins chargés | Historique complet ? |", "|---|---:|---:|---|"]
    datasets = set(state["baseline"]) | set(state["trial_charges"])
    for dataset in sorted(datasets):
        base = state["baseline"].get(dataset, {})
        trials = base.get("declared_trials")
        lines.append(f"| {dataset} | {trials if trials is not None else 'UNKNOWN'} | {state['trial_charges'].get(dataset, 0)} | {'oui' if base.get('history_complete') else 'UNKNOWN'} |")
    lines += ["", "40 = B2 36 + B4 4 pour le même panel, sans double addition. Les fenêtres protégées et réservations F1 restent fermées.",
              "", "## Coût et limites", "", "| Mesure | Valeur |", "|---|---|"]
    labels = {"paid_usd": "Dépenses autorisées/engagées USD", "tokens": "Tokens", "cpu_seconds": "CPU mesuré des opérations locales",
              "wall_seconds": "Durée mesurée des opérations locales", "metadata_bytes": "Octets de payload de métadonnées",
              "network_bytes": "Trafic réseau total", "human_seconds": "Temps humain"}
    for name, label in labels.items():
        value = state["usage"][name]
        lines.append(f"| {label} | {round(value, 4) if isinstance(value, float) else value if value is not None else 'NON MESURÉ'} |")
    lines += ["", control["notes"], "", "Aucun achat, capital réel ou trading live autorisé. Coût du polling du modèle et facture totale NON MESURÉS.",
              "Claude : pas de revue simulée ; contradiction ciblée après disponibilité, sans seconde boucle.",
              "", "## Exécutions et apprentissages", ""]
    for identity, item in state["decisions"].items():
        if item["status"] == "OPEN" and not question_due(item):
            lines.append(f"- `{identity}` : reprise programmée après `{item['not_before']}` ; aucun probe anticipé.")
    for job in state["jobs"].values():
        lines.append(f"- `{job['task_id']}` : `{job['status']}` ; look `{job['metadata']['look_id']}`.")
    if not state["jobs"]:
        lines.append("Aucun worker économique exécuté. La qualification et la veille ne sont pas un backtest.")
    for identity, item in state["decisions"].items():
        if item["status"] != "OPEN":
            next_action = item.get("next_action", item["question"])
            lines.append(f"- `{identity}` : **{item['status']}** — {clean(next_action)} ; preuves {', '.join(item['evidence'])}.")
    lines += ["", "Les verdicts économiques importés conservent leur portée. Source inaccessible, manque de puissance et défaut logiciel restent distincts.",
              "", f"[Audit et méthodes externes]({state['imported']['audit']}) · [Fonctionnement et reprise](README.md)", ""]
    content = "\n".join(lines)
    if discovery is not None:
        from .discovery import project as discovery_project
        view = discovery_project(discovery, control)
        pending = view.get("next")
        content = ("# Quant — Discovery V4.2 / Validation V3\n\n"
                   + f"Discovery : **{view['status']}** ; Validation : **{live['operational_status']}**.\n\n"
                   + "Prochain test : " + (pending["id"] if pending else "aucun test admissible") + ".\n\n"
                   + f"Tests économiques terminés : {discovery.get('metrics', {}).get('completed_economic_tests', 0)}. "
                   + "Les fichiers acquis et contrôles logiciels ne sont pas des résultats économiques.\n\n"
                   + content)
    return content


def render(directory):
    root = Path(directory)
    lab = Lab(directory)
    state, control = lab.snapshot()
    status = root / "STATUS.md"
    discovery = None
    if (root / "discovery/STATE.json").exists():
        from .discovery import load
        discovery = load(root / "discovery")
    content = markdown_state(state, control, discovery)
    live = live_state(state, control, discovery=discovery)
    status.write_text(content)
    (root / "LIVE.json").write_text(json.dumps(live, ensure_ascii=False, indent=2) + "\n")
    return status


def server(directory, port=8765):
    lab = Lab(directory)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, code, content, kind="text/html; charset=utf-8"):
            body = content.encode()
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            host = f"127.0.0.1:{self.server.server_port}"
            if self.headers.get("Host") != host:
                return self.reply(403, "Local host required")
            if self.path == "/api/state":
                state, control = lab.snapshot()
                return self.reply(200, json.dumps({"state": state, "control": control}), "application/json")
            if self.path == "/api/live":
                return self.reply(200, json.dumps(live_state(*lab.snapshot()), ensure_ascii=False), "application/json")
            if self.path != "/":
                return self.reply(404, "Not found")
            page = """<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
            <title>Quant — recherche V3</title><style>body{font:16px system-ui;max-width:1100px;margin:2em auto;padding:0 1em;background:#101b29;color:#e2eaf4}pre{white-space:pre-wrap;font:14px/1.6 system-ui}button{padding:.7em 1.3em;margin-right:1em;background:#b1dbcf;border:0;border-radius:5px}</style>
            <h1>Quant — recherche V3</h1><form action="/control/pause" method="post"><button>Pause persistante</button></form>
            <form action="/control/resume" method="post"><button>Reprendre</button></form><p>La vue reflète l'état enregistré. Recharger pour voir le dernier cycle.</p><pre>"""
            self.reply(200, page + html.escape(markdown(directory)) + "</pre></html>")

        def do_POST(self):
            expected = f"http://127.0.0.1:{self.server.server_port}"
            if self.headers.get("Origin") != expected or self.headers.get("Host") != expected.removeprefix("http://"):
                return self.reply(403, "Same-origin local control required")
            if self.path not in ("/control/pause", "/control/resume"):
                return self.reply(404, "Not found")
            if int(self.headers.get("Content-Length", "0")) > 1024:
                return self.reply(413, "Too large")
            try:
                lab.store.pause(self.path.endswith("pause"), "Owner local panel")
                render(directory)
                self.reply(200, '<p>Contrôle enregistré. <a href="/">Retour</a></p><p>Publier CONTROL.json sur la branche pour piloter le scheduler distant.</p>')
            except Refused as exc:
                self.reply(409, html.escape(str(exc)))

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)
