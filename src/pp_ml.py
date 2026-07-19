"""Famille de modèles ML sur données historiques (Étape P5, la plus complexe).

Reprend EXACTEMENT le contrat `Source` et le même backtest OOS que les autres
briques, avec des apprenants plus flexibles que la régression structurelle :
régression logistique, forêt aléatoire, gradient boosting, XGBoost (optionnel).

Cible : part 2nd tour de la référence (régression) ; la version logistique
classe l'issue binaire puis la mappe vers une part. Features : les mêmes
variables fondamentales (croissance, chômage, approbation, ancienneté, sortant).

AVERTISSEMENT DE PRINCIPE (biais-variance) : l'historique présidentiel FR ne
compte que ~11 observations. Des modèles à forte capacité (RF/GB/XGB) vont
sur-ajuster et NE devraient PAS battre le modèle parcimonieux hors-échantillon.
C'est le vrai terrain du ML « par circonscription » (législatives : ~577 sièges
× plusieurs cycles) qui apporterait les effectifs nécessaires — cf. le schéma de
données documenté dans scripts/run_etape_P5_ml.py.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LogisticRegression

from pp_types import ElectionContext, SourceSignal, TrainingExample, clamp_share

try:  # XGBoost est optionnel : le module fonctionne sans lui.
    from xgboost import XGBRegressor  # type: ignore

    _HAS_XGB = True
except Exception:  # pragma: no cover - dépend de l'environnement
    _HAS_XGB = False

FEATURES = ["gdp_growth", "unemployment", "approval", "tenure_years", "incumbent_running"]
SD_FLOOR = 0.05          # incertitude irréductible d'un 2nd tour (cf. P1)
# Mapping proba de victoire -> part (classifieur logistique). Monotone, amorti :
# p=1 -> part 0.5 + K/2 ; p=0 -> 0.5 - K/2.
LOGIT_SHARE_K = 0.60


class MlSource:
    """Source ML générique implémentant le protocole `Source`.

    model : "logistic" | "rf" | "gb" | "xgb". "logistic" classe l'issue binaire
    (référence gagne) puis mappe la proba en part ; les autres régressent
    directement la part 2nd tour.
    """

    def __init__(self, model: str = "rf", min_train: int = 4) -> None:
        if model == "xgb" and not _HAS_XGB:
            raise RuntimeError("XGBoost non disponible dans cet environnement.")
        self.model = model
        self.name = f"ml_{model}"
        self.min_train = min_train
        self._est = None
        self._mean = None
        self._sd = None
        self._is_classifier = model == "logistic"

    # -- construction de l'estimateur ------------------------------------- #
    def _make_estimator(self):
        if self.model == "logistic":
            return LogisticRegression(C=1.0, max_iter=1000)
        if self.model == "rf":
            # max_depth borné : brider (un peu) le sur-ajustement a priori.
            return RandomForestRegressor(n_estimators=300, max_depth=3, random_state=0)
        if self.model == "gb":
            return GradientBoostingRegressor(n_estimators=200, max_depth=2, random_state=0)
        if self.model == "xgb":
            return XGBRegressor(n_estimators=200, max_depth=2, learning_rate=0.1,
                                random_state=0, verbosity=0)
        raise ValueError(f"modèle ML inconnu : {self.model}")

    def _features(self, ctx: ElectionContext) -> np.ndarray | None:
        f = ctx.features
        if any(k not in f for k in FEATURES):
            return None
        return np.array([f[k] for k in FEATURES], dtype=float)

    # -- protocole Source -------------------------------------------------- #
    def fit(self, history: Sequence[TrainingExample]) -> "MlSource":
        X, y = [], []
        for ex in history:
            ctx, res = ex.context, ex.result
            share = res.r2_reference_share(ctx.reference_id)
            x = self._features(ctx)
            if x is None or not np.isfinite(share):
                continue
            X.append(x)
            y.append(int(res.winner_id == ctx.reference_id) if self._is_classifier else share)
        if len(X) < self.min_train:
            self._est = None
            return self
        X = np.array(X, float)
        y = np.array(y, float)
        self._mean = X.mean(axis=0)
        self._sd = np.maximum(X.std(axis=0, ddof=1), 1e-6)
        Xs = (X - self._mean) / self._sd
        # LogisticRegression exige au moins deux classes en apprentissage.
        if self._is_classifier and len(np.unique(y)) < 2:
            self._est = None
            self._const_share = 0.5 + LOGIT_SHARE_K * (float(y[0]) - 0.5)
            return self
        est = self._make_estimator()
        est.fit(Xs, y)
        self._est = est
        return self

    def predict(self, ctx: ElectionContext) -> SourceSignal:
        x = self._features(ctx)
        if self._est is None or x is None:
            share = getattr(self, "_const_share", 0.5)
            return SourceSignal(self.name, ctx.election_id, clamp_share(share), 0.09,
                                available=True, meta={"reason": "fallback"})
        xs = (x - self._mean) / self._sd
        if self._is_classifier:
            p_win = float(self._est.predict_proba(xs.reshape(1, -1))[0, 1])
            share = 0.5 + LOGIT_SHARE_K * (p_win - 0.5)
            sd = SD_FLOOR
        else:
            share = float(self._est.predict(xs.reshape(1, -1))[0])
            sd = SD_FLOOR
            if self.model == "rf":  # dispersion inter-arbres -> incertitude
                preds = np.array([t.predict(xs.reshape(1, -1))[0] for t in self._est.estimators_])
                sd = max(float(preds.std()), SD_FLOOR)
        return SourceSignal(self.name, ctx.election_id, clamp_share(share), sd, available=True)


def available_models() -> list[str]:
    """Liste des modèles ML disponibles (XGBoost inclus seulement s'il est installé)."""
    base = ["logistic", "rf", "gb"]
    return base + (["xgb"] if _HAS_XGB else [])
