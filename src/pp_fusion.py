"""Fusion bayésienne multi-source (Étape P4).

Combine les signaux hétérogènes (fondamentaux, marchés, NLP) en un posterior
unique sur la part 2nd tour du candidat de référence — l'esprit « Nate Silver »
mais SANS sondage déclaratif : les entrées sont un prior fondamental + des
vraisemblances (marchés, NLP).

Méthode : chaque source fournit une estimation gaussienne (moyenne, écart-type)
de la part 2nd tour. On passe en espace LOGIT (la part est bornée dans (0,1),
le logit la rend approximativement gaussienne et non bornée), où la fusion
gaussienne exacte est une pondération par la précision (inverse-variance) :

    z_post = (Σ w_i·τ_i·z_i) / (Σ w_i·τ_i)          τ_i = 1/σ_zi²
    τ_post = Σ w_i·τ_i

`w_i` est une fiabilité a priori PAR SOURCE (défaut 1.0). Elle doit rester un
PRIOR — l'ajuster sur l'échantillon de test serait du data-snooping ; toute
calibration doit se faire hors-échantillon (cf. src/pp_backtest.py).

Un prior faible (centré sur 0.5, très diffus) régularise le cas où une seule
source, voire aucune, est disponible.
"""
from __future__ import annotations

import math
from typing import Mapping, Sequence

from scipy.stats import norm

from pp_types import (
    ElectionContext,
    Posterior,
    Source,
    SourceSignal,
    TrainingExample,
    clamp_share,
)

# Prior diffus en logit : moyenne 0 (= part 0.5), grand écart-type => précision
# faible. Il ne domine jamais une source informative mais évite les divisions
# par zéro et ancre le résultat en l'absence de source.
PRIOR_LOGIT_MEAN = 0.0
PRIOR_LOGIT_SD = 2.0

_EPS = 1e-6


def _logit(p: float) -> float:
    p = min(1 - _EPS, max(_EPS, p))
    return math.log(p / (1 - p))


def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def _sd_share_to_logit(mean: float, sd: float) -> float:
    """Propage l'écart-type de l'espace part vers l'espace logit (delta method).

    d logit / d p = 1 / (p(1-p)), donc σ_z ≈ σ_p / (p(1-p)).
    """
    p = min(1 - _EPS, max(_EPS, mean))
    denom = max(_EPS, p * (1 - p))
    return sd / denom


def _sd_logit_to_share(mean_share: float, sd_logit: float) -> float:
    """Retour part : σ_p ≈ σ_z · p(1-p)."""
    p = min(1 - _EPS, max(_EPS, mean_share))
    return sd_logit * p * (1 - p)


def fuse_signals(
    signals: Sequence[SourceSignal],
    reference_id: str,
    election_id: str,
    reliabilities: Mapping[str, float] | None = None,
    use_prior: bool = True,
    min_sd_share: float = 0.03,
) -> Posterior:
    """Fusionne des SourceSignal en un Posterior (pondération par précision, logit).

    Les signaux `available=False` ou de précision nulle sont ignorés.
    `contributions` renvoie le poids relatif (normalisé) de chaque source.

    Plancher d'incertitude (anti-sur-confiance) : la pondération par précision
    de sources supposées INDÉPENDANTES rétrécit la variance plus vite que la
    réalité (les sources sont corrélées et déjà sur-confiantes). On borne donc
    l'écart-type du posterior par celui de la meilleure source unique
    disponible (partial pooling), jamais sous `min_sd_share`. P(victoire) est
    ensuite calculée dans l'espace des PARTS avec cet écart-type honnête, pas
    dans l'espace logit saturé.
    """
    reliabilities = reliabilities or {}

    num = 0.0        # Σ w·τ·z
    den = 0.0        # Σ w·τ  (précision totale)
    raw_weights: dict[str, float] = {}
    source_sds: list[float] = []   # écarts-types (part) des sources retenues

    if use_prior:
        tau_prior = 1.0 / (PRIOR_LOGIT_SD * PRIOR_LOGIT_SD)
        num += tau_prior * PRIOR_LOGIT_MEAN
        den += tau_prior
        raw_weights["prior"] = tau_prior

    for sig in signals:
        prec = sig.precision()
        if prec <= 0.0:
            continue
        w = float(reliabilities.get(sig.source, 1.0))
        if w <= 0.0:
            continue
        z = _logit(sig.r2_share_mean)
        sz = _sd_share_to_logit(sig.r2_share_mean, sig.r2_share_sd)
        tau_z = 1.0 / (sz * sz)
        contrib = w * tau_z
        num += contrib * z
        den += contrib
        raw_weights[sig.source] = raw_weights.get(sig.source, 0.0) + contrib
        source_sds.append(sig.r2_share_sd)

    z_post = num / den
    sd_z_post = math.sqrt(1.0 / den)

    mean_share = clamp_share(_sigmoid(z_post))
    # Écart-type « naïf » de la fusion, puis plancher = meilleure source unique.
    sd_share_raw = _sd_logit_to_share(mean_share, sd_z_post)
    floor = max(min_sd_share, min(source_sds)) if source_sds else PRIOR_LOGIT_SD
    sd_share = max(sd_share_raw, floor)
    # P(part > 0.5) avec l'écart-type honnête (espace des parts).
    p_win = float(norm.cdf((mean_share - 0.5) / sd_share))

    total = sum(raw_weights.values()) or 1.0
    contributions = {k: v / total for k, v in raw_weights.items()}

    return Posterior(
        election_id=election_id,
        reference_id=reference_id,
        r2_share_mean=mean_share,
        r2_share_sd=sd_share,
        p_reference_wins=p_win,
        contributions=contributions,
    )


class FusionSource:
    """Méta-source : orchestre des sous-sources et implémente `Source`.

    `fit(history)` entraîne chaque sous-source sur le MÊME historique (passé
    strict, garanti par le backtest). `predict(ctx)` collecte leurs signaux,
    les fusionne et renvoie le posterior sous forme de `SourceSignal` — ce qui
    permet de brancher la fusion directement dans `run_oos`.
    """

    name = "fusion"

    def __init__(
        self,
        sources: Sequence[Source],
        reliabilities: Mapping[str, float] | None = None,
        use_prior: bool = True,
    ) -> None:
        self.sources = list(sources)
        self.reliabilities = dict(reliabilities or {})
        self.use_prior = use_prior
        self._last_posterior: Posterior | None = None

    def fit(self, history: Sequence[TrainingExample]) -> "FusionSource":
        for s in self.sources:
            s.fit(history)
        return self

    def posterior(self, ctx: ElectionContext) -> Posterior:
        signals = [s.predict(ctx) for s in self.sources]
        post = fuse_signals(
            signals,
            reference_id=ctx.reference_id,
            election_id=ctx.election_id,
            reliabilities=self.reliabilities,
            use_prior=self.use_prior,
        )
        self._last_posterior = post
        return post

    def predict(self, ctx: ElectionContext) -> SourceSignal:
        post = self.posterior(ctx)
        return SourceSignal(
            source=self.name,
            election_id=ctx.election_id,
            r2_share_mean=post.r2_share_mean,
            r2_share_sd=post.r2_share_sd,
            available=True,
            meta={"p_reference_wins": post.p_reference_wins},
        )
