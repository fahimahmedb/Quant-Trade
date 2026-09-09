"""Générateur de jeux de données synthétiques (Lot IA-0, docs/feature-plans/ia-f5-f9.md §1-2).

Code de test uniquement — jamais importé par l'application (section 2 du
document). Graine fixe obligatoire (IA-04, déterminisme) : chaque builder
crée son propre `random.Random(seed)` dédié, jamais l'état global de
`random`, pour qu'un test ne dépende jamais de l'ordre d'exécution d'un
autre test qui aurait aussi tiré des nombres aléatoires.

Interface : la section 2 demande « une interface unique paramétrée »
(semaines, facteurs par jour, jours de fermeture, bruit, dérives,
aberrations, graine). Les neuf jeux SYN-A à SYN-I couvrent des scénarios
trop hétérogènes (saisonnalité des ventes, dérive de grammage, cycle de
livraison, food cost) pour qu'une seule signature de fonction les couvre
sans devenir illisible. Cette contrainte est donc satisfaite par un petit
jeu de primitives réellement partagées et paramétrées (`noisy`,
`generate_weekly_quantities`, `run_count_session`, `import_sales_rows` —
semaines, facteurs, jours fermés, bruit et graine y sont de vrais
paramètres), que chaque `build_syn_*` compose avec les valeurs propres à
son scénario — plutôt que par une fonction monolithique à vingt paramètres
optionnels dont la plupart ne s'appliqueraient à aucun jeu donné.

Chaque `build_syn_*` retourne un dataclass exposant :
- les objets métier créés (ingrédients, plats, sessions...), pour appeler
  directement le code applicatif à tester ;
- la vérité terrain injectée, interrogeable par le test sans avoir à la
  redériver depuis les objets métier.
"""
from __future__ import annotations

import csv
import io
import random
import statistics
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import counting, deliveries, recipes, sales_import, settings_service


# ==========================================================================
# Primitives partagées
# ==========================================================================

def noisy(rng: random.Random, value: float, noise_pct: float = 0.10) -> float:
    """`value` perturbée de ±noise_pct (bruit uniforme), jamais négative.

    Sans bruit, un modèle trivial (recopier l'entrée) passerait tous les
    tests SYN — le bruit ±10% par défaut est un principe explicite du
    document (§1.1), pas un raffinement optionnel.
    """
    if value <= 0:
        return 0.0
    facteur = 1 + rng.uniform(-noise_pct, noise_pct)
    return max(0.0, value * facteur)


def generate_weekly_quantities(
    rng: random.Random, *, start: datetime, weeks: int, base_qty: float,
    day_factors: dict[int, float] | None = None, closed_days: set[int] = frozenset(),
    noise_pct: float = 0.10,
) -> list[tuple[datetime, float]]:
    """Une quantité par jour sur `weeks` semaines.

    `day_factors`/`closed_days` utilisent `date.weekday()` (0=lundi ...
    6=dimanche). Un jour fermé n'apparaît pas dans la sortie (pas une ligne
    à quantité nulle : un restaurant fermé n'a pas de ticket de caisse ce
    jour-là, et F6 doit détecter l'ABSENCE de données, pas une vente à 0).
    """
    day_factors = day_factors or {}
    out = []
    for day_offset in range(weeks * 7):
        date = start + timedelta(days=day_offset)
        wd = date.weekday()
        if wd in closed_days:
            continue
        factor = day_factors.get(wd, 1.0)
        out.append((date, noisy(rng, base_qty * factor, noise_pct)))
    return out


def ingredient(
    db: Session, name: str, *, unit=models.Unit.GRAMME, unit_cost: float = 0.01,
    zone=models.StorageZone.SEC, stock_qty: float = 100_000.0,
    alert_threshold: float | None = None,
) -> models.Ingredient:
    ing = models.Ingredient(
        name=name, unit=unit, unit_cost=unit_cost, storage_zone=zone,
        current_theoretical_stock=stock_qty, alert_threshold=alert_threshold,
    )
    db.add(ing)
    db.commit()
    db.refresh(ing)
    return ing


def dish(db: Session, name: str, lines: dict[int, float]) -> models.Dish:
    return recipes.upsert_dish(
        db, dish_id=None, name=name, is_active=True,
        lines=[recipes.RecipeLineInput(ingredient_id=iid, quantity=q) for iid, q in lines.items()],
    )


def sales_csv(rows: list[tuple[datetime, str, float, float | None]]) -> str:
    """Le CSV équivalent (section 2) : mêmes ventes, en-têtes reconnus par
    le parseur d'import réel (`app/services/sales_import.HEADER_ALIASES`)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "plat", "quantite", "prix_unitaire"])
    for date, dish_name, qty, price in rows:
        writer.writerow([
            date.strftime("%Y-%m-%d"), dish_name, f"{qty:.3f}",
            "" if price is None else f"{price:.2f}",
        ])
    return buf.getvalue()


def import_sales_rows(db: Session, rows, filename: str = "synthetic.csv"):
    """Fait passer les ventes générées par le vrai parseur CSV (section 2 :
    « objets métier directement, et un export CSV équivalent pour tester le
    parseur d'import de bout en bout ») — un seul chemin de code pour les
    deux, plutôt que deux constructions parallèles qui pourraient diverger."""
    return sales_import.import_sales(db, filename, sales_csv(rows))


def run_count_session(
    db: Session, *, counted_by: str, counted: dict[int, float],
    ended_at: datetime | None = None,
) -> models.CountSession:
    """Un comptage complet : démarre, saisit `counted` (ingredient_id ->
    quantité comptée) pour les ingrédients concernés, laisse les autres
    conformes (comptés à leur valeur théorique), termine. Recale le stock
    théorique comme le ferait un vrai comptage."""
    session = counting.start_count_session(db, counted_by=counted_by)
    for line in session.lines:
        valeur = counted.get(line.ingredient_id, line.theoretical_quantity)
        counting.confirm_count_line(db, line.id, counted_quantity=valeur)
    counting.complete_count_session(db, session.id, ended_at=ended_at)
    db.refresh(session)
    return session


# ==========================================================================
# SYN-A — Saisonnalité hebdomadaire connue (cible : F6)
# ==========================================================================

@dataclass
class SynA:
    ingredient: models.Ingredient
    dish: models.Dish
    day_factors: dict[int, float]
    closed_days: set[int]
    base_daily_qty: float
    weeks: int
    noise_pct: float


def build_syn_a(db: Session, seed: int = 1, weeks: int = 12) -> SynA:
    """docs/feature-plans/ia-f5-f9.md §1.2. Lundi fermé. Facteurs : mar 1,0 / mer 1,1 /
    jeu 1,2 / ven 2,0 / sam 2,2 / dim 0,8. Un plat, un ingrédient au ratio
    1:1 (pas de dilution entre plats) : le facteur mesurable sur les ventes
    est alors exactement celui mesurable sur la consommation de
    l'ingrédient, ce que F6 doit retrouver à ±10%."""
    rng = random.Random(seed)
    day_factors = {1: 1.0, 2: 1.1, 3: 1.2, 4: 2.0, 5: 2.2, 6: 0.8}  # 0=lundi absent (fermé)
    closed_days = {0}
    ing = ingredient(db, "Ingrédient SYN-A", stock_qty=10_000_000.0)
    plat = dish(db, "Plat SYN-A", {ing.id: 1.0})
    start = datetime(2026, 1, 5)  # un lundi
    rows_qty = generate_weekly_quantities(
        rng, start=start, weeks=weeks, base_qty=20.0,
        day_factors=day_factors, closed_days=closed_days, noise_pct=0.10,
    )
    rows = [(date, plat.name, qty, None) for date, qty in rows_qty]
    import_sales_rows(db, rows, filename="syn_a.csv")
    return SynA(
        ingredient=ing, dish=plat, day_factors=day_factors, closed_days=closed_days,
        base_daily_qty=20.0, weeks=weeks, noise_pct=0.10,
    )


# ==========================================================================
# SYN-B — Dérive de grammage (cible : F5)
# ==========================================================================

@dataclass
class SynB:
    ingredient: models.Ingredient
    dish_drifted: models.Dish
    dish_other: models.Dish
    declared_g: float
    actual_g: float
    burger_share: float
    counts: list[models.CountSession]
    burger_counts_per_period: list[int]


def build_syn_b(db: Session, seed: int = 2) -> SynB:
    """docs/feature-plans/ia-f5-f9.md §1.3. Le parseur de ventes ne connaît que la
    quantité DÉCLARÉE (150 g) : c'est elle qui décrémente le stock
    théorique à chaque vente, comme dans l'app réelle. La dérive
    (+22 g/burger, soit 172 g réels) n'apparaît que dans l'écart constaté
    au comptage physique — jamais dans le stock théorique lui-même,
    exactement comme un sous-portionnage jamais mesuré tant que personne
    ne compte. Un second plat (« Assiette ») consomme le même ingrédient
    sans dérive, pour tenir le partage ~80/20 exigé par la condition de F5."""
    rng = random.Random(seed)
    declared_g, actual_g = 150.0, 172.0
    drift_g = actual_g - declared_g
    autre_g = 60.0
    autre_n = 32  # constant : ~20% de la conso théorique cumulée (calculé plus bas)

    steak = ingredient(db, "Steak haché SYN-B", unit_cost=0.012, stock_qty=500_000.0)
    burger = dish(db, "Burger SYN-B", {steak.id: declared_g})
    autre = dish(db, "Assiette SYN-B", {steak.id: autre_g})

    burger_counts = [40, 65, 30, 75, 45, 55]  # variable -> corrélation mesurable avec l'écart
    sessions = []
    start = datetime(2026, 2, 2)
    for i, burger_n in enumerate(burger_counts):
        # Comptages hebdomadaires : 6 périodes = 5 semaines de ventes, au-dessus
        # du gate « >= 4 semaines de ventes » de specs-v2 §4 (F5). L'espacement
        # n'influence ni la corrélation ni la pente — seules les quantités par
        # période comptent — mais un jeu qui ne franchit pas le gate de la spec
        # ne peut rien prouver de la fonctionnalité que la spec décrit.
        period_start = start + timedelta(days=i * 7)
        rows = [
            (period_start, burger.name, float(burger_n), None),
            (period_start, autre.name, float(autre_n), None),
        ]
        import_sales_rows(db, rows, filename=f"syn_b_{i}.csv")

        vrai_manque = noisy(rng, drift_g * burger_n, 0.10)
        session = run_count_session(
            db, counted_by="SYN-B",
            counted={steak.id: steak.current_theoretical_stock - vrai_manque},
            ended_at=period_start + timedelta(hours=2),
        )
        sessions.append(session)

    burger_theorique = declared_g * sum(burger_counts)
    autre_theorique = autre_g * autre_n * len(burger_counts)
    burger_share = burger_theorique / (burger_theorique + autre_theorique)

    return SynB(
        ingredient=steak, dish_drifted=burger, dish_other=autre,
        declared_g=declared_g, actual_g=actual_g, burger_share=burger_share,
        counts=sessions, burger_counts_per_period=burger_counts,
    )


# ==========================================================================
# SYN-C — Contre-exemple de dérive (cible : F5, faux positif)
# ==========================================================================

@dataclass
class SynC:
    ingredient: models.Ingredient
    dishes: list[models.Dish]
    counts: list[models.CountSession]


def build_syn_c(db: Session, seed: int = 3) -> SynC:
    """docs/feature-plans/ia-f5-f9.md §1.4. Trois plats à parts rigoureusement égales
    (33% chacun) : aucun n'atteint la condition des 50% de F5. Un écart réel
    existe (bruit générique, non corrélé à un plat précis) — F5 ne doit
    proposer AUCUNE correction de grammage ici."""
    rng = random.Random(seed)
    ing = ingredient(db, "Ingrédient SYN-C", unit_cost=0.01, stock_qty=200_000.0)
    plats = [dish(db, f"Plat SYN-C {n}", {ing.id: 100.0}) for n in "ABC"]

    sessions = []
    start = datetime(2026, 3, 2)
    for i in range(4):
        # 4 comptages espacés de 10 jours : exactement le minimum de comptages
        # du gate F5, avec plus de 4 semaines de ventes derrière (specs-v2 §4).
        period_start = start + timedelta(days=i * 10)
        rows = [(period_start, p.name, 30.0, None) for p in plats]  # parts rigoureusement égales
        import_sales_rows(db, rows, filename=f"syn_c_{i}.csv")
        perte = noisy(rng, 500.0, 0.10)  # écart générique, non attribuable à un seul plat
        session = run_count_session(
            db, counted_by="SYN-C",
            counted={ing.id: ing.current_theoretical_stock - perte},
            ended_at=period_start + timedelta(hours=2),
        )
        sessions.append(session)
    return SynC(ingredient=ing, dishes=plats, counts=sessions)


# ==========================================================================
# SYN-D — Perte récurrente vs anomalie ponctuelle vs sous-seuil (cible : F5)
# ==========================================================================

@dataclass
class SynD:
    ingredient_recurrent: models.Ingredient
    ingredient_anomaly: models.Ingredient
    ingredient_below_threshold: models.Ingredient
    recurrent_pct: float
    recurrent_loss_per_session: list[float]
    recurrent_sessions: list[models.CountSession]
    anomaly_sessions: list[models.CountSession]
    below_threshold_sessions: list[models.CountSession]


def build_syn_d(db: Session, seed: int = 4, anomaly_above_threshold: bool = True) -> SynD:
    """SYN-D2 dans avancement-lot-ia-0 (décision actée) pour le scénario
    "anomalie" ; SYN-D1 est un jeu séparé, voir `build_syn_d1` ci-dessous.
    Trois ingrédients indépendants (un plat chacun, la dérive de grammage
    n'est pas ce que ce jeu teste — seule la SUITE des écarts au fil des
    comptages compte) :
    - récurrent : 8% d'écart sur 5 comptages consécutifs -> badge attendu
      « perte récurrente », cumul en € exact.
    - anomalie (SYN-D2, médiane historique nulle) : 4 comptages conformes
      puis un écart isolé injecté juste au-dessus (`anomaly_above_threshold=True`,
      badge attendu) ou juste en dessous (`False`, aucun badge) du seuil
      absolu `Settings.loss_alert_eur` — c'est la règle formalisée pour le
      cas dégénéré où « 3x la médiane » n'a pas de sens (médiane nulle),
      qui réutilise la même variable réglable que la perte récurrente
      plutôt qu'un pourcentage de stock arbitraire.
    - sous-seuil : 8% d'écart mais seulement 2 comptages -> aucun badge
      (le seuil de 3 comptages n'est pas atteint).
    """
    rng = random.Random(seed)
    pct = 0.08
    base = datetime(2026, 4, 1)
    # Le seuil réglable doit exister avant qu'on le lise : `get_settings`
    # crée la ligne Settings avec ses valeurs par défaut si elle est absente.
    seuil_eur = settings_service.get_settings(db).loss_alert_eur

    ing1 = ingredient(db, "Ingrédient SYN-D récurrent", unit_cost=0.02, stock_qty=100_000.0)
    plat1 = dish(db, "Plat SYN-D récurrent", {ing1.id: 100.0})
    sessions1, pertes1 = [], []
    for i in range(5):
        d = base + timedelta(days=i * 7)
        import_sales_rows(db, [(d, plat1.name, 20.0, None)], filename=f"syn_d1_{i}.csv")
        perte = noisy(rng, ing1.current_theoretical_stock * pct, 0.05)
        pertes1.append(perte)
        sessions1.append(run_count_session(
            db, counted_by="SYN-D",
            counted={ing1.id: ing1.current_theoretical_stock - perte},
            ended_at=d + timedelta(hours=2),
        ))
    # `start_count_session` compte TOUS les ingrédients actifs : sans ça, les
    # comptages des scénarios suivants ajouteraient des lignes "conformes"
    # parasites à l'historique de ing1, faussant sa série de pertes.
    ing1.is_active = False
    db.commit()

    ing2 = ingredient(db, "Ingrédient SYN-D anomalie", unit_cost=0.02, stock_qty=100_000.0)
    plat2 = dish(db, "Plat SYN-D anomalie", {ing2.id: 100.0})
    sessions2 = []
    for i in range(4):
        d = base + timedelta(days=i * 7)
        import_sales_rows(db, [(d, plat2.name, 20.0, None)], filename=f"syn_d2_{i}.csv")
        sessions2.append(run_count_session(
            db, counted_by="SYN-D", counted={ing2.id: ing2.current_theoretical_stock},
            ended_at=d + timedelta(hours=2),
        ))
    d = base + timedelta(days=4 * 7)
    import_sales_rows(db, [(d, plat2.name, 20.0, None)], filename="syn_d2_4.csv")
    # Marge large (2 €) pour rester du bon côté du seuil quel que soit
    # l'arrondi de `unit_cost` — ce test vérifie un côté de la frontière,
    # pas sa valeur exacte au centime.
    marge_eur = 2.0
    valeur_visee = seuil_eur + marge_eur if anomaly_above_threshold else seuil_eur - marge_eur
    anomalie = valeur_visee / ing2.unit_cost
    sessions2.append(run_count_session(
        db, counted_by="SYN-D",
        counted={ing2.id: ing2.current_theoretical_stock - anomalie},
        ended_at=d + timedelta(hours=2),
    ))
    ing2.is_active = False
    db.commit()

    ing3 = ingredient(db, "Ingrédient SYN-D sous-seuil", unit_cost=0.02, stock_qty=100_000.0)
    plat3 = dish(db, "Plat SYN-D sous-seuil", {ing3.id: 100.0})
    sessions3 = []
    for i in range(2):
        d = base + timedelta(days=i * 7)
        import_sales_rows(db, [(d, plat3.name, 20.0, None)], filename=f"syn_d3_{i}.csv")
        perte = noisy(rng, ing3.current_theoretical_stock * pct, 0.05)
        sessions3.append(run_count_session(
            db, counted_by="SYN-D",
            counted={ing3.id: ing3.current_theoretical_stock - perte},
            ended_at=d + timedelta(hours=2),
        ))

    return SynD(
        ingredient_recurrent=ing1, ingredient_anomaly=ing2, ingredient_below_threshold=ing3,
        recurrent_pct=pct, recurrent_loss_per_session=pertes1,
        recurrent_sessions=sessions1, anomaly_sessions=sessions2,
        below_threshold_sessions=sessions3,
    )


# ==========================================================================
# SYN-D1 — Anomalie ponctuelle, régime « médiane non nulle » (cible : F5)
# ==========================================================================

@dataclass
class SynD1:
    ingredient: models.Ingredient
    dish: models.Dish
    historical_variances_g: list[float]
    median_g: float
    sessions: list[models.CountSession]


def build_syn_d1(db: Session, seed: int = 41, ratio: float = 3.1) -> SynD1:
    """avancement-lot-ia-0 (décision actée) : régime « médiane non nulle »
    du badge « inhabituel », complément de SYN-D2 (`build_syn_d`, médiane
    nulle). 4 écarts historiques VARIABLES (pas une valeur répétée : sinon
    la médiane serait triviale et ne distinguerait rien) donnent une
    médiane non nulle connue, puis un 5ᵉ écart est injecté à exactement
    `ratio` fois cette médiane — la frontière exacte de la règle nominale
    (ANOMALY_RATIO = 3.0, specs-v2 §4) : 3,1 doit déclencher le badge,
    2,9 ne doit pas le déclencher.

    Les 4 écarts historiques restent sous les deux seuils de significativité
    (`loss_alert_pct`/`loss_alert_eur`, par construction : 4,25 % de la
    consommation de la période au maximum, moins de 2 € chacun) pour
    qu'aucun ne puisse former une série "récurrente" avec le 5ᵉ — seule la
    comparaison à la médiane doit décider du badge, pas un effet de bord
    du seuil de récurrence.
    """
    ing = ingredient(db, f"Ingrédient SYN-D1 x{ratio:g}".replace(".", ","), unit_cost=0.02, stock_qty=100_000.0)
    plat = dish(db, f"Plat SYN-D1 x{ratio:g}".replace(".", ","), {ing.id: 100.0})
    base = datetime(2026, 5, 4)
    historical_g = [40.0, 55.0, 70.0, 85.0]  # < 5% de 2000 g de conso/période, < 10 € : jamais significatifs
    sessions = []
    for i, perte in enumerate(historical_g):
        d = base + timedelta(days=i * 7)
        import_sales_rows(db, [(d, plat.name, 20.0, None)], filename=f"syn_d1_hist_{i}.csv")
        sessions.append(run_count_session(
            db, counted_by="SYN-D1",
            counted={ing.id: ing.current_theoretical_stock - perte},
            ended_at=d + timedelta(hours=2),
        ))

    mediane = statistics.median(historical_g)
    d = base + timedelta(days=len(historical_g) * 7)
    import_sales_rows(db, [(d, plat.name, 20.0, None)], filename="syn_d1_final.csv")
    perte_finale = mediane * ratio
    sessions.append(run_count_session(
        db, counted_by="SYN-D1",
        counted={ing.id: ing.current_theoretical_stock - perte_finale},
        ended_at=d + timedelta(hours=2),
    ))

    return SynD1(ingredient=ing, dish=plat, historical_variances_g=historical_g, median_g=mediane, sessions=sessions)


# ==========================================================================
# SYN-E — Sous le gate de données (cible : F5, F6, IA-02)
# ==========================================================================

@dataclass
class SynE:
    ingredient: models.Ingredient
    dish: models.Dish
    weeks: int
    count_sessions: list[models.CountSession]


def build_syn_e(db: Session, seed: int = 5) -> SynE:
    """docs/feature-plans/ia-f5-f9.md §1.6. 4 semaines de ventes (F6 exige >= 6, section 0)
    et 3 comptages seulement (F5 exige >= 4 — message exact du document :
    « 3 comptages sur 4 nécessaires »)."""
    rng = random.Random(seed)
    ing = ingredient(db, "Ingrédient SYN-E", stock_qty=100_000.0)
    plat = dish(db, "Plat SYN-E", {ing.id: 100.0})
    start = datetime(2026, 5, 4)
    rows_qty = generate_weekly_quantities(rng, start=start, weeks=4, base_qty=15.0, noise_pct=0.10)
    rows = [(date, plat.name, qty, None) for date, qty in rows_qty]
    import_sales_rows(db, rows, filename="syn_e.csv")

    sessions = []
    for i in range(3):
        d = start + timedelta(days=i * 7)
        sessions.append(run_count_session(
            db, counted_by="SYN-E", counted={ing.id: ing.current_theoretical_stock},
            ended_at=d + timedelta(hours=2),
        ))
    return SynE(ingredient=ing, dish=plat, weeks=4, count_sessions=sessions)


# ==========================================================================
# SYN-F — Données aberrantes (cible : IA-08, robustesse de F6)
# ==========================================================================

@dataclass
class SynF:
    clean: SynA
    ingredient: models.Ingredient
    dish: models.Dish
    day_factors: dict[int, float]
    closed_days: set[int]
    weeks: int
    outlier_sale_date: datetime
    zero_count_session: models.CountSession


def build_syn_f(db: Session, seed: int = 6, weeks: int = 12) -> SynF:
    """docs/feature-plans/ia-f5-f9.md §1.7. Un jeu SYN-A propre (`clean`, pour comparer)
    et une copie indépendante avec deux injections : une vente ×100 (erreur
    de saisie) et un comptage à 0 (oubli de saisie). F6 sur la copie ne doit
    pas s'écarter de plus de ±10% de sa prévision sur `clean`."""
    clean = build_syn_a(db, seed=seed, weeks=weeks)

    rng = random.Random(seed)
    ing = ingredient(db, "Ingrédient SYN-F", stock_qty=10_000_000.0)
    plat = dish(db, "Plat SYN-F", {ing.id: 1.0})
    day_factors = {1: 1.0, 2: 1.1, 3: 1.2, 4: 2.0, 5: 2.2, 6: 0.8}
    closed_days = {0}
    start = datetime(2026, 1, 5)
    rows_qty = generate_weekly_quantities(
        rng, start=start, weeks=weeks, base_qty=20.0,
        day_factors=day_factors, closed_days=closed_days, noise_pct=0.10,
    )
    # Un mardi de l'avant-dernière semaine, donc DANS les 8 dernières
    # occurrences du mardi que F6 retient (specs-v2 §4). Une aberration plus
    # ancienne serait écartée par la seule troncature de la fenêtre : le test
    # de robustesse IA-08 passerait sans que rien de robuste soit exercé.
    outlier_date = start + timedelta(days=(weeks - 2) * 7 + 1)
    rows = [
        (date, plat.name, qty * 100 if date == outlier_date else qty, None)
        for date, qty in rows_qty
    ]
    import_sales_rows(db, rows, filename="syn_f.csv")

    zero_session = run_count_session(
        db, counted_by="SYN-F", counted={ing.id: 0.0},
        ended_at=start + timedelta(days=weeks * 7, hours=1),
    )

    return SynF(
        clean=clean, ingredient=ing, dish=plat, day_factors=day_factors,
        closed_days=closed_days, weeks=weeks, outlier_sale_date=outlier_date,
        zero_count_session=zero_session,
    )


# ==========================================================================
# SYN-G — Cycle complet de commande (cible : F7)
# ==========================================================================

@dataclass
class SynG:
    ingredient: models.Ingredient
    variant: str  # "G1" | "G2" | "G3"
    delivery_weekdays: set[int]  # 0=lundi ... 1=mardi, 4=vendredi
    shelf_life_days: int
    daily_consumption: float
    current_stock: float
    pack_size: float
    today: datetime
    order_cutoff_passed: bool


def build_syn_g(db: Session, seed: int = 7, variant: str = "G1") -> SynG:
    """docs/feature-plans/ia-f5-f9.md §1.8. Tomate : livraisons mardi/vendredi,
    conservation 5 jours, conso 2 kg/jour, stock 1 kg, conditionnement 5 kg.
    On se place un mercredi.
    - G1 : nominal.
    - G2 : heure limite de commande dépassée -> bascule sur la livraison suivante.
    - G3 : conservation 2 jours, livraison hebdomadaire seule (mardi) —
      fréquence insuffisante face à la conservation.

    F7 n'est pas encore implémentée : ce builder expose les paramètres du
    scénario en clair (pas de champ « conservation »/« fournisseur » sur
    Ingredient aujourd'hui — ce sera à l'implémentation de F7 de décider où
    les stocker), pour qu'une future implémentation de F7 puisse s'y brancher
    sans redéfinir le jeu de données.
    """
    shelf_life = 2 if variant == "G3" else 5
    delivery_weekdays = {1} if variant == "G3" else {1, 4}
    ing = ingredient(
        db, f"Tomate SYN-G {variant}", unit_cost=0.003,
        zone=models.StorageZone.FRIGO_POSITIF, stock_qty=1000.0,
    )
    today = datetime(2026, 6, 3)  # un mercredi
    return SynG(
        ingredient=ing, variant=variant, delivery_weekdays=delivery_weekdays,
        shelf_life_days=shelf_life, daily_consumption=2000.0, current_stock=1000.0,
        pack_size=5000.0, today=today, order_cutoff_passed=(variant == "G2"),
    )


# ==========================================================================
# SYN-H — Food cost complet (cible : F9)
# ==========================================================================

@dataclass
class SynH:
    ingredient: models.Ingredient
    dish: models.Dish
    weeks: int
    theoretical_food_cost_pct: float
    real_food_cost_pct: float
    opening_count: models.CountSession
    closing_count: models.CountSession
    revenue: float


def build_syn_h(db: Session, seed: int = 8, weeks: int = 8) -> SynH:
    """docs/feature-plans/ia-f5-f9.md §1.9. Food cost théorique = coût recette / prix de
    vente = pile 30,0% par construction (300 g à 0,01 €/g = 3,00 € sur un
    plat à 10,00 €). Food cost réel dérivé pour tomber pile à 32,5% :
    réception dimensionnée à rebours de (stock d'ouverture + réception −
    stock de clôture visé = 32,5% du revenu réel), plutôt qu'une perte
    approximative injectée au hasard — l'écart de 2,5 points doit être
    exact à ±0,1 point (critère du document), pas juste plausible.

    Stock d'ouverture ET de clôture délibérément non triviaux (20 000 g et
    50 000 g, pas 0) : un stock d'ouverture nul rendrait ce terme de la
    formule impossible à distinguer d'un bug qui l'omettrait purement et
    simplement — un test qui ne peut pas détecter une régression ne prouve
    rien (cf. discipline de non-vacuité, CLAUDE.md).
    """
    rng = random.Random(seed)
    unit_cost = 0.01
    grammage = 300.0
    prix_vente = 10.00
    target_real_pct = 32.5
    opening_qty = 20_000.0
    closing_qty = 50_000.0

    ing = ingredient(db, "Ingrédient SYN-H", unit_cost=unit_cost, stock_qty=0.0)
    plat = dish(db, "Plat SYN-H", {ing.id: grammage})

    start = datetime(2026, 7, 6)
    opening = run_count_session(db, counted_by="SYN-H ouverture", counted={ing.id: opening_qty}, ended_at=start)

    total_qty_sold = 0.0
    rows = []
    for day_offset in range(1, weeks * 7 + 1):
        date = start + timedelta(days=day_offset)
        qty = noisy(rng, 40.0, 0.10)
        total_qty_sold += qty
        rows.append((date, plat.name, qty, prix_vente))

    revenue = total_qty_sold * prix_vente
    opening_value = opening_qty * unit_cost
    closing_value = closing_qty * unit_cost
    real_cost_value = revenue * target_real_pct / 100.0
    # real_cost = opening_value + receipt_value - closing_value == real_cost_value
    receipt_qty = (real_cost_value - opening_value + closing_value) / unit_cost

    # Réception AVANT les ventes : le stock ne transite jamais par du négatif
    # pendant la construction (sans conséquence sur le calcul F9, qui ne lit
    # que les comptages encadrants et les réceptions de la période — mais
    # plus lisible si on inspecte l'historique de mouvements).
    deliveries.record_delivery(
        db, received_on=start + timedelta(hours=1), supplier="Fournisseur SYN-H",
        lines=[deliveries.DeliveryLineInput(ingredient_id=ing.id, quantity=receipt_qty, unit_price=unit_cost)],
    )
    import_sales_rows(db, rows, filename="syn_h.csv")

    ending = start + timedelta(days=weeks * 7 + 1)
    closing = run_count_session(db, counted_by="SYN-H clôture", counted={ing.id: closing_qty}, ended_at=ending)

    return SynH(
        ingredient=ing, dish=plat, weeks=weeks,
        theoretical_food_cost_pct=(grammage * unit_cost / prix_vente) * 100.0,
        real_food_cost_pct=target_real_pct,
        opening_count=opening, closing_count=closing, revenue=revenue,
    )


# ==========================================================================
# SYN-I — Cold start (cible : F6/F13, non couvert par les specs V2)
# ==========================================================================

@dataclass
class SynI:
    ingredient: models.Ingredient
    dish_existing: models.Dish
    dish_new: models.Dish
    new_dish_start_week: int
    weeks: int


def build_syn_i(db: Session, seed: int = 9, weeks: int = 12, new_dish_week: int = 9) -> SynI:
    """docs/feature-plans/ia-f5-f9.md §1.10. Un ingrédient partagé par un plat ancien
    (tout l'historique) et un nouveau plat introduit en semaine 9 sur 12 :
    la prévision au niveau de l'INGRÉDIENT doit continuer de fonctionner
    sur tout l'historique, sans extrapoler silencieusement une vente du
    nouveau plat sur les 8 semaines où il n'existait pas."""
    rng = random.Random(seed)
    ing = ingredient(db, "Ingrédient SYN-I", stock_qty=10_000_000.0)
    ancien = dish(db, "Plat SYN-I ancien", {ing.id: 100.0})
    nouveau = dish(db, "Plat SYN-I nouveau", {ing.id: 80.0})

    start = datetime(2026, 8, 3)
    rows = []
    for day_offset in range(weeks * 7):
        date = start + timedelta(days=day_offset)
        week_index = day_offset // 7
        rows.append((date, ancien.name, noisy(rng, 15.0, 0.10), None))
        if week_index >= new_dish_week:
            rows.append((date, nouveau.name, noisy(rng, 10.0, 0.10), None))
    import_sales_rows(db, rows, filename="syn_i.csv")

    return SynI(
        ingredient=ing, dish_existing=ancien, dish_new=nouveau,
        new_dish_start_week=new_dish_week, weeks=weeks,
    )


# ==========================================================================
# SYN-J — Répartition de valeur Pareto connue (cible : F10, Lot IA-1)
# ==========================================================================

@dataclass
class SynJ:
    gros: list[models.Ingredient]
    petit_grand: models.Ingredient
    petits_small: list[models.Ingredient]
    weeks: int


def build_syn_j(db: Session, seed: int = 10, weeks: int = 8) -> SynJ:
    """docs/feature-plans/ia-f10-f19.md §1/§11 (F10). 20 ingrédients à un
    plat chacun (grammage 100 g, ratio 1:1, comme SYN-A : le facteur mesuré
    sur les ventes est directement celui mesuré sur l'ingrédient).

    Répartition de valeur annuelle injectée (unit_cost = 0,01 €/g, donc
    valeur annuelle = qté/jour x 0,01 x 365) :
    - 3 « gros » à 250 € chacun (cumul séquentiel 25% / 50% / 75% du total)
      -> marge de 5 points sous le seuil de 80% de la classe A, quel que
      soit le bruit.
    - 1 « petit-grand » à 80 € : seul, franchit la frontière (75%+80=83%,
      soit 3 points AU-DESSUS de 80%) — un item unique et distinctement
      plus gros que les 16 suivants, pour que le franchissement de la
      frontière A/B soit déterministe (pas de valeurs à égalité de part et
      d'autre de 80%, qui rendraient le classement dépendant de l'ordre
      arbitraire de tri des ex-æquo).
    - 16 « petits » à 10,625 € chacun (le reste, 170 €) : la cumulée étant
      déjà strictement croissante et au-dessus de 80% dès le petit-grand,
      aucun ne peut plus jamais retomber en classe A.
    Total = 1000 €. Bruit réduit (2%, pas les 10% habituels) : ce jeu teste
    la précision d'une frontière de classification, pas la robustesse au
    bruit (déjà couverte par SYN-F pour F6) — moyenné sur 8 semaines, l'écart
    résiduel attendu est de l'ordre de 0,15 point, très en dessous des
    marges ci-dessus.
    """
    rng = random.Random(seed)
    unit_cost = 0.01
    grammage = 100.0
    start = datetime(2026, 9, 7)
    noise_pct = 0.02

    def _build(name: str, annual_value: float) -> models.Ingredient:
        daily_qty = annual_value / (unit_cost * 365.0)
        ing = ingredient(db, name, unit_cost=unit_cost, stock_qty=10_000_000.0)
        plat = dish(db, f"Plat {name}", {ing.id: grammage})
        rows = [
            (start + timedelta(days=d), plat.name, noisy(rng, daily_qty / grammage, noise_pct), None)
            for d in range(weeks * 7)
        ]
        import_sales_rows(db, rows, filename=f"{name}.csv")
        return ing

    gros = [_build(f"Ingrédient SYN-J gros {i + 1}", 250.0) for i in range(3)]
    petit_grand = _build("Ingrédient SYN-J petit-grand", 80.0)
    petits_small = [_build(f"Ingrédient SYN-J petit {i + 1:02d}", 10.625) for i in range(16)]

    return SynJ(gros=gros, petit_grand=petit_grand, petits_small=petits_small, weeks=weeks)


# ==========================================================================
# SYN-O — Historique d'imports avec anomalies connues (cible : F15, Lot IA-1)
# ==========================================================================

@dataclass
class SynO:
    dish: models.Dish
    start: datetime
    end: datetime
    missing_day: date
    low_volume_day: date
    low_volume_typical: int
    low_volume_actual: int
    vacation_start: date
    vacation_end: date
    normal_daily_rows: int


def build_syn_o(db: Session, seed: int = 15, weeks: int = 12) -> SynO:
    """docs/feature-plans/ia-f10-f19.md §11 (F15). Un plat vendu tous les
    jours à un rythme régulier (10 ventes/jour, pour que chaque "ligne"
    corresponde à un client), sur lequel trois anomalies connues sont
    injectées :
    - un jour isolé sans aucune vente (trou d'un jour) ;
    - un jour à -80% du volume habituel (2 lignes au lieu de 10) ;
    - une période de congés de 14 jours consécutifs (aucune vente).
    Les trois sont placées loin les unes des autres, et il reste 2 semaines
    de données normales APRÈS les congés (semaines 11-12) : sans elles, la
    fenêtre d'historique connue s'arrêterait pile à la fin des congés, et
    la période de congés elle-même — hors de toute fenêtre [début, fin
    connue] — ne serait jamais parcourue par la détection de trous.
    """
    rng = random.Random(seed)
    ing = ingredient(db, "Ingrédient SYN-O", stock_qty=10_000_000.0)
    plat = dish(db, "Plat SYN-O", {ing.id: 10.0})
    start = datetime(2026, 1, 5)  # un lundi
    normal_rows = 10

    missing_day = (start + timedelta(days=35)).date()  # semaine 6, un lundi
    low_volume_day = (start + timedelta(days=49)).date()  # semaine 8, un lundi
    low_volume_actual = 2  # -80% de 10
    vacation_start = (start + timedelta(days=56)).date()  # semaine 9
    vacation_end = vacation_start + timedelta(days=13)  # 14 jours

    rows = []
    for day_offset in range(weeks * 7):
        d = (start + timedelta(days=day_offset)).date()
        if d == missing_day or vacation_start <= d <= vacation_end:
            continue
        n = low_volume_actual if d == low_volume_day else normal_rows
        for _ in range(n):
            rows.append((
                datetime.combine(d, datetime.min.time()), plat.name,
                noisy(rng, 1.0, 0.05), 5.0,
            ))
    import_sales_rows(db, rows, filename="syn_o.csv")

    return SynO(
        dish=plat, start=start, end=start + timedelta(days=weeks * 7 - 1),
        missing_day=missing_day, low_volume_day=low_volume_day,
        low_volume_typical=normal_rows, low_volume_actual=low_volume_actual,
        vacation_start=vacation_start, vacation_end=vacation_end,
        normal_daily_rows=normal_rows,
    )


# ==========================================================================
# SYN-K — Ingrédients stables et volatils, historique de comptages (cible : F11)
# ==========================================================================

@dataclass
class SynK:
    syn_j: SynJ
    stable_ingredient: models.Ingredient
    unstable_ingredient: models.Ingredient
    stable_low_value: models.Ingredient
    new_ingredient: models.Ingredient
    sessions: list[models.CountSession]


def build_syn_k(db: Session, seed: int = 11) -> SynK:
    """docs/feature-plans/ia-f10-f19.md §11 (F11). Réutilise l'axe criticité
    de SYN-J (3 "gros" classés A, 16 "petits" classés B/C selon leur rang —
    mêmes garanties de frontière déterministe que `build_syn_j`) plutôt que
    d'en reconstruire un second à partir de zéro. Ajoute par-dessus 8
    comptages avec des écarts CONTRÔLÉS sur des ingrédients repères, pour
    couvrir les coins de la grille fréquence x criticité de F11 :
    - `stable_ingredient` (un "gros", classe A) : conforme sur 8 comptages
      -> streak >= 6, attendu HEBDOMADAIRE (un ingrédient critique ne
      descend jamais à mensuel, même stable).
    - `unstable_ingredient` (un autre "gros", classe A) : écart massif
      (50 € de valeur, largement au-dessus du seuil de significativité)
      sur les 2 derniers comptages -> streak < 3, attendu QUOTIDIEN.
    - `stable_low_value` (le dernier "petit", classe C) : conforme sur 8
      comptages -> streak >= 6, attendu MENSUEL.
    - `new_ingredient` : aucune vente du tout -> gate F10 non atteint,
      attendu QUOTIDIEN par défaut (TC-F11-06).
    Les comptages démarrent après la fin de la fenêtre de ventes de SYN-J,
    pour ne jamais chevaucher les dates que F10 utilise pour son propre
    calcul de gate/dormance.
    """
    syn_j = build_syn_j(db, seed=seed)
    stable = syn_j.gros[0]
    unstable = syn_j.gros[1]
    # Un ingrédient dédié, PAS un des 16 "petits" de SYN-J : leur frontière
    # B/C est calibrée au plus juste pour SYN-J seul (voir sa docstring) et
    # devient sensible au bruit de mesure une fois la fenêtre de ventes
    # prolongée pour les besoins de SYN-K (composition différente de la
    # fenêtre = léger déplacement de la moyenne). Une valeur annuelle >10x
    # plus petite que le plus petit "petit" (10,625 €) tombe en C avec une
    # marge large, sans dépendre d'aucune frontière déjà mise sous tension.
    stable_low = ingredient(db, "Ingrédient SYN-K stable_low", unit_cost=0.01, stock_qty=10_000_000.0)
    dish(db, f"Plat {stable_low.name}", {stable_low.id: 100.0})

    # SYN-J n'injecte des ventes que sur ses 8 semaines d'origine (jusqu'au
    # 2026-11-01 environ). Sans continuation, F10 verrait TOUS ces
    # ingrédients "dormants" (0 consommation dans les 21 jours précédant
    # les dates de comptage ci-dessous, largement postérieures) — et les
    # exclurait du calcul Pareto (build_syn_j exclut les dormants du
    # classement des autres, par design). Ne prolonger que 3 ingrédients
    # sur 20 réduirait l'univers Pareto à ces 3 seuls et casserait la
    # frontière soigneusement calibrée de SYN-J (deux "gros" à 250 € côte
    # à côte, sans rien entre les deux pour absorber le passage de 49% à
    # 98% de cumul d'un coup, tomberaient tout droit en C en sautant B) —
    # tous les ingrédients de SYN-J sont donc prolongés, chacun au MÊME
    # rythme que son injection d'origine, pour préserver l'univers Pareto
    # complet et donc la classe de criticité mesurée.
    unit_cost, grammage = 0.01, 100.0
    syn_j_end = datetime(2026, 9, 7) + timedelta(weeks=8)
    prolongation_fin = datetime(2026, 12, 31)  # couvre large la dernière date utilisée par les tests F11 (~21/12)
    jours = (prolongation_fin - syn_j_end).days
    tous_les_ingredients = [(ing, 250.0) for ing in syn_j.gros]
    tous_les_ingredients.append((syn_j.petit_grand, 80.0))
    tous_les_ingredients += [(ing, 10.625) for ing in syn_j.petits_small]
    tous_les_ingredients.append((stable_low, 1.0))
    for ing, valeur_annuelle in tous_les_ingredients:
        qty_jour = valeur_annuelle / (unit_cost * 365.0) / grammage
        plat = db.query(models.Dish).filter_by(name=f"Plat {ing.name}").one()
        rows = [
            (syn_j_end + timedelta(days=d), plat.name, noisy(random.Random(seed * 1000 + ing.id * 100 + d), qty_jour, 0.02), None)
            for d in range(jours)
        ]
        import_sales_rows(db, rows, filename=f"prolongation_{ing.id}.csv")

    base = datetime(2026, 11, 2)  # après la fin des ventes SYN-J (2026-09-07 + 8 semaines)
    sessions = []
    for i in range(8):
        d = base + timedelta(days=i * 3)
        counted = {
            stable.id: stable.current_theoretical_stock,
            stable_low.id: stable_low.current_theoretical_stock,
            unstable.id: (
                unstable.current_theoretical_stock - 5000.0 if i >= 6
                else unstable.current_theoretical_stock
            ),
        }
        sessions.append(run_count_session(db, counted_by="SYN-K", counted=counted, ended_at=d))

    new_ingredient = ingredient(db, "Ingrédient SYN-K nouveau", stock_qty=10_000_000.0)

    return SynK(
        syn_j=syn_j, stable_ingredient=stable, unstable_ingredient=unstable,
        stable_low_value=stable_low, new_ingredient=new_ingredient, sessions=sessions,
    )


# ==========================================================================
# SYN-M — Rotation lente, conservation courte (cible : F14)
# ==========================================================================

@dataclass
class SynM:
    ingredient: models.Ingredient
    dish: models.Dish
    daily_consumption_g: float
    shelf_life_days: float
    stock_at_risk: float
    stock_safe: float


def build_syn_m(db: Session, seed: int = 14) -> SynM:
    """docs/feature-plans/ia-f10-f19.md §11 (F14). Conservation 5 jours,
    consommation quotidienne connue (2000 g/jour, établie par de vraies
    ventes sur les 7 derniers jours pour que la moyenne glissante v1 la
    retrouve). Le seuil de péremption (conservation x conso) vaut alors
    précisément 10 000 g. Deux niveaux de stock fournis pour couvrir la
    frontière : `stock_at_risk` (12 000 g, 2 000 g = 6,00 € en trop) et
    `stock_safe` (8 000 g, jamais à risque).
    """
    rng = random.Random(seed)
    unit_cost = 0.003
    grammage = 100.0
    ing = ingredient(db, "Ingrédient SYN-M", unit_cost=unit_cost, stock_qty=12_000.0)
    plat = dish(db, "Plat SYN-M", {ing.id: grammage})

    now = datetime.utcnow()
    rows = [
        (now - timedelta(days=d), plat.name, noisy(rng, 2000.0 / grammage, 0.05), None)
        for d in range(7)
    ]
    import_sales_rows(db, rows, filename="syn_m.csv")

    return SynM(
        ingredient=ing, dish=plat, daily_consumption_g=2000.0, shelf_life_days=5.0,
        stock_at_risk=12_000.0, stock_safe=8_000.0,
    )
