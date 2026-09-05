"""Générateur de jeux de données synthétiques (Lot IA-0, docs/IA scope.md §1-2).

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
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services import counting, deliveries, recipes, sales_import


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
    """docs/IA scope.md §1.2. Lundi fermé. Facteurs : mar 1,0 / mer 1,1 /
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
    """docs/IA scope.md §1.3. Le parseur de ventes ne connaît que la
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
        period_start = start + timedelta(days=i * 5)
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
    """docs/IA scope.md §1.4. Trois plats à parts rigoureusement égales
    (33% chacun) : aucun n'atteint la condition des 50% de F5. Un écart réel
    existe (bruit générique, non corrélé à un plat précis) — F5 ne doit
    proposer AUCUNE correction de grammage ici."""
    rng = random.Random(seed)
    ing = ingredient(db, "Ingrédient SYN-C", unit_cost=0.01, stock_qty=200_000.0)
    plats = [dish(db, f"Plat SYN-C {n}", {ing.id: 100.0}) for n in "ABC"]

    sessions = []
    start = datetime(2026, 3, 2)
    for i in range(4):
        period_start = start + timedelta(days=i * 7)
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


def build_syn_d(db: Session, seed: int = 4) -> SynD:
    """docs/IA scope.md §1.5. Trois ingrédients indépendants (un plat
    chacun, la dérive de grammage n'est pas ce que ce jeu teste — seule la
    SUITE des écarts au fil des comptages compte) :
    - récurrent : 8% d'écart sur 5 comptages consécutifs -> badge attendu
      « perte récurrente », cumul en € exact.
    - anomalie : 4 comptages conformes puis un écart isolé massif -> badge
      attendu « inhabituel », jamais « récurrent ». Note : « 10x la médiane »
      (le texte du document) n'a pas de médiane non nulle à calculer ici
      (les 4 comptages précédents sont à 0% par construction) — interprété
      comme « un ordre de grandeur sans ambiguïté au-dessus d'un écart
      normal », matérialisé par une perte à 50% du stock plutôt qu'une
      dérive de quelques %.
    - sous-seuil : 8% d'écart mais seulement 2 comptages -> aucun badge
      (le seuil de 3 comptages n'est pas atteint).
    """
    rng = random.Random(seed)
    pct = 0.08
    base = datetime(2026, 4, 1)

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
    anomalie = ing2.current_theoretical_stock * 0.5
    sessions2.append(run_count_session(
        db, counted_by="SYN-D",
        counted={ing2.id: ing2.current_theoretical_stock - anomalie},
        ended_at=d + timedelta(hours=2),
    ))

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
# SYN-E — Sous le gate de données (cible : F5, F6, IA-02)
# ==========================================================================

@dataclass
class SynE:
    ingredient: models.Ingredient
    dish: models.Dish
    weeks: int
    count_sessions: list[models.CountSession]


def build_syn_e(db: Session, seed: int = 5) -> SynE:
    """docs/IA scope.md §1.6. 4 semaines de ventes (F6 exige >= 6, section 0)
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
    """docs/IA scope.md §1.7. Un jeu SYN-A propre (`clean`, pour comparer)
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
    outlier_date = start + timedelta(days=8)  # un mardi de la 2e semaine
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
    """docs/IA scope.md §1.8. Tomate : livraisons mardi/vendredi,
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
    """docs/IA scope.md §1.9. Food cost théorique = coût recette / prix de
    vente = pile 30,0% par construction (300 g à 0,01 €/g = 3,00 € sur un
    plat à 10,00 €). Food cost réel dérivé pour tomber pile à 32,5% :
    réception dimensionnée à rebours de (revenu réel × 32,5% + stock de
    clôture visé), plutôt qu'une perte approximative injectée au hasard —
    l'écart de 2,5 points doit être exact à ±0,1 point (critère du document),
    pas juste plausible.
    """
    rng = random.Random(seed)
    unit_cost = 0.01
    grammage = 300.0
    prix_vente = 10.00
    target_real_pct = 32.5
    closing_qty = 500.0  # tampon arbitraire, juste pour ne pas finir à 0 pile

    ing = ingredient(db, "Ingrédient SYN-H", unit_cost=unit_cost, stock_qty=0.0)
    plat = dish(db, "Plat SYN-H", {ing.id: grammage})

    start = datetime(2026, 7, 6)
    opening = run_count_session(db, counted_by="SYN-H ouverture", counted={ing.id: 0.0}, ended_at=start)

    total_qty_sold = 0.0
    rows = []
    for day_offset in range(1, weeks * 7 + 1):
        date = start + timedelta(days=day_offset)
        qty = noisy(rng, 40.0, 0.10)
        total_qty_sold += qty
        rows.append((date, plat.name, qty, prix_vente))

    revenue = total_qty_sold * prix_vente
    closing_value = closing_qty * unit_cost
    real_cost_value = revenue * target_real_pct / 100.0
    receipt_qty = (real_cost_value + closing_value) / unit_cost  # opening = 0

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
    """docs/IA scope.md §1.10. Un ingrédient partagé par un plat ancien
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
