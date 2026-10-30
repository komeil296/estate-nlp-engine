"""Typed domain models for Persian real-estate NLP."""

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Generic, Literal, TypeVar


FieldStatus = Literal[
    "extracted",
    "not_found",
    "ambiguous",
    "conflict",
]

DocumentType = Literal[
    "listing",
    "customer_requirement",
    "conversation",
    "unknown",
]

TransactionType = Literal[
    "sale",
    "rent",
    "temporary_rent",
    "presale",
    "partnership",
    "service",
    "unknown",
]

PropertyType = Literal[
    "apartment",
    "house",
    "villa",
    "land",
    "shop",
    "office",
    "workspace",
    "industrial",
    "suite",
    "other",
    "unknown",
]

RoomCount = Literal[
    "no_room",
    "one",
    "two",
    "three",
    "four",
    "five_or_more",
    "unknown",
]

SemanticRole = Literal[
    "asking_price",
    "budget",
    "deposit",
    "monthly_rent",
    "daily_rent",
    "weekend_rent",
    "special_day_rent",
    "price_per_sqm",
    "cost_per_extra_person",
    "unknown",
]

Currency = Literal["toman", "rial", "unspecified"]

Period = Literal[
    "day",
    "month",
    "year",
    "one_time",
    "unspecified",
]

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class FieldResult(Generic[T]):
    """A field value with evidence and ambiguity information."""

    value: T | None
    status: FieldStatus
    evidence: tuple[str, ...] = ()
    confidence: None = None
    candidates: tuple[T, ...] = ()

    def __post_init__(self):
        if self.status not in {
            "extracted", "not_found", "ambiguous", "conflict"
        }:
            raise ValueError("Invalid field status.")

        if self.confidence is not None:
            raise ValueError(
                "Confidence must remain None until calibration."
            )

        for item in self.evidence:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("Evidence entries must be non-empty strings.")

        for candidate in self.candidates:
            if candidate is None:
                raise ValueError("Candidates cannot contain None.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "status": self.status,
            "evidence": list(self.evidence),
            "confidence": None,
            "candidates": list(self.candidates),
        }


@dataclass(frozen=True, slots=True)
class Location:
    city: FieldResult[str]
    neighborhood: FieldResult[str]

    def to_dict(self):
        return {
            "city": self.city.to_dict(),
            "neighborhood": self.neighborhood.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class BuildingDetails:
    floor: FieldResult[str]
    total_floors: FieldResult[float]
    units_per_floor: FieldResult[float]
    construction_year: FieldResult[float]
    is_rebuilt: FieldResult[bool]
    deed_type: FieldResult[str]
    building_direction: FieldResult[str]
    floor_material: FieldResult[str]

    def to_dict(self):
        return {
            "floor": self.floor.to_dict(),
            "total_floors": self.total_floors.to_dict(),
            "units_per_floor": self.units_per_floor.to_dict(),
            "construction_year": self.construction_year.to_dict(),
            "is_rebuilt": self.is_rebuilt.to_dict(),
            "deed_type": self.deed_type.to_dict(),
            "building_direction": self.building_direction.to_dict(),
            "floor_material": self.floor_material.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class PropertyFeatures:
    parking: FieldResult[bool]
    elevator: FieldResult[bool]
    warehouse: FieldResult[bool]
    balcony: FieldResult[bool]
    pool: FieldResult[bool]
    jacuzzi: FieldResult[bool]
    sauna: FieldResult[bool]
    water: FieldResult[bool]
    electricity: FieldResult[bool]
    gas: FieldResult[bool]
    heating: FieldResult[bool]
    cooling: FieldResult[bool]
    restroom: FieldResult[bool]
    security_guard: FieldResult[bool]

    def to_dict(self):
        return {
            name: getattr(self, name).to_dict()
            for name in (
                "parking",
                "elevator",
                "warehouse",
                "balcony",
                "pool",
                "jacuzzi",
                "sauna",
                "water",
                "electricity",
                "gas",
                "heating",
                "cooling",
                "restroom",
                "security_guard",
            )
        }


@dataclass(frozen=True, slots=True)
class PropertyDetails:
    building_area_sqm: FieldResult[float]
    land_area_sqm: FieldResult[float]
    rooms: FieldResult[RoomCount]
    building: BuildingDetails
    features: PropertyFeatures

    def to_dict(self):
        return {
            "building_area_sqm": self.building_area_sqm.to_dict(),
            "land_area_sqm": self.land_area_sqm.to_dict(),
            "rooms": self.rooms.to_dict(),
            "building": self.building.to_dict(),
            "features": self.features.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class FinancialMention:
    semantic_role: SemanticRole
    raw_value: str
    normalized_value: int | float | None
    currency: Currency
    period: Period
    evidence: str

    def __post_init__(self):
        if not self.raw_value.strip():
            raise ValueError("Financial raw_value cannot be empty.")

        if not self.evidence.strip():
            raise ValueError("Financial evidence cannot be empty.")

        value = self.normalized_value

        if value is not None:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError("normalized_value must be numeric or None.")

            if not isfinite(value) or value < 0:
                raise ValueError("normalized_value must be finite and non-negative.")

        if self.currency not in {"toman", "rial", "unspecified"}:
            raise ValueError("Invalid currency.")

        if self.period not in {
            "day", "month", "year", "one_time", "unspecified"
        }:
            raise ValueError("Invalid financial period.")

        if self.semantic_role not in {
            "asking_price",
            "budget",
            "deposit",
            "monthly_rent",
            "daily_rent",
            "weekend_rent",
            "special_day_rent",
            "price_per_sqm",
            "cost_per_extra_person",
            "unknown",
        }:
            raise ValueError("Invalid financial semantic role.")

    def to_dict(self):
        return {
            "semantic_role": self.semantic_role,
            "raw_value": self.raw_value,
            "normalized_value": self.normalized_value,
            "currency": self.currency,
            "period": self.period,
            "evidence": self.evidence,
        }


@dataclass(frozen=True, slots=True)
class RentalConditions:
    allow_single_person: FieldResult[bool]

    def to_dict(self):
        return {
            "allow_single_person": self.allow_single_person.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class Provenance:
    source: str | None
    source_style: str | None
    source_row: int | None
    original_dataset_labels: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.source_row is not None:
            if (
                isinstance(self.source_row, bool)
                or not isinstance(self.source_row, int)
                or self.source_row < 1
            ):
                raise ValueError("source_row must be a positive integer or None.")

    def to_dict(self):
        return {
            "source": self.source,
            "source_style": self.source_style,
            "source_row": self.source_row,
            "original_dataset_labels": dict(self.original_dataset_labels),
        }


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    document_type: FieldResult[DocumentType]
    transaction_type: FieldResult[TransactionType]
    property_type: FieldResult[PropertyType]
    location: Location
    property: PropertyDetails
    financial_mentions: tuple[FinancialMention, ...]
    rental_conditions: RentalConditions
    provenance: Provenance
    schema_version: str = "0.2"

    def __post_init__(self):
        if self.schema_version != "0.2":
            raise ValueError("Unsupported schema version.")

    def to_dict(self):
        return {
            "schema_version": self.schema_version,
            "document_type": self.document_type.to_dict(),
            "transaction_type": self.transaction_type.to_dict(),
            "property_type": self.property_type.to_dict(),
            "location": self.location.to_dict(),
            "property": self.property.to_dict(),
            "financial_mentions": [
                item.to_dict()
                for item in self.financial_mentions
            ],
            "rental_conditions": self.rental_conditions.to_dict(),
            "provenance": self.provenance.to_dict(),
        }