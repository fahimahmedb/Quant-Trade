"""F27 — apprentissage statistique réel : lissage exponentiel triple
(Holt-Winters additif, tendance + saisonnalité hebdomadaire), dont les
paramètres (α, β, γ) sont APPRIS par recherche en grille minimisant
l'erreur de backtest — jamais choisis à la main.

Différence de fond avec F6 et tous les seuils du projet (F12, F17, F20,
F23...) : ceux-là sont des RÈGLES — une formule ou une constante que j'ai
écrite, puis vérifiée sur un jeu synthétique avant de la figer. Ici, rien
n'est figé par moi : chaque ingrédient obtient ses PROPRES α/β/γ, trouvés
en testant plusieurs candidats sur l'historique réel de CET ingrédient et
en gardant celui qui prédit le mieux (`_fit`, ci-dessous). Le modèle
découvre par exemple lui-même qu'un jour est systématiquement fermé
(indice saisonnier appris proche de zéro) sans qu'aucune règle
« >= 4 occurrences à zéro » ne le lui dise — vérifié empiriquement
(scratchpad probe_f27_hw.py, Test 2) avant d'écrire les tests.

Pas de réseau de neurones ni de bibliothèque d'apprentissage (numpy/
scipy/statsmodels ne sont pas des dépendances du projet) : avec quelques
semaines de ventes d'un seul restaurant, un modèle à beaucoup de
paramètres sur-apprendrait le bruit plutôt que le signal. Holt-Winters
(3 paramètres) est un algorithme d'apprentissage statistique standard,
dimensionné pour ce volume de données — pas moins « réel » pour être
implémenté en Python pur et être vérifiable ligne par ligne.

Ce que F6 (moyenne pondérée par récence des 8 dernières occurrences) ne
peut structurellement pas faire : extrapoler une TENDANCE. Sur une
activité en croissance ou déclin régulier, une moyenne du passé récent
reste toujours en retard sur la réalité — vérifié empiriquement
(scratchpad probe_f27_hw.py, Test 1) : ~5 % d'erreur pour Holt-Winters
contre ~20 % pour l'équivalent F6 sur une série à tendance forte connue.

`compare_models` étend `ai_forecast.backtest_vs_v1` (F18) à trois
candidats (v1, F6, F27) plutôt que deux — même philosophie exactement
(« prédire chaque semaine N à partir des semaines < N », même métrique
MAPE, jamais un chiffre théorique non rejoué) : la preuve que ce modèle
apprend mieux que les règles n'est jamais affirmée, toujours mesurée sur
les données réelles de CHAQUE ingrédient, semaine par semaine.

Mode ombre, comme F6 : aucun chemin de code ne montre ce résultat à un
restaurateur, ce module existe pour être comparé aux règles en place,
pas pour les remplacer sans preuve.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import ai_forecast, settings_service

PERIOD = 7  # cycle hebdomadaire — même granularité que F6
GRID = (0.1, 0.3, 0.5, 0.7, 0.9)  # recherche en grille : simple et vérifiable, pas un optimiseur continu opaque


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f27_enabled


def _dense_daily_series(daily: dict[date, float], start: date, end: date) -> list[float]:
    """Une valeur par jour CALENDAIRE, `end` inclus (0.0 si absent) — même
    principe que `ai_forecast._calendar_series` : un jour sans vente
    ENREGISTRÉE vaut 0, jamais « inconnu »."""
    out = []
    d = start
    while d <= end:
        out.append(daily.get(d, 0.0))
        d += timedelta(days=1)
    return out


def _holt_winters_run(
    series: list[float], period: int, alpha: float, beta: float, gamma: float,
) -> tuple[float, float, list[float]]:
    """Récursion additive standard. Initialisation par les deux premiers
    cycles complets (niveau = moyenne du premier cycle, tendance = pente
    entre les deux premiers cycles, saisonnalité = écart du premier cycle
    à sa moyenne) — la méthode d'initialisation la plus courante pour ce
    modèle, pas une invention locale."""
    avg1 = sum(series[0:period]) / period
    avg2 = sum(series[period:2 * period]) / period
    level = avg1
    trend = (avg2 - avg1) / period
    seasonal = [series[i] - avg1 for i in range(period)]

    for t in range(period, len(series)):
        s_idx = t % period
        y = series[t]
        level_prev, trend_prev = level, trend
        level = alpha * (y - seasonal[s_idx]) + (1 - alpha) * (level_prev + trend_prev)
        trend = beta * (level - level_prev) + (1 - beta) * trend_prev
        seasonal[s_idx] = gamma * (y - level) + (1 - gamma) * seasonal[s_idx]

    return level, trend, seasonal


def _forecast_ahead(
    level: float, trend: float, seasonal: list[float], period: int, n: int, horizon: int,
) -> list[float]:
    """`horizon` valeurs futures à partir de la position `n` (longueur de
    la série déjà vue). Plancher à 0 (une quantité ne peut pas être
    négative) — une extrapolation de tendance déclinante peut, elle,
    légitimement passer sous zéro sans ce plancher."""
    return [
        max(0.0, level + h * trend + seasonal[(n + h - 1) % period])
        for h in range(1, horizon + 1)
    ]


@dataclass
class LearnedParams:
    alpha: float
    beta: float
    gamma: float
    holdout_mape: float | None  # None si la semaine de validation interne n'avait aucun jour > 0


def _fit(series: list[float], period: int, grid: tuple[float, ...] = GRID) -> tuple[LearnedParams, float, float, list[float]]:
    """Recherche en grille : chaque triplet (α, β, γ) est jugé sur sa
    capacité à prédire la DERNIÈRE semaine connue à partir de tout ce qui
    précède (un holdout, jamais la série entière — sinon les paramètres
    « appris » ne seraient qu'un ajustement au bruit déjà vu). Les
    meilleurs paramètres trouvés sont ensuite réappliqués sur TOUTE la
    série, holdout compris, pour la prévision finale — ne rien gâcher
    d'une semaine réelle disponible une fois le choix fait."""
    fit_series = series[:-period]
    holdout = series[-period:]

    best: tuple[float, float, float, float] | None = None
    for alpha in grid:
        for beta in grid:
            for gamma in grid:
                level, trend, seasonal = _holt_winters_run(fit_series, period, alpha, beta, gamma)
                preds = _forecast_ahead(level, trend, seasonal, period, len(fit_series), period)
                errors = [abs(p - a) / a for p, a in zip(preds, holdout) if a > 0]
                if not errors:
                    continue
                mape = sum(errors) / len(errors)
                if best is None or mape < best[0]:
                    best = (mape, alpha, beta, gamma)

    if best is None:
        # Aucun jour > 0 dans la semaine de validation : impossible de
        # départager les candidats — repli neutre documenté, jamais un
        # plantage (dégradation silencieuse, même principe que partout
        # ailleurs dans le projet).
        holdout_mape, alpha, beta, gamma = None, 0.3, 0.1, 0.3
    else:
        holdout_mape, alpha, beta, gamma = best

    level, trend, seasonal = _holt_winters_run(series, period, alpha, beta, gamma)
    return LearnedParams(alpha=alpha, beta=beta, gamma=gamma, holdout_mape=holdout_mape), level, trend, seasonal


@dataclass
class LearnedForecastResult:
    ok: bool
    message: str | None
    expected_daily_qty: dict[int, float] | None = None  # weekday() -> quantité, même forme que F6
    params: LearnedParams | None = None
    trend_per_day: float | None = None
    explanation: str = ""


def learned_forecast(db: Session, ingredient_id: int, *, as_of: date | None = None) -> LearnedForecastResult:
    """backlog : F27. Même gate d'historique que F6 (6 semaines,
    `ai_forecast.MIN_WEEKS_OF_SALES`) — comparaison honnête, pas un
    modèle qui se déclencherait plus tôt ou plus tard que celui auquel il
    est censé se mesurer."""
    if not _feature_enabled(db):
        return LearnedForecastResult(ok=False, message="Fonctionnalité F27 désactivée (feature flag éteint).")

    ingredient = db.get(models.Ingredient, ingredient_id)
    if ingredient is None:
        return LearnedForecastResult(ok=False, message="Ingrédient introuvable.")

    daily = ai_forecast.ingredient_daily_consumption(db, ingredient_id)
    as_of = as_of or date.today()
    daily = {d: qty for d, qty in daily.items() if d < as_of}
    if not daily:
        return LearnedForecastResult(ok=False, message="Aucune vente pour cet ingrédient.")

    window_start = min(daily)
    window_end = as_of - timedelta(days=1)
    weeks = ((window_end - window_start).days + 1) / 7.0
    if weeks < ai_forecast.MIN_WEEKS_OF_SALES:
        return LearnedForecastResult(
            ok=False,
            message=f"{weeks:.1f} semaines de ventes sur {ai_forecast.MIN_WEEKS_OF_SALES:.0f} nécessaires (même gate que F6).",
        )

    series = _dense_daily_series(daily, window_start, window_end)
    params, level, trend, seasonal = _fit(series, PERIOD)
    forecast_values = _forecast_ahead(level, trend, seasonal, PERIOD, len(series), PERIOD)

    first_forecast_day = window_end + timedelta(days=1)  # == as_of
    expected_daily_qty = {
        (first_forecast_day + timedelta(days=h)).weekday(): forecast_values[h]
        for h in range(PERIOD)
    }

    tendance = "en hausse" if trend > 0.05 else "en baisse" if trend < -0.05 else "stable"
    explanation = (
        f"Paramètres appris sur l'historique de {ingredient.name} (pas choisis) : "
        f"α={params.alpha:.1f}, β={params.beta:.1f}, γ={params.gamma:.1f}. "
        f"Tendance détectée : {tendance} ({trend:+.2f}/jour)."
    )

    return LearnedForecastResult(
        ok=True, message=None, expected_daily_qty=expected_daily_qty,
        params=params, trend_per_day=trend, explanation=explanation,
    )


@dataclass
class ThreeWayWeeklyComparison:
    week_start: date
    mape_v1: float
    mape_f6: float | None  # None si F6 pas encore disponible cette semaine-là (son propre gate)
    mape_f27: float | None  # None si F27 pas encore disponible (même gate que F6)


@dataclass
class ModelComparisonResult:
    ok: bool
    message: str | None
    weeks_evaluated: int = 0
    mape_v1: float | None = None
    mape_f6: float | None = None
    mape_f27: float | None = None
    best_model: str | None = None  # "v1" | "F6" | "F27"
    weekly_results: list[ThreeWayWeeklyComparison] = field(default_factory=list)


def compare_models(db: Session, ingredient_id: int) -> ModelComparisonResult:
    """Étend `ai_forecast.backtest_vs_v1` (F18) de deux candidats à
    trois — même boucle, même métrique MAPE, même principe (« prédire la
    semaine N à partir des semaines < N »). Le gagnant n'est jamais
    supposé : mesuré semaine par semaine sur l'historique réel de CET
    ingrédient précis."""
    if not _feature_enabled(db):
        return ModelComparisonResult(ok=False, message="Fonctionnalité F27 désactivée (feature flag éteint).")

    daily = ai_forecast.ingredient_daily_consumption(db, ingredient_id)
    if not daily:
        return ModelComparisonResult(ok=False, message="Aucune vente pour cet ingrédient.")

    window_days = settings_service.get_settings(db).rolling_window_days
    debut, fin = min(daily), max(daily)
    premier_lundi = debut - timedelta(days=debut.weekday())
    semaine = premier_lundi + timedelta(weeks=int(ai_forecast.MIN_WEEKS_OF_SALES) + 1)

    erreurs_v1: list[float] = []
    erreurs_f6: list[float] = []
    erreurs_f27: list[float] = []
    weekly: list[ThreeWayWeeklyComparison] = []
    semaines = 0

    while semaine <= fin:
        v1 = ai_forecast._v1_rolling_average(daily, semaine, window_days)
        f6_outcome = ai_forecast._weekday_forecast_core(db, ingredient_id, as_of=semaine)
        f27_outcome = learned_forecast(db, ingredient_id, as_of=semaine)

        jours_v1: list[float] = []
        jours_f6: list[float] = []
        jours_f27: list[float] = []
        for offset in range(7):
            jour = semaine + timedelta(days=offset)
            reel = daily.get(jour)
            if reel is None or reel <= 0:
                continue
            jours_v1.append(abs(v1 - reel) / reel)
            if f6_outcome.gate_ok:
                prevu_f6 = f6_outcome.forecast.expected_daily_qty.get(jour.weekday())
                if prevu_f6 is not None:
                    jours_f6.append(abs(prevu_f6 - reel) / reel)
            if f27_outcome.ok:
                prevu_f27 = f27_outcome.expected_daily_qty.get(jour.weekday())
                if prevu_f27 is not None:
                    jours_f27.append(abs(prevu_f27 - reel) / reel)

        if jours_v1:
            semaines += 1
            erreurs_v1.extend(jours_v1)
            mape_f6_semaine = sum(jours_f6) / len(jours_f6) if jours_f6 else None
            mape_f27_semaine = sum(jours_f27) / len(jours_f27) if jours_f27 else None
            if jours_f6:
                erreurs_f6.extend(jours_f6)
            if jours_f27:
                erreurs_f27.extend(jours_f27)
            weekly.append(ThreeWayWeeklyComparison(
                week_start=semaine, mape_v1=sum(jours_v1) / len(jours_v1),
                mape_f6=mape_f6_semaine, mape_f27=mape_f27_semaine,
            ))
        semaine += timedelta(weeks=1)

    if semaines < ai_forecast.BACKTEST_MIN_WEEKS:
        return ModelComparisonResult(
            ok=False,
            message=f"{semaines} semaines rejouables sur {ai_forecast.BACKTEST_MIN_WEEKS} nécessaires",
            weeks_evaluated=semaines,
        )

    mape_v1 = sum(erreurs_v1) / len(erreurs_v1)
    mape_f6 = sum(erreurs_f6) / len(erreurs_f6) if erreurs_f6 else None
    mape_f27 = sum(erreurs_f27) / len(erreurs_f27) if erreurs_f27 else None

    candidats = {"v1": mape_v1}
    if mape_f6 is not None:
        candidats["F6"] = mape_f6
    if mape_f27 is not None:
        candidats["F27"] = mape_f27
    best_model = min(candidats, key=candidats.get)

    return ModelComparisonResult(
        ok=True, message=None, weeks_evaluated=semaines,
        mape_v1=mape_v1, mape_f6=mape_f6, mape_f27=mape_f27,
        best_model=best_model, weekly_results=weekly,
    )
