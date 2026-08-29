from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ResolutionMethod(StrEnum):
    EXACT_GEO_ID = "EXACT_GEO_ID"
    EXACT_HIERARCHY = "EXACT_HIERARCHY"
    EXACT_ALIAS = "EXACT_ALIAS"
    FUZZY_FLAGGED = "FUZZY_FLAGGED"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"


class GeographicIdentity(BaseModel):
    geo_id: str
    state: str = "West Bengal"
    district: str
    subdivision: str | None = None
    locality: str
    locality_type: str
    census_code: str | None = None
    lgd_code: str | None = None
    block: str | None = None
    gram_panchayat: str | None = None
    municipality: str | None = None
    ward: str | None = None
    pin_codes: list[str] = Field(default_factory=list)
    latitude: float | None = None
    longitude: float | None = None
    aliases: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)
    osm_ids: list[str] = Field(default_factory=list)


class CurrentGeoEntity(BaseModel):
    canonical_current_id: str
    canonical_name: str
    entity_type: str
    parent_current_id: str | None = None
    district_current_id: str
    current_district: str
    official_code: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
    source_geo_id: str | None = None
    source: str
    payload: GeographicIdentity | None = None


class HistoricalGeoEntity(BaseModel):
    source: str
    source_geo_id: str
    source_name: str
    source_parent: str | None = None
    source_district: str
    observation_year: int


class GeoCrosswalk(BaseModel):
    source: str
    source_geo_id: str
    canonical_current_id: str
    relation: str
    confidence: float = Field(ge=0, le=1)
    effective_from: str | None = None
    effective_to: str | None = None
    notes: str


class GeographicResolution(BaseModel):
    query_state: str
    query_district: str | None = None
    query_locality: str
    resolved_geo_id: str | None = None
    resolution_method: ResolutionMethod
    confidence: float = Field(ge=0, le=1)
    source_ids: list[str] = Field(default_factory=list)
    matched_ids: dict[str, str] = Field(default_factory=dict)
    ambiguity_flags: list[str] = Field(default_factory=list)
    candidates: list[GeographicIdentity] = Field(default_factory=list)
