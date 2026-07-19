"""Modèle structurel des fondamentaux (économie politique, style Jérôme-Speziari / Lewis-Beck-Nadeau).

Prédit la part 2nd tour de la référence par régression linéaire sur les variables
macro-politiques : croissance PIB, chômage, approbation, tenure du camp au pouvoir.

Discipline anti-data-snooping : le fit() utilise UNIQUEMENT l'historique passé,
les coefficients et la standardisation sont estimés hors-sample, jamais observés.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.linear_model import Ridge

from pp_types import ElectionContext, Source, SourceSignal, TrainingExample, clamp_share


class FundamentalsSource:
    """Régression structurelle des fondamentaux sur la part 2nd tour de la référence.

    Modèle de court terme politique : la part du candidat de continuité au 2nd tour
    dépend de l'état de l'économie et de la satisfaction vis-à-vis du camp au pouvoir.
    Adaptation du cadre Lewis-Beck & Nadeau (prévision à court terme) au cas français.

    Attributs (après fit) :
      - coefs : coefficients de régression (standardisés -> à interpréter après déstandardisation)
      - feature_means : moyennes d'entraînement de chaque feature
      - feature_sds : écarts-types d'entraînement
      - residual_sd : écart-type des résidus OOS (pour quantifier l'incertitude)
    """

    name: str = "fundamentals"

    # Features utilisées (ordre fixe pour cohérence)
    FEATURES = ["gdp_growth", "unemployment", "approval", "tenure_years", "incumbent_running"]

    # Seuil de prior : si trop peu d'observations d'entraînement
    MIN_TRAIN_FOR_REGRESSION = 3

    def __init__(self):
        """Initialise le modèle (vierge avant fit)."""
        self.coefs_: np.ndarray | None = None
        self.intercept_: float | None = None
        self.feature_means_: np.ndarray | None = None
        self.feature_sds_: np.ndarray | None = None
        self.residual_sd_: float | None = None

    def fit(self, history: Sequence[TrainingExample]) -> FundamentalsSource:
        """Entraîne le modèle sur l'historique des élections passées.

        Étapes :
        1. Extrait les features et la cible (part 2nd tour de la référence)
        2. Filtre les cas valides (référence finaliste au 2nd tour)
        3. Standardise les features sur l'historique
        4. Ajuste une régression Ridge
        5. Mémorise les résidus pour estimer l'incertitude prédictive

        Args :
            history : liste d'exemples (ElectionContext, ElectionResult)

        Returns :
            self (pour chaînage fit().predict())
        """
        ex = list(history)

        # Extraction des features et cibles
        X_list, y_list = [], []
        for example in ex:
            ctx, res = example.context, example.result
            y = res.r2_reference_share(ctx.reference_id)

            # Filtre : la référence doit avoir une part 2nd tour valide (NaN = éliminé 1er tour)
            if not np.isfinite(y):
                continue

            # Collecte les features
            x = self._extract_features(ctx)
            if x is None:
                continue

            X_list.append(x)
            y_list.append(y)

        if len(X_list) < self.MIN_TRAIN_FOR_REGRESSION:
            # Trop peu de données : on gardera un prior bayésien
            self.coefs_ = None
            self.intercept_ = None
            self.feature_means_ = None
            self.feature_sds_ = None
            self.residual_sd_ = None
            return self

        # Conversion en arrays
        X = np.array(X_list, dtype=float)  # (n_obs, n_features)
        y = np.array(y_list, dtype=float)  # (n_obs,)

        # Standardisation sur l'historique
        self.feature_means_ = X.mean(axis=0)
        self.feature_sds_ = X.std(axis=0, ddof=1)

        # Évite division par 0 (si une feature est constante)
        self.feature_sds_ = np.maximum(self.feature_sds_, 1e-6)

        X_std = (X - self.feature_means_) / self.feature_sds_

        # Régression Ridge (alpha petit vu le peu de points n=11)
        ridge = Ridge(alpha=0.1, fit_intercept=True)
        ridge.fit(X_std, y)

        self.coefs_ = ridge.coef_
        self.intercept_ = ridge.intercept_

        # Résidus et incertitude
        y_pred = ridge.predict(X_std)
        residuals = y - y_pred
        self.residual_sd_ = float(np.std(residuals, ddof=1))

        return self

    def predict(self, ctx: ElectionContext) -> SourceSignal:
        """Prédit la part 2nd tour de la référence et son incertitude.

        Args :
            ctx : contexte de l'élection (features + reference_id + election_id)

        Returns :
            SourceSignal avec r2_share_mean (prédiction), r2_share_sd (incertitude),
            available=True si la prédiction est valide.
        """
        # Si pas d'entraînement : renvoie un prior
        if self.coefs_ is None:
            return self._prior_signal(ctx)

        # Extrait les features
        x = self._extract_features(ctx)
        if x is None:
            # Feature manquante : fallback prior
            return self._prior_signal(ctx)

        # Standardise selon les stats d'entraînement
        x_std = (x - self.feature_means_) / self.feature_sds_

        # Prédiction
        pred_share = float(self.intercept_ + np.dot(self.coefs_, x_std))
        pred_share = clamp_share(pred_share)

        # Incertitude : max(écart-type résiduel OOS, plancher de 0.03)
        oos_sd = max(self.residual_sd_ or 0.08, 0.03)

        return SourceSignal(
            source=self.name,
            election_id=ctx.election_id,
            r2_share_mean=pred_share,
            r2_share_sd=oos_sd,
            available=True,
            meta={
                "coefs_gdp": float(self.coefs_[0] / self.feature_sds_[0]) if self.coefs_ is not None else 0.0,
                "coefs_unemp": float(self.coefs_[1] / self.feature_sds_[1]) if self.coefs_ is not None else 0.0,
                "coefs_appr": float(self.coefs_[2] / self.feature_sds_[2]) if self.coefs_ is not None else 0.0,
            }
        )

    def _extract_features(self, ctx: ElectionContext) -> np.ndarray | None:
        """Extrait les 5 features du contexte, dans l'ordre standard.

        Returns :
            Array de shape (5,) ou None si une feature critique manque.
        """
        feat = ctx.features
        x = []
        for fname in self.FEATURES:
            if fname not in feat:
                # Feature manquante : renvoie None (on fera un prior)
                return None
            x.append(feat[fname])
        return np.array(x, dtype=float)

    def _prior_signal(self, ctx: ElectionContext) -> SourceSignal:
        """Prior bayésien : 0.50 + petite prime au sortant si incumbent_running, sd large.

        Utilisé quand :
        - Historique trop court (<3 obs)
        - Features manquantes pour cette élection

        Prior : part de base 0.50 + 0.02 si sortant concourt. sd = 0.08 (très incertain).
        """
        prior_share = 0.50
        if ctx.incumbent_running:
            prior_share += 0.02

        prior_share = clamp_share(prior_share)

        return SourceSignal(
            source=self.name,
            election_id=ctx.election_id,
            r2_share_mean=prior_share,
            r2_share_sd=0.08,
            available=True,
            meta={"reason": "prior_due_to_short_history_or_missing_features"}
        )

    def report_coefficients(self) -> str:
        """Résumé interprétable des coefficients du modèle.

        Affiche les sens attendus et les valeurs estimées.
        """
        if self.coefs_ is None:
            return "Modèle non entraîné (historique insuffisant)."

        lines = []
        lines.append("\n### Interprétation structurelle des coefficients\n")
        lines.append("Variables standardisées. Les coefficients attendus (théorie économique politique) :")
        lines.append("")

        # Coefficients bruts (sur standardisé)
        gdp_coef = float(self.coefs_[0])
        unemp_coef = float(self.coefs_[1])
        appr_coef = float(self.coefs_[2])
        tenure_coef = float(self.coefs_[3])
        incumbent_coef = float(self.coefs_[4])

        lines.append(f"1. **Croissance PIB** (gdp_growth) : {gdp_coef:+.4f}")
        lines.append(f"   Théorie : + → part sortant ↑ (succès économique). Observé : {'✓' if gdp_coef > 0 else '✗'}")
        lines.append("")

        lines.append(f"2. **Chômage** (unemployment) : {unemp_coef:+.4f}")
        lines.append(f"   Théorie : + → part sortant ↓ (malaise économique). Observé : {'✓' if unemp_coef < 0 else '✗'}")
        lines.append("")

        lines.append(f"3. **Approbation du camp sortant** (approval) : {appr_coef:+.4f}")
        lines.append(f"   Théorie : + → part sortant ↑ (satisfaction électorale). Observé : {'✓' if appr_coef > 0 else '✗'}")
        lines.append("")

        lines.append(f"4. **Ancienneté du pouvoir** (tenure_years) : {tenure_coef:+.4f}")
        lines.append(f"   Théorie : + → part sortant ↓ (usure du pouvoir). Observé : {'✓' if tenure_coef < 0 else '✗'}")
        lines.append("")

        lines.append(f"5. **Sortant concourt** (incumbent_running) : {incumbent_coef:+.4f}")
        lines.append(f"   Théorie : + → part sortant ↑ (avantage du sortant). Observé : {'✓' if incumbent_coef > 0 else '✗'}")
        lines.append("")

        lines.append(f"Intercept (prior) : {self.intercept_:.4f}")
        lines.append(f"Écart-type des résidus (historique) : {self.residual_sd_:.4f}")
        lines.append("")

        return "\n".join(lines)
