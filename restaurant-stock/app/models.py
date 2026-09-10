"""Modèle de données.

Simplification volontaire (documentée dans le README) : chaque ingrédient a
une seule unité de référence (g, kg, mL, L ou unité/pièce) utilisée partout
— stock, grammage des fiches techniques, coût unitaire, saisie de comptage.
Pas de conversion automatique entre unités en v1.
"""
import enum
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.utcnow()


def str_enum(enum_cls):
    """Colonne Enum qui persiste `.value` (ex. "frigo_positif") plutôt que le
    nom du membre Python — plus lisible en inspectant la base SQLite directement."""
    return Enum(enum_cls, values_callable=lambda cls: [e.value for e in cls])


class Unit(str, enum.Enum):
    GRAMME = "g"
    KILOGRAMME = "kg"
    MILLILITRE = "mL"
    LITRE = "L"
    UNITE = "unité"


class StorageZone(str, enum.Enum):
    SEC = "sec"
    FRIGO_POSITIF = "frigo_positif"
    FRIGO_NEGATIF = "frigo_negatif"
    CAVE = "cave"

    @property
    def label(self) -> str:
        return {
            StorageZone.SEC: "Stock sec",
            StorageZone.FRIGO_POSITIF: "Frigo positif",
            StorageZone.FRIGO_NEGATIF: "Frigo négatif (surgelé)",
            StorageZone.CAVE: "Cave",
        }[self]


class VarianceReason(str, enum.Enum):
    CASSE = "casse"
    PERIME = "perime"
    OFFERT = "offert"
    ERREUR_SAISIE = "erreur_saisie"
    AUTRE = "autre"

    @property
    def label(self) -> str:
        return {
            VarianceReason.CASSE: "Casse",
            VarianceReason.PERIME: "Périmé",
            VarianceReason.OFFERT: "Offert",
            VarianceReason.ERREUR_SAISIE: "Erreur de saisie",
            VarianceReason.AUTRE: "Autre",
        }[self]


class MovementType(str, enum.Enum):
    VENTE = "vente"
    COMPTAGE = "comptage"
    AJUSTEMENT = "ajustement"
    RECEPTION = "reception"

    @property
    def label(self) -> str:
        return {
            MovementType.VENTE: "Vente",
            MovementType.COMPTAGE: "Comptage",
            MovementType.AJUSTEMENT: "Ajustement",
            MovementType.RECEPTION: "Réception",
        }[self]


class SuggestionDecision(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    ACCEPTEE = "acceptee"
    MODIFIEE = "modifiee"
    REJETEE = "rejetee"


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    unit: Mapped[Unit] = mapped_column(str_enum(Unit), default=Unit.GRAMME)
    unit_cost: Mapped[float] = mapped_column(Float, default=0.0)
    storage_zone: Mapped[StorageZone] = mapped_column(
        str_enum(StorageZone), default=StorageZone.SEC
    )
    current_theoretical_stock: Mapped[float] = mapped_column(Float, default=0.0)
    alert_threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )

    # F7 (Lot IA-0, docs/feature-plans/ia-f5-f9.md §1.8) : champs optionnels, zéro saisie
    # obligatoire — un ingrédient sans ces champs garde le comportement v1
    # (app/services/ordering.py) sans dégradation. `delivery_weekdays`
    # stocke les jours de livraison sous forme d'entiers date.weekday()
    # (0=lundi..6=dimanche) séparés par des virgules, ex. "1,4" (mar/ven) :
    # pas de table Fournisseur en v1, le champ existe déjà en texte libre
    # sur DeliveryReceipt, une normalisation viendrait avec F16.
    shelf_life_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    delivery_weekdays: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pack_size: Mapped[float | None] = mapped_column(Float, nullable=True)

    # F10 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §1) : forçage manuel de
    # la classe de criticité ("A"/"B"/"C"), prioritaire sur tout recalcul
    # automatique (AC-F10-3 : « le forçage manuel survit à un recalcul ») —
    # doit donc être stocké, pas seulement recalculé à chaque appel comme le
    # reste de la classification.
    criticality_override: Mapped[str | None] = mapped_column(String(1), nullable=True)

    # F16 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §7) : champs optionnels,
    # zéro saisie obligatoire — un ingrédient sans fournisseur va dans le
    # groupe "non attribué" (AC-F16-1), jamais une erreur. Le document liste
    # "franco de port" et "minimum de commande" comme deux données
    # distinctes, mais son propre plan de test n'exerce que le franco :
    # traité comme un seul seuil ici plutôt que deux concepts parallèles
    # dont l'un resterait non testé (voir ai_supplier_consolidation.py).
    supplier_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    supplier_free_shipping_threshold: Mapped[float | None] = mapped_column(Float, nullable=True)

    # F18 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §9) : bascule
    # automatique vers la règle v1 pour CET ingrédient quand F6 se dégrade
    # sous la v1 sur 3 semaines consécutives (AC-F18-1) — distincte du
    # flag global `feature_f6_enabled`, qui reste allumé pour les autres
    # ingrédients. Lue directement par `ai_forecast.weekday_forecast` pour
    # que TOUT consommateur de F6 (F7, F14...) la respecte automatiquement,
    # sans mise à jour séparée de chacun.
    f6_reverted_to_v1: Mapped[bool] = mapped_column(default=False)

    # F13 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §4) : marqueur optionnel,
    # zéro saisie obligatoire (AC-F13-1 : aucun ingrédient marqué -> fonction
    # invisible). La durée de conservation de la préparation réutilise
    # `shelf_life_days` ci-dessus (champ F7 déjà prévu) plutôt qu'un second
    # champ qui dupliquerait le même concept.
    is_prepared_in_house: Mapped[bool] = mapped_column(default=False)

    recipe_lines: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan"
    )
    movements: Mapped[list["StockMovement"]] = relationship(back_populates="ingredient")
    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="ingredient", cascade="all, delete-orphan",
        order_by="PriceHistory.recorded_at.desc()",
    )


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow
    )

    # F23 (Lot IA-2, docs/feature-plans/backlog-lot-ia-2.md ticket 5) :
    # estimation de vente quotidienne initiale du chef, saisie à la
    # création du plat — optionnelle (dégradation silencieuse : absente,
    # le plat garde le comportement actuel, aucune suggestion tant
    # qu'aucune vente réelle n'existe).
    initial_daily_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)

    recipe_lines: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="dish", cascade="all, delete-orphan"
    )
    aliases: Mapped[list["DishAlias"]] = relationship(
        back_populates="dish", cascade="all, delete-orphan"
    )

    @property
    def food_cost(self) -> float:
        return sum(line.quantity * line.ingredient.unit_cost for line in self.recipe_lines)


class RecipeIngredient(Base):
    """Ligne de fiche technique : un ingrédient et son grammage pour un plat."""

    __tablename__ = "recipe_ingredients"
    __table_args__ = (UniqueConstraint("dish_id", "ingredient_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    quantity: Mapped[float] = mapped_column(Float)  # dans l'unité de l'ingrédient

    dish: Mapped[Dish] = relationship(back_populates="recipe_lines")
    ingredient: Mapped[Ingredient] = relationship(back_populates="recipe_lines")


class DishAlias(Base):
    """Alias reliant un intitulé brut de caisse (CSV) à un plat existant.

    Évite de re-mapper le même nom de plat à chaque import (section 9 du
    brief : chaque logiciel de caisse a ses propres intitulés).
    """

    __tablename__ = "dish_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"))

    dish: Mapped[Dish] = relationship(back_populates="aliases")


class ClosedDay(Base):
    """F15 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §6) : un jour marqué
    explicitement comme fermeture (par le gérant, en réponse à une alerte de
    trou dans l'historique des ventes). Exclu de la détection de jour
    manquant tant qu'il reste dans cette table."""

    __tablename__ = "closed_days"

    id: Mapped[int] = mapped_column(primary_key=True)
    closed_on: Mapped[date] = mapped_column(Date, unique=True)
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class DailySessionOverride(Base):
    """F11 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §2) : choix manuel du
    chef d'ajouter ou de retirer un ingrédient de la session du jour
    suggérée — mémorisé (TC-F11-07), mais jamais plus fort qu'un badge F5
    actif (la sécurité prime la préférence, voir ai_rotating_count.py)."""

    __tablename__ = "daily_session_overrides"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), unique=True)
    include: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    ingredient: Mapped["Ingredient"] = relationship()


class ExceptionalDay(Base):
    """F20 (Lot IA-2, docs/feature-plans/backlog-lot-ia-2.md ticket 4) :
    marquage manuel d'un jour ouvert mais à fréquentation atypique
    (concert, match, marché local...) — construit ce qui restait comme
    écran « non construit » depuis le Lot IA-0 (bilan-ia-0.md, item F6).

    Distinct de `ClosedDay` (F15) : ClosedDay explique une ABSENCE de
    vente (jour fermé), ExceptionalDay qualifie un jour OUVERT dont la
    fréquentation est notable — les deux ne se recouvrent jamais.

    Indépendant du feature flag F20 : une saisie reste possible même F20
    éteint (ia-f10-f19.md §... backlog-lot-ia-2.md ticket 4 : « le
    marquage manuel reste disponible même sans F20 actif, c'est une
    saisie, indépendante du calcul qui l'exploite ensuite »). Global au
    restaurant (un concert à proximité touche toute la fréquentation, pas
    un ingrédient en particulier) — jamais associé à un ingrédient précis."""

    __tablename__ = "exceptional_days"

    id: Mapped[int] = mapped_column(primary_key=True)
    on_date: Mapped[date] = mapped_column(Date, unique=True)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class ModelDecisionLog(Base):
    """F18 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §9, AC-F18-2) :
    journal des bascules automatiques modèle <-> règle v1. Première brique
    du "journal de décision du modèle" resté en suspens depuis
    avancement-lot-ia-0-trois-decisions §1 — construite ici au périmètre
    strict dont F18 a besoin (une bascule est un événement rare et
    significatif, pas une sortie F10-F19 courante), pas un système
    générique pour toutes les fonctionnalités IA."""

    __tablename__ = "model_decision_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    feature: Mapped[str] = mapped_column(String(10))  # "F18"
    ingredient_id: Mapped[int | None] = mapped_column(ForeignKey("ingredients.id"), nullable=True)
    event: Mapped[str] = mapped_column(String(50))  # "revert_to_v1" | "reactivated"
    detail: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    ingredient: Mapped["Ingredient | None"] = relationship()


class SalesImport(Base):
    __tablename__ = "sales_imports"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    unmatched_count: Mapped[int] = mapped_column(Integer, default=0)
    # F15 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §6) : empreinte du
    # contenu brut, pour détecter un même fichier réimporté deux fois
    # ("détection de doublon de fichier déjà prévue en F8, conservée ici").
    # Nullable : les imports antérieurs à cette colonne n'ont pas d'empreinte,
    # ce qui les exclut simplement de la détection, sans jamais planter.
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    lines: Mapped[list["SaleLine"]] = relationship(
        back_populates="sales_import", cascade="all, delete-orphan"
    )


class SaleLine(Base):
    __tablename__ = "sale_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    sales_import_id: Mapped[int] = mapped_column(ForeignKey("sales_imports.id"))
    sale_date: Mapped[datetime] = mapped_column(DateTime)
    raw_dish_name: Mapped[str] = mapped_column(String(200))
    dish_id: Mapped[int | None] = mapped_column(ForeignKey("dishes.id"), nullable=True)
    quantity_sold: Mapped[float] = mapped_column(Float)
    unit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    stock_applied: Mapped[bool] = mapped_column(default=False)

    sales_import: Mapped[SalesImport] = relationship(back_populates="lines")
    dish: Mapped[Dish | None] = relationship()


class StockMovement(Base):
    """Journal des mouvements de stock théorique (traçabilité, indicateur 8)."""

    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    movement_type: Mapped[MovementType] = mapped_column(str_enum(MovementType))
    quantity_delta: Mapped[float] = mapped_column(Float)
    resulting_stock: Mapped[float] = mapped_column(Float)
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    ingredient: Mapped[Ingredient] = relationship(back_populates="movements")


class CountSession(Base):
    """Session de comptage physique (section 5 du brief)."""

    __tablename__ = "count_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    counted_by: Mapped[str | None] = mapped_column(String(200), nullable=True)

    lines: Mapped[list["CountLine"]] = relationship(
        back_populates="count_session", cascade="all, delete-orphan"
    )

    @property
    def is_completed(self) -> bool:
        return self.ended_at is not None

    @property
    def duration_seconds(self) -> float | None:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at).total_seconds()


class CountLine(Base):
    __tablename__ = "count_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    count_session_id: Mapped[int] = mapped_column(ForeignKey("count_sessions.id"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    theoretical_quantity: Mapped[float] = mapped_column(Float)
    counted_quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    variance_reason: Mapped[VarianceReason | None] = mapped_column(
        str_enum(VarianceReason), nullable=True
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    count_session: Mapped[CountSession] = relationship(back_populates="lines")
    ingredient: Mapped[Ingredient] = relationship()

    @property
    def variance(self) -> float | None:
        """Écart théorique - réel : positif = perte (il manque du stock)."""
        if self.counted_quantity is None:
            return None
        return self.theoretical_quantity - self.counted_quantity

    @property
    def variance_pct(self) -> float | None:
        if self.counted_quantity is None or self.theoretical_quantity == 0:
            return None
        return self.variance / self.theoretical_quantity * 100

    @property
    def variance_value(self) -> float | None:
        """Valorisation de l'écart en euros, avec le coût unitaire actuel."""
        if self.counted_quantity is None:
            return None
        return self.variance * self.ingredient.unit_cost


class OrderSuggestionBatch(Base):
    """Un lot de suggestions de commande généré à un instant donné."""

    __tablename__ = "order_suggestion_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    lines: Mapped[list["OrderSuggestionLine"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )


class OrderSuggestionLine(Base):
    __tablename__ = "order_suggestion_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("order_suggestion_batches.id"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    current_stock: Mapped[float] = mapped_column(Float)
    avg_daily_consumption: Mapped[float] = mapped_column(Float)
    threshold_used: Mapped[float] = mapped_column(Float)
    suggested_quantity: Mapped[float] = mapped_column(Float)
    final_quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision: Mapped[SuggestionDecision] = mapped_column(
        str_enum(SuggestionDecision), default=SuggestionDecision.EN_ATTENTE
    )
    validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    batch: Mapped[OrderSuggestionBatch] = relationship(back_populates="lines")
    ingredient: Mapped[Ingredient] = relationship()


class ProductionSuggestion(Base):
    """F25 (Lot IA-2, docs/feature-plans/backlog-lot-ia-2.md ticket 3) :
    mémorisation prévision/décision réelle pour F13 (mise en place),
    referme le gap laissé ouvert au ticket 9 du Lot IA-1. Reprend le
    schéma de `OrderSuggestionLine` (F7) — suggested_quantity/
    final_quantity/decision/validated_at, même `SuggestionDecision` —
    sans le concept de lot (`OrderSuggestionBatch`) : F13 génère une
    suggestion par appel, par ingrédient, jamais une fournée quotidienne
    comme F7."""

    __tablename__ = "production_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    window_days: Mapped[int] = mapped_column(Integer)
    suggested_quantity: Mapped[float] = mapped_column(Float)
    final_quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    decision: Mapped[SuggestionDecision] = mapped_column(
        str_enum(SuggestionDecision), default=SuggestionDecision.EN_ATTENTE
    )
    validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    ingredient: Mapped[Ingredient] = relationship()


class ErrorLog(Base):
    """Journal des erreurs applicatives (F2), consultable par l'équipe projet.

    Volontairement sans données personnelles ni contenu de formulaire : on
    garde le chemin (sans query string), la méthode, le type et le message
    de l'exception, et la trace technique.
    """

    __tablename__ = "error_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    method: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(255))
    error_type: Mapped[str] = mapped_column(String(120))
    message: Mapped[str] = mapped_column(String(1000))
    traceback: Mapped[str] = mapped_column(Text)


class Account(Base):
    """Compte de l'établissement (F2). Un seul par installation en V1.1 :
    l'appareil de la cuisine est partagé, le « votre nom » du comptage reste
    déclaratif. Pas de rôles tant qu'il n'y a qu'un établissement."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    restaurant_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class DeliveryReceipt(Base):
    """Réception de livraison (F1) : la seule entrée de stock de l'application."""

    __tablename__ = "delivery_receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    received_on: Mapped[datetime] = mapped_column(DateTime)
    supplier: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    lines: Mapped[list["DeliveryLine"]] = relationship(
        back_populates="receipt", cascade="all, delete-orphan"
    )

    @property
    def total_value(self) -> float:
        return sum(line.quantity * line.unit_price for line in self.lines)


class DeliveryLine(Base):
    __tablename__ = "delivery_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    receipt_id: Mapped[int] = mapped_column(ForeignKey("delivery_receipts.id"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    quantity: Mapped[float] = mapped_column(Float)  # dans l'unité de l'ingrédient
    unit_price: Mapped[float] = mapped_column(Float)  # € par unité de référence
    previous_unit_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    receipt: Mapped[DeliveryReceipt] = relationship(back_populates="lines")
    ingredient: Mapped[Ingredient] = relationship()

    @property
    def price_change_pct(self) -> float | None:
        if not self.previous_unit_price:
            return None
        return (self.unit_price - self.previous_unit_price) / self.previous_unit_price * 100


class PriceHistory(Base):
    """Archive des prix d'achat successifs d'un ingrédient (F1, AC-F1-4)."""

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"))
    unit_price: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    supplier: Mapped[str | None] = mapped_column(String(200), nullable=True)
    receipt_id: Mapped[int | None] = mapped_column(
        ForeignKey("delivery_receipts.id"), nullable=True
    )

    ingredient: Mapped[Ingredient] = relationship(back_populates="price_history")


class Settings(Base):
    """Table à une seule ligne (id=1) pour les réglages ajustables par le gérant."""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    safety_days: Mapped[float] = mapped_column(Float, default=2.0)
    target_days: Mapped[float] = mapped_column(Float, default=5.0)
    rolling_window_days: Mapped[int] = mapped_column(Integer, default=7)
    price_alert_pct: Mapped[float] = mapped_column(Float, default=15.0)

    # Seuils IA rendus réglables par specs-v2-ia-plan-test.md (§4) plutôt que
    # codés en dur : F5 « écart valorisé dépassant 5 % de la consommation
    # théorique de la période OU 10 € », F7 « marge de sécurité, défaut 15 % ».
    # Le document précise (§8) que ce sont « des valeurs de départ raisonnées,
    # pas des constantes validées », à revoir après le pilote — d'où la
    # colonne, pas la constante.
    loss_alert_pct: Mapped[float] = mapped_column(Float, default=5.0)
    loss_alert_eur: Mapped[float] = mapped_column(Float, default=10.0)
    order_safety_margin_pct: Mapped[float] = mapped_column(Float, default=15.0)

    # Fonctionnalités IA (lot IA-0, docs/feature-plans/ia-f5-f9.md) : implémentées et
    # prouvées sur données synthétiques, mais gatées par des données réelles
    # du pilote qui n'existent pas encore. Toutes éteintes par défaut — leur
    # activation est une décision du pilote, jamais un effet de bord d'un
    # déploiement de code.
    feature_f5_enabled: Mapped[bool] = mapped_column(default=False)
    feature_f6_enabled: Mapped[bool] = mapped_column(default=False)
    feature_f7_enabled: Mapped[bool] = mapped_column(default=False)
    feature_f9_enabled: Mapped[bool] = mapped_column(default=False)

    # Lot IA-1 (docs/feature-plans/ia-f10-f19.md), même principe : éteintes
    # par défaut.
    feature_f10_enabled: Mapped[bool] = mapped_column(default=False)
    feature_f11_enabled: Mapped[bool] = mapped_column(default=False)
    feature_f12_enabled: Mapped[bool] = mapped_column(default=False)
    feature_f14_enabled: Mapped[bool] = mapped_column(default=False)
    feature_f15_enabled: Mapped[bool] = mapped_column(default=False)
    feature_f16_enabled: Mapped[bool] = mapped_column(default=False)

    # F12 (Lot IA-1) : "coefficient sous un seuil réglable, défaut 3,0"
    # (ia-f10-f19.md §3), même principe que les seuils du Lot IA-0.
    margin_coefficient_threshold: Mapped[float] = mapped_column(Float, default=3.0)
    margin_drop_pct_threshold: Mapped[float] = mapped_column(Float, default=10.0)
    feature_f18_enabled: Mapped[bool] = mapped_column(default=False)

    # F17 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §8) : diagnostic de
    # cause d'écart. Même principe que les autres flags F10-F19.
    feature_f17_enabled: Mapped[bool] = mapped_column(default=False)

    # F13 (Lot IA-1, docs/feature-plans/ia-f10-f19.md §4) : prévision de
    # mise en place. Même principe que les autres flags F10-F19.
    feature_f13_enabled: Mapped[bool] = mapped_column(default=False)

    # F22 (Lot IA-2, docs/feature-plans/backlog-lot-ia-2.md ticket 1) :
    # gaspillage consolidé et valorisé. Fenêtre glissante en JOURS plutôt
    # que « mois calendaire » (le backlog l'évoquait ainsi, mais aucune
    # autre fenêtre temporelle du projet ne raisonne en mois civils —
    # COMPARISON_WINDOW_DAYS de F12 est le précédent direct) : décision
    # purement technique, documentée ici (backlog-lot-ia-2.md §1 règle 4).
    feature_f22_enabled: Mapped[bool] = mapped_column(default=False)
    waste_summary_window_days: Mapped[float] = mapped_column(Float, default=90.0)

    # F25 (Lot IA-2, docs/feature-plans/backlog-lot-ia-2.md ticket 3) :
    # indicateur de confiance étendu (mémorisation prévision/décision F13).
    feature_f25_enabled: Mapped[bool] = mapped_column(default=False)

    # F20 (Lot IA-2, docs/feature-plans/backlog-lot-ia-2.md ticket 4) :
    # signaux calendaires (jours fériés, vacances scolaires, jours
    # exceptionnels). `school_vacation_zone` optionnel ("A"/"B"/"C") :
    # sans lui, le signal vacances scolaires reste inerte (dégradation
    # silencieuse), les fériés et jours exceptionnels restent actifs.
    feature_f20_enabled: Mapped[bool] = mapped_column(default=False)
    school_vacation_zone: Mapped[str | None] = mapped_column(String(1), nullable=True)

    # F24 (backlog-lot-ia-2.md §5, débloqué a posteriori) : comparaison de
    # prix multi-fournisseurs. Aucun nouveau champ de données requis —
    # `PriceHistory.supplier` (F1) porte déjà l'information par réception ;
    # ce flag gate uniquement l'agrégation en lecture (ai_supplier_price_
    # comparison.py), jamais un second schéma de fournisseurs.
    feature_f24_enabled: Mapped[bool] = mapped_column(default=False)

    # F27 : apprentissage statistique réel (lissage exponentiel triple,
    # paramètres appris par ingrédient — jamais une constante réglable
    # unique ici, contrairement à tous les flags précédents : c'est
    # justement la différence entre une règle et un modèle qui apprend).
    feature_f27_enabled: Mapped[bool] = mapped_column(default=False)

    # F23 (Lot IA-2, docs/feature-plans/backlog-lot-ia-2.md ticket 5) : cold
    # start d'un plat sans historique. `cold_start_smoothing_days` est la
    # constante de lissage du ticket (« combien de jours avant que le réel
    # pèse la moitié ») — valeur de départ raisonnée et vérifiée sur SYN-S
    # avant d'être figée (comme les autres seuils du projet, jamais une
    # intuition non vérifiée), réglable ensuite comme tous les seuils IA.
    feature_f23_enabled: Mapped[bool] = mapped_column(default=False)
    cold_start_smoothing_days: Mapped[float] = mapped_column(Float, default=14.0)

    # F15 (Lot IA-1) : « écart > 40%, réglable » (ia-f10-f19.md §6), même
    # principe que les seuils du Lot IA-0 (§8 des specs V2) — valeur de
    # départ raisonnée, jamais une constante figée.
    import_volume_alert_pct: Mapped[float] = mapped_column(Float, default=40.0)

    # F11 (Lot IA-1) : « un comptage complet reste imposé périodiquement
    # (défaut : toutes les 4 semaines, réglable) » (ia-f10-f19.md §2).
    full_count_interval_days: Mapped[float] = mapped_column(Float, default=28.0)
