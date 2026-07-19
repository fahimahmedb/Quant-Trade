"""Source « marches de prediction » (Polymarket / PredictIt / Betfair-like).

Le prix d'un marche de prediction est une probabilite implicite de victoire
au 2nd tour, agregee par des agents qui parient de l'argent reel (ou virtuel
liquide) sur l'issue. Contrairement aux fondamentaux (pp_fundamentals.py),
rien n'est "appris" sur l'historique : le seul traitement applique est un
DEBIAISAGE du biais favori-outsider (favorite-longshot bias), documente comme
un prior fixe issu de la litterature (pas ajuste sur le jeu de test).

Discipline anti-data-snooping : `fit()` est un no-op (voir docstring de
`MarketsSource`). Les marches n'existent pas pour les vieilles elections
(avant l'essor Polymarket/PredictIt/Betfair sur la presidentielle francaise,
en pratique a partir de 2017) : `predict()` renvoie alors
`SourceSignal(..., available=False)`, ce qui est un cas ATTENDU du backtest
OOS (cf. run_etape_P2_marches.py), pas une erreur.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Sequence

import numpy as np

from pp_types import ElectionContext, Source, SourceSignal, TrainingExample, clamp_share

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SNAPSHOT_PATH = DATA / "fr_markets_snapshot.json"

# Timeout court : un backtest ne doit JAMAIS rester bloque sur un appel reseau.
LIVE_TIMEOUT_S = 2.0

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Loader hybride : tentative live (best-effort, timeout court) -> snapshot     #
# --------------------------------------------------------------------------- #


def _fetch_live(election_id: str, timeout: float = LIVE_TIMEOUT_S) -> dict | None:
    """Tentative de recuperation EN DIRECT du prix de marche (best-effort).

    Point d'extension volontairement non cable vers un endpoint precis : les
    URLs/API des marches electoraux Polymarket/PredictIt/Betfair pour une
    election francaise donnee changent trop souvent (marche cree/ferme au
    fil de la campagne) pour etre codees en dur ici sans maintenance
    continue. Brancher ici un vrai appel HTTP le moment venu, avec un
    `timeout` COURT (ne jamais laisser un fetch bloquer le backtest).

    Convention de retour :
    - dict {"p_reference_wins": float, "n_trades_or_volume": float} si un
      prix a reellement ete recupere ;
    - None si aucun marche live n'existe pour cette election (pas une
      erreur : cas normal pour la plupart des `election_id`).

    Toute exception (reseau, DNS, timeout, JSON malforme, ...) doit etre
    laissee remonter : c'est `load_market_prob` qui l'attrape et bascule
    silencieusement sur le snapshot offline.
    """
    raise NotImplementedError(
        "Aucun endpoint live cable dans ce depot : le fallback snapshot "
        "(data/fr_markets_snapshot.json) est la voie normale d'execution."
    )


def load_market_prob(
    election_id: str, snapshot_path: str | Path = SNAPSHOT_PATH
) -> dict | None:
    """Loader HYBRIDE : tente le live (timeout court), sinon lit le snapshot.

    Le fallback est systematique et silencieux (logue en debug) : l'absence
    de reseau, ou l'absence d'endpoint live cable (`_fetch_live` leve
    `NotImplementedError` par defaut, voir sa docstring), ne doit jamais
    faire echouer un script ou un backtest.

    Retourne None si aucune donnee (ni live ni snapshot) n'existe pour
    `election_id` -> la source appelante doit alors se declarer indisponible.
    """
    try:
        live = _fetch_live(election_id, timeout=LIVE_TIMEOUT_S)
        if live is not None:
            return live
    except Exception as exc:  # noqa: BLE001 - tout echec live -> fallback silencieux
        logger.debug(
            "Fetch live marches indisponible pour %s (%s) -> fallback snapshot.",
            election_id, exc,
        )

    raw = json.loads(Path(snapshot_path).read_text())
    return raw.get("markets", {}).get(election_id)


# --------------------------------------------------------------------------- #
# Calibration du biais favori-outsider (favorite-longshot bias)                #
# --------------------------------------------------------------------------- #

# Facteur d'extremisation en espace logit (k > 1). PRIOR FIXE, jamais estime
# sur les elections scorees par le backtest (sinon fuite d'information).
# Justification empirique : la litterature sur les marches de paris et de
# prediction (Wolfers & Zitzewitz 2004 ; Snowberg & Wolfers 2010) documente un
# biais systematique "favorite-longshot" : les prix SOUS-estiment les favoris
# et SUR-estiment les outsiders (prime payee pour le gain "loterie" improbable
# de l'outsider). Le marche compresse donc les probabilites vers 0.5 par
# rapport a la verite ; on corrige en les repoussant plus loin de 0.5.
FAVORITE_LONGSHOT_K = 1.15

# Pente de conversion probabilite (debiaisee) -> part de vote 2nd tour. Une
# quasi-certitude de marche (p~0.9) correspond historiquement a une victoire
# confortable mais pas ecrasante (66% pour Macron en 2017 avec p_marche~0.87,
# pas 90%+ des voix) : le mapping est volontairement amorti (slope < 1).
# PRIOR FIXE, non ajuste sur le test.
SHARE_SLOPE_K = 0.35

# Incertitude fixe attribuee a la source marches : un prix liquide agrege de
# l'information et reste, en general, un estimateur assez fiable -> sd
# modeste (0.03-0.05), nettement plus bas que les priors "sans information"
# (0.08, cf. pp_fundamentals.py).
MARKET_SD = 0.04


def debias_favorite_longshot(p: float, k: float = FAVORITE_LONGSHOT_K) -> float:
    """Corrige le biais favori-outsider par extremisation en espace logit.

        p_debiased = sigmoid(k * logit(p)),  k > 1

    k > 1 eloigne p de 0.5 (favori pousse vers 1, outsider pousse vers 0),
    ce qui corrige la compression documentee des prix de marche vers le
    centre. `k` est un prior fixe (voir FAVORITE_LONGSHOT_K), jamais recalibre
    sur les elections que le backtest note.
    """
    p = min(max(float(p), 1e-6), 1 - 1e-6)
    logit_p = np.log(p / (1 - p))
    debiased_logit = k * logit_p
    return float(1.0 / (1.0 + np.exp(-debiased_logit)))


def prob_to_share(p_debiased: float, slope: float = SHARE_SLOPE_K) -> float:
    """Convertit une probabilite de victoire debiaisee en part de vote 2nd tour.

    Mapping monotone amorti : share = 0.5 + slope * (p_debiased - 0.5), puis
    `clamp_share` (bornes de securite communes du contrat). slope < 1 evite
    de traduire une quasi-certitude de marche en score plebiscitaire
    improbable.
    """
    share = 0.5 + slope * (p_debiased - 0.5)
    return clamp_share(share)


# --------------------------------------------------------------------------- #
# Source                                                                        #
# --------------------------------------------------------------------------- #


class MarketsSource:
    """Source « marches de prediction » : lit un prix de marche et le debiaise.

    Contrairement aux fondamentaux (regression entrainee sur l'historique),
    un prix de marche est deja une agregation d'information par des agents
    qui engagent de l'argent : il n'y a rien a "apprendre" sur les elections
    passees. `fit()` est donc un NO-OP explicite : le seul traitement
    applique (debiaisage favori-outsider) est un prior fixe issu de la
    litterature empirique, pas un parametre estime sur le jeu de test -> la
    discipline anti-data-snooping du backtest OOS (pp_backtest.py) reste
    respectee meme si `fit()` ne fait rien d'utile.
    """

    name: str = "markets"

    def __init__(self, snapshot_path: str | Path = SNAPSHOT_PATH):
        self.snapshot_path = snapshot_path

    def fit(self, history: Sequence[TrainingExample]) -> "MarketsSource":
        """No-op (voir docstring de classe) : `history` n'est pas utilise.

        Un prix de marche ne se "reentrai­ne" pas sur le passe electoral ; la
        seule correction (biais favori-outsider) est un prior fixe applique
        identiquement, quel que soit l'historique disponible au pli courant.
        """
        return self

    def predict(self, ctx: ElectionContext) -> SourceSignal:
        """Renvoie le signal marche pour `ctx`, ou `available=False` si absent.

        Les marches de prediction n'existent pas (avec un volume exploitable)
        pour les vieilles elections francaises : c'est un cas ATTENDU, pas
        une erreur, pour toute election avant l'essor de ces plateformes sur
        la presidentielle (en pratique : avant 2017 dans ce depot).
        """
        data = load_market_prob(ctx.election_id, snapshot_path=self.snapshot_path)
        if not data or "p_reference_wins" not in data:
            return SourceSignal(
                source=self.name,
                election_id=ctx.election_id,
                r2_share_mean=0.5,
                r2_share_sd=1.0,
                available=False,
                meta={"reason": "aucun_marche_pour_cette_election"},
            )

        p_raw = float(data["p_reference_wins"])
        p_debiased = debias_favorite_longshot(p_raw)
        share = prob_to_share(p_debiased)

        return SourceSignal(
            source=self.name,
            election_id=ctx.election_id,
            r2_share_mean=share,
            r2_share_sd=MARKET_SD,
            available=True,
            meta={
                "p_market_raw": p_raw,
                "p_market_debiased": p_debiased,
                "n_trades_or_volume": float(data.get("n_trades_or_volume", 0.0)),
            },
        )
