"""Pointers to published facts, not a second copy of market outcomes."""
from quant.state import utc_now
from .store import event

REPO = "https://github.com/fahimahmedb/Quant-Trade"
BRANCH = "research/edge-lab-continuous"
BASE = "09ba64b8bee1419076ec8a30f8d75a916932c2ba"
REPORT = REPO + "/blob/fae3be50549d8b023c3e9a42eb14a51613bcb8c4/research/mission_audit_2026-10-10/REPORT.md"
AUTOMATION = "6ac978ecda1081918fba4d76dee437f4"


def initial_state():
    families = {
        "treasury-auction-zf": {
            "label": "Treasury/ZF — pression d'adjudication", "priority": 1,
            "status": "BLOCKED_DATA_ACCESS", "sha": "5bb78345e0cc9d02ac38c13d2c0981cb380021be",
            "ref": "sol/scout-macro-tauc-gfs", "dataset": "treasury-zf-bbo",
            "next": "Qualifier droits, BBO, rolls PIT et prix du paquet complet ; aucun achat.",
            "wake": "Source primaire couvrant le paquet complet ou accès déjà autorisé vérifié."},
        "eurusd-technical-grid": {
            "label": "EUR/USD — grille technique sur proxy", "priority": 2,
            "status": "FROZEN_NOT_EXECUTED", "sha": "e42d4924a33efa78bab97939d654424cc1501fb8",
            "ref": "research/technical-signals-literature-2026-10-10", "dataset": "eurusd-histdata",
            "freeze": "c891771ddc74adeae95b5492f708ad1c3cc07eca92da78ffe5b5346570d71de2",
            "next": "Réutiliser le gel/harnais ; qualifier proxy, droits et historique d'expositions.",
            "wake": "Admission documentée et réservation publiée ; les 433 jours planifiés ne sont pas consommés au démarrage."},
        "hyperliquid-forced-flow": {
            "label": "Hyperliquid — flux forcés", "priority": 3,
            "status": "BLOCKED_HOST", "sha": "a6961e5fc02785c7c2d797f0e1fca94425150705",
            "ref": "sol/scout-crypto-20261008-1847", "dataset": "hyperliquid-global-fills",
            "next": "Vérifier un hôte qualifié et les global fills ; ne pas substituer trades WS.",
            "wake": "Hôte et budget de collecte/stockage réellement vérifiés."},
        "f1-crypto-carry": {
            "label": "F1 carry crypto", "priority": 99, "status": "REJECTED_CLOSED",
            "sha": "ea9d2d0e0e057199bb168249c963acbc88e89de5",
            "ref": "builder/f1-sealed-stage-b-capture-2026-10-09", "dataset": "crypto-carry-f1",
            "next": "Conserver la disposition publique ; aucune ouverture des outcomes A/B.",
            "wake": "Aucune relance de l'expression gelée."},
        "prediction-negative-risk": {
            "label": "Prediction negative-risk", "priority": 99, "status": "REJECTED_CLOSED",
            "sha": "2b66b1937257651b3a941bba6d7a1e5e45c01137", "ref": "sol/scout-prediction-flb-nr",
            "dataset": "prediction-flb", "next": "Conserver KILL du rerun valide, séparé du premier résultat invalidé.",
            "wake": "Aucune réexécution du test rejeté."},
        "daily-etf-b2-b4": {
            "label": "B2/B4 ETF daily", "priority": 99, "status": "REJECTED_CLOSED",
            "sha": "1e88c6b82d682ae6d6d71b0732cb1bdb232cea3a", "ref": "team/weather-v4-a2-coordination-2026-10-08",
            "dataset": "daily-etf-panel", "next": "Conserver rejets, 40 essais déclarés et shadow non lu.",
            "wake": "Aucune réouverture par renommage ou nouveau fournisseur."},
        "f2-prediction-access": {
            "label": "F2 — accès prediction", "priority": 4, "status": "BLOCKED_PERMISSION",
            "sha": "e7344cfda865b987e57c0d0ad8eb37f4f164cf9e", "ref": "research/f2-primary-terms-decision-2026-10-09",
            "dataset": "prediction-f2", "next": "Attendre une permission explicite ; ce blocage n'est pas un rejet économique.",
            "wake": "Droits d'accès vérifiables."},
        "sec-events": {
            "label": "Form 4/F3 et 13D distinct", "priority": 5, "status": "BLOCKED_DATA_CHAIN",
            "sha": "afd69b74c12d02cb9b8f731137ba5c357819ab24", "ref": "sol/scout-events-f413d",
            "dataset": "sec-equities-pit", "next": "Réutiliser census ; qualifier CIK/security PIT et delist prices.",
            "wake": "Chaîne prix actions et identités admissible."},
    }
    state = {
        "schema": 1, "created_at": utc_now(), "updated_at": utc_now(),
        "real_capital_authorized": False, "live_trading_authorized": False,
        "imported": {"base": BASE, "audit": REPORT, "instructions_sha": "9b2b956961b434b83a038f0bb92d9bec46c1520c",
                     "audit_evidence": REPO + "/blob/fae3be50549d8b023c3e9a42eb14a51613bcb8c4/research/mission_audit_2026-10-10/EVIDENCE.jsonl",
                     "fast_rail": "claude/data-feeds-6vr22g@20cc984c9414155452c3955720d21cd89fa3e4b0 ; 54 entrées, pas 54 essais indépendants ; overlaps UNKNOWN",
                     "public_exposures": "R19 : page produit ZF datée 2026-10-05 et résultats littérature ; EVIDENCE audit conservé ; aucun holdout rendu vierge",
                     "memory": ["research/memory.jsonl", "research/opportunity_map.json", "src/quant/learning/store.py"],
                     "reservations": ["f1/crypto-carry-001-stage-a-look@8d93861edc4e1ff07b6265d4e80e6a429cffd0b7",
                                      "f1/crypto-carry-001-stage-b-look@2620ba065e790b1c255f43bcd941fc336ad5ef4d"],
                     "separate_collector": ".github/workflows/data-feeds.yml — H001 exclu de ce labo"},
        "baseline": {
            "daily-etf-panel": {"declared_trials": 40, "effective_trials": None,
                                "history_complete": False, "source": "STATE_MD_NO_REGISTRY : B2=36 + B4=4, total=40 ; ne pas additionner 40 une seconde fois",
                                "spent": [["2016-09-12", "2022-03-09"], ["2022-03-09", "2025-03-12"]],
                                "protected": [["2025-03-12", "2026-09-12"]]},
            "crypto-carry-f1": {"declared_trials": None, "effective_trials": None, "history_complete": False,
                                "spent": [], "protected": [["0001-01-01", "9999-12-31"]],
                                "source": "Disposition publique uniquement ; Stage B=1004 jours, pas 457 observations indépendantes par jour."},
            "prediction-flb": {"declared_trials": None, "effective_trials": None, "history_complete": False,
                               "spent": [], "protected": [], "source": "1260 routes dépendantes ; rerun valide KILL ; premier run invalide conservé."},
            "eurusd-histdata": {"declared_trials": None, "effective_trials": None, "history_complete": False,
                                "spent": [], "protected": [["2025-02-01", "2026-10-01"]],
                                "source": "Fenêtre réservée au protocole gelé ; MAIN + NO_ADDS + STATIC_GRID, 6 chemins de coûts ; privé UNKNOWN."},
            "treasury-zf-bbo": {"declared_trials": None, "effective_trials": None, "history_complete": False,
                                "spent": [], "protected": [], "source": "Protocole gelé depuis 2015 ; BBO historiques payants manquants."},
        },
        "families": families, "protocols": {}, "looks": {}, "trial_charges": {},
        "evidence": {}, "decisions": {}, "jobs": {}, "sources": {}, "events": [],
        "scheduler": {"id": AUTOMATION, "enabled_confirmed_at": None, "last_tick": None,
                      "external_run": None, "mode": "existing_hourly_automation"},
        "usage": {"paid_usd": 0, "tokens": None, "cpu_seconds": 0.0, "network_bytes": None, "metadata_bytes": 0,
                  "wall_seconds": 0.0, "human_seconds": None},
    }
    event(state, "OWNER_BUILD_AUTHORIZED", {"instruction": "Construction autonome du labo ; protéger N et essais ; aucun capital réel/live/achat.",
                                           "base": BASE, "report": REPORT})
    for family in ("treasury-auction-zf", "eurusd-technical-grid", "hyperliquid-forced-flow"):
        state["decisions"]["qualify:" + family] = {
            "status": "OPEN", "family": family, "priority": families[family]["priority"],
            "question": families[family]["next"], "created_at": utc_now(), "evidence": [],
            "reason": "Décision économique d'accès à partir de l'audit, sans lecture d'outcomes."}
    return state


def initial_control():
    return {"schema": 1, "paused": False, "pause_reason": None, "changed_at": utc_now(),
            "real_capital_authorized": False, "live_trading_authorized": False,
            "limits": {"paid_usd_total": 0, "tokens_total": None, "cpu_seconds_total": None,
                       "job_wall_seconds": 120, "metadata_bytes_per_tick": 2097152},
            "notes": "Pas de budget Owner total chiffré. 120 s/2 MiB sont des bornes techniques par opération, pas une allocation économique. Tokens NON MESURÉS. Aucun quota d'expériences ni Sharpe cible."}
