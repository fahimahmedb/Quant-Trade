"""F6 — prévision de consommation par jour de semaine, EN MODE OMBRE
(specs-v2-ia-plan-test.md §4 ; jeux synthétiques SYN-A/E/F/I de
docs/feature-plans/ia-f5-f9.md §1.2/1.7/1.10).

Mode ombre : cette fonction n'est appelée par aucun chemin de code qui
affiche son résultat à un restaurateur — rien dans ce lot ne l'expose. Elle
existe pour être comparée à la règle v1 (`app/services/ordering.py`) sur
l'historique disponible une fois le pilote en cours (IA-01/IA-05, le seul
gate d'activation réel), jamais pour remplacer quoi que ce soit ici.

Opère au niveau de l'INGRÉDIENT (comme F13/F14 le supposent), pas du plat :
la consommation d'un ingrédient un jour donné est la somme, sur tous les
plats de sa fiche technique, de grammage × quantité vendue ce jour-là.

Estimateur — deux exigences du document qui se contredisent, et comment
elles sont conciliées :
- §4 (F6) : « moyenne des 8 dernières occurrences du même jour de semaine,
  pondérée par récence (les 4 plus récentes comptent double) ».
- §6.3 (IA-08) : une vente ×100 saisie par erreur doit être « détectée
  comme anomalie ponctuelle », « pas d'effet sur la prévision au-delà de
  ±10 % ».
Une moyenne pondérée seule échoue franchement à IA-08 : un point à ×100
parmi 8 déplace la prévision de plus de 1500 %. La lettre d'IA-08 donne
elle-même la sortie — « détection PUIS pas d'effet » : les occurrences
au-delà de 3× la médiane du jour concerné sont écartées comme aberrations
(le même facteur 3× que le badge « inhabituel » de F5, §4), puis la moyenne
pondérée du document s'applique aux occurrences restantes. Les dates
écartées sont rapportées (`excluded_outliers`) plutôt que supprimées en
silence : IA-03 exige que toute sortie soit explicable avec ses chiffres.
"""
import statistics
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import settings_service

MIN_WEEKS_OF_SALES = 6.0
MIN_OCCURRENCES_PER_WEEKDAY = 4  # specs-v2 §4 : « >= 4 occurrences de chaque jour ouvré »
FORECAST_WINDOW_OCCURRENCES = 8  # « les 8 dernières occurrences du même jour de semaine »
RECENCY_DOUBLED_COUNT = 4  # « les 4 plus récentes comptent double »
RECENCY_WEIGHT = 2.0
OUTLIER_MEDIAN_RATIO = 3.0  # cf. docstring : conciliation §4 (F6) / §6.3 (IA-08)


@dataclass
class PartialDish:
    dish_id: int
    dish_name: str
    first_sale_on: date


@dataclass
class WeekdayEstimate:
    """Jamais une valeur seule : AC-F6-4 impose un intervalle et le nombre
    d'occurrences derrière chaque prévision (« mardi : 2,9 kg attendus
    (habituellement entre 2,4 et 3,5 kg, 8 mardis d'historique) »)."""
    weekday: int
    expected_qty: float
    low: float
    high: float
    occurrences: int
    excluded_outliers: list[date] = field(default_factory=list)


@dataclass
class WeekdayForecast:
    ingredient_id: int
    expected_daily_qty: dict[int, float]  # weekday() -> quantité attendue ; jamais un jour fermé
    estimates: dict[int, WeekdayEstimate]
    closed_days: set[int]
    weeks_of_history: float
    partial_dishes: list[PartialDish] = field(default_factory=list)


@dataclass
class ForecastResult:
    gate_ok: bool
    gate_message: str | None
    forecast: WeekdayForecast | None


def _feature_enabled(db: Session) -> bool:
    return settings_service.get_settings(db).feature_f6_enabled


def _ingredient_daily_consumption(db: Session, ingredient_id: int) -> dict[date, float]:
    """{date -> quantité consommée ce jour, tous plats confondus} pour cet
    ingrédient — dérivé des VENTES, jamais du stock théorique (qui mélange
    réceptions, comptages, ajustements sans rapport avec la saisonnalité)."""
    recipe_lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    daily: dict[date, float] = {}
    for rl in recipe_lines:
        sales = db.query(models.SaleLine).filter_by(dish_id=rl.dish_id).all()
        for sale in sales:
            d = sale.sale_date.date()
            daily[d] = daily.get(d, 0.0) + rl.quantity * sale.quantity_sold
    return daily


def _partial_dishes(db: Session, ingredient_id: int, window_start: date) -> list[PartialDish]:
    """Un plat dont la première vente arrive après le début de la fenêtre
    d'historique a un historique partiel (SYN-I, cold start) : F6 continue
    de fonctionner au niveau de l'ingrédient (il ne fabrique aucune vente
    rétroactive pour ce plat), mais un appelant doit pouvoir le signaler
    plutôt que de laisser croire que tout l'historique est plein."""
    recipe_lines = db.query(models.RecipeIngredient).filter_by(ingredient_id=ingredient_id).all()
    out = []
    for rl in recipe_lines:
        first = (
            db.query(models.SaleLine)
            .filter_by(dish_id=rl.dish_id)
            .order_by(models.SaleLine.sale_date)
            .first()
        )
        if first is not None and first.sale_date.date() > window_start:
            out.append(PartialDish(dish_id=rl.dish_id, dish_name=rl.dish.name, first_sale_on=first.sale_date.date()))
    return out


def _calendar_series(daily: dict[date, float], start: date, end: date) -> dict[int, list[tuple[date, float]]]:
    """Une occurrence par jour CALENDAIRE de la fenêtre, pas seulement par
    jour où une vente existe : un jour ouvré sans vente de cet ingrédient a
    bien consommé zéro, et c'est cette distinction qui rend mesurable la
    règle « zéro vente sur >= 4 occurrences du même jour » (jour de
    fermeture) de specs-v2 §4."""
    series: dict[int, list[tuple[date, float]]] = {}
    d = start
    while d <= end:
        series.setdefault(d.weekday(), []).append((d, daily.get(d, 0.0)))
        d += timedelta(days=1)
    return series


def _estimate(weekday: int, points: list[tuple[date, float]]) -> WeekdayEstimate:
    window = points[-FORECAST_WINDOW_OCCURRENCES:]
    mediane = statistics.median([q for _, q in window])

    kept: list[tuple[float, float]] = []  # (quantité, poids)
    excluded: list[date] = []
    for index, (d, qty) in enumerate(window):
        poids = RECENCY_WEIGHT if index >= len(window) - RECENCY_DOUBLED_COUNT else 1.0
        if mediane > 0 and qty >= mediane * OUTLIER_MEDIAN_RATIO:
            excluded.append(d)
        else:
            kept.append((qty, poids))
    if not kept:  # garde-fou : la médiane ne peut pas écarter toutes les occurrences
        kept = [(qty, 1.0) for _, qty in window]
        excluded = []

    poids_total = sum(w for _, w in kept)
    attendu = sum(q * w for q, w in kept) / poids_total
    quantites = [q for q, _ in kept]
    return WeekdayEstimate(
        weekday=weekday, expected_qty=attendu, low=min(quantites), high=max(quantites),
        occurrences=len(kept), excluded_outliers=excluded,
    )


def weekday_forecast(
    db: Session, ingredient_id: int, *, as_of: date | None = None,
) -> ForecastResult:
    """specs-v2-ia-plan-test.md §4 (F6) ; jeux SYN-A/E/F/I.

    `as_of` borne l'historique aux ventes STRICTEMENT antérieures à cette
    date. Sans lui, aucun rejeu honnête n'est possible : le backtest d'IA-01
    (« prédire chaque semaine N à partir des semaines < N ») lirait l'avenir
    qu'il prétend prédire.
    """
    if not _feature_enabled(db):
        return ForecastResult(
            gate_ok=False, gate_message="Fonctionnalité F6 désactivée (feature flag éteint).", forecast=None,
        )

    daily = _ingredient_daily_consumption(db, ingredient_id)
    if as_of is not None:
        daily = {d: qty for d, qty in daily.items() if d < as_of}
    if not daily:
        return ForecastResult(gate_ok=False, gate_message="Aucune vente pour cet ingrédient.", forecast=None)

    window_start, window_end = min(daily), max(daily)
    weeks = ((window_end - window_start).days + 1) / 7.0
    if weeks < MIN_WEEKS_OF_SALES:
        return ForecastResult(
            gate_ok=False,
            gate_message=f"{weeks:.1f} semaines de ventes sur {MIN_WEEKS_OF_SALES:.0f} nécessaires",
            forecast=None,
        )

    series = _calendar_series(daily, window_start, window_end)
    closed_days = {
        wd for wd, points in series.items()
        if len(points) >= MIN_OCCURRENCES_PER_WEEKDAY and all(qty == 0 for _, qty in points)
    }
    # La seconde moitié du gate de specs-v2 §4 — « avec >= 4 occurrences de
    # chaque jour ouvré » — est automatiquement satisfaite dès que la
    # première l'est : une fenêtre de 6 semaines contient au moins 6
    # occurrences calendaires de chaque jour de la semaine. Aucun test ne
    # pourrait donc distinguer un code qui la vérifie d'un code qui ne la
    # vérifie pas ; elle n'est pas ré-écrite ici en branche morte. La
    # constante reste utilisée par la règle « zéro vente sur >= 4
    # occurrences » (jour de fermeture) ci-dessus, elle.
    ouvres = {wd: points for wd, points in series.items() if wd not in closed_days}
    estimates = {wd: _estimate(wd, points) for wd, points in ouvres.items()}
    forecast = WeekdayForecast(
        ingredient_id=ingredient_id,
        expected_daily_qty={wd: e.expected_qty for wd, e in estimates.items()},
        estimates=estimates, closed_days=closed_days, weeks_of_history=weeks,
        partial_dishes=_partial_dishes(db, ingredient_id, window_start),
    )
    return ForecastResult(gate_ok=True, gate_message=None, forecast=forecast)


# ==========================================================================
# IA-01 — backtest de F6 contre la règle v1 (specs-v2-ia-plan-test.md §6.3)
# ==========================================================================

BACKTEST_MIN_WEEKS = 4  # « son erreur est inférieure d'au moins 15 % à la v1 sur >= 4 semaines »
BACKTEST_REQUIRED_IMPROVEMENT = 0.15


@dataclass
class BacktestResult:
    ok: bool
    message: str | None
    mape_f6: float | None = None
    mape_v1: float | None = None
    weeks_evaluated: int = 0
    improvement: float | None = None  # part d'erreur en moins par rapport à la v1
    should_activate: bool = False


def _v1_rolling_average(daily: dict[date, float], as_of: date, window_days: int) -> float:
    """Équivalent de `ordering.rolling_avg_daily_consumption`, mais calculé
    sur la MÊME série de consommation dérivée des ventes que F6.

    La fonction v1 lit `StockMovement.created_at`, horodaté à l'exécution
    réelle et non à la date de vente : sur un historique antidaté — celui
    de tout jeu synthétique, et de tout import de reprise — sa fenêtre
    glissante ne mesure pas la période qu'elle croit mesurer. La comparer
    telle quelle à F6 ferait gagner F6 pour une raison qui n'a rien à voir
    avec la qualité de sa prévision. Ici les deux règles voient exactement
    les mêmes jours.
    """
    if window_days <= 0:
        return 0.0
    debut = as_of - timedelta(days=window_days)
    return sum(qty for d, qty in daily.items() if debut <= d < as_of) / window_days


def backtest_vs_v1(db: Session, ingredient_id: int) -> BacktestResult:
    """IA-01 : « sur l'historique réel, prédire chaque semaine N à partir
    des semaines < N, comparer l'erreur (MAPE) de F6 et de la règle v1.
    F6 activée pour un ingrédient seulement si son erreur est inférieure
    d'au moins 15 % à la v1 sur >= 4 semaines. Sinon, v1 reste. »

    C'est le seul gate d'activation qui compte, et il n'a de sens que sur
    les données du pilote : cette fonction est l'outil pour le passer, pas
    une preuve que F6 le passera.
    """
    if not _feature_enabled(db):
        return BacktestResult(ok=False, message="Fonctionnalité F6 désactivée (feature flag éteint).")

    daily = _ingredient_daily_consumption(db, ingredient_id)
    if not daily:
        return BacktestResult(ok=False, message="Aucune vente pour cet ingrédient.")

    window_days = settings_service.get_settings(db).rolling_window_days
    debut, fin = min(daily), max(daily)
    # Première semaine évaluable : celle qui suit le gate de 6 semaines.
    premier_lundi = debut - timedelta(days=debut.weekday())
    semaine = premier_lundi + timedelta(weeks=int(MIN_WEEKS_OF_SALES) + 1)

    erreurs_f6: list[float] = []
    erreurs_v1: list[float] = []
    semaines = 0
    while semaine <= fin:
        outcome = weekday_forecast(db, ingredient_id, as_of=semaine)
        if not outcome.gate_ok:
            semaine += timedelta(weeks=1)
            continue
        v1 = _v1_rolling_average(daily, semaine, window_days)
        jours_evalues = 0
        for offset in range(7):
            jour = semaine + timedelta(days=offset)
            reel = daily.get(jour)
            if reel is None or reel <= 0:
                continue  # un jour fermé ou sans vente ne dit rien d'une erreur relative
            prevu = outcome.forecast.expected_daily_qty.get(jour.weekday())
            if prevu is None:
                continue
            erreurs_f6.append(abs(prevu - reel) / reel)
            erreurs_v1.append(abs(v1 - reel) / reel)
            jours_evalues += 1
        if jours_evalues:
            semaines += 1
        semaine += timedelta(weeks=1)

    if semaines < BACKTEST_MIN_WEEKS or not erreurs_f6:
        return BacktestResult(
            ok=False,
            message=f"{semaines} semaines rejouables sur {BACKTEST_MIN_WEEKS} nécessaires",
            weeks_evaluated=semaines,
        )

    mape_f6 = sum(erreurs_f6) / len(erreurs_f6)
    mape_v1 = sum(erreurs_v1) / len(erreurs_v1)
    amelioration = (mape_v1 - mape_f6) / mape_v1 if mape_v1 > 0 else 0.0
    return BacktestResult(
        ok=True, message=None, mape_f6=mape_f6, mape_v1=mape_v1,
        weeks_evaluated=semaines, improvement=amelioration,
        should_activate=amelioration >= BACKTEST_REQUIRED_IMPROVEMENT,
    )
