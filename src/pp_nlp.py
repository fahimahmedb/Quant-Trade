"""Source NLP / sentiment (Étape P3) : proxy comportemental de notoriété + tonalité.

Chargeur HYBRIDE (`load_nlp_features`) : tentative de collecte live (Google
Trends via `pytrends`, protégée par try/except + timeout court) puis repli
IMMÉDIAT sur un instantané (snapshot) offline versionné dans
`data/fr_nlp_snapshot.csv`. Aucune requête réseau bloquante n'est jamais
exécutée dans cet environnement : `pytrends` n'est pas une dépendance du
projet, donc `_fetch_live` échoue à l'import et repart aussitôt sur le
snapshot (voir docstring de `_fetch_live`).

Google Trends n'existe (au sens exploitable) que depuis ~2004 : les
présidentielles antérieures (1965-2002) n'ont donc structurellement AUCUNE
donnée NLP -> `SourceSignal(available=False)`, ce que le backtest OOS traite
comme un pli non scorable (cf. `pp_backtest.markdown_table`).

Discipline anti-data-snooping : `fit()` ne recalibre qu'un facteur d'échelle
global (pas les poids des features, n trop petit) sur l'historique STRICT
passé, jamais sur l'élection à prédire ni sur le futur.

ÉCHAFAUDAGE 2027-LIVE — cette source ne produit AUCUN résultat sur
l'historique : les lignes rétrospectives (2007-2022) étaient en réalité
rédigées en connaissant l'issue (hindsight) et ont été supprimées du
snapshot. `predict()` se déclare donc systématiquement indisponible sur
tout l'historique de ce dépôt (0 pli scoré). Ce n'est PAS une brique
opérationnelle démontrée : sa valeur ne pourra être mesurée que sur un
scrutin futur (2027), avec de vraies données horodatées avant le vote —
ce qui suppose de câbler `_fetch_live` (actuellement un stub, voir sa
docstring) ou d'alimenter le snapshot par une collecte vérifiable.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Mapping, Sequence

import pandas as pd

from pp_types import ElectionContext, Source, SourceSignal, TrainingExample, clamp_share

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SNAPSHOT_PATH = DATA / "fr_nlp_snapshot.csv"

# Google Trends (service public) est lancé en 2004 : toute élection antérieure
# est structurellement hors de portée de cette source (documentaire, pas un
# réglage à ajuster au vu des résultats).
NLP_DATA_START_YEAR = 2004

FEATURE_COLS = [
    "ref_trends_share",
    "opp_trends_share",
    "ref_mention_volume",
    "ref_tonality",
    "opp_tonality",
]


def _fetch_live(election_id: str, timeout: float = 2.5) -> dict[str, float] | None:
    """Tentative OPTIONNELLE de collecte live (Google Trends + presse en ligne).

    HONNÊTETÉ : contrairement à `pp_markets._fetch_live` (qui interroge
    réellement une API), cette fonction est un STUB NON CÂBLÉ. `pytrends`
    n'est volontairement pas une dépendance du projet, donc l'import échoue
    systématiquement avant toute tentative réseau : AUCUNE requête HTTP
    n'est jamais émise ici, ni vers Google Trends ni vers une presse en
    ligne. Le mapping mot-clé → candidat et le moteur de tonalité ne sont
    pas implémentés. Cette fonction renvoie donc toujours `None` dans cet
    environnement -- elle documente un point d'extension futur, pas une
    collecte live opérationnelle.

    Contrat : toute exception -- import manquant, timeout réseau, panne API,
    format inattendu -- déclenche un repli IMMÉDIAT sur le snapshot offline,
    JAMAIS de blocage ni de tentative de nouvelle connexion. `pytrends` n'est
    volontairement PAS une dépendance du projet (poids, fragilité, risque
    réseau en CI) : dans cet environnement, l'import échoue systématiquement
    et cette fonction renvoie `None` sans jamais émettre de requête HTTP.
    Elle est conservée pour documenter le point d'extension "live" du
    chargeur hybride demandé par le contrat.
    """
    try:
        from pytrends.request import TrendReq  # type: ignore  # pragma: no cover

        # Le mapping mot-clé de recherche -> candidat de référence / principal
        # adversaire, ainsi que le moteur de tonalité (presse en ligne),
        # restent à brancher : non implémentés ici par choix (voir contrat --
        # pas de dépendance réseau dans ce module au moment de l'exécution).
        TrendReq(hl="fr-FR", tz=60, timeout=(timeout, timeout))  # pragma: no cover
        raise NotImplementedError("collecte live non branchée dans cet environnement")
    except Exception:
        return None


def load_nlp_features(election_id: str) -> Mapping[str, float] | None:
    """Charge les features NLP d'une élection : live (best-effort) puis snapshot.

    Renvoie `None` si l'élection n'a de donnée ni en live ni dans le
    snapshot -- typiquement une élection antérieure à ~2004, ou un
    `election_id` absent du fichier.
    """
    live = _fetch_live(election_id)
    if live is not None:
        return live

    df = pd.read_csv(SNAPSHOT_PATH, comment="#")
    row = df[df["election_id"] == election_id]
    if row.empty:
        return None
    r = row.iloc[0]
    return {c: float(r[c]) for c in FEATURE_COLS}


class NlpSource:
    """Signal directionnel construit sur le différentiel de notoriété/tonalité.

    Mapping (documenté, monotone, volontairement simple -- pas de boîte
    noire) :

        raw   = w1 * (ref_trends_share - opp_trends_share)
              + w2 * (ref_tonality      - opp_tonality)
        share = 0.5 + 0.5 * tanh(scale * raw)

    `w1`/`w2` sont FIXÉS a priori (pas ré-estimés : n trop petit pour
    régresser deux poids sans surapprendre) ; seul `scale` peut être
    recalibré par `fit()` sur l'historique disponible. La sigmoïde `tanh`
    assure une part dans ]0, 1[, ensuite bornée par `clamp_share`.

    Source BRUYANTE par nature (proxy comportemental + tonalité agrégée, pas
    une déclaration d'intention de vote ; manipulable par des campagnes
    coordonnées) : `r2_share_sd` reste volontairement large, dans
    [0.06, 0.09], pour que la fusion bayésienne (pondération 1/variance) ne
    lui accorde qu'un poids marginal face aux fondamentaux/marchés.
    """

    name: str = "nlp"

    W1_TRENDS = 1.6     # poids du différentiel de notoriété (trends_share, déjà dans [-1, 1])
    W2_TONALITY = 0.9   # poids du différentiel de tonalité (déjà dans [-2, 2])
    SCALE_DEFAULT = 1.0
    SD_BASE = 0.075
    SD_MIN, SD_MAX = 0.06, 0.09

    # bornes de garde-fou pour la recalibration de fit() : au-delà, on
    # suspecte un artefact (trop peu de points) et on garde le défaut.
    SCALE_SLOPE_MIN, SCALE_SLOPE_MAX = 0.05, 5.0

    def __init__(self) -> None:
        self.scale_: float = self.SCALE_DEFAULT

    def fit(self, history: Sequence[TrainingExample]) -> "NlpSource":
        """Recalibre LÉGÈREMENT l'échelle du mapping sur l'historique passé.

        On n'entraîne PAS les poids w1/w2 (risque d'overfit avec 2-4 élections
        NLP disponibles) : on ajuste uniquement `scale_`, un facteur d'échelle
        global, par une régression 1D sans intercept du score brut vers
        `(part_réelle - 0.5)`. Si moins de 2 élections avec donnée NLP sont
        disponibles dans `history`, ou si la pente estimée sort d'une plage
        plausible, on conserve `SCALE_DEFAULT` (pas de calibration -> pas de
        risque d'aberration). `history` est déjà restreint aux élections
        strictement antérieures par `pp_backtest.run_oos` : aucun accès au
        futur.
        """
        scores: list[float] = []
        targets: list[float] = []
        for ex in history:
            ctx, res = ex.context, ex.result
            feats = load_nlp_features(ctx.election_id)
            if feats is None:
                continue
            y = res.r2_reference_share(ctx.reference_id)
            if not math.isfinite(y):
                continue
            scores.append(self._raw_score(feats))
            targets.append(y - 0.5)

        if len(scores) < 2:
            self.scale_ = self.SCALE_DEFAULT
            return self

        num = sum(s * t for s, t in zip(scores, targets))
        den = sum(s * s for s in scores) + 1e-9
        slope = num / den  # pente score_brut -> (part - 0.5)

        # scale_ doit convertir raw en argument de tanh ; facteur 4 choisi car
        # tanh'(0) = 1 et 0.5*tanh(x) ~= x pour x petit, donc pente(score->y-0.5)
        # ~= 0.5 * scale_ ; on veut aussi une marge (x4) pour rester réactif à
        # l'échelle observée sans saturer la tanh sur des scores usuels.
        candidate_scale = 4.0 * float(slope)
        if self.SCALE_SLOPE_MIN <= abs(candidate_scale) <= self.SCALE_SLOPE_MAX:
            self.scale_ = candidate_scale
        else:
            self.scale_ = self.SCALE_DEFAULT
        return self

    def _raw_score(self, feats: Mapping[str, float]) -> float:
        d_trends = feats["ref_trends_share"] - feats["opp_trends_share"]
        d_tonality = feats["ref_tonality"] - feats["opp_tonality"]
        return self.W1_TRENDS * d_trends + self.W2_TONALITY * d_tonality

    def predict(self, ctx: ElectionContext) -> SourceSignal:
        feats = load_nlp_features(ctx.election_id)
        if feats is None:
            return SourceSignal(
                source=self.name,
                election_id=ctx.election_id,
                r2_share_mean=0.5,
                r2_share_sd=1.0,
                available=False,
                meta={"reason": "no_nlp_data_pre_2004_or_missing_snapshot_row"},
            )

        raw = self._raw_score(feats)
        z = self.scale_ * raw
        share = clamp_share(0.5 + 0.5 * math.tanh(z))

        # Volume de mentions extrême (campagne inhabituellement calme ou
        # hyper-virale) : signal moins fiable -> incertitude légèrement accrue.
        vol = float(feats.get("ref_mention_volume", 100.0))
        vol_penalty = 0.01 if (vol < 60.0 or vol > 160.0) else 0.0
        sd = min(self.SD_MAX, max(self.SD_MIN, self.SD_BASE + vol_penalty))

        return SourceSignal(
            source=self.name,
            election_id=ctx.election_id,
            r2_share_mean=share,
            r2_share_sd=sd,
            available=True,
            meta={
                "d_trends_share": float(feats["ref_trends_share"] - feats["opp_trends_share"]),
                "d_tonality": float(feats["ref_tonality"] - feats["opp_tonality"]),
                "raw_score": float(raw),
                "scale": float(self.scale_),
            },
        )


# Vérification statique (mypy/duck-typing) : NlpSource respecte le Protocol Source.
_: type[Source] = NlpSource
