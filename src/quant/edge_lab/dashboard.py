"""Derived Owner view and local pause/resume; this server is not a scheduler."""
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .engine import Lab
from .seed import BRANCH, REPO
from .store import Refused


def clean(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def markdown(directory):
    lab = Lab(directory)
    state, control = lab.snapshot()
    return markdown_state(state, control)


def markdown_state(state, control):
    """Pure projection, also usable while the writer holds the state lock."""
    tick = state["scheduler"]["last_tick"] or {}
    due = [(k, v) for k, v in state["decisions"].items() if v["status"] == "OPEN"]
    decision = None if control["paused"] else min(due, key=lambda x: (x[1]["priority"], x[1]["created_at"], x[0]), default=None)
    lines = ["# Quant — labo de recherche", "",
             "**État : " + ("PAUSED" if control["paused"] else tick.get("status", "NOT_STARTED")) + "**",
             "", "Un état IDLE/BLOCKED est normal lorsqu'aucun travail économique n'est admissible.",
             "", f"Dernier cycle attesté : `{tick.get('at', 'NON OBSERVÉ')}` ; acteur `{tick.get('actor', 'aucun')}`.",
             f"Scheduler activé (confirmation outil) : `{state['scheduler']['enabled_confirmed_at'] or 'NON CONFIRMÉ'}`.",
             "L'activité d'un worker économique est attestée par une réservation et un reçu d'exécution, pas un commit récent.",
             "", f"[Pause/reprise persistante : modifier `paused` dans CONTROL.json]({REPO}/edit/{BRANCH}/research/edge_lab/CONTROL.json)",
             "La pause empêche tout nouveau travail. Le scheduler reste chargé de lire ce contrôle ; sa désactivation arrête aussi ses réveils.",
             "", "## Prochaine décision utile", "",
             (("Construction : " if decision[1].get("reason") == "CONSTRUCTION_ADMISSION" else "")
              + decision[1]["question"] + " (`" + decision[0] + "`)") if decision else "Aucune question ouverte ; attendre une preuve ou un accès nouveau.",
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
    return "\n".join(lines)


def render(directory):
    path = Path(directory) / "STATUS.md"
    content = markdown(directory)
    # Derived view; never the authority for pause, jobs or statistical accounting.
    path.write_text(content)
    return path


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
            if self.path != "/":
                return self.reply(404, "Not found")
            page = """<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
            <title>Quant — recherche</title><style>body{font:16px system-ui;max-width:1100px;margin:2em auto;padding:0 1em;background:#101b29;color:#e2eaf4}pre{white-space:pre-wrap;font:14px/1.6 system-ui}button{padding:.7em 1.3em;margin-right:1em;background:#b1dbcf;border:0;border-radius:5px}</style>
            <h1>Quant — recherche</h1><form action="/control/pause" method="post"><button>Pause persistante</button></form>
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
